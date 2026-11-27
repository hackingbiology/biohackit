# SPDX-License-Identifier: AGPL-3.0-or-later
"""Protocol and ProtocolVersion API (M03 TG-f part 1). Synthetic values only."""

from datetime import timedelta
from typing import Any

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import User
from protocols.models import (
    ChangeEvent,
    ImmutableRecordError,
    Protocol,
    ProtocolVersion,
)

URL = "/api/protocols/"
RAPA = {"name": "synthetic-drug-x", "amount": "6", "unit": "mg", "schedule": "weekly"}


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def other(db):
    return User.objects.create_user(email="b@example.com", password="correct-horse-9")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


def _create(client: APIClient, **extra: Any) -> dict[str, Any]:
    body = {
        "title": "Synthetic protocol",
        "level": "research",
        "interventions": [RAPA],
        **extra,
    }
    response = client.post(URL, body, format="json")
    assert response.status_code == 201, response.content
    return response.json()


def _active(client: APIClient) -> int:
    pid = _create(client)["id"]
    r = client.patch(
        f"{URL}{pid}/", {"state": "active", "reason": "start"}, format="json"
    )
    assert r.status_code == 200, r.content
    return pid


def _dose(client: APIClient, pid: int, amount: str, reason: str | None = "dose up"):
    body: dict[str, Any] = {"interventions": [{**RAPA, "amount": amount}]}
    if reason is not None:
        body["reason"] = reason
    return client.patch(f"{URL}{pid}/", body, format="json")


# scenario: protocols::draft-saved-incrementally
def test_draft_saved_incrementally_lists_what_is_missing(client):
    created = client.post(URL, {"title": "Half done"}, format="json").json()
    assert created["state"] == "draft" and created["level"] == ""
    assert "No interventions yet." in created["missing"]
    assert "No efficacy markers yet." in created["missing"]
    assert "No goal yet." in created["missing"]
    r = client.patch(
        f"{URL}{created['id']}/",
        {"measures": [{"loinc_code": "0000-0", "purpose": "efficacy"}], "goals": ["g"]},
        format="json",
    )
    assert r.status_code == 200
    assert "No efficacy markers yet." not in r.json()["missing"]
    assert "No goal yet." not in r.json()["missing"]
    assert ProtocolVersion.objects.count() == 0


# scenario: protocols::a-saved-draft-is-editable-in-place
def test_draft_edited_three_times_has_no_version_and_needs_no_reason(client):
    pid = client.post(URL, {"title": "T"}, format="json").json()["id"]
    for amount in ("1", "2", "3"):
        r = _dose(client, pid, amount, reason=None)
        assert r.status_code == 200 and r.json()["interventions"][0]["amount"] == amount
    assert ProtocolVersion.objects.count() == 0
    assert Protocol.objects.get(pk=pid).state == "draft"


# scenario: protocols::a-change-without-a-reason-is-refused
def test_leaving_draft_without_reason_is_refused(client):
    pid = _create(client)["id"]
    for body in ({"state": "active"}, {"state": "active", "reason": "   "}):
        assert client.patch(f"{URL}{pid}/", body, format="json").status_code == 400
    assert Protocol.objects.get(pk=pid).state == "draft"
    assert ProtocolVersion.objects.count() == 0


# scenario: protocols::a-change-without-a-reason-is-refused
def test_facet_change_without_reason_leaves_version_unchanged(client):
    pid = _active(client)
    before = client.get(f"{URL}{pid}/versions/1/").json()
    assert _dose(client, pid, "8", reason=None).status_code == 400
    assert _dose(client, pid, "8", reason="   ").status_code == 400
    assert ProtocolVersion.objects.filter(protocol_id=pid).count() == 1
    assert client.get(f"{URL}{pid}/versions/1/").json() == before


def test_leaving_draft_needs_a_level_chosen_by_the_user(client):
    pid = client.post(URL, {"title": "T"}, format="json").json()["id"]
    r = client.patch(f"{URL}{pid}/", {"state": "active", "reason": "go"}, format="json")
    assert r.status_code == 400 and "level" in r.json()
    assert Protocol.objects.get(pk=pid).state == "draft"


# scenario: protocols::a-dose-change-is-a-tracked-event
def test_dose_change_creates_version_with_change_event(client, user):
    pid = _active(client)
    before = client.get(f"{URL}{pid}/versions/1/").json()
    assert _dose(client, pid, "8", reason=None).status_code == 400
    assert _dose(client, pid, "8", reason="  ").status_code == 400
    assert ProtocolVersion.objects.filter(protocol_id=pid).count() == 1
    r = _dose(client, pid, "8", reason="response was weak")
    assert r.status_code == 200 and r.json()["latest_version"] == 2
    (event,) = r.json()["version"]["events"]
    assert event["field"] == "interventions[0].amount"
    assert (event["old"], event["new"]) == ("6", "8")
    assert event["reason"] == "response was weak" and event["actor"] == user.pk
    assert event["timestamp"]
    assert client.get(f"{URL}{pid}/versions/1/").json() == before
    assert before["snapshot"]["interventions"][0]["amount"] == "6"


# scenario: protocols::diff-between-versions
def test_diff_between_versions_is_exact(client):
    pid = _active(client)
    _dose(client, pid, "8")
    r = client.get(f"{URL}{pid}/diff/?from=1&to=2")
    assert r.status_code == 200
    body = r.json()
    assert body["changes"] == [{"field": "doses[0].amount", "old": "6", "new": "8"}]
    assert body["facets"]["interventions"] == {"changed": False, "unified": []}
    assert body["facets"]["doses"]["unified"] == [
        "--- v1",
        "+++ v2",
        "@@ -1,6 +1,6 @@",
        " [",
        "   {",
        '-    "amount": "6",',
        '+    "amount": "8",',
        '     "name": "synthetic-drug-x",',
        '     "unit": "mg"',
        "   }",
    ]
    assert client.get(f"{URL}{pid}/diff/?from=1").status_code == 400
    assert client.get(f"{URL}{pid}/diff/?from=1&to=9").status_code == 404


def test_diff_uses_stdlib_difflib_and_no_new_dependency():
    import protocols.diffing as diffing

    assert diffing.difflib.__name__ == "difflib"


# scenario: protocols::an-older-version-cannot-be-edited
def test_older_version_cannot_be_edited_by_api_or_orm(client):
    pid = _active(client)
    _dose(client, pid, "8")
    before = client.get(f"{URL}{pid}/versions/1/").json()
    url = f"{URL}{pid}/versions/1/"
    assert client.patch(url, {"reason": "x"}, format="json").status_code == 405
    assert client.put(url, {}, format="json").status_code == 405
    assert client.delete(url).status_code == 405
    assert client.get(url).json() == before
    version = ProtocolVersion.objects.get(protocol_id=pid, number=1)
    version.reason = "rewritten"
    with pytest.raises(ImmutableRecordError):
        version.save()
    with pytest.raises(ImmutableRecordError):
        ProtocolVersion.objects.filter(protocol_id=pid).update(reason="x")
    with pytest.raises(ImmutableRecordError):
        ProtocolVersion.objects.filter(protocol_id=pid).delete()
    with pytest.raises(ImmutableRecordError):
        version.delete()
    event = ChangeEvent.objects.first()
    assert event is not None
    with pytest.raises(ImmutableRecordError):
        event.save()
    with pytest.raises(ImmutableRecordError):
        ChangeEvent.objects.update(reason="x")
    assert client.get(url).json() == before


# scenario: protocols::an-older-version-cannot-be-edited
@pytest.mark.django_db(transaction=True)
def test_new_instance_with_existing_pk_cannot_overwrite_a_version(client):
    from django.db import IntegrityError

    pid = _active(client)
    stored = ProtocolVersion.objects.get(protocol_id=pid, number=1)
    clone = ProtocolVersion(
        id=stored.id,
        protocol=stored.protocol,
        number=99,
        snapshot={},
        created_at=stored.created_at,
        actor=stored.actor,
        reason="overwritten",
    )
    with pytest.raises(IntegrityError):
        clone.save()
    stored.refresh_from_db()
    assert stored.number == 1
    assert stored.reason != "overwritten"


# scenario: protocols::editing-the-latest-version-creates-a-new-version
def test_correcting_version_two_creates_version_three(client):
    pid = _active(client)
    _dose(client, pid, "8")
    v2 = client.get(f"{URL}{pid}/versions/2/").json()
    r = _dose(client, pid, "7", reason="typo in v2")
    assert r.json()["latest_version"] == 3
    assert client.get(f"{URL}{pid}/versions/2/").json() == v2
    v3 = client.get(f"{URL}{pid}/versions/3/").json()
    assert v3["reason"] == "typo in v2"
    assert v3["snapshot"]["interventions"][0]["amount"] == "7"
    assert len(client.get(f"{URL}{pid}/versions/").json()) == 3


def test_pause_is_versioned_and_unchanged_edit_is_refused(client):
    pid = _active(client)
    r = client.patch(
        f"{URL}{pid}/", {"state": "paused", "reason": "travel"}, format="json"
    )
    assert r.json()["version"]["events"][0]["field"] == "state"
    assert (
        client.patch(
            f"{URL}{pid}/", {"state": "paused", "reason": "again"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"{URL}{pid}/", {"state": "draft", "reason": "no"}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.patch(
            f"{URL}{pid}/", {"in_effect_since": "2026-01-01"}, format="json"
        ).status_code
        == 400
    )


# scenario: protocols::baseline-capture-for-someone-mid-protocol
def test_import_already_running_is_active_with_version_one(client):
    since = (timezone.localdate() - timedelta(days=90)).isoformat()
    data = _create(
        client, already_running=True, in_effect_since=since, reason="started in spring"
    )
    assert data["state"] == "active" and data["in_effect_since"] == since
    assert data["tracked_since"] == timezone.localdate().isoformat()
    assert data["history"] == "analytic"
    assert data["version"]["number"] == 1
    assert data["version"]["reason"] == "imported as already running. started in spring"
    assert "invited, not required" in data["notes"][0]
    future = (timezone.localdate() + timedelta(days=1)).isoformat()
    for bad in ({}, {"in_effect_since": future}):
        r = client.post(
            URL,
            {"title": "T", "level": "medical", "already_running": True, **bad},
            format="json",
        )
        assert r.status_code == 400
    assert Protocol.objects.count() == 1


# scenario: protocols::synthesized-history-when-reconstruction-is-hard
def test_synthesized_history_stores_lineage_note(client):
    since = (timezone.localdate() - timedelta(days=400)).isoformat()
    data = _create(
        client,
        already_running=True,
        in_effect_since=since,
        history="synthesized",
        lineage_note="Started low, raised twice; I do not remember when.",
    )
    assert data["history"] == "synthesized"
    assert data["lineage_note"].startswith("Started low")
    got = client.get(f"{URL}{data['id']}/").json()
    assert (
        got["history"] == "synthesized" and got["lineage_note"] == data["lineage_note"]
    )
    r = client.post(URL, {"title": "T", "lineage_note": "n"}, format="json")
    assert r.status_code == 400


def test_owner_isolation_and_curated_origin(client, other):
    pid = _active(client)
    _dose(client, pid, "8")
    stranger = APIClient()
    stranger.force_authenticate(other)
    for url in (
        f"{URL}{pid}/",
        f"{URL}{pid}/versions/",
        f"{URL}{pid}/versions/1/",
        f"{URL}{pid}/diff/?from=1&to=2",
    ):
        assert stranger.get(url).status_code == 404
    assert (
        stranger.patch(
            f"{URL}{pid}/", {"title": "x", "reason": "r"}, format="json"
        ).status_code
        == 404
    )
    assert stranger.get(URL).json() == []
    assert (
        client.post(URL, {"title": "T", "origin": "curated"}, format="json").status_code
        == 403
    )
    assert APIClient().get(URL).status_code in (401, 403)
    other.is_staff = True
    other.save()
    r = stranger.post(URL, {"title": "T", "origin": "curated"}, format="json")
    assert r.status_code == 201 and r.json()["origin"] == "curated"


def test_facet_validation_keeps_amounts_exact(client):
    bad = [
        {"interventions": [{"name": "x", "amount": 6, "unit": "mg"}]},
        {"interventions": [{"name": "x", "amount": "NaN", "unit": "mg"}]},
        {"interventions": [{"name": "x", "amount": "-1", "unit": "mg"}]},
        {"interventions": [{"name": "x", "amount": "1"}]},
        {"interventions": [{"name": "x", "dose": "1"}]},
        {"cycles": [{"label": "c", "on_days": True, "off_days": 1}]},
        {"measures": [{"loinc_code": "0000-0", "purpose": "other"}]},
        {"goals": [""]},
        {"colour": "red"},
    ]
    for body in bad:
        assert (
            client.post(URL, {"title": "T", **body}, format="json").status_code == 400
        ), body
    ok = client.post(
        URL,
        {
            "title": "T",
            "interventions": [{"name": "x", "amount": "0.10", "unit": "mg"}],
        },
        format="json",
    )
    assert ok.json()["interventions"][0]["amount"] == "0.10"
    assert Protocol.objects.count() == 1


def _iv(**kw: Any) -> list[dict[str, Any]]:
    return [{"name": "n", "amount": "1", "unit": "mg", **kw}]


BAD_CREATE: list[dict[str, Any]] = [
    {"title": "t", "interventions": "x"},
    {"title": "t", "interventions": ["x"]},
    {"title": "t", "interventions": _iv(bogus=1)},
    {"title": "t", "interventions": [{"amount": "1", "unit": "mg"}]},
    {"title": "t", "interventions": _iv(name=5)},
    {"title": "t", "interventions": _iv(name="a" * 501)},
    {"title": "t", "interventions": _iv(name="  ")},
    {"title": "t", "interventions": _iv(amount=6)},
    {"title": "t", "interventions": _iv(amount="abc")},
    {"title": "t", "interventions": _iv(amount="-1")},
    {"title": "t", "interventions": _iv(amount="NaN")},
    {"title": "t", "cycles": [{"label": "c", "on_days": True, "off_days": 1}]},
    {"title": "t", "cycles": [{"label": "c", "on_days": -1, "off_days": 1}]},
    {"title": "t", "measures": [{"loinc_code": "x", "purpose": "other"}]},
    {"title": "t", "goals": [1]},
    {"title": "t", "level": "other"},
    {"title": "t", "in_effect_since": "not-a-date"},
    {"title": "t", "in_effect_since": "2026-13-45"},
    {"title": "t", "in_effect_since": 5},
    {"title": "t", "lineage_note": 5},
    {"title": "t", "reason": 5},
    {"title": "t", "origin": "other"},
    {"title": "t", "already_running": "yes"},
    {"title": "t", "state": "active"},
    {"title": "t", "bogus": 1},
    {"level": "research"},
    {"title": 5},
    {"title": "t", "history": "other"},
]


@pytest.mark.parametrize("body", BAD_CREATE)
def test_invalid_input_is_a_400_and_creates_nothing(client, body):
    response = client.post(URL, body, format="json")
    assert response.status_code == 400, response.content
    assert Protocol.objects.count() == 0
