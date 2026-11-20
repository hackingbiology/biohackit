# SPDX-License-Identifier: AGPL-3.0-or-later
"""m00b — low-friction login: one test per SHALL scenario."""

import base64
import re
from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.core import mail
from django.test import Client, override_settings

from accounts.models import SocialHandle, User
from accounts.providers.discourse_connect import protocol

SECRET = "forum-shared-secret"
FORUM = "https://forum.rapamycin.news"
FORUM_SETTINGS = {
    "discourse_connect": {
        "APPS": [
            {
                "client_id": "rapamycin_news",
                "secret": SECRET,
                "settings": {"url": FORUM},
            }
        ]
    }
}
BASE = "/_allauth/browser/v1"
CALLBACK = "/accounts/discourse_connect/callback/"


def start(client) -> str:
    """Begin the DiscourseConnect flow; return the nonce sent to the forum."""
    r = client.post(
        f"{BASE}/auth/provider/redirect",
        {"provider": "discourse_connect", "callback_url": "/", "process": "login"},
    )
    assert r.status_code == 302
    assert r["Location"].startswith(f"{FORUM}/session/sso_provider?")
    q = parse_qs(urlparse(r["Location"]).query)
    sso, sig = q["sso"][0], q["sig"][0]
    assert sig == protocol.sign(SECRET, sso)
    return dict(parse_qsl(base64.b64decode(sso).decode()))["nonce"]


def forum_reply(nonce, secret=SECRET, **fields):
    data = {
        "nonce": nonce,
        "external_id": "42",
        "email": "forum@example.com",
        "username": "sirolimus_fan",
        "name": "Sir Olimus",
        **fields,
    }
    payload = base64.b64encode(urlencode(data).encode()).decode()
    return {"sso": payload, "sig": protocol.sign(secret, payload)}


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_discourse_valid_payload_logs_in_and_sets_handle():
    c = Client()
    nonce = start(c)
    r = c.get(CALLBACK, forum_reply(nonce))
    assert r.status_code == 302
    user = User.objects.get(email="forum@example.com")
    assert int(c.session["_auth_user_id"]) == user.pk
    h = SocialHandle.objects.get(profile__user=user, platform="rapamycin_news")
    assert h.handle == "sirolimus_fan"
    assert h.url == f"{FORUM}/u/sirolimus_fan"


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_discourse_bad_signature_rejected():
    c = Client()
    nonce = start(c)
    c.get(CALLBACK, forum_reply(nonce, secret="wrong"))
    assert not User.objects.filter(email="forum@example.com").exists()
    assert "_auth_user_id" not in c.session


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_discourse_replayed_nonce_rejected():
    c = Client()
    nonce = start(c)
    reply = forum_reply(nonce)
    c.get(CALLBACK, reply)
    c.post("/accounts/logout/")
    c.get(CALLBACK, reply)  # same signed payload again
    assert "_auth_user_id" not in c.session


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_discourse_expired_nonce_rejected():
    session = {}
    nonce = protocol.issue_nonce(session, "state", now=1000.0)
    reply = forum_reply(nonce)
    with pytest.raises(protocol.InvalidPayloadError):
        protocol.verify_response(
            SECRET, reply["sso"], reply["sig"], session, now=1000.0 + 601
        )


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_config_lists_only_configured_providers():
    ids = [
        p["id"]
        for p in Client()
        .get(f"{BASE}/config")
        .json()["data"]["socialaccount"]["providers"]
    ]
    assert ids == ["discourse_connect"]


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS={})
def test_config_works_with_zero_providers():
    r = Client().get(f"{BASE}/config")
    assert r.status_code == 200
    assert r.json()["data"]["socialaccount"]["providers"] == []


@pytest.mark.django_db
def test_login_by_code_flow():
    user = User.objects.create_user("code@example.com", "pw-not-used-12345")
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
    c = Client()
    r = c.post(
        f"{BASE}/auth/code/request",
        {"email": user.email},
        content_type="application/json",
    )
    assert r.status_code == 401  # pending flow: code entry
    code = re.search(r"\b([A-Z0-9]{4}-[A-Z0-9]{4})\b", mail.outbox[-1].body).group(1)
    r = c.post(
        f"{BASE}/auth/code/confirm", {"code": code}, content_type="application/json"
    )
    assert r.status_code == 200
    assert r.json()["meta"]["is_authenticated"] is True


@pytest.mark.django_db
def test_passkey_options_endpoint_reachable():
    r = Client().get(f"{BASE}/auth/webauthn/login")
    assert r.status_code == 200
    assert "request_options" in r.json()["data"]


def _existing_user():
    user = User.objects.create_user("forum@example.com", "pw-not-used-12345")
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
    return user


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_unverified_social_email_does_not_connect():
    existing = _existing_user()
    c = Client()
    nonce = start(c)
    c.get(CALLBACK, forum_reply(nonce, require_activation="true"))
    assert not SocialAccount.objects.filter(user=existing).exists()
    assert c.session.get("_auth_user_id") != str(existing.pk)


@pytest.mark.django_db
@override_settings(SOCIALACCOUNT_PROVIDERS=FORUM_SETTINGS)
def test_verified_social_email_connects_to_existing_account():
    existing = _existing_user()
    c = Client()
    nonce = start(c)
    c.get(CALLBACK, forum_reply(nonce))
    assert SocialAccount.objects.filter(user=existing).count() == 1
    assert c.session["_auth_user_id"] == str(existing.pk)


def test_requested_scopes_are_identity_only(monkeypatch):
    import importlib

    from django.conf import settings

    for k, v in {
        "GOOGLE": 1,
        "MICROSOFT": 1,
        "APPLE": 1,
        "FACEBOOK": 1,
        "WEIXIN": 1,
    }.items():
        monkeypatch.setenv(f"{k}_CLIENT_ID", "id")
        monkeypatch.setenv(f"{k}_SECRET", "s")
    monkeypatch.setenv("RAPAMYCIN_NEWS_URL", FORUM)
    monkeypatch.setenv("RAPAMYCIN_NEWS_SSO_SECRET", SECRET)
    mod = importlib.import_module("biohackit.settings")
    built = mod._build_social_providers()
    assert set(built) == {
        "google",
        "microsoft",
        "apple",
        "facebook",
        "weixin",
        "discourse_connect",
    }
    allowed = {"profile", "email", "openid", "name", "User.Read", "snsapi_login"}
    for pid, cfg in built.items():
        assert set(cfg.get("SCOPE", [])) <= allowed, pid
    assert settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION is True
