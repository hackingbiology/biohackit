# SPDX-License-Identifier: AGPL-3.0-or-later
"""CSV lab import with review and rollback (M02 TG-c part 1). Synthetic rows only."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabReportOrigin, LabResult
from terminology.models import Source, Unit, UnitConversion

PREVIEW = "/api/labs/imports/csv/preview/"
CONFIRM = "/api/labs/imports/csv/confirm/"
HEAD = "loinc_code,value,unit,collected_at,reported_at,laboratory,method\n"


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


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def analyte(source):
    unit = Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)
    return Biomarker.objects.create(
        name="synthetic analyte",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


def upload(content, name="labs.csv"):
    data = content if isinstance(content, bytes) else content.encode()
    return {"file": SimpleUploadedFile(name, data, content_type="text/csv")}


def post(client, url, content, name="labs.csv", **extra):
    return client.post(url, {**upload(content, name), **extra}, format="multipart")


def counts():
    return LabReport.objects.count(), LabResult.objects.count()


def test_requires_authentication(db, analyte):
    resp = APIClient().post(PREVIEW, upload(HEAD), format="multipart")
    assert resp.status_code in (401, 403)


# scenario: biomarkers-and-labs::unrecognised-line-item
def test_preview_flags_unknown_code_and_stores_nothing(client, analyte):
    csv_text = HEAD + "0000-0,2.5,xa/L,,,,\n9999-9,1,xa/L,,,,\n0000-0,3,,,,,\n"
    resp = post(client, PREVIEW, csv_text)
    assert resp.status_code == 200
    rows = resp.json()["rows"]
    assert [r["row"] for r in rows] == [1, 2, 3]
    assert [r["status"] for r in rows] == [
        "recognised",
        "not_recognised",
        "not_recognised",
    ]
    assert "loinc_code" in rows[1]["reason"]
    assert "unit" in rows[2]["reason"]
    assert rows[0]["plausibility"]["status"] == "not_checked"
    assert counts() == (0, 0)


# scenario: biomarkers-and-labs::unrecognised-line-item
def test_confirm_refuses_while_a_row_is_not_recognised(client, analyte):
    csv_text = HEAD + "0000-0,2.5,xa/L,,,,\n9999-9,1,xa/L,,,,\n0000-0,x,xa/L,,,,\n"
    resp = post(client, CONFIRM, csv_text)
    assert resp.status_code == 400
    body = resp.json()
    assert [r["row"] for r in body["rows"]] == [2, 3]
    assert "2, 3" in body["detail"]
    assert counts() == (0, 0)


def test_bad_time_is_not_recognised_naming_the_column(client, analyte):
    rows = post(client, PREVIEW, HEAD + "0000-0,1,xa/L,yesterday,,,\n").json()["rows"]
    assert rows[0]["status"] == "not_recognised"
    assert "collected_at" in rows[0]["reason"]


@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
def test_nul_in_loinc_code_is_not_recognised_not_500(client, analyte, url):
    resp = post(client, url, HEAD + "00\x000-0,1,xa/L,,,,\n")
    assert resp.status_code in (200, 400)
    row = resp.json()["rows"][0]
    assert row["status"] == "not_recognised"
    assert "loinc_code" in row["reason"]
    assert counts() == (0, 0)


def test_ragged_row_is_not_recognised(client, analyte):
    rows = post(client, PREVIEW, HEAD + "0000-0,1\n").json()["rows"]
    assert rows[0]["status"] == "not_recognised"


def test_blank_lines_are_skipped_but_keep_line_numbers(client, analyte):
    csv_text = HEAD + "0000-0,1,xa/L,,,,\n\n,,,,,,\n0000-0,2,xa/L,,,,\n\n"
    rows = post(client, PREVIEW, csv_text).json()["rows"]
    assert [(r["row"], r["status"]) for r in rows] == [
        (1, "recognised"),
        (4, "recognised"),
    ]
    resp = post(client, CONFIRM, csv_text)
    assert resp.status_code == 201
    assert counts() == (1, 2)


def test_confirm_stores_one_import_report_with_shared_save_rules(
    client, user, analyte, source
):
    other_unit = Unit.objects.create(ucum_code="xb/L", display="xb/L", source=source)
    UnitConversion.objects.create(
        from_unit=other_unit, to_unit=analyte.unit, factor=Decimal("2"), source=source
    )
    csv_text = (
        HEAD
        + "0000-0,2.50,xa/L,2026-01-02T03:04:05+00:00,,Lab X,Method Y\n"
        + "0000-0,3,xb/L,,,,\n"
    )
    resp = post(client, CONFIRM, csv_text, name="my labs.csv", laboratory="Rep Lab")
    assert resp.status_code == 201
    data = resp.json()
    report = LabReport.objects.get()
    assert report.pk == data["id"]
    assert (report.origin, report.import_name, report.owner) == (
        LabReportOrigin.IMPORT,
        "my labs.csv",
        user,
    )
    first, second = LabResult.objects.order_by("pk")
    assert first.reported_value == Decimal("2.5")
    assert first.aggregation_eligible is True
    assert first.validation_state == "reviewed"
    assert second.normalised_value == Decimal("6")
    assert second.normalised_unit == "xa/L"
    assert second.laboratory == "Rep Lab" and second.method is None
    assert second.aggregation_eligible is False
    assert len(data["results"]) == 2


def test_value_failing_save_rules_stores_nothing(client, analyte):
    csv_text = HEAD + "0000-0,2.5,xa/L,,,,\n0000-0,1.1234567,xa/L,,,,\n"
    resp = post(client, CONFIRM, csv_text)
    assert resp.status_code == 400
    assert [r["row"] for r in resp.json()["rows"]] == [2]
    assert counts() == (0, 0)


def test_bad_header_is_rejected_naming_it(client, analyte):
    for head in ("code,value,unit\n", "loinc_code,value\n", HEAD.strip() + ",extra\n"):
        resp = post(client, PREVIEW, head + "0000-0,1,xa/L\n")
        assert resp.status_code == 400
        assert "header" in resp.json()["file"]
    assert counts() == (0, 0)


@pytest.mark.parametrize(
    ("content", "word"),
    [
        (HEAD + "x" * (1024 * 1024), "1 MiB"),
        (HEAD + "0000-0,1,xa/L,,,,\n" * 201, "200 data rows"),
        (HEAD + "0000-0," + "1" * 41 + ",xa/L,,,,\n", "value"),
        (HEAD + "0000-0,1,xa/L,,,," + "m" * 201 + "\n", "method"),
        (HEAD.encode() + b"0000-0,\xff,xa/L,,,,\n", "UTF-8"),
    ],
)
@pytest.mark.parametrize("url", [PREVIEW, CONFIRM])
def test_bounds_give_400_naming_the_bound(client, analyte, url, content, word):
    resp = post(client, url, content)
    assert resp.status_code == 400
    assert word in resp.json()["file"]
    assert counts() == (0, 0)


def test_missing_file_is_400(client, analyte):
    assert client.post(PREVIEW, {}, format="multipart").status_code == 400


def _import(client, rows="0000-0,2.5,xa/L,,,,\n"):
    resp = post(client, CONFIRM, HEAD + rows)
    assert resp.status_code == 201
    return resp.json()["id"]


# scenario: biomarkers-and-labs::rollback-removes-the-import-s-results-and-report
# scenario: biomarkers-and-labs::undo-an-import
def test_delete_removes_import_report_and_results(client, analyte):
    report_id = _import(client, "0000-0,2.5,xa/L,,,,\n0000-0,3,xa/L,,,,\n")
    assert counts() == (1, 2)
    resp = client.delete(f"/api/labs/reports/{report_id}/")
    assert resp.status_code == 204
    assert counts() == (0, 0)


# scenario: biomarkers-and-labs::rollback-leaves-other-results-untouched
def test_delete_leaves_other_reports_untouched(client, user, analyte):
    first = _import(client)
    second = _import(client, "0000-0,7,xa/L,,,,\n")
    manual = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    LabResult.objects.create(
        report=manual,
        biomarker=analyte,
        reported_value=Decimal("9"),
        reported_unit="xa/L",
    )
    assert client.delete(f"/api/labs/reports/{first}/").status_code == 204
    assert sorted(LabReport.objects.values_list("pk", flat=True)) == sorted(
        [second, manual.pk]
    )
    values = sorted(LabResult.objects.values_list("reported_value", flat=True))
    assert values == [Decimal("7"), Decimal("9")]


def test_delete_by_another_user_is_404(client, other, analyte):
    report_id = _import(client)
    intruder = APIClient()
    intruder.force_authenticate(other)
    assert intruder.delete(f"/api/labs/reports/{report_id}/").status_code == 404
    assert counts() == (1, 1)


def test_delete_of_manual_report_is_refused(client, user, analyte):
    manual = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    resp = client.delete(f"/api/labs/reports/{manual.pk}/")
    assert resp.status_code == 409
    assert LabReport.objects.filter(pk=manual.pk).exists()
