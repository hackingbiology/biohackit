# SPDX-License-Identifier: AGPL-3.0-or-later
"""Range models and the optimal-range provenance gate. All values are synthetic test
fixtures, not reference data."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.models import Biomarker, BiomarkerRole
from terminology.models import (
    OptimalRange,
    ReferenceRange,
    SafetyThreshold,
    Source,
    Unit,
)
from terminology.selectors import displayable_optimal_range


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="test fixture",
        licence="test only",
        url="https://example.org/test-fixture",
        retrieved_at=date(2026, 11, 25),
    )


@pytest.fixture
def unit(source):
    return Unit.objects.create(ucum_code="mg/L", display="mg/L", source=source)


@pytest.fixture
def biomarker(unit, source):
    return Biomarker.objects.create(
        name="test analyte",
        loinc_code="TEST-1",
        role=BiomarkerRole.SAFETY,
        unit=unit,
        source=source,
    )


COMPLETE = {
    "population": "synthetic test population",
    "endpoint": "synthetic test endpoint",
    "evidence_grade": "synthetic test grade",
    "last_reviewed": date(2026, 1, 1),
}


def optimal(biomarker, unit, source, **kw):
    fields = {**COMPLETE, **kw}
    return OptimalRange.objects.create(
        biomarker=biomarker,
        unit=unit,
        source=source,
        low=Decimal("1"),
        high=Decimal("2"),
        **fields,
    )


MODELS = [ReferenceRange, OptimalRange, SafetyThreshold]


@pytest.mark.parametrize("model", MODELS)
def test_range_without_source_rejected(model, biomarker, unit):
    with pytest.raises(ValidationError, match="requires a source"):
        model(biomarker=biomarker, unit=unit, low=Decimal("1")).save()


# scenario: terminology-reference-data::range-bounds-in-analyte-unit
@pytest.mark.parametrize("model", MODELS)
def test_range_unit_must_equal_analyte_unit(model, biomarker, source):
    other = Unit.objects.create(ucum_code="g/L", display="g/L", source=source)
    with pytest.raises(ValidationError, match="unit"):
        model(biomarker=biomarker, unit=other, low=Decimal("1"), source=source).save()
    assert model.objects.count() == 0


@pytest.mark.parametrize("model", MODELS)
def test_range_low_above_high_rejected(model, biomarker, unit, source):
    with pytest.raises(ValidationError, match="low"):
        model(
            biomarker=biomarker,
            unit=unit,
            source=source,
            low=Decimal("2"),
            high=Decimal("1"),
        ).save()


@pytest.mark.parametrize("model", MODELS)
def test_range_needs_a_bound(model, biomarker, unit, source):
    with pytest.raises(ValidationError, match="bound"):
        model(biomarker=biomarker, unit=unit, source=source).save()


@pytest.mark.parametrize("model", MODELS)
def test_range_equal_and_open_bounds_accepted(model, biomarker, unit, source):
    kw = {"biomarker": biomarker, "unit": unit, "source": source}
    model(low=Decimal("1"), high=Decimal("1"), **kw).save()
    model(low=Decimal("1"), **kw).save()
    model(high=Decimal("1"), **kw).save()
    assert model.objects.count() == 3


@pytest.mark.parametrize("model", MODELS)
def test_database_constraints_back_up_the_validation(model, biomarker, unit, source):
    kw = {"biomarker": biomarker, "unit": unit, "source": source}
    for bounds in ({}, {"low": Decimal("2"), "high": Decimal("1")}):
        with pytest.raises(IntegrityError), transaction.atomic():
            model.objects.bulk_create([model(**bounds, **kw)])


# scenario: terminology-reference-data::complete-provenance
def test_complete_optimal_range_is_returned(biomarker, unit, source):
    row = optimal(biomarker, unit, source)
    assert displayable_optimal_range(biomarker) == row


# scenario: terminology-reference-data::incomplete-provenance
@pytest.mark.parametrize("field", ["population", "endpoint", "evidence_grade"])
@pytest.mark.parametrize("blank", [None, "", "   "])
def test_optimal_range_with_blank_text_field_not_displayable(
    biomarker, unit, source, field, blank
):
    optimal(biomarker, unit, source, **{field: blank})
    assert displayable_optimal_range(biomarker) is None


# scenario: terminology-reference-data::incomplete-provenance
def test_optimal_range_without_last_reviewed_not_displayable(biomarker, unit, source):
    optimal(biomarker, unit, source, last_reviewed=None)
    assert displayable_optimal_range(biomarker) is None


# scenario: terminology-reference-data::incomplete-provenance
def test_optimal_range_without_source_not_displayable(biomarker, unit, source):
    row = optimal(biomarker, unit, source)
    row.source_id = None  # an unsaved, source-less instance: the gate checks it too
    from terminology.selectors import _complete

    assert _complete(row, biomarker) is False


# scenario: terminology-reference-data::range-bounds-in-analyte-unit
def test_unit_change_blocked_while_ranges_use_old_unit(biomarker, unit, source):
    optimal(biomarker, unit, source)
    other = Unit.objects.create(ucum_code="g/L", display="g/L", source=source)
    biomarker.unit = other
    with pytest.raises(ValidationError):
        biomarker.save()
    biomarker.refresh_from_db()
    assert biomarker.unit_id == unit.pk


# scenario: terminology-reference-data::range-bounds-in-analyte-unit
def test_unit_change_allowed_without_ranges(biomarker, source):
    other = Unit.objects.create(ucum_code="g/L", display="g/L", source=source)
    biomarker.unit = other
    biomarker.save()
    biomarker.refresh_from_db()
    assert biomarker.unit_id == other.pk


# scenario: terminology-reference-data::range-bounds-in-analyte-unit
def test_selector_ignores_row_whose_unit_differs_from_analyte(biomarker, unit, source):
    row = optimal(biomarker, unit, source)
    other = Unit.objects.create(ucum_code="g/L", display="g/L", source=source)
    # bypass save() to simulate stale data (e.g. a raw update)
    Biomarker.objects.filter(pk=biomarker.pk).update(unit=other)
    biomarker.refresh_from_db()
    assert row.unit_id != biomarker.unit_id
    assert displayable_optimal_range(biomarker) is None


def test_no_optimal_range_is_none(biomarker):
    assert displayable_optimal_range(biomarker) is None


def test_several_complete_rows_return_none(biomarker, unit, source):
    optimal(biomarker, unit, source)
    optimal(biomarker, unit, source, population="another synthetic population")
    assert displayable_optimal_range(biomarker) is None


def test_one_complete_among_incomplete_rows_is_returned(biomarker, unit, source):
    row = optimal(biomarker, unit, source)
    optimal(biomarker, unit, source, endpoint=None)
    assert displayable_optimal_range(biomarker) == row
