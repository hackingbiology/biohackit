# SPDX-License-Identifier: AGPL-3.0-or-later
"""Stratified range selection. All rows are synthetic TEST FIXTURES, not reference data."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.models import Biomarker, BiomarkerRole
from terminology.models import OptimalRange, ReferenceRange, Source, Unit
from terminology.selectors import (
    Subject,
    applicable_reference_range,
    displayable_optimal_range,
)

COMPLETE = {
    "population": "synthetic test population",
    "endpoint": "synthetic test endpoint",
    "evidence_grade": "synthetic test grade",
    "last_reviewed": date(2026, 1, 1),
}


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="TEST FIXTURE",
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


@pytest.fixture
def make(biomarker, unit, source):
    def _make(model=OptimalRange, **kw):
        fields = dict(COMPLETE) if model is OptimalRange else {}
        fields.update(kw)
        return model.objects.create(
            biomarker=biomarker,
            unit=unit,
            source=source,
            low=Decimal("1"),
            high=Decimal("2"),
            **fields,
        )

    return _make


# scenario: terminology-reference-data::most-specific-stratum-wins
def test_most_specific_stratum_wins(biomarker, make):
    make()
    sex_row = make(sex="F")
    assert displayable_optimal_range(biomarker, Subject(sex="F")) == sex_row


# scenario: terminology-reference-data::most-specific-stratum-wins
def test_more_dimensions_beat_fewer(biomarker, make):
    make(sex="F")
    both = make(sex="F", age_min_years=18, age_max_years=40)
    assert displayable_optimal_range(biomarker, Subject(age_years=20, sex="F")) == both


# scenario: terminology-reference-data::non-matching-stratum-is-excluded
def test_other_sex_is_excluded(biomarker, make):
    make(sex="M")
    assert displayable_optimal_range(biomarker, Subject(sex="F")) is None


# scenario: terminology-reference-data::non-matching-stratum-is-excluded
def test_outside_age_band_is_excluded(biomarker, make):
    unstrat = make()
    make(age_min_years=18, age_max_years=40)
    assert displayable_optimal_range(biomarker, Subject(age_years=50)) == unstrat


# scenario: terminology-reference-data::non-matching-stratum-is-excluded
def test_other_ancestry_is_excluded(biomarker, make):
    make(ancestry="synthetic group A")
    assert displayable_optimal_range(biomarker, Subject(ancestry="group B")) is None


@pytest.mark.parametrize(
    ("age", "matches"), [(17, False), (18, True), (39, True), (40, False)]
)
def test_age_band_min_inclusive_max_exclusive(biomarker, make, age, matches):
    row = make(age_min_years=18, age_max_years=40)
    expected = row if matches else None
    assert displayable_optimal_range(biomarker, Subject(age_years=age)) == expected


def test_open_ended_age_bands(biomarker, make):
    row = make(age_min_years=65)
    assert displayable_optimal_range(biomarker, Subject(age_years=90)) == row
    assert displayable_optimal_range(biomarker, Subject(age_years=64)) is None


# scenario: terminology-reference-data::unknown-subject-attribute
def test_unknown_sex_skips_sex_row(biomarker, make):
    make(sex="F")
    unstrat = make(population="synthetic unstratified")
    assert displayable_optimal_range(biomarker, Subject(sex=None)) == unstrat


# scenario: terminology-reference-data::unknown-subject-attribute
def test_unknown_age_and_ancestry_match_only_null_strata(biomarker, make):
    make(age_min_years=1, age_max_years=5)
    make(ancestry="synthetic group A")
    assert displayable_optimal_range(biomarker, Subject()) is None
    assert displayable_optimal_range(biomarker) is None


# scenario: terminology-reference-data::tie-between-equally-specific-strata
def test_tie_at_top_specificity_returns_none(biomarker, make):
    make(sex="F", population="synthetic one")
    make(sex="F", population="synthetic two")
    assert displayable_optimal_range(biomarker, Subject(sex="F")) is None


# scenario: terminology-reference-data::tie-between-equally-specific-strata
def test_tie_between_different_dimensions_returns_none(biomarker, make):
    make(sex="F")
    make(age_min_years=18, age_max_years=40)
    assert displayable_optimal_range(biomarker, Subject(age_years=20, sex="F")) is None


# scenario: terminology-reference-data::incomplete-specific-row-does-not-win
def test_incomplete_specific_row_does_not_win(biomarker, make):
    unstrat = make()
    make(sex="F", endpoint=None)
    assert displayable_optimal_range(biomarker, Subject(sex="F")) == unstrat


# scenario: terminology-reference-data::complete-provenance
def test_no_subject_returns_single_unstratified_row(biomarker, make):
    row = make()
    assert displayable_optimal_range(biomarker) == row


# scenario: terminology-reference-data::incomplete-provenance
def test_incomplete_only_row_returns_none_for_subject(biomarker, make):
    make(sex="F", evidence_grade="  ")
    assert displayable_optimal_range(biomarker, Subject(sex="F")) is None


@pytest.mark.parametrize("model", [ReferenceRange, OptimalRange])
@pytest.mark.parametrize(("low", "high"), [(40, 18), (18, 18)])
def test_clean_rejects_age_min_not_below_max(biomarker, make, model, low, high):
    with pytest.raises(ValidationError, match="age_min_years"):
        make(model, age_min_years=low, age_max_years=high)


@pytest.mark.parametrize("model", [ReferenceRange, OptimalRange])
def test_database_constraint_rejects_age_min_not_below_max(
    biomarker, unit, source, model
):
    row = model(
        biomarker=biomarker,
        unit=unit,
        source=source,
        low=Decimal("1"),
        age_min_years=40,
        age_max_years=18,
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        model.objects.bulk_create([row])


def test_blank_ancestry_is_stored_as_none(make):
    row = make(ancestry="   ")
    row.refresh_from_db()
    assert row.ancestry is None


def test_blank_sex_is_stored_as_none(make):
    row = make(sex="  ")
    row.refresh_from_db()
    assert row.sex is None


@pytest.mark.parametrize("bad", ["f", "Z", "MF"])
def test_invalid_sex_is_rejected(make, bad):
    with pytest.raises(ValidationError):
        make(sex=bad)


def test_ancestry_matches_after_strip_and_casefold(biomarker, make):
    row = make(ancestry="  Synthetic Group A ")
    assert (
        displayable_optimal_range(biomarker, Subject(ancestry="synthetic group a"))
        == row
    )


def test_reference_range_selector_uses_strata(biomarker, make):
    make(ReferenceRange)
    sex_row = make(ReferenceRange, sex="M", evidence_grade="synthetic test grade")
    assert applicable_reference_range(biomarker, Subject(sex="M")) == sex_row
    assert applicable_reference_range(biomarker, Subject(sex="F")) is not None
    make(ReferenceRange, sex="M", lab="another")
    assert applicable_reference_range(biomarker, Subject(sex="M")) is None
