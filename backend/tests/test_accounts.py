# SPDX-License-Identifier: AGPL-3.0-or-later
import pytest
from rest_framework.test import APIClient

from accounts.models import Profile, SocialHandle, User

PW = "correct-horse-battery-9"


@pytest.fixture
def client():
    return APIClient()


def register(client, email="a@example.com", **extra):
    return client.post(
        "/api/auth/register/",
        {"email": email, "password": PW, **extra},
        format="json",
    )


@pytest.mark.django_db
def test_register_creates_user(client):
    r = register(client)
    assert r.status_code == 201
    assert User.objects.filter(email="a@example.com").exists()
    assert Profile.objects.get(user__email="a@example.com").is_public is True


@pytest.mark.django_db
def test_register_requires_email(client):
    r = client.post("/api/auth/register/", {"password": PW}, format="json")
    assert r.status_code == 400


@pytest.mark.django_db
def test_login_returns_jwt(client):
    register(client)
    r = client.post(
        "/api/auth/token/", {"email": "a@example.com", "password": PW}, format="json"
    )
    assert r.status_code == 200
    assert "access" in r.data and "refresh" in r.data


@pytest.mark.django_db
def test_refresh_token(client):
    register(client)
    tok = client.post(
        "/api/auth/token/", {"email": "a@example.com", "password": PW}, format="json"
    ).data
    r = client.post(
        "/api/auth/token/refresh/", {"refresh": tok["refresh"]}, format="json"
    )
    assert r.status_code == 200
    assert "access" in r.data


@pytest.mark.django_db
def test_public_profile_readable_without_auth(client):
    register(client, display_name="alice")
    r = client.get("/api/profiles/alice/")
    assert r.status_code == 200
    assert r.data["display_name"] == "alice"


@pytest.mark.django_db
def test_profile_biological_attributes(client):
    register(client, display_name="bob")
    Profile.objects.filter(display_name="bob").update(
        date_of_birth="1980-05-01", sex="M", height_cm="180.5", ethnicity="Italian"
    )
    d = client.get("/api/profiles/bob/").data
    assert d["date_of_birth"] == "1980-05-01"
    assert d["sex"] == "M"
    assert d["height_cm"] == "180.5"
    assert d["ethnicity"] == "Italian"


@pytest.mark.django_db
def test_social_handles_created(client):
    register(client, display_name="carol")
    p = Profile.objects.get(display_name="carol")
    SocialHandle.objects.create(profile=p, platform="telegram", handle="@carol")
    SocialHandle.objects.create(profile=p, platform="rapamycin_news", handle="carol1")
    platforms = {
        h["platform"] for h in client.get("/api/profiles/carol/").data["social_handles"]
    }
    assert platforms == {"telegram", "rapamycin_news"}


@pytest.mark.django_db
def test_private_write_requires_auth(client):
    register(client)
    assert client.get("/api/auth/me/").status_code == 401


@pytest.mark.django_db
def test_me_with_token(client):
    register(client)
    tok = client.post(
        "/api/auth/token/", {"email": "a@example.com", "password": PW}, format="json"
    ).data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok}")
    r = client.get("/api/auth/me/")
    assert r.status_code == 200 and r.data["email"] == "a@example.com"


@pytest.mark.django_db
def test_non_public_profile_hidden(client):
    register(client, display_name="dan")
    Profile.objects.filter(display_name="dan").update(is_public=False)
    assert client.get("/api/profiles/dan/").status_code == 404
