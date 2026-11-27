# SPDX-License-Identifier: AGPL-3.0-or-later
"""Substance catalog codes (M03 TG-a). Synthetic values only: nothing here is a real identifier."""

import re
from pathlib import Path

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from substances.models import Substance, SubstanceCode

URL = "/api/substances/"
BACKEND = Path(__file__).resolve().parents[1]
MAX_BYTES = 100_000
RELEASE_NAMES = re.compile(r"rxnorm|rxnconso|unii|atc_?(tree|ddd)|ddd", re.I)
CODE = {
    "system": "rxcui",
    "code": "  TEST-RXCUI-1 ",
    "source": "synthetic test source",
    "fetched_on": "2026-01-02",
}


def _client(db, *, staff: bool) -> APIClient:
    user = User.objects.create_user(
        email=f"{'s' if staff else 'u'}@example.com", password="correct-horse-9"
    )
    user.is_staff = staff
    user.save()
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.fixture
def staff(db) -> APIClient:
    return _client(db, staff=True)


@pytest.fixture
def member(db) -> APIClient:
    return _client(db, staff=False)


def test_code_is_stored_with_source_and_fetch_date_and_returned_unchanged(staff):
    # scenario: interventions-and-catalog::a-code-is-stored-with-its-source-and-fetch-date
    r = staff.post(
        URL,
        {"name": "Synthetic substance", "codes": [CODE]},
        format="json",
    )
    assert r.status_code == 201, r.content
    got = staff.get(f"{URL}{r.json()['id']}/").json()["codes"][0]
    assert got["code"] == "TEST-RXCUI-1"
    assert got["system"] == "rxcui"
    assert got["source"] == "synthetic test source"
    assert got["fetched_on"] == "2026-01-02"
    assert got["provisional"] is True


@pytest.mark.parametrize(
    "change",
    [
        {"source": ""},
        {"source": "   "},
        {"fetched_on": None},
        {"fetched_on": "not-a-date"},
        {"fetched_on": "2999-01-01"},
        {"code": " "},
        {"system": "snomed"},
        {"provisional": "yes"},
        {"provisional": False},
    ],
)
def test_code_without_source_or_date_is_refused(staff, change):
    # scenario: interventions-and-catalog::a-code-is-stored-with-its-source-and-fetch-date
    body = {"name": "Synthetic substance", "codes": [{**CODE, **change}]}
    assert staff.post(URL, body, format="json").status_code == 400
    assert not Substance.objects.exists()
    sid = Substance.objects.create(name="x").pk
    r = staff.post(f"{URL}{sid}/codes/", {**CODE, **change}, format="json")
    assert r.status_code == 400
    assert not SubstanceCode.objects.exists()


def test_service_level_and_database_refuse_a_missing_source(staff, db):
    # scenario: interventions-and-catalog::a-code-is-stored-with-its-source-and-fetch-date
    from django.db import IntegrityError, transaction

    s = Substance.objects.create(name="x")
    with pytest.raises(IntegrityError), transaction.atomic():
        SubstanceCode.objects.create(
            substance=s, system="atc", code="C", source="", fetched_on="2026-01-01"
        )


def test_add_correct_and_duplicate_codes(staff):
    sid = staff.post(URL, {"name": "S"}, format="json").json()["id"]
    r = staff.post(f"{URL}{sid}/codes/", CODE, format="json")
    assert r.status_code == 201
    cid = r.json()["id"]
    assert staff.post(f"{URL}{sid}/codes/", CODE, format="json").status_code == 400
    r = staff.patch(
        f"{URL}{sid}/codes/{cid}/", {"source": "another synthetic"}, format="json"
    )
    assert r.status_code == 200 and r.json()["source"] == "another synthetic"
    assert (
        staff.patch(f"{URL}{sid}/codes/{cid}/", {"source": ""}, format="json")
    ).status_code == 400
    other = staff.post(f"{URL}{sid}/codes/", {**CODE, "code": "TEST-2"}, format="json")
    clash = staff.patch(
        f"{URL}{sid}/codes/{other.json()['id']}/",
        {"code": "TEST-RXCUI-1"},
        format="json",
    )
    assert clash.status_code == 400
    assert staff.patch(f"{URL}{sid}/codes/9999/", {}, format="json").status_code == 404


def test_substance_validation_and_edit(staff):
    assert staff.post(URL, {"name": " "}, format="json").status_code == 400
    assert staff.post(URL, {"name": 5}, format="json").status_code == 400
    assert staff.post(URL, {"name": "x" * 201}, format="json").status_code == 400
    assert (
        staff.post(URL, {"name": "x", "codes": "no"}, format="json").status_code == 400
    )
    assert (
        staff.post(URL, {"name": "x", "codes": [CODE, CODE]}, format="json").status_code
        == 400
    )
    assert staff.post(URL, [1], format="json").status_code == 400
    sid = staff.post(URL, {"name": "x"}, format="json").json()["id"]
    r = staff.patch(
        f"{URL}{sid}/", {"name": " y ", "substance_class": ""}, format="json"
    )
    assert r.status_code == 200
    assert r.json()["name"] == "y" and r.json()["substance_class"] == ""
    assert staff.patch(f"{URL}{sid}/", {"name": ""}, format="json").status_code == 400
    assert staff.patch(f"{URL}999999/", {}, format="json").status_code == 404
    assert staff.get(f"{URL}999999/").status_code == 404
    assert len(staff.get(URL).json()) == 1


def test_non_staff_reads_but_cannot_write_and_anonymous_is_refused(member, staff):
    sid = staff.post(URL, {"name": "x"}, format="json").json()["id"]
    assert member.get(URL).status_code == 200
    assert member.get(f"{URL}{sid}/").status_code == 200
    assert member.post(URL, {"name": "y"}, format="json").status_code == 403
    assert member.patch(f"{URL}{sid}/", {"name": "y"}, format="json").status_code == 403
    assert member.post(f"{URL}{sid}/codes/", CODE, format="json").status_code == 403
    anonymous = APIClient()
    assert anonymous.get(URL).status_code in (401, 403)
    assert anonymous.post(URL, {"name": "y"}, format="json").status_code in (401, 403)


def test_no_migration_inserts_rows():
    # scenario: interventions-and-catalog::no-bulk-terminology-file-is-stored
    for path in (BACKEND / "substances" / "migrations").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not re.search(r"RunPython|RunSQL|bulk_create|\.create\(", text), path


def test_nothing_is_seeded(db):
    # scenario: interventions-and-catalog::no-bulk-terminology-file-is-stored
    assert not Substance.objects.exists() and not SubstanceCode.objects.exists()


def test_no_bulk_terminology_file_under_backend():
    # scenario: interventions-and-catalog::no-bulk-terminology-file-is-stored
    skip = {".venv", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules"}
    bad = []
    for path in BACKEND.rglob("*"):
        if skip & set(path.relative_to(BACKEND).parts) or not path.is_file():
            continue
        if path.name.startswith(".coverage"):
            continue
        if path.stat().st_size > MAX_BYTES or (
            path.suffix in {".rrf", ".csv", ".tsv", ".zip", ".json", ".txt"}
            and RELEASE_NAMES.search(path.name)
        ):
            bad.append(str(path.relative_to(BACKEND)))
    # uv.lock and other pre-existing large files are not terminology files
    assert [b for b in bad if b != "uv.lock"] == []


def test_class_needs_source_and_fetch_date_and_is_returned_unchanged(staff):
    # scenario: interventions-and-catalog::a-code-is-stored-with-its-source-and-fetch-date
    bad = {"name": "x", "substance_class": "TEST-CLASS"}
    r = staff.post(URL, bad, format="json")
    assert r.status_code == 400 and "class_source" in r.json()
    r = staff.post(URL, {**bad, "class_source": "TEST-SOURCE"}, format="json")
    assert r.status_code == 400 and "class_fetched_on" in r.json()
    r = staff.post(
        URL,
        {**bad, "class_source": "TEST-SOURCE", "class_fetched_on": "bad"},
        format="json",
    )
    assert r.status_code == 400
    ok = {**bad, "class_source": " TEST-SOURCE ", "class_fetched_on": "2026-01-02"}
    r = staff.post(URL, ok, format="json")
    assert r.status_code == 201
    body = r.json()
    assert body["class_source"] == "TEST-SOURCE"
    assert body["class_fetched_on"] == "2026-01-02"
    r = staff.patch(f"{URL}{body['id']}/", {"class_source": ""}, format="json")
    assert r.status_code == 400
    r = staff.patch(f"{URL}{body['id']}/", {"substance_class": ""}, format="json")
    assert r.json()["class_source"] == "" and r.json()["class_fetched_on"] is None
