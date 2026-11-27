# SPDX-License-Identifier: AGPL-3.0-or-later
"""Synonyms, name resolution and the review queue (M03 TG-b). Synthetic values only."""

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from substances.models import (
    Substance,
    SubstanceCode,
    SubstanceReviewItem,
    SubstanceSynonym,
)

URL = "/api/substances/"


def _client(db, *, staff: bool) -> tuple[APIClient, User]:
    user = User.objects.create_user(
        email=f"{'s' if staff else 'u'}@example.com", password="correct-horse-9"
    )
    user.is_staff = staff
    user.save()
    client = APIClient()
    client.force_authenticate(user)
    return client, user


@pytest.fixture
def staff_user(db) -> User:
    return User.objects.create_user(
        email="s@example.com", password="correct-horse-9", is_staff=True
    )


@pytest.fixture
def staff(staff_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(staff_user)
    return client


@pytest.fixture
def member(db) -> APIClient:
    return _client(db, staff=False)[0]


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


def _synonym(substance, name, language, user=None) -> SubstanceSynonym:
    from django.utils import timezone

    return SubstanceSynonym.objects.create(
        substance=substance,
        name=name,
        normalised_name=" ".join(name.casefold().split()),
        language=language,
        source="synthetic test source",
        reviewer=user,
        reviewed_at=timezone.now() if user else None,
    )


def _resolve(client, name, language=None):
    return client.post(
        f"{URL}resolve/", {"name": name, "language": language}, format="json"
    )


def test_italian_and_english_reviewed_synonyms_resolve_to_the_same_substance(
    member, substance, staff_user
):
    # scenario: interventions-and-catalog::italian-input-resolves
    _synonym(substance, "rapamicina", "it", staff_user)
    _synonym(substance, "sirolimus", "en", staff_user)
    for name in (" Rapamicina ", "SIROLIMUS", "rapamicina\t"):
        body = _resolve(member, name).json()
        assert body["status"] == "resolved"
        assert body["substance"]["id"] == substance.pk
        assert [c["code"] for c in body["codes"]] == ["SYNTHETIC-TEST-CODE"]
        assert body["review_item_id"] is None
    assert not SubstanceReviewItem.objects.exists()


def test_a_synonym_without_a_reviewer_does_not_resolve(member, substance):
    # scenario: interventions-and-catalog::a-synonym-without-a-reviewer-does-not-resolve
    _synonym(substance, "rapamicina", "it")
    body = _resolve(member, "Rapamicina").json()
    assert body["status"] == "ambiguous"
    assert body["reason"] == "unreviewed_synonym"
    assert body["substance"] is None
    assert body["codes"] == []
    item = SubstanceReviewItem.objects.get()
    assert item.status == "open"
    assert item.pk == body["review_item_id"]


def test_a_member_never_sees_the_substance_behind_an_unreviewed_match(
    member, staff, substance
):
    _synonym(substance, "Rapamicina", "it")
    body = _resolve(member, "Rapamicina").json()
    assert body["reason"] == "unreviewed_synonym"
    assert body["candidates"] == []
    assert body["substance"] is None
    assert body["review_item_id"] is not None
    assert [c["id"] for c in _resolve(staff, "Rapamicina").json()["candidates"]] == [
        substance.pk
    ]


def test_a_near_match_is_proposed_not_resolved(member, staff, substance, staff_user):
    # scenario: interventions-and-catalog::a-near-match-is-proposed-not-resolved
    _synonym(substance, "rapamycin", "en", staff_user)
    body = _resolve(member, "rapamycn").json()
    assert body["status"] == "ambiguous"
    assert body["reason"] == "near_match"
    assert body["substance"] is None
    assert body["candidates"] == []
    staff_body = _resolve(staff, "rapycn").json()
    assert staff_body["reason"] == "near_match"
    assert [c["id"] for c in staff_body["candidates"]] == [substance.pk]
    item = SubstanceReviewItem.objects.get(pk=body["review_item_id"])
    assert item.resolved_substance is None
    assert item.candidate_substance_ids == [substance.pk]
    # closing the item is a separate staff action
    r = staff.post(
        f"{URL}review-queue/{item.pk}/resolve/",
        {"substance": substance.pk},
        format="json",
    )
    assert r.status_code == 200
    assert r.json()["resolved_substance"] == substance.pk
    assert r.json()["status"] == "resolved"


def test_unresolved_name_is_queued_once_and_kept(member, staff, substance):
    # scenario: interventions-and-catalog::unresolved-substance-is-surfaced-not-dropped
    first = _resolve(member, "zzz unknown").json()
    again = _resolve(member, "  ZZZ   Unknown ").json()
    assert first["status"] == again["status"] == "ambiguous"
    assert first["reason"] == "no_match"
    assert first["review_item_id"] == again["review_item_id"]
    assert SubstanceReviewItem.objects.filter(status="open").count() == 1
    listed = staff.get(f"{URL}review-queue/").json()
    assert [i["id"] for i in listed] == [first["review_item_id"]]
    assert listed[0]["submitted_name"] == "zzz unknown"
    r = staff.post(f"{URL}review-queue/{first['review_item_id']}/reject/")
    assert r.status_code == 200
    assert staff.get(f"{URL}review-queue/").json() == []
    assert SubstanceReviewItem.objects.count() == 1


def test_several_substances_is_ambiguous_never_a_pick(
    member, staff, substance, staff_user
):
    other = Substance.objects.create(name="Other synthetic substance")
    _synonym(substance, "shared name", "en", staff_user)
    _synonym(other, "shared name", "en", staff_user)
    assert _resolve(member, "Shared Name").json()["candidates"] == []
    body = _resolve(staff, "Shared Name").json()
    assert body["status"] == "ambiguous"
    assert body["reason"] == "several_substances"
    assert body["substance"] is None
    assert {c["id"] for c in body["candidates"]} == {substance.pk, other.pk}


def test_synonym_needs_source_and_a_client_cannot_send_a_reviewer(staff, substance):
    ok = {
        "substance": substance.pk,
        "name": "Rapamicina",
        "language": "it",
        "source": "synthetic",
    }
    for bad in (
        {**ok, "source": ""},
        {**ok, "source": "   "},
        {**ok, "language": ""},
        {**ok, "reviewer": 1},
        {**ok, "reviewed_at": "2026-01-01T00:00:00Z"},
        {**ok, "name": "a\x00b"},
        {**ok, "name": "x" * 201},
        {**ok, "substance": 99999},
    ):
        assert staff.post(f"{URL}synonyms/", bad, format="json").status_code == 400
    assert not SubstanceSynonym.objects.exists()
    r = staff.post(f"{URL}synonyms/", ok, format="json")
    assert r.status_code == 201
    assert r.json()["reviewer"] is None
    assert staff.post(f"{URL}synonyms/", ok, format="json").status_code == 400


def test_approval_sets_reviewer_from_the_request_user(
    staff, staff_user, member, substance
):
    syn = _synonym(substance, "rapamicina", "it")
    assert _resolve(member, "rapamicina").json()["status"] == "ambiguous"
    r = staff.post(f"{URL}synonyms/{syn.pk}/approve/", {"reviewer": 999}, format="json")
    assert r.status_code == 200
    assert r.json()["reviewer"] == staff_user.pk
    assert r.json()["reviewed_at"] is not None
    assert staff.post(f"{URL}synonyms/{syn.pk}/approve/").status_code == 400
    assert _resolve(member, "rapamicina").json()["status"] == "resolved"


def test_permissions_on_synonym_and_queue_routes(member, substance):
    item = SubstanceReviewItem.objects.create(
        submitted_name="x", normalised_name="x", reason="no_match"
    )
    syn = _synonym(substance, "abc", "en")
    calls = [
        ("get", f"{URL}synonyms/"),
        ("post", f"{URL}synonyms/"),
        ("post", f"{URL}synonyms/{syn.pk}/approve/"),
        ("get", f"{URL}review-queue/"),
        ("post", f"{URL}review-queue/{item.pk}/resolve/"),
        ("post", f"{URL}review-queue/{item.pk}/reject/"),
    ]
    anonymous = APIClient()
    for method, url in calls:
        assert getattr(member, method)(url, format="json").status_code == 403
        assert getattr(anonymous, method)(url, format="json").status_code in (401, 403)
    assert anonymous.post(
        f"{URL}resolve/", {"name": "x"}, format="json"
    ).status_code in (401, 403)


def test_resolve_refuses_bad_names(member):
    assert _resolve(member, "a\x00b").status_code == 400
    assert _resolve(member, "x" * 201).status_code == 400
    assert _resolve(member, "   ").status_code == 400
    assert _resolve(member, "ok", "it\x00").status_code == 400
    assert member.post(f"{URL}resolve/", {"name": 5}, format="json").status_code == 400


def test_no_synonym_is_seeded(db):
    assert not SubstanceSynonym.objects.exists()
    assert not SubstanceReviewItem.objects.exists()


def test_code_change_needs_a_new_fetch_date(staff, substance):
    # scenario: interventions-and-catalog::a-code-is-stored-with-its-source-and-fetch-date
    code = substance.codes.get()
    url = f"{URL}{substance.pk}/codes/{code.pk}/"
    for field, value in (("code", "NEW"), ("system", "unii"), ("source", "other")):
        assert staff.patch(url, {field: value}, format="json").status_code == 400
    code.refresh_from_db()
    assert code.code == "SYNTHETIC-TEST-CODE"
    r = staff.patch(url, {"code": "NEW", "fetched_on": "2026-02-03"}, format="json")
    assert r.status_code == 200
    assert r.json()["fetched_on"] == "2026-02-03"


def test_class_change_needs_a_new_fetch_date(staff, substance):
    # scenario: interventions-and-catalog::a-code-is-stored-with-its-source-and-fetch-date
    url = f"{URL}{substance.pk}/"
    body = {"substance_class": "synthetic class", "class_source": "synthetic"}
    assert staff.patch(url, body, format="json").status_code == 400
    ok = staff.patch(url, {**body, "class_fetched_on": "2026-01-02"}, format="json")
    assert ok.status_code == 200
    assert (
        staff.patch(url, {"class_source": "changed"}, format="json").status_code == 400
    )
    assert staff.patch(url, {"name": "renamed"}, format="json").status_code == 200
    assert staff.patch(url, {"substance_class": ""}, format="json").status_code == 200


def test_nul_character_in_a_text_field_is_400_not_500(staff, substance):
    assert staff.post(URL, {"name": "a\x00b"}, format="json").status_code == 400
    assert (
        staff.patch(
            f"{URL}{substance.pk}/", {"name": "a\x00b"}, format="json"
        ).status_code
        == 400
    )
    code = {
        "system": "rxcui",
        "code": "a\x00",
        "source": "s",
        "fetched_on": "2026-01-02",
    }
    assert (
        staff.post(f"{URL}{substance.pk}/codes/", code, format="json").status_code
        == 400
    )
    klass = {
        "substance_class": "c\x00",
        "class_source": "s",
        "class_fetched_on": "2026-01-02",
    }
    assert staff.patch(f"{URL}{substance.pk}/", klass, format="json").status_code == 400


def test_a_folded_name_longer_than_the_column_is_400_not_500(member, staff, substance):
    # "\u00df" folds to "ss", so 200 of them fold to 400 characters.
    long_name = "\u00df" * 200
    assert _resolve(member, long_name).status_code == 400
    body = {
        "substance": substance.pk,
        "name": long_name,
        "language": "de",
        "source": "synthetic test source",
    }
    assert staff.post(f"{URL}synonyms/", body, format="json").status_code == 400
    assert not SubstanceReviewItem.objects.exists()


def test_erasing_a_reviewer_keeps_the_review_records(substance, staff_user):
    synonym = _synonym(substance, "rapamicina", "it", staff_user)
    item = SubstanceReviewItem.objects.create(
        submitted_name="x",
        normalised_name="x",
        reason="no_match",
        status="resolved",
        resolved_by=staff_user,
    )
    staff_user.delete()
    synonym.refresh_from_db()
    item.refresh_from_db()
    assert synonym.reviewer is None and synonym.reviewed_at is not None
    assert item.resolved_by is None


def test_a_reviewed_synonym_on_a_substance_without_codes_is_queued(
    staff, substance, staff_user
):
    # scenario: interventions-and-catalog::unresolved-substance-is-surfaced-not-dropped
    member = staff
    substance.codes.all().delete()
    _synonym(substance, "rapamicina", "it", staff_user)
    body = _resolve(member, "rapamicina").json()
    assert body["status"] == "ambiguous"
    assert body["reason"] == "no_code"
    assert body["substance"] is None
    assert [c["id"] for c in body["candidates"]] == [substance.pk]
    assert SubstanceReviewItem.objects.get().status == "open"
