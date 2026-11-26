# SPDX-License-Identifier: AGPL-3.0-or-later
"""Calculated quotient markers (M02 TG-n part 1). Synthetic rows only: the analytes,
units, conversion and definition are test fixtures, not seeded data (Q83)."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework.test import APIClient

from accounts.models import User
from core.calculated_markers import compute_ratios
from core.models import (
    Biomarker,
    BiomarkerRole,
    CalculatedRatioDefinition,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
)
from terminology.models import Source, Unit, UnitConversion


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
    return {
        c: Unit.objects.create(ucum_code=c, display=c, source=source)
        for c in ("u1", "u2", "u3")
    }


@pytest.fixture
def num(units, source):
    return Biomarker.objects.create(
        name="synthetic num",
        loinc_code="T-num",
        role=BiomarkerRole.BASELINE,
        unit=units["u1"],
        source=source,
    )


@pytest.fixture
def den(units, source):
    return Biomarker.objects.create(
        name="synthetic den",
        loinc_code="T-den",
        role=BiomarkerRole.BASELINE,
        unit=units["u2"],
        source=source,
    )


@pytest.fixture
def definition(num, den, units, source):
    return CalculatedRatioDefinition.objects.create(
        name="synthetic ratio",
        numerator=num,
        denominator=den,
        numerator_unit=units["u1"],
        denominator_unit=units["u2"],
        source=source,
    )


@pytest.fixture
def report(user):
    return LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)


def add(report, biomarker, value, unit, **kw):
    return LabResult.objects.create(
        report=report,
        biomarker=biomarker,
        reported_value=value,
        reported_unit=unit,
        **kw,
    )


def call(user, pk):
    client = APIClient()
    client.force_authenticate(user)
    return client.get(f"/api/labs/reports/{pk}/calculated/")


def only_marker(user, report):
    response = call(user, report.pk)
    assert response.status_code == 200
    (marker,) = response.json()["markers"]
    return marker


# scenario: biomarkers-and-labs::a-ratio-is-computed-from-its-inputs
def test_computed_with_exact_unit_match(user, report, definition, num, den):
    n = add(report, num, "6", "u1", collected_at="2026-11-01T08:00:00Z")
    d = add(report, den, "4", "u2", reported_at="2026-11-02T08:00:00Z")
    marker = only_marker(user, report)
    assert marker["status"] == "computed"
    assert marker["calculated"] is True
    assert Decimal(marker["value"]) == Decimal("1.5")
    assert marker["source"]["name"] == "synthetic fixture"
    by_role = {i["role"]: i for i in marker["inputs"]}
    assert by_role["numerator"]["lab_result_id"] == n.pk
    assert by_role["denominator"]["lab_result_id"] == d.pk
    assert by_role["numerator"]["collected_at"].startswith("2026-11-01")
    assert by_role["denominator"]["reported_at"].startswith("2026-11-02")
    assert by_role["numerator"]["converted"] is False
    assert marker["unit_note"].startswith("u1 / u2")


# scenario: biomarkers-and-labs::a-ratio-is-computed-from-its-inputs
def test_computed_through_stored_conversion(
    user, report, definition, num, den, units, source
):
    UnitConversion.objects.create(
        from_unit=units["u3"],
        to_unit=units["u2"],
        factor=Decimal("2"),
        source=source,
    )
    add(report, num, "6", "u1")
    add(report, den, "1", "u3")
    marker = only_marker(user, report)
    assert Decimal(marker["value"]) == Decimal("3")
    denominator = next(i for i in marker["inputs"] if i["role"] == "denominator")
    assert denominator["converted"] is True
    assert denominator["conversion_source"]["name"] == "synthetic fixture"
    numerator = next(i for i in marker["inputs"] if i["role"] == "numerator")
    assert numerator["conversion_source"] is None
    assert denominator["reported_value"] == "1.000000"
    assert denominator["reported_unit"] == "u3"
    assert denominator["unit_used"] == "u2"


# scenario: biomarkers-and-labs::a-missing-input-yields-no-value
def test_missing_numerator(user, report, definition, den):
    add(report, den, "4", "u2")
    marker = only_marker(user, report)
    assert marker["status"] == "not_computable"
    assert marker["value"] is None
    assert marker["calculated"] is True
    assert marker["reasons"] == ["missing_input:numerator"]
    assert "inputs" not in marker


# scenario: biomarkers-and-labs::a-missing-input-yields-no-value
def test_missing_denominator(user, report, definition, num):
    add(report, num, "4", "u1")
    marker = only_marker(user, report)
    assert marker["value"] is None
    assert marker["reasons"] == ["missing_input:denominator"]


# scenario: biomarkers-and-labs::a-missing-input-yields-no-value
def test_denominator_zero(user, report, definition, num, den):
    add(report, num, "4", "u1")
    add(report, den, "0", "u2")
    marker = only_marker(user, report)
    assert marker["value"] is None
    assert marker["reasons"] == ["denominator_zero"]


# scenario: biomarkers-and-labs::a-missing-input-yields-no-value
def test_unit_not_convertible(user, report, definition, num, den):
    add(report, num, "4", "u3")
    add(report, den, "2", "u2")
    marker = only_marker(user, report)
    assert marker["value"] is None
    assert marker["reasons"] == ["unit_not_convertible:numerator"]


# scenario: biomarkers-and-labs::a-missing-input-yields-no-value
def test_two_candidates_are_ambiguous(user, report, definition, num, den):
    add(report, num, "4", "u1")
    add(report, num, "5", "u1")
    add(report, den, "2", "u2")
    marker = only_marker(user, report)
    assert marker["value"] is None
    assert marker["reasons"] == ["ambiguous_input:numerator"]


# scenario: biomarkers-and-labs::a-missing-input-yields-no-value
@pytest.mark.parametrize(
    "state", [LabResultValidation.RETRACTED, LabResultValidation.DISPUTED]
)
def test_excluded_states_ignored(user, report, definition, num, den, state):
    add(report, num, "4", "u1", validation_state=state)
    add(report, den, "2", "u2")
    marker = only_marker(user, report)
    assert marker["value"] is None
    assert marker["reasons"] == ["missing_input:numerator"]


# scenario: biomarkers-and-labs::a-ratio-is-computed-from-its-inputs
def test_excluded_duplicate_does_not_make_ambiguous(user, report, definition, num, den):
    add(report, num, "9", "u1", validation_state=LabResultValidation.RETRACTED)
    add(report, num, "4", "u1")
    add(report, den, "2", "u2")
    assert Decimal(only_marker(user, report)["value"]) == Decimal("2")


# scenario: biomarkers-and-labs::a-ratio-is-computed-from-its-inputs
def test_deterministic(user, report, definition, num, den):
    add(report, num, "1", "u1")
    add(report, den, "3", "u2")
    first = call(user, report.pk).json()
    assert call(user, report.pk).json() == first
    assert first["markers"][0]["value"] == "0.3333333333333333333333333333"
    assert compute_ratios(report) == first["markers"]


def test_other_users_report_is_404(user, report, definition):
    other = User.objects.create_user(email="b@example.com", password="correct-horse-9")
    assert call(other, report.pk).status_code == 404


def test_missing_report_is_404(user):
    assert call(user, 999999).status_code == 404


def test_unauthenticated_refused(report):
    response = APIClient().get(f"/api/labs/reports/{report.pk}/calculated/")
    assert response.status_code in (401, 403)


def test_no_definitions_gives_empty_list(user, report):
    body = call(user, report.pk).json()
    assert body == {
        "report_id": report.pk,
        "markers": [],
        "note": "no_definitions_stored",
    }


def test_definition_without_source_refused(num, den, units):
    with pytest.raises(ValidationError):
        CalculatedRatioDefinition.objects.create(
            name="no source",
            numerator=num,
            denominator=den,
            numerator_unit=units["u1"],
            denominator_unit=units["u2"],
        )


def test_numerator_equal_denominator_refused(num, units, source):
    with pytest.raises(ValidationError):
        CalculatedRatioDefinition.objects.create(
            name="same",
            numerator=num,
            denominator=num,
            numerator_unit=units["u1"],
            denominator_unit=units["u1"],
            source=source,
        )


def test_database_check_constraint(num, units, source):
    row = CalculatedRatioDefinition(
        name="same",
        numerator=num,
        denominator=num,
        numerator_unit=units["u1"],
        denominator_unit=units["u1"],
        source=source,
    )
    with pytest.raises(IntegrityError):
        super(CalculatedRatioDefinition, row).save()


def test_duplicate_inputs_refused(definition, units, source):
    with pytest.raises(IntegrityError):
        CalculatedRatioDefinition.objects.create(
            name="other name",
            numerator=definition.numerator,
            denominator=definition.denominator,
            numerator_unit=units["u1"],
            denominator_unit=units["u2"],
            source=source,
        )
