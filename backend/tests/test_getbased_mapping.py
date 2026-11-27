# SPDX-License-Identifier: AGPL-3.0-or-later
"""Stored, cited mapping from get-based marker keys (X01 part 2a). Synthetic rows only."""

from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from core.models import Biomarker, BiomarkerRole, GetbasedMarkerMapping
from terminology.models import Source, Unit

SHA = "a" * 40
PATH = "js/marker-schema/synthetic.ts"


@pytest.fixture
def source(db):
    return Source.objects.create(
        name="synthetic mapping source",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 27),
    )


@pytest.fixture
def unit(source):
    return Unit.objects.create(ucum_code="xa/L", display="xa/L", source=source)


@pytest.fixture
def analyte(source, unit):
    return Biomarker.objects.create(
        name="synthetic analyte",
        loinc_code="0000-0",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )


def _row(source, **kw):
    kw.setdefault("kind", "measured")
    return GetbasedMarkerMapping(
        getbased_key=kw.pop("key", "syn.a"), source=source, **kw
    )


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
def test_valid_measured_row_with_unit_citation_saves(source, analyte, unit):
    row = _row(
        source,
        biomarker=analyte,
        unit=unit,
        unit_source_path=PATH,
        unit_source_commit=SHA,
    )
    row.save()
    assert GetbasedMarkerMapping.objects.get().unit_source_commit == SHA


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
def test_measured_row_without_unit_citation_saves_but_is_unverified(source, analyte):
    _row(source, biomarker=analyte).save()
    assert GetbasedMarkerMapping.objects.get().unit is None


# scenario: biomarkers-and-labs::mapping-row-cites-the-get-based-catalogue-unit
@pytest.mark.parametrize(
    ("with_unit", "path", "commit"),
    [
        (False, PATH, ""),  # path without unit and sha
        (False, "", SHA),  # sha without unit and path
        (True, PATH, "abc123"),  # sha is not 40 hex characters
        (True, PATH, "A" * 40),  # uppercase is not the pinned form
        (True, "", SHA),  # unit and sha without a path
        (True, PATH, ""),  # unit and path without a sha
    ],
)
def test_partial_or_malformed_unit_citation_is_refused(
    source, analyte, unit, with_unit, path, commit
):
    row = _row(
        source,
        biomarker=analyte,
        unit=unit if with_unit else None,
        unit_source_path=path,
        unit_source_commit=commit,
    )
    with pytest.raises(ValidationError):
        row.save()
    assert GetbasedMarkerMapping.objects.count() == 0


def test_measured_row_without_biomarker_is_refused(source):
    with pytest.raises(ValidationError):
        _row(source).save()


# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
def test_measured_row_for_calculated_ratio_key_is_refused(source, analyte):
    with pytest.raises(ValidationError):
        _row(source, key="calculatedRatios.x", biomarker=analyte).save()


# scenario: biomarkers-and-labs::calculated-ratios-are-never-stored-as-measured
def test_deny_list_row_saves_and_carries_no_biomarker_or_unit(source, analyte, unit):
    _row(source, key="calculatedRatios.x", kind="calculated").save()
    _row(source, key="syn.homa", kind="calculated").save()
    assert GetbasedMarkerMapping.objects.count() == 2
    with pytest.raises(ValidationError):
        _row(source, key="syn.b", kind="calculated", biomarker=analyte).save()
    with pytest.raises(ValidationError):
        _row(
            source,
            key="syn.c",
            kind="calculated",
            unit=unit,
            unit_source_path=PATH,
            unit_source_commit=SHA,
        ).save()


def test_duplicate_key_is_refused(source, analyte):
    _row(source, biomarker=analyte).save()
    with pytest.raises(IntegrityError), transaction.atomic():
        _row(source, biomarker=analyte).save()


def test_row_requires_a_source_and_a_known_kind(source, analyte):
    with pytest.raises(ValidationError):
        GetbasedMarkerMapping(getbased_key="syn.a", kind="measured").save()
    with pytest.raises(ValidationError):
        _row(source, kind="guessed", biomarker=analyte).save()


def test_database_refuses_rows_that_skip_the_model_checks(source, analyte, unit):
    with pytest.raises(IntegrityError), transaction.atomic():
        GetbasedMarkerMapping.objects.bulk_create([_row(source)])
    with pytest.raises(IntegrityError), transaction.atomic():
        GetbasedMarkerMapping.objects.bulk_create(
            [_row(source, key="calculatedRatios.y", biomarker=analyte)]
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        GetbasedMarkerMapping.objects.bulk_create(
            [_row(source, biomarker=analyte, unit_source_path=PATH)]
        )
    with pytest.raises(IntegrityError), transaction.atomic():
        GetbasedMarkerMapping.objects.bulk_create(
            [_row(source, kind="calculated", biomarker=analyte)]
        )


def test_str_is_the_key(source, analyte):
    assert str(_row(source, biomarker=analyte)) == "syn.a"
