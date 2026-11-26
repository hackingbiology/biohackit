# SPDX-License-Identifier: AGPL-3.0-or-later
"""Analyte category and the DEXA/microbiome provenance rule (M02 TG-a part 2). Synthetic rows only."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from accounts.models import User
from core.models import (
    AnalyteCategory,
    Biomarker,
    BiomarkerRole,
    LabReport,
    LabReportOrigin,
    LabResult,
)
from terminology.models import Source, Unit


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
def report(db):
    user = User.objects.create_user(
        email="cat@example.com", password="correct-horse-battery-9"
    )
    return LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)


def analyte(unit, source, code, category=None):
    return Biomarker.objects.create(
        name=f"synthetic {code}",
        loinc_code=code,
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
        category=category,
        category_source=source if category else None,
    )


def add(report, biomarker, **kw):
    return LabResult.objects.create(
        report=report,
        biomarker=biomarker,
        reported_value=Decimal("2"),
        reported_unit="xa/L",
        **kw,
    )


def test_dexa_without_method_is_refused(report, unit, source):
    # scenario: biomarkers-and-labs::a-dexa-or-microbiome-result-without-provenance-is-not-stored
    dexa = analyte(unit, source, "1-1", AnalyteCategory.BODY_COMPOSITION)
    with pytest.raises(ValidationError, match="method"):
        add(report, dexa, laboratory="Lab X")
    assert LabResult.objects.count() == 0


def test_microbiome_without_laboratory_is_refused(report, unit, source):
    # scenario: biomarkers-and-labs::result-without-provenance
    micro = analyte(unit, source, "2-2", AnalyteCategory.MICROBIOME)
    with pytest.raises(ValidationError, match="laboratory"):
        add(report, micro, method="M")
    assert LabResult.objects.count() == 0


def test_report_laboratory_alone_does_not_satisfy_method(report, unit, source):
    # scenario: biomarkers-and-labs::a-dexa-or-microbiome-result-without-provenance-is-not-stored
    report.laboratory = "Lab R"
    report.save()
    micro = analyte(unit, source, "2-2", AnalyteCategory.MICROBIOME)
    with pytest.raises(ValidationError, match="method") as err:
        add(report, micro, method="  ")
    assert "laboratory" not in str(err.value)
    assert LabResult.objects.count() == 0


def test_dexa_with_provenance_is_stored_and_eligible_once_confirmed(
    report, unit, source
):
    # scenario: biomarkers-and-labs::dexa-result-recorded
    dexa = analyte(unit, source, "1-1", AnalyteCategory.BODY_COMPOSITION)
    when = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)
    row = add(
        report,
        dexa,
        laboratory="Lab X",
        method="M",
        collected_at=when,
        validation_state="user_confirmed",
    )
    row.refresh_from_db()
    assert (row.laboratory, row.method, row.collected_at) == ("Lab X", "M", when)
    assert row.aggregation_eligible is True


@pytest.mark.parametrize("category", [None, AnalyteCategory.BLOOD])
def test_blood_and_uncategorised_still_stored_and_flagged(
    report, unit, source, category
):
    # scenario: biomarkers-and-labs::a-result-without-laboratory-or-method-is-not-aggregation-eligible
    blood = analyte(unit, source, "3-3", category)
    row = add(report, blood)
    assert LabResult.objects.get(pk=row.pk).aggregation_eligible is False


@pytest.mark.parametrize("category", [None, AnalyteCategory.BLOOD])
def test_whitespace_provenance_is_not_eligible(report, unit, source, category):
    # scenario: biomarkers-and-labs::a-result-without-laboratory-or-method-is-not-aggregation-eligible
    blood = analyte(unit, source, "3-4", category)
    row = add(report, blood, laboratory="  ", method="\t ")
    row.refresh_from_db()
    assert row.aggregation_eligible is False
    assert (row.laboratory, row.method) == (None, None)


def test_category_and_source_are_set_together(unit, source):
    # scenario: biomarkers-and-labs::a-dexa-or-microbiome-result-without-provenance-is-not-stored
    kw = dict(
        name="n",
        loinc_code="4-4",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=source,
    )
    with pytest.raises(ValidationError):
        Biomarker.objects.create(category=AnalyteCategory.MICROBIOME, **kw)
    with pytest.raises(ValidationError):
        Biomarker.objects.create(category_source=source, **kw)
    assert Biomarker.objects.count() == 0


def _recategorise(biomarker, source, category):
    biomarker.category = category
    biomarker.category_source = source
    biomarker.save()


@pytest.mark.parametrize(
    "category", [AnalyteCategory.BODY_COMPOSITION, AnalyteCategory.MICROBIOME]
)
def test_recategorising_with_unprovenanced_results_is_refused(
    report, unit, source, category
):
    # scenario: biomarkers-and-labs::a-dexa-or-microbiome-result-without-provenance-is-not-stored
    blood = analyte(unit, source, "5-5")
    row = add(report, blood, laboratory="Lab X")
    with pytest.raises(ValidationError, match="method"):
        _recategorise(blood, source, category)
    blood.refresh_from_db()
    assert blood.category is None
    assert LabResult.objects.filter(pk=row.pk).exists()


def test_recategorising_with_provenanced_results_is_allowed(report, unit, source):
    # scenario: biomarkers-and-labs::dexa-result-recorded
    blood = analyte(unit, source, "5-6")
    add(report, blood, laboratory="Lab X", method="M")
    _recategorise(blood, source, AnalyteCategory.BODY_COMPOSITION)
    blood.refresh_from_db()
    assert blood.category == AnalyteCategory.BODY_COMPOSITION
