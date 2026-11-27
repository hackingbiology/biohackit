# SPDX-License-Identifier: AGPL-3.0-or-later
"""Batch resolve, staged commit, constrained-column validator, throttles (M03 TG-c).
Synthetic values only."""

import pytest
from django.conf import settings
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from accounts.models import User
from substances.models import (
    CodeSystem,
    Extraction,
    ExtractionAmbiguity,
    Substance,
    SubstanceCode,
    SubstanceReviewItem,
    SubstanceSynonym,
)
from substances.validator import validate_proposal

URL = "/api/substances/extractions/"


@pytest.fixture
def reviewer(db) -> User:
    return User.objects.create_user(
        email="rev@example.com", password="correct-horse-9", is_staff=True
    )


@pytest.fixture
def owner(db) -> User:
    return User.objects.create_user(email="o@example.com", password="correct-horse-9")


@pytest.fixture
def client(owner: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(owner)
    return c


@pytest.fixture
def substance(db) -> Substance:
    s = Substance.objects.create(name="Synthetic test substance")
    SubstanceCode.objects.create(
        substance=s,
        system="rxcui",
        code="SYNTHETIC-TEST-CODE",
        source="synthetic test source",
        fetched_on="2026-01-02",
    )
    return s


def _reviewed(substance: Substance, name: str, user: User | None) -> SubstanceSynonym:
    return SubstanceSynonym.objects.create(
        substance=substance,
        name=name,
        normalised_name=name.casefold(),
        language="en",
        source="synthetic test source",
        reviewer=user,
        reviewed_at=timezone.now() if user else None,
    )


def _submit(client: APIClient, entries: list[dict]):
    return client.post(URL, {"entries": entries}, format="json")


def _eight(substance: Substance, reviewer: User) -> list[dict]:
    for i in range(5):
        _reviewed(substance, f"known{i}", reviewer)
    return [{"name": f"known{i}"} for i in range(5)] + [
        {"name": f"stranger{i}"} for i in range(3)
    ]


def test_eight_in_five_recognised_then_correct_or_confirm(client, substance, reviewer):
    # scenario: interventions-and-catalog::8-in-5-recognised
    # scenario: interventions-and-catalog::unresolved-substance-is-surfaced-not-dropped
    body = _submit(client, _eight(substance, reviewer)).json()
    assert (body["submitted"], body["recognised"], body["not_understood"]) == (8, 5, 3)
    lost = [i for i in body["items"] if i["status"] == "not_understood"]
    assert [i["submitted_name"] for i in lost] == [
        "stranger0",
        "stranger1",
        "stranger2",
    ]
    assert all(i["review_item_id"] for i in lost)
    assert SubstanceReviewItem.objects.filter(status="open").count() == 3
    # nothing is committed or attached
    assert Extraction.objects.get().committed_at is None
    assert not substance.synonyms.filter(name__startswith="stranger").exists()

    base = f"{URL}{body['id']}/"
    assert client.post(f"{base}commit/").status_code == 400
    first, second, third = (i["id"] for i in lost)
    ok = client.post(
        f"{base}items/{first}/decide/",
        {"decision": "corrected", "substance": substance.pk},
        format="json",
    )
    assert ok.status_code == 200
    assert ok.json()["decided_substance"] == substance.pk
    client.post(
        f"{base}items/{second}/decide/", {"decision": "left_out"}, format="json"
    )
    refused = client.post(f"{base}commit/")
    assert refused.status_code == 400
    assert "1 name" in refused.json()["detail"]
    client.post(f"{base}items/{third}/decide/", {"decision": "left_out"}, format="json")
    done = client.post(f"{base}commit/")
    assert done.status_code == 200
    assert done.json()["committed_at"]
    # a correction is not a reviewed synonym (Q122)
    assert not SubstanceSynonym.objects.filter(name="stranger0").exists()
    assert client.post(f"{base}commit/").status_code == 400
    assert (
        client.post(
            f"{base}items/{first}/decide/", {"decision": "left_out"}, format="json"
        ).status_code
        == 400
    )


def test_decide_validation(client, substance, reviewer):
    body = _submit(client, [{"name": "zzz"}, {"name": "known"}]).json()
    _reviewed(substance, "known", reviewer)
    base = f"{URL}{body['id']}/items/"
    zzz = body["items"][0]["id"]
    for bad in (
        {"decision": "maybe"},
        {"decision": "corrected"},
        {"decision": "corrected", "substance": True},
        {"decision": "corrected", "substance": 0},
    ):
        assert (
            client.post(f"{base}{zzz}/decide/", bad, format="json").status_code == 400
        )
    # a name that was recognised cannot be overridden
    body2 = _submit(client, [{"name": "known"}]).json()
    known = body2["items"][0]["id"]
    resp = client.post(
        f"{URL}{body2['id']}/items/{known}/decide/",
        {"decision": "left_out"},
        format="json",
    )
    assert resp.status_code == 400


def test_duplicate_names_count_each_and_share_one_decision(client, substance):
    body = _submit(
        client, [{"name": "Dup"}, {"name": " dup "}, {"name": "other"}]
    ).json()
    assert (body["submitted"], body["recognised"], body["not_understood"]) == (3, 0, 3)
    ids = [i["id"] for i in body["items"]]
    base = f"{URL}{body['id']}/"
    client.post(
        f"{base}items/{ids[0]}/decide/", {"decision": "left_out"}, format="json"
    )
    after = client.get(base).json()["items"]
    assert [i["decision"] for i in after] == ["left_out", "left_out", ""]


def test_submit_validation(client, monkeypatch):
    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {"substance_extraction": "1000/min"}
    )
    too_many = [{"name": f"n{i}"} for i in range(51)]
    for bad in (
        [],
        "x",
        ["x"],
        [{"name": 1}],
        [{"name": "a", "proposed": []}],
        [{"name": "a", "language": 3}],
        [{"name": "a", "proposed": {"notes": "a\x00b"}}],
        [{"name": ""}],
        [{"name": "a" * 201}],
        too_many,
    ):
        resp = client.post(URL, {"entries": bad}, format="json")
        assert resp.status_code == 400
    assert not Extraction.objects.exists()
    assert client.post(URL, ["x"], format="json").status_code == 400


def test_overlong_and_out_of_enum_become_ambiguous_with_siblings_kept(
    client, substance, reviewer
):
    # scenario: interventions-and-catalog::over-long-model-output-does-not-corrupt-persistence
    _reviewed(substance, "known", reviewer)
    long_code = "C" * 65
    bad_enum = "not-a-system"
    body = _submit(
        client,
        [
            {
                "name": "known",
                "proposed": {
                    "code": long_code,
                    "system": bad_enum,
                    "source": "synthetic source",
                },
            },
            {"name": "sibling", "proposed": {"system": "atc", "code": "X1"}},
        ],
    ).json()
    first, second = body["items"]
    assert first["accepted_fields"] == {"source": "synthetic source"}
    by_field = {a["field"]: a for a in first["ambiguous"]}
    assert by_field["code"]["value"] == long_code
    assert by_field["code"]["reason"] == "too_long"
    assert by_field["system"]["value"] == bad_enum
    assert by_field["system"]["reason"] == "not_in_enum"
    assert ExtractionAmbiguity.objects.get(field="code").value == long_code
    assert second["accepted_fields"] == {"system": "atc", "code": "X1"}
    assert (body["submitted"], body["recognised"]) == (2, 1)


def test_free_text_goes_to_notes_never_to_a_constrained_column(client):
    text = "free text " * 100
    body = _submit(client, [{"name": "zzz", "proposed": {"notes": text}}]).json()
    item = body["items"][0]
    assert item["notes"] == text
    assert item["accepted_fields"] == {}
    assert item["ambiguous"] == []


def test_validator_routes_every_kind_of_value(db):
    result = validate_proposal(
        SubstanceCode,
        {
            "system": CodeSystem.UNII,
            "code": 5,
            "source": "s",
            "notes": "n",
            "extra": {"a": "b"},
        },
        ("system", "code", "source"),
    )
    assert result.accepted == {"system": "unii", "source": "s"}
    assert result.notes == "n"
    assert {(a.field, a.reason) for a in result.ambiguous} == {
        ("code", "not_text"),
        ("extra", "unknown_field"),
    }
    assert [a.value for a in result.ambiguous if a.field == "extra"] == ['{"a": "b"}']
    exact = validate_proposal(SubstanceCode, {"code": "c" * 64}, ("code",))
    assert exact.accepted == {"code": "c" * 64}
    assert (
        validate_proposal(SubstanceCode, {"notes": 3}, ("code",)).ambiguous[0].reason
        == "not_text"
    )
    with pytest.raises(ValueError):
        validate_proposal(Substance, {}, ("created_at",))


def test_other_users_get_404_and_anonymous_401(client, substance, reviewer):
    body = _submit(client, [{"name": "zzz"}]).json()
    base = f"{URL}{body['id']}/"
    item = body["items"][0]["id"]
    other = APIClient()
    other.force_authenticate(
        User.objects.create_user(email="x@example.com", password="correct-horse-9")
    )
    anon = APIClient()
    calls = (
        ("get", base, None),
        ("post", f"{base}items/{item}/decide/", {"decision": "left_out"}),
        ("post", f"{base}commit/", None),
    )
    for method, url, data in calls:
        assert getattr(other, method)(url, data, format="json").status_code == 404
        assert getattr(anon, method)(url, data, format="json").status_code == 401
    assert anon.post(URL, {"entries": []}, format="json").status_code == 401
    # an item of another extraction is not reachable through one's own
    mine = _submit(client, [{"name": "yyy"}]).json()
    wrong = client.post(
        f"{URL}{mine['id']}/items/{item}/decide/",
        {"decision": "left_out"},
        format="json",
    )
    assert wrong.status_code == 404


def test_staff_sees_candidates_owner_does_not(client, substance, reviewer):
    _reviewed(substance, "rapamycin", reviewer)
    owner_view = _submit(client, [{"name": "rapamycn"}]).json()["items"][0]
    assert owner_view["candidates"] == []
    staff = APIClient()
    staff.force_authenticate(reviewer)
    staff_view = _submit(staff, [{"name": "rapamycn"}]).json()["items"][0]
    assert staff_view["status"] == "not_understood"
    assert staff_view["candidates"] == [substance.pk]


def test_submit_is_rate_limited(client, monkeypatch):
    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {"substance_extraction": "2/min"}
    )
    codes = [_submit(client, [{"name": "zzz"}]).status_code for _ in range(3)]
    assert codes == [201, 201, 429]


def test_submit_is_charged_per_name(client, monkeypatch):
    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {"substance_extraction": "5/min"}
    )
    three = [{"name": f"zzz{i}"} for i in range(3)]
    codes = [_submit(client, three).status_code for _ in range(3)]
    assert codes == [201, 429, 429]
    assert _submit(client, [{"name": "a"}, {"name": "b"}]).status_code == 201


def test_throttle_rates_are_configured():
    rates = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
    assert rates["substance_resolve"]
    assert rates["substance_extraction"]


def test_per_entry_throttle_passes_through_without_scope_or_key(monkeypatch):
    from types import SimpleNamespace

    from substances.throttles import PerEntryScopedRateThrottle

    request = SimpleNamespace(data=dict())
    assert PerEntryScopedRateThrottle().allow_request(request, SimpleNamespace())
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", dict(s="1/min"))
    monkeypatch.setattr(PerEntryScopedRateThrottle, "get_cache_key", lambda *a: None)
    scoped = SimpleNamespace(throttle_scope="s")
    assert PerEntryScopedRateThrottle().allow_request(request, scoped)
