# SPDX-License-Identifier: AGPL-3.0-or-later
"""Publish with per-item withhold, origin and level (M03 TG-k). Synthetic data."""

from typing import Any

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from accounts.models import User
from protocols.models import ChangeEvent, Protocol, ProtocolVersion, Publication

URL = "/api/protocols/"
PUBLIC = "/api/public/protocols/"
SECRET = "Secret LOINC 99999-9"


def _user(email: str, staff: bool = False) -> APIClient:
    c = APIClient()
    user = User.objects.create_user(email=email, password="correct-horse-9")
    if staff:
        user.is_staff = True
        user.save()
    c.force_authenticate(user)
    return c


@pytest.fixture
def owner(db):
    return _user("o@example.com")


def _active(client: APIClient, **extra: Any) -> int:
    body = {
        "title": "Synth protocol",
        "level": "medical",
        "interventions": [
            {"name": "Synth A", "amount": "1", "unit": "mg"},
            {"name": "Synth B", "genomic": True},
        ],
        "measures": [
            {"loinc_code": "11111-1", "purpose": "efficacy"},
            {"loinc_code": SECRET, "purpose": "safety"},
            {"loinc_code": "22222-2", "purpose": "baseline", "genomic": True},
        ],
        **extra,
    }
    r = client.post(URL, body, format="json")
    assert r.status_code == 201, r.content
    pid = r.json()["id"]
    r = client.patch(
        URL + f"{pid}/", {"state": "active", "reason": "go"}, format="json"
    )
    assert r.status_code == 200, r.content
    return int(pid)


def _publish(client, pid, **extra):
    return client.post(
        f"{URL}{pid}/publish/", {"reason": "share", **extra}, format="json"
    )


# scenario: protocols::public-by-default-withhold-one-marker
def test_public_by_default_withholding_one_marker(owner):
    pid = _active(owner)
    r = _publish(owner, pid, withheld_items=["measures[1]"])
    assert r.status_code == 200, r.content
    body = APIClient().get(f"{PUBLIC}{pid}/").json()
    assert [i["name"] for i in body["interventions"]] == ["Synth A"]
    assert [m["loinc_code"] for m in body["measures"]] == ["11111-1"]
    assert SECRET not in str(body) and "measures[1]" not in str(body)
    assert body["origin"] == "community" and body["level"] == "medical"
    assert "o@example.com" not in str(body)
    assert "owner" not in body


def test_genomic_item_is_never_public(owner):
    pid = _active(owner)
    _publish(owner, pid)
    body = APIClient().get(f"{PUBLIC}{pid}/").json()
    assert "Synth B" not in str(body) and "22222-2" not in str(body)
    assert len(body["measures"]) == 2


def test_draft_and_unpublished_and_foreign_are_hidden(owner):
    draft = owner.post(URL, {"title": "D"}, format="json").json()["id"]
    assert _publish(owner, draft).status_code == 400
    anon = APIClient()
    assert anon.get(f"{PUBLIC}{draft}/").status_code == 404
    pid = _active(owner)
    assert anon.get(f"{PUBLIC}{pid}/").status_code == 404
    assert anon.get(PUBLIC).json() == []
    _publish(owner, pid)
    assert [p["id"] for p in anon.get(PUBLIC).json()] == [pid]
    other = _user("x@example.com")
    assert _publish(other, pid).status_code == 404
    assert (
        other.post(f"{URL}{pid}/unpublish/", {"reason": "r"}, format="json").status_code
        == 404
    )
    owner.post(f"{URL}{pid}/unpublish/", {"reason": "back"}, format="json")
    assert anon.get(f"{PUBLIC}{pid}/").status_code == 404
    assert anon.get(PUBLIC).json() == []


def test_reason_required_and_events_recorded_versions_untouched(owner):
    pid = _active(owner)
    assert owner.post(f"{URL}{pid}/publish/", {}, format="json").status_code == 400
    assert not Publication.objects.exists()
    before = list(ProtocolVersion.objects.values("id", "snapshot", "reason"))
    assert _publish(owner, pid).status_code == 200
    assert owner.post(f"{URL}{pid}/unpublish/", {}, format="json").status_code == 400
    assert Publication.objects.get().published is True
    owner.post(f"{URL}{pid}/unpublish/", {"reason": "stop"}, format="json")
    events = ChangeEvent.objects.filter(field="publication")
    assert [e.reason for e in events] == ["share", "stop"]
    assert events[1].new["published"] is False
    assert list(ProtocolVersion.objects.values("id", "snapshot", "reason")) == before
    assert (
        owner.post(
            f"{URL}{pid}/unpublish/", {"reason": "again"}, format="json"
        ).status_code
        == 400
    )


def test_bad_withheld_items_are_refused(owner):
    pid = _active(owner)
    for bad in (["measures[9]"], "measures[0]", ["foo"], [3]):
        assert _publish(owner, pid, withheld_items=bad).status_code == 400
    assert _publish(owner, pid, unknown=1).status_code == 400


def test_public_view_stays_on_pinned_version_until_republished(owner):
    pid = _active(owner)
    _publish(owner, pid)
    r = owner.patch(URL + f"{pid}/", {"title": "Renamed", "reason": "r"}, format="json")
    assert r.status_code == 200
    anon = APIClient()
    assert anon.get(f"{PUBLIC}{pid}/").json()["title"] == "Synth protocol"
    _publish(owner, pid, withheld_items=["interventions[0]"])
    body = anon.get(f"{PUBLIC}{pid}/").json()
    assert body["title"] == "Renamed" and body["published_version"] == 2
    assert body["interventions"] == []


def test_only_staff_set_curated_and_origin_level_everywhere(owner):
    r = owner.post(URL, {"title": "C", "origin": "curated"}, format="json")
    assert r.status_code == 403
    staff = _user("s@example.com", staff=True)
    pid = _active(staff, origin="curated", title="Curated synth")
    _publish(staff, pid)
    assert APIClient().get(f"{PUBLIC}{pid}/").json()["origin"] == "curated"
    assert APIClient().get(PUBLIC).json()[0]["level"] == "medical"
    row = staff.get(URL).json()[0]
    assert row["origin"] == "curated" and row["level"] == "medical"
    assert staff.get(f"{URL}{pid}/").json()["origin"] == "curated"
    version = staff.get(f"{URL}{pid}/versions/").json()[0]
    assert version["origin"] == "curated" and version["level"] == "medical"
    one = staff.get(f"{URL}{pid}/versions/1/").json()
    assert one["origin"] == "curated" and one["level"] == "medical"


def test_genomic_flag_must_be_boolean(owner):
    r = owner.post(
        URL,
        {
            "title": "G",
            "measures": [
                {"loinc_code": "1-1", "purpose": "baseline", "genomic": "yes"}
            ],
        },
        format="json",
    )
    assert r.status_code == 400 and "genomic" in str(r.json())


def test_public_endpoints_are_throttled_and_read_only(owner, monkeypatch):
    rates = {**ScopedRateThrottle.THROTTLE_RATES, "public_protocols": "2/min"}
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", rates)
    cache.clear()
    anon = APIClient()
    codes = [anon.get(PUBLIC).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    cache.clear()
    assert anon.post(PUBLIC, {}, format="json").status_code == 405
    assert Protocol.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_account_erasure_removes_published_protocol():
    # Q57: erasing the account must not be blocked by a Publication.
    user = User.objects.create_user(email="e@example.com", password="correct-horse-9")
    client = APIClient()
    client.force_authenticate(user)
    pid = _active(client)
    assert _publish(client, pid).status_code == 200
    body = {"choice": "delete_everything", "confirm": True}
    r = client.post("/api/auth/me/erase/", body, format="json")
    assert r.status_code == 200, r.content
    assert not Protocol.objects.exists()
    assert not ProtocolVersion.objects.exists()
    assert not Publication.objects.exists()


def test_republish_without_withheld_items_keeps_earlier_withholds(owner):
    pid = _active(owner)
    _publish(owner, pid, withheld_items=["measures[1]"])
    owner.patch(URL + f"{pid}/", {"title": "Renamed", "reason": "r"}, format="json")
    assert _publish(owner, pid).status_code == 200
    body = APIClient().get(f"{PUBLIC}{pid}/").json()
    assert SECRET not in str(body) and body["title"] == "Renamed"
    assert _publish(owner, pid, withheld_items=[]).status_code == 200
    assert SECRET in str(APIClient().get(f"{PUBLIC}{pid}/").json())


def test_republish_refused_when_earlier_withholds_no_longer_match(owner):
    pid = _active(owner)
    _publish(owner, pid, withheld_items=["measures[1]"])
    measures = [{"loinc_code": "33333-3", "purpose": "efficacy"}]
    r = owner.patch(
        URL + f"{pid}/", {"measures": measures, "reason": "r"}, format="json"
    )
    assert r.status_code == 200, r.content
    assert _publish(owner, pid).status_code == 400
    assert Publication.objects.get().version.number == 1


def test_public_view_shows_live_state(owner):
    pid = _active(owner)
    _publish(owner, pid)
    r = owner.patch(URL + f"{pid}/", {"state": "paused", "reason": "r"}, format="json")
    assert r.status_code == 200, r.content
    assert APIClient().get(f"{PUBLIC}{pid}/").json()["state"] == "paused"
