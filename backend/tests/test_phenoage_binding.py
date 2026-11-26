# SPDX-License-Identifier: AGPL-3.0-or-later
"""PhenoAge from stored results (M02 TG-i part 2). Synthetic rows only: the codes
"T-n" and the conversion row are test fixtures, not seeded data, and are patched into
the code map because no real LOINC code could be verified (Q79)."""

import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.apps import apps
from rest_framework.test import APIClient

from accounts.models import User
from core import phenoage_binding
from core.models import (
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
)
from core.phenoage import PhenoAgeInputs, compute_phenoage
from core.phenoage_binding import S2_UNITS
from terminology.models import Source, Unit, UnitConversion

VALUES = {
    "albumin_g_per_l": "45",
    "creatinine_umol_per_l": "80",
    "glucose_mmol_per_l": "5",
    "crp_mg_per_dl": "0.1",
    "lymphocyte_percent": "30",
    "mcv_fl": "90",
    "rdw_percent": "13",
    "alp_u_per_l": "70",
    "wbc_10e3_per_ul": "6",
}
AGE = 40.0
REAL_CODES = dict(phenoage_binding.LOINC_BY_FIELD)  # before the fixture patches it
CODES = {f: f"T-{i}" for i, f in enumerate(S2_UNITS)}


def expected_years():
    inputs = PhenoAgeInputs(age_years=AGE, **{f: float(v) for f, v in VALUES.items()})
    result = compute_phenoage(inputs)
    assert result is not None
    return result


@pytest.fixture(autouse=True)
def code_map(monkeypatch):
    monkeypatch.setattr(phenoage_binding, "LOINC_BY_FIELD", CODES)


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
def units(source):
    codes = set(S2_UNITS.values()) | {"g/dL"}
    return {
        c: Unit.objects.create(ucum_code=c, display=c, source=source) for c in codes
    }


@pytest.fixture
def analytes(units, source):
    return {
        f: Biomarker.objects.create(
            name=f"synthetic {f}",
            loinc_code=CODES[f],
            role=BiomarkerRole.BASELINE,
            unit=units[u],
            source=source,
        )
        for f, u in S2_UNITS.items()
    }


@pytest.fixture
def report(user):
    return LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)


def add(report, analytes, field, value=None, unit=None, **kw):
    return LabResult.objects.create(
        report=report,
        biomarker=analytes[field],
        reported_value=value or VALUES[field],
        reported_unit=unit or S2_UNITS[field],
        **kw,
    )


@pytest.fixture
def full(report, analytes):
    return {f: add(report, analytes, f) for f in S2_UNITS}


def call(user, pk, query="?age_years=40"):
    client = APIClient()
    client.force_authenticate(user)
    return client.get(f"/api/labs/reports/{pk}/phenoage/{query}")


def counts():
    return {m._meta.label: m.objects.count() for m in apps.get_models()}


def refusal(response):
    assert response.status_code == 200
    return response.json()["refusal"]


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_api_equals_engine(user, report, full):
    before = counts()
    body = call(user, report.pk).json()
    expected = expected_years()
    assert body["phenoage_years"] == expected.phenoage_years
    assert body["mortality_score"] == expected.mortality_score
    assert body["xb"] == expected.xb
    assert body["constants_version"] == expected.constants_version
    assert body["method"].startswith("PhenoAge (Levine 2018)")
    assert {i["field"] for i in body["inputs"]} == set(S2_UNITS)
    assert all(not i["converted"] for i in body["inputs"])
    assert body["inputs"][0]["lab_result_id"] == full["albumin_g_per_l"].pk
    assert counts() == before


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_stored_conversion_is_used(user, report, analytes, units, source):
    for f in S2_UNITS:
        if f != "albumin_g_per_l":
            add(report, analytes, f)
    UnitConversion.objects.create(  # synthetic factor, test only
        from_unit=units["g/dL"],
        to_unit=units["g/L"],
        factor=Decimal("10"),
        source=source,
    )
    add(report, analytes, "albumin_g_per_l", "4.5", "g/dL")
    body = call(user, report.pk).json()
    albumin = body["inputs"][0]
    assert albumin["converted"] is True
    assert albumin["value"] == 45.0
    assert albumin["unit"] == "g/L"
    assert body["phenoage_years"] == expected_years().phenoage_years


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_binder_converts_when_row_created_after_result(
    user, report, analytes, units, source
):
    for f in S2_UNITS:
        if f != "albumin_g_per_l":
            add(report, analytes, f)
    add(report, analytes, "albumin_g_per_l", "4.5", "g/dL")  # normalised stays NULL
    UnitConversion.objects.create(  # synthetic factor, test only
        from_unit=units["g/dL"],
        to_unit=units["g/L"],
        factor=Decimal("10"),
        source=source,
    )
    albumin = call(user, report.pk).json()["inputs"][0]
    assert albumin["value"] == 45.0
    assert albumin["converted"] is True


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_s2_unit_result_with_differing_biomarker_unit(
    user, report, analytes, units, source
):
    for f in S2_UNITS:
        if f != "albumin_g_per_l":
            add(report, analytes, f)
    albumin = analytes["albumin_g_per_l"]
    albumin.unit = units["g/dL"]  # Biomarker unit differs from the S2 unit
    albumin.save()
    UnitConversion.objects.create(  # synthetic factor, test only
        from_unit=units["g/L"],
        to_unit=units["g/dL"],
        factor=Decimal("0.1"),
        source=source,
    )
    add(report, analytes, "albumin_g_per_l")  # reported in g/L, normalised to g/dL
    body = call(user, report.pk).json()
    assert body["inputs"][0]["value"] == 45.0
    assert body["inputs"][0]["converted"] is False
    assert body["phenoage_years"] == expected_years().phenoage_years


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_no_stored_conversion_refuses(user, report, analytes):
    for f in S2_UNITS:
        if f != "albumin_g_per_l":
            add(report, analytes, f)
    add(report, analytes, "albumin_g_per_l", "4.5", "g/dL")
    assert refusal(call(user, report.pk)) == {
        "reason": "unit_not_convertible",
        "field": "albumin_g_per_l",
    }


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_missing_analyte_refuses(user, report, full):
    full["mcv_fl"].delete()
    got = refusal(call(user, report.pk))
    assert got == {"reason": "missing_input", "field": "mcv_fl"}


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize(
    "state", [LabResultValidation.RETRACTED, LabResultValidation.DISPUTED]
)
def test_excluded_state_makes_analyte_missing(user, report, full, state):
    full["rdw_percent"].set_validation_state(state)
    assert refusal(call(user, report.pk)) == {
        "reason": "missing_input",
        "field": "rdw_percent",
    }


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_two_candidates_are_ambiguous(user, report, analytes, full):
    add(report, analytes, "alp_u_per_l", "71")
    assert refusal(call(user, report.pk)) == {
        "reason": "ambiguous_analyte",
        "field": "alp_u_per_l",
    }


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_engine_refusal_passes_through(user, report, analytes):
    for f in S2_UNITS:
        add(report, analytes, f, "0" if f == "crp_mg_per_dl" else None)
    assert refusal(call(user, report.pk)) == {
        "reason": "crp_not_positive",
        "field": "crp_mg_per_dl",
    }


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_unmapped_analyte_refuses(user, report, full, monkeypatch):
    monkeypatch.setattr(phenoage_binding, "LOINC_BY_FIELD", {})
    assert refusal(call(user, report.pk)) == {
        "reason": "analyte_not_mapped",
        "field": "albumin_g_per_l",
    }


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_access_rules(user, report, full):
    stranger = User.objects.create_user(
        email="b@example.com", password="correct-horse-9"
    )
    assert call(stranger, report.pk).status_code == 404
    assert call(user, report.pk).status_code == 200
    assert call(user, 999999).status_code == 404
    url = f"/api/labs/reports/{report.pk}/phenoage/?age_years=40"
    assert APIClient().get(url).status_code in (401, 403)


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize(
    "query", ["", "?age_years=", "?age_years=abc", "?age_years=nan", "?age_years=inf"]
)
def test_bad_age_is_400_naming_age_years(user, report, full, query):
    response = call(user, report.pk, query)
    assert response.status_code == 400
    assert "age_years" in response.json()


def test_no_conversion_factor_literal_in_binding():
    text = Path(phenoage_binding.__file__).read_text().replace("10*3/uL", "")
    assert not re.search(r"\*\s*\d|\d\s*\*|/\s*\d", text)


def test_codes_in_code_are_documented():
    root = Path(__file__).parents[2]
    doc = (root / "docs/research/phenoage-coefficients.md").read_text()
    # the real map is empty until a code is verified on loinc.org (Q79)
    for code in REAL_CODES.values():
        assert code in doc
