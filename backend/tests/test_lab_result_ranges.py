# SPDX-License-Identifier: AGPL-3.0-or-later
"""A stored result against its three ranges (M02 TG-m part 1).
All ranges, sources and bounds here are synthetic test fixtures; nothing is seeded."""

from datetime import date

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabReportOrigin, LabResult
from terminology.models import (
    OptimalRange,
    ReferenceRange,
    SafetyThreshold,
    Source,
    Unit,
    UnitConversion,
)


@pytest.fixture
def user(db):
    return User.objects.create_user(email="a@example.com", password="correct-horse-9")


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic range fixture",
        version="t1",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def units(source):
    return {
        code: Unit.objects.create(ucum_code=code, display=code, source=source)
        for code in ("xa/L", "xb/L")
    }


@pytest.fixture
def analyte(source, units):
    return Biomarker.objects.create(
        name="synthetic 0000-0",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=units["xa/L"],
        source=source,
    )


def make_result(user, analyte, value="5", unit="xa/L", **extra):
    report = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    return LabResult.objects.create(
        report=report,
        biomarker=analyte,
        reported_value=value,
        reported_unit=unit,
        **extra,
    )


def get(user, result):
    client = APIClient()
    client.force_authenticate(user)
    return client.get(f"/api/labs/results/{result.pk}/ranges/")


def reference(analyte, units, source, low, high, **extra):
    return ReferenceRange.objects.create(
        biomarker=analyte,
        unit=units["xa/L"],
        low=low,
        high=high,
        source=source,
        **extra,
    )


def optimal(analyte, units, source, low, high, **extra):
    fields = {
        "population": "synthetic population",
        "endpoint": "synthetic endpoint",
        "evidence_grade": "synthetic grade",
        "last_reviewed": date(2026, 11, 1),
    }
    fields.update(extra)
    return OptimalRange.objects.create(
        biomarker=analyte,
        unit=units["xa/L"],
        low=low,
        high=high,
        source=source,
        **fields,
    )


def test_inside_reference_but_above_complete_optimal(user, analyte, units, source):
    # scenario: biomarkers-and-labs::a-value-near-the-optimal-edge-but-within-reference
    reference(analyte, units, source, "1", "10")
    optimal(analyte, units, source, "2", "4")
    data = get(user, make_result(user, analyte, "5")).json()
    assert data["reference_range"]["status"] == "inside"
    assert data["optimal_range"]["status"] == "above"
    opt = data["optimal_range"]
    assert opt["source"]["name"] == "synthetic range fixture"
    assert opt["population"] == "synthetic population"
    assert opt["endpoint"] == "synthetic endpoint"
    assert opt["evidence_grade"] == "synthetic grade"
    assert opt["last_reviewed"] == "2026-11-01"
    assert data["reported_value"] == "5.000000"


@pytest.mark.parametrize(
    "missing", ["population", "endpoint", "evidence_grade", "last_reviewed"]
)
def test_incomplete_optimal_range_is_not_returned(
    user, analyte, units, source, missing
):
    # scenario: biomarkers-and-labs::inspecting-an-optimal-range
    optimal(analyte, units, source, "2", "4", **{missing: None})
    data = get(user, make_result(user, analyte)).json()
    assert data["optimal_range"] == {"status": "no_range"}


def test_three_ranges_are_separate_and_safety_alone(user, analyte, units, source):
    SafetyThreshold.objects.create(
        biomarker=analyte, unit=units["xa/L"], high="8", source=source
    )
    data = get(user, make_result(user, analyte, "9")).json()
    assert data["reference_range"] == {"status": "no_range"}
    assert data["optimal_range"] == {"status": "no_range"}
    assert data["safety_threshold"]["status"] == "above"
    assert data["safety_threshold"]["low"] is None
    assert data["safety_threshold"]["source"]["url"] == "https://example.org/synthetic"


def test_several_safety_thresholds_give_no_range(user, analyte, units, source):
    for high in ("8", "9"):
        SafetyThreshold.objects.create(
            biomarker=analyte, unit=units["xa/L"], high=high, source=source
        )
    data = get(user, make_result(user, analyte)).json()
    assert data["safety_threshold"]["status"] == "no_range"


def test_stored_conversion_uses_normalised_value(user, analyte, units, source):
    UnitConversion.objects.create(
        from_unit=units["xb/L"], to_unit=units["xa/L"], factor="2", source=source
    )
    reference(analyte, units, source, "1", "10")
    data = get(user, make_result(user, analyte, "3", "xb/L")).json()
    assert data["comparison_value"] is not None
    assert float(data["comparison_value"]) == 6.0
    assert data["comparison_unit"] == "xa/L"
    assert data["reported_unit"] == "xb/L"
    assert data["reference_range"]["status"] == "inside"
    assert data["converted"] is True
    assert data["conversion_source"]["name"] == source.name


def test_reported_unit_in_analyte_unit_has_no_conversion_source(
    user, analyte, units, source
):
    data = get(user, make_result(user, analyte)).json()
    assert data["converted"] is False
    assert data["conversion_source"] is None


def test_stratified_specific_row_does_not_hide_generic_fallback(
    user, analyte, units, source
):
    reference(analyte, units, source, "1", "2", lab="My Lab", sex="F")
    reference(analyte, units, source, "1", "10")
    result = make_result(user, analyte, "5", laboratory="My Lab")
    ref = get(user, result).json()["reference_range"]
    assert ref["high"] == "10.000000"
    assert ref["status"] == "inside"


def test_no_conversion_is_not_comparable(user, analyte, units, source):
    reference(analyte, units, source, "1", "10")
    optimal(analyte, units, source, "2", "4")
    data = get(user, make_result(user, analyte, "3", "xb/L")).json()
    assert data["comparison_value"] is None
    for key in ("reference_range", "optimal_range"):
        assert data[key]["status"] == "not_comparable"
        assert data[key]["reason"] == "no_value_in_analyte_unit"


def test_reference_lab_and_method_must_match(user, analyte, units, source):
    reference(analyte, units, source, "1", "10", lab="Other Lab")
    result = make_result(user, analyte, laboratory="My Lab")
    assert get(user, result).json()["reference_range"] == {"status": "no_range"}


def test_matching_lab_and_method_beats_generic(user, analyte, units, source):
    reference(analyte, units, source, "1", "2")
    reference(analyte, units, source, "6", "7", lab=" my lab ", method="Assay X")
    result = make_result(user, analyte, "5", laboratory="MY LAB", method="assay x")
    ref = get(user, result).json()["reference_range"]
    assert ref["low"] == "6.000000"
    assert ref["status"] == "below"
    assert ref["lab"] == " my lab "


def test_generic_row_is_fallback(user, analyte, units, source):
    reference(analyte, units, source, "1", "10")
    result = make_result(user, analyte, "5", laboratory="My Lab")
    assert get(user, result).json()["reference_range"]["status"] == "inside"


def test_equally_specific_reference_rows_give_no_range(user, analyte, units, source):
    reference(analyte, units, source, "1", "10")
    reference(analyte, units, source, "2", "9")
    assert get(user, make_result(user, analyte)).json()["reference_range"] == {
        "status": "no_range"
    }


def test_bounds_inclusive_and_open(user, analyte, units, source):
    reference(analyte, units, source, "5", "5")
    assert (
        get(user, make_result(user, analyte, "5")).json()["reference_range"]["status"]
        == "inside"
    )
    SafetyThreshold.objects.create(
        biomarker=analyte, unit=units["xa/L"], low="6", source=source
    )
    data = get(user, make_result(user, analyte, "1000")).json()
    assert data["safety_threshold"]["status"] == "inside"
    assert data["safety_threshold"]["high"] is None


def test_other_user_gets_404_and_anonymous_is_refused(user, analyte):
    result = make_result(user, analyte)
    other = User.objects.create_user(email="b@example.com", password="correct-horse-9")
    assert get(other, result).status_code == 404
    response = APIClient().get(f"/api/labs/results/{result.pk}/ranges/")
    assert response.status_code in (401, 403)
