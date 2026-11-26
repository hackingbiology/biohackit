# SPDX-License-Identifier: AGPL-3.0-or-later
"""LabReport / LabResult (M02 TG-a part 1). Synthetic rows only: no real ranges or factors."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from core.models import (
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
    LabResultValidation,
)
from terminology.models import Source, Unit, UnitConversion


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="lab@example.com", password="correct-horse-battery-9"
    )


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )


@pytest.fixture
def unit_a(source):
    return Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)


@pytest.fixture
def unit_b(source):
    return Unit.objects.create(ucum_code="xb/L", display="xb/L", source=source)


@pytest.fixture
def analyte(unit_a, source):
    return Biomarker.objects.create(
        name="synthetic analyte",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit_a,
        source=source,
    )


@pytest.fixture
def report(user):
    return LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)


def result(report, analyte, **kw):
    kw.setdefault("reported_value", Decimal("2"))
    kw.setdefault("reported_unit", "xa/L")
    return LabResult.objects.create(report=report, biomarker=analyte, **kw)


def test_result_records_its_source(user, analyte):
    # scenario: biomarkers-and-labs::a-result-records-its-source
    imported = LabReport.objects.create(
        owner=user, origin=LabReportOrigin.IMPORT, import_name="synthetic.csv"
    )
    row = result(imported, analyte)
    row.refresh_from_db()
    assert row.report.origin == "import"
    assert row.report.import_name == "synthetic.csv"
    assert row.validation_state == LabResultValidation.UNREVIEWED


def test_import_requires_a_name(user):
    # scenario: biomarkers-and-labs::a-result-records-its-source
    with pytest.raises(ValidationError):
        LabReport.objects.create(owner=user, origin=LabReportOrigin.IMPORT)


def test_no_method_is_stored_and_not_eligible(report, analyte):
    # scenario: biomarkers-and-labs::a-result-without-laboratory-or-method-is-not-aggregation-eligible
    row = result(report, analyte, laboratory="Lab X")
    assert LabResult.objects.get(pk=row.pk).aggregation_eligible is False
    full = result(report, analyte, laboratory="Lab X", method="Method Y")
    assert full.aggregation_eligible is True


def test_laboratory_inherited_only_when_report_states_it(user, analyte):
    # scenario: biomarkers-and-labs::a-result-without-laboratory-or-method-is-not-aggregation-eligible
    stated = LabReport.objects.create(
        owner=user, origin=LabReportOrigin.MANUAL, laboratory="Lab R"
    )
    assert result(stated, analyte, method="M").laboratory == "Lab R"
    silent = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    row = result(silent, analyte, method="M")
    assert row.laboratory is None
    assert row.aggregation_eligible is False


def test_reported_value_kept(report, analyte, unit_b):
    # scenario: biomarkers-and-labs::a-stored-result-keeps-the-reported-value
    UnitConversion.objects.create(
        from_unit=unit_b,
        to_unit=analyte.unit,
        factor=Decimal("3"),
        source=analyte.source,
    )
    row = result(report, analyte, reported_value=Decimal("5"), reported_unit="xb/L")
    row.refresh_from_db()
    assert row.reported_value == Decimal("5")
    assert row.reported_unit == "xb/L"
    assert row.reported_unit_ref == unit_b


def test_same_unit_is_identity(report, analyte):
    # scenario: biomarkers-and-labs::reported-unit-equals-the-analyte-unit
    row = result(report, analyte, reported_value=Decimal("7.5"))
    assert row.normalised_value == Decimal("7.5")
    assert row.normalised_unit == "xa/L"
    assert row.normalised_source is None  # identity: no factor used


def test_stored_factor_normalises(report, analyte, unit_b):
    # scenario: biomarkers-and-labs::a-stored-factor-yields-the-normalised-value
    UnitConversion.objects.create(
        from_unit=unit_b,
        to_unit=analyte.unit,
        factor=Decimal("3"),
        source=analyte.source,
    )
    row = result(report, analyte, reported_value=Decimal("5"), reported_unit="xb/L")
    assert row.normalised_value == Decimal("15")
    assert row.normalised_unit == "xa/L"
    assert row.normalised_source == analyte.source  # provenance of the factor


def test_no_factor_leaves_normalised_empty(report, analyte, unit_b):
    # scenario: biomarkers-and-labs::no-conversion-factor-leaves-the-normalised-value-empty
    row = result(report, analyte, reported_value=Decimal("5"), reported_unit="xb/L")
    row.refresh_from_db()
    assert row.normalised_value is None
    assert row.normalised_unit is None
    assert row.normalised_source is None
    assert row.reported_value == Decimal("5")
    assert row.reported_unit == "xb/L"


def test_unknown_unit_is_kept_without_reference(report, analyte):
    # scenario: biomarkers-and-labs::no-conversion-factor-leaves-the-normalised-value-empty
    row = result(report, analyte, reported_unit="not-stored")
    row.refresh_from_db()
    assert row.reported_unit_ref is None
    assert row.normalised_value is None
    assert row.reported_unit == "not-stored"


def test_collected_and_reported_times_are_distinct(report, analyte):
    # scenario: biomarkers-and-labs::collected-and-reported-times-are-distinct
    when = datetime(2026, 11, 1, 8, 0, tzinfo=UTC)
    row = result(report, analyte, collected_at=when)
    row.refresh_from_db()
    assert row.collected_at == when
    assert row.reported_at is None


def test_both_times_round_trip_separately(report, analyte):
    # scenario: biomarkers-and-labs::collected-and-reported-times-are-distinct
    collected = datetime(2026, 11, 1, 8, 0, tzinfo=UTC)
    reported = datetime(2026, 11, 3, 15, 30, tzinfo=UTC)
    row = result(report, analyte, collected_at=collected, reported_at=reported)
    row.refresh_from_db()
    assert row.collected_at == collected
    assert row.reported_at == reported


def test_reported_only_leaves_collected_empty(report, analyte):
    # scenario: biomarkers-and-labs::collected-and-reported-times-are-distinct
    reported = datetime(2026, 11, 3, 15, 30, tzinfo=UTC)
    row = result(report, analyte, reported_at=reported)
    row.refresh_from_db()
    assert row.reported_at == reported
    assert row.collected_at is None


@pytest.mark.parametrize("origin", ["", "foo"])
def test_report_requires_a_valid_origin(user, origin):
    # scenario: biomarkers-and-labs::a-result-records-its-source
    with pytest.raises(ValidationError):
        LabReport.objects.create(owner=user, origin=origin)
    assert not LabReport.objects.exists()


@pytest.mark.parametrize(
    "bad",
    [
        Decimal("1.2345678"),
        Decimal("123456789012345"),
        Decimal("1.0000000000000000000000000001"),
    ],
)
def test_value_that_does_not_fit_is_rejected(report, analyte, bad):
    # scenario: biomarkers-and-labs::a-stored-result-keeps-the-reported-value
    with pytest.raises(ValidationError):
        result(report, analyte, reported_value=bad)
    assert not LabResult.objects.exists()


@pytest.mark.parametrize("bad", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_value_is_rejected(report, analyte, bad):
    # scenario: biomarkers-and-labs::a-stored-result-keeps-the-reported-value
    with pytest.raises(ValidationError):
        result(report, analyte, reported_value=bad)
    assert not LabResult.objects.exists()


def test_six_decimals_round_trip_exactly(report, analyte, unit_b):
    # scenario: biomarkers-and-labs::a-stored-result-keeps-the-reported-value
    UnitConversion.objects.create(
        from_unit=unit_b,
        to_unit=analyte.unit,
        factor=Decimal("3"),
        source=analyte.source,
    )
    row = result(
        report, analyte, reported_value=Decimal("1.234567"), reported_unit="xb/L"
    )
    row.refresh_from_db()
    assert row.reported_value == Decimal("1.234567")
    assert row.normalised_value == Decimal("1.234567") * 3


def test_trailing_zeros_beyond_six_decimals_are_accepted(report, analyte):
    # scenario: biomarkers-and-labs::a-stored-result-keeps-the-reported-value
    row = result(report, analyte, reported_value=Decimal("5.1000000"))
    row.refresh_from_db()
    assert row.reported_value == Decimal("5.1")


def test_float_input_has_no_binary_noise(report, analyte):
    # scenario: biomarkers-and-labs::a-stored-result-keeps-the-reported-value
    row = result(report, analyte, reported_value=0.1)
    row.refresh_from_db()
    assert row.reported_value == Decimal("0.1")
