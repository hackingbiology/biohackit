# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owner-only OMOP MEASUREMENT export of a stored lab report (M02 TG-j part 2)."""

import json
from datetime import UTC, date, datetime

import pytest
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APIClient

from accounts.models import User
from core.models import (
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
)
from core.omop import MEASUREMENT_COLUMNS, lab_result_to_omop_measurement
from terminology.models import Source, Unit

CONCEPT_COLUMNS = [c for c in MEASUREMENT_COLUMNS if c.endswith("_concept_id")]


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def analyte(db):
    source = Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )
    unit = Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)
    return Biomarker.objects.create(
        name="synthetic 0000-0",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


@pytest.fixture
def report(user):
    return LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)


def add(report, analyte, value, **kw):
    return LabResult.objects.create(
        report=report,
        biomarker=analyte,
        reported_value=value,
        reported_unit="xa/L",
        **kw,
    )


def client_for(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def as_json(row):
    return json.loads(JSONRenderer().render(row))


def test_owner_exports_rows_equal_to_mapper(user, report, analyte):
    # scenario: biomarkers-and-labs::an-owner-exports-a-report-as-omop-measurement-rows
    # scenario: biomarkers-and-labs::a-result-maps-to-omop-measurement
    when = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    first = add(report, analyte, "3.5", collected_at=when)
    second = add(report, analyte, "2.5")
    first.refresh_from_db()
    second.refresh_from_db()
    response = client_for(user).get(f"/api/labs/reports/{report.pk}/omop/")
    assert response.status_code == 200
    body = response.json()
    assert body["omop_cdm_version"] == "5.4"
    assert body["columns"] == list(MEASUREMENT_COLUMNS)
    assert [r["measurement_id"] for r in body["rows"]] == [first.pk, second.pk]
    assert body["rows"] == [
        as_json(lab_result_to_omop_measurement(r)) for r in (first, second)
    ]
    for row in body["rows"]:
        assert list(row) == list(MEASUREMENT_COLUMNS)
        assert row["measurement_source_value"] == "0000-0"
        assert row["unit_source_value"] == "xa/L"
    assert body["rows"][0]["value_source_value"] == "3.500000"
    assert body["rows"][0]["measurement_date"] == "2026-01-02"


def test_no_concept_id_or_person_is_invented(user, report, analyte):
    # scenario: biomarkers-and-labs::an-owner-exports-a-report-as-omop-measurement-rows
    add(report, analyte, "2.5")
    rows = client_for(user).get(f"/api/labs/reports/{report.pk}/omop/").json()["rows"]
    assert rows
    for row in rows:
        for column in [*CONCEPT_COLUMNS, "person_id"]:
            assert row[column] is None


def test_retracted_result_is_not_exported(user, report, analyte):
    # scenario: biomarkers-and-labs::a-retracted-result-is-not-exported
    kept = add(report, analyte, "2.5", validation_state=LabResultValidation.DISPUTED)
    add(report, analyte, "9.5", validation_state=LabResultValidation.RETRACTED)
    rows = client_for(user).get(f"/api/labs/reports/{report.pk}/omop/").json()["rows"]
    assert [r["measurement_id"] for r in rows] == [kept.pk]


def test_another_user_and_anonymous_cannot_export(user, report, analyte):
    # scenario: biomarkers-and-labs::another-user-cannot-export-a-report
    add(report, analyte, "2.5")
    url = f"/api/labs/reports/{report.pk}/omop/"
    stranger = User.objects.create_user(
        email="b@example.com", password="correct-horse-9"
    )
    response = client_for(stranger).get(url)
    assert response.status_code == 404
    assert "0000-0" not in response.content.decode()
    assert APIClient().get(url).status_code in (401, 403)
