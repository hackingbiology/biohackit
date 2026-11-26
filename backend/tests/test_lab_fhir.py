# SPDX-License-Identifier: AGPL-3.0-or-later
"""FHIR export of a stored lab report (M02 TG-j part 1). Synthetic rows only."""

import json
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from core.fhir import lab_report_to_fhir_bundle, render_fhir_json
from core.models import Biomarker, BiomarkerRole, LabReport, LabReportOrigin, LabResult
from terminology.models import Source, Unit


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def unit(source):
    return Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)


@pytest.fixture
def analytes(unit, source):
    return [
        Biomarker.objects.create(
            name=f"synthetic {code}",
            loinc_code=code,
            role=BiomarkerRole.BASELINE,
            unit=unit,
            source=source,
        )
        for code in ("0000-0", "1111-1")
    ]


@pytest.fixture
def report(user):
    return LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)


def add(report, analyte, **kw):
    kw.setdefault("reported_value", "2.5")
    kw.setdefault("reported_unit", "xa/L")
    return LabResult.objects.create(report=report, biomarker=analyte, **kw)


def resources(bundle, kind):
    return [
        e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == kind
    ]


def test_report_exports_with_one_observation_per_result(report, analytes):
    # scenario: biomarkers-and-labs::a-report-exports-as-diagnosticreport-with-observations
    add(report, analytes[0], reported_value="2.123456")
    add(report, analytes[1], reported_value="7")
    bundle = lab_report_to_fhir_bundle(report)
    (dr,) = resources(bundle, "DiagnosticReport")
    by_url = {e["fullUrl"]: e["resource"] for e in bundle["entry"]}
    assert len(dr["result"]) == 2
    observations = [by_url[r["reference"]] for r in dr["result"]]
    assert [o["resourceType"] for o in observations] == ["Observation"] * 2
    assert [o["code"]["coding"] for o in observations] == [
        [{"system": "http://loinc.org", "code": "0000-0"}],
        [{"system": "http://loinc.org", "code": "1111-1"}],
    ]
    assert observations[0]["valueQuantity"]["value"] == Decimal("2.123456")
    assert observations[1]["valueQuantity"]["value"] == Decimal("7")
    # exact JSON number, not rounded and not a string
    parsed = json.loads(render_fhir_json(bundle), parse_float=Decimal)
    values = [
        e["resource"]["valueQuantity"]["value"]
        for e in parsed["entry"]
        if e["resource"]["resourceType"] == "Observation"
    ]
    assert values == [Decimal("2.123456"), Decimal("7")]
    # no padding zeros from the 6-decimal column (equal Decimals differ in text)
    text = render_fhir_json(bundle)
    assert '"value": 7}' in text
    assert "7.0" not in text


def test_observation_carries_laboratory_and_method(report, analytes):
    # scenario: biomarkers-and-labs::observation-carries-laboratory-and-method-when-known
    add(report, analytes[0], laboratory="Synthetic Lab", method="synthetic method")
    bundle = lab_report_to_fhir_bundle(report)
    (obs,) = resources(bundle, "Observation")
    (org,) = resources(bundle, "Organization")
    assert obs["method"] == {"text": "synthetic method"}
    assert org == {"resourceType": "Organization", "name": "Synthetic Lab"}
    urls = {e["fullUrl"]: e["resource"] for e in bundle["entry"]}
    assert urls[obs["performer"][0]["reference"]] is org


def test_missing_provenance_is_omitted(report, analytes):
    # scenario: biomarkers-and-labs::missing-provenance-is-omitted-not-invented
    add(report, analytes[0])
    bundle = lab_report_to_fhir_bundle(report)
    (obs,) = resources(bundle, "Observation")
    for key in ("method", "performer", "effectiveDateTime", "issued"):
        assert key not in obs
    assert resources(bundle, "Organization") == []


def test_reported_unit_matching_ucum_carries_system_and_code(report, analytes):
    # scenario: biomarkers-and-labs::reported-unit-matches-a-stored-ucum-unit
    add(report, analytes[0], reported_unit="xa/L")
    (obs,) = resources(lab_report_to_fhir_bundle(report), "Observation")
    quantity = obs["valueQuantity"]
    assert quantity["system"] == "http://unitsofmeasure.org"
    assert quantity["code"] == "xa/L"
    assert "unit" not in quantity


def test_non_ucum_reported_unit_is_text_only(report, analytes):
    # scenario: biomarkers-and-labs::non-ucum-reported-unit
    add(report, analytes[0], reported_unit="zz per litre")
    (obs,) = resources(lab_report_to_fhir_bundle(report), "Observation")
    quantity = obs["valueQuantity"]
    assert quantity["unit"] == "zz per litre"
    assert "system" not in quantity
    assert "code" not in quantity


def test_times_stay_separate_and_export_is_deterministic(report, analytes):
    add(
        report,
        analytes[0],
        collected_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
        reported_at=datetime(2026, 1, 3, 3, 4, 5, tzinfo=UTC),
    )
    first = lab_report_to_fhir_bundle(report)
    (obs,) = resources(first, "Observation")
    assert obs["effectiveDateTime"] == "2026-01-02T03:04:05+00:00"
    assert obs["issued"] == "2026-01-03T03:04:05+00:00"
    assert render_fhir_json(first) == render_fhir_json(
        lab_report_to_fhir_bundle(report)
    )


def test_endpoint_owner_other_and_anonymous(user, report, analytes):
    add(report, analytes[0])
    url = f"/api/labs/reports/{report.pk}/fhir/"
    owner = APIClient()
    owner.force_authenticate(user)
    response = owner.get(url)
    assert response.status_code == 200
    assert json.loads(response.content)["resourceType"] == "Bundle"
    stranger = User.objects.create_user(
        email="b@example.com", password="correct-horse-9"
    )
    other = APIClient()
    other.force_authenticate(stranger)
    assert other.get(url).status_code == 404
    assert APIClient().get(url).status_code in (401, 403)
