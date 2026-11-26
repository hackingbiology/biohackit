# SPDX-License-Identifier: AGPL-3.0-or-later
"""LabResult -> OMOP MEASUREMENT mapping (M02 TG-a part 3). Synthetic rows only."""

import re
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from accounts.models import User
from core.models import Biomarker, BiomarkerRole, LabReport, LabReportOrigin, LabResult
from core.omop import MEASUREMENT_COLUMNS, lab_result_to_omop_measurement
from terminology.models import Source, Unit, UnitConversion

DOC = Path(__file__).resolve().parents[2] / "docs" / "omop" / "measurement-mapping.md"
SOURCE_COLUMNS = {
    "measurement_id",
    "measurement_date",
    "measurement_datetime",
    "measurement_time",
    "value_as_number",
    "measurement_source_value",
    "unit_source_value",
    "value_source_value",
}


@pytest.fixture
def base(db):
    src = Source.objects.create(
        name="synthetic fixture",
        licence="test only",
        url="https://example.org/synthetic",
        retrieved_at=date(2026, 11, 26),
    )
    unit = Unit.objects.create(ucum_code="xa/L", display="xa/L", source=src)
    bm = Biomarker.objects.create(
        name="synthetic analyte",
        loinc_code="1-1",
        role=BiomarkerRole.BASELINE,
        unit=unit,
        source=src,
    )
    user = User.objects.create_user(
        email="omop@example.com", password="correct-horse-battery-9"
    )
    report = LabReport.objects.create(owner=user, origin=LabReportOrigin.MANUAL)
    return report, bm


def test_documented_columns_match_module():
    # scenario: biomarkers-and-labs::a-result-maps-to-omop-measurement
    documented = re.findall(r"^\| `([a-z_]+)` \| ", DOC.read_text(), flags=re.M)
    assert tuple(documented) == MEASUREMENT_COLUMNS


def test_full_result_maps_every_column(base):
    # scenario: biomarkers-and-labs::a-result-maps-to-omop-measurement
    report, bm = base
    res = LabResult.objects.create(
        report=report,
        biomarker=bm,
        laboratory="Lab X",
        method="M",
        collected_at=datetime(2026, 3, 4, 7, 5, 9, tzinfo=UTC),
        reported_at=datetime(2026, 3, 6, 1, 0, 0, tzinfo=UTC),
        reported_value=Decimal("5.500"),
        reported_unit="xa/L",
    )
    res = LabResult.objects.get(pk=res.pk)
    row = lab_result_to_omop_measurement(res)
    assert tuple(row) == MEASUREMENT_COLUMNS
    assert row["measurement_id"] == res.pk
    assert row["measurement_date"] == date(2026, 3, 4)
    assert row["measurement_datetime"] == datetime(2026, 3, 4, 7, 5, 9)
    assert row["measurement_time"] == "07:05:09"
    assert row["measurement_source_value"] == "1-1"
    assert row["unit_source_value"] == "xa/L"
    assert row["value_source_value"] == "5.500000"
    assert res.normalised_value is not None
    assert row["value_as_number"] == res.normalised_value
    for name in set(MEASUREMENT_COLUMNS) - SOURCE_COLUMNS:
        assert row[name] is None, name


def test_sparse_result_leaves_empty_and_ignores_reported_time(base):
    # scenario: biomarkers-and-labs::a-result-maps-to-omop-measurement
    report, bm = base
    res = LabResult.objects.create(
        report=report,
        biomarker=bm,
        reported_at=datetime(2026, 3, 6, 1, 0, 0, tzinfo=UTC),
        reported_value=Decimal("2"),
        reported_unit="unknown-unit",
    )
    res = LabResult.objects.get(pk=res.pk)
    row = lab_result_to_omop_measurement(res)
    assert tuple(row) == MEASUREMENT_COLUMNS
    assert row["measurement_date"] is None
    assert row["measurement_datetime"] is None
    assert row["measurement_time"] is None
    assert row["value_as_number"] is None
    assert row["unit_source_value"] == "unknown-unit"
    assert row["value_source_value"] == "2.000000"


def test_converted_value_is_paired_with_its_normalised_unit(base):
    # scenario: biomarkers-and-labs::a-result-maps-to-omop-measurement
    report, bm = base
    other = Unit.objects.create(ucum_code="xb/L", display="xb/L", source=bm.source)
    UnitConversion.objects.create(
        from_unit=other,
        to_unit=bm.unit,
        factor=Decimal("2"),
        biomarker=bm,
        source=bm.source,
    )
    res = LabResult.objects.create(
        report=report,
        biomarker=bm,
        reported_value=Decimal("3"),
        reported_unit="xb/L",
    )
    row = lab_result_to_omop_measurement(LabResult.objects.get(pk=res.pk))
    assert row["value_as_number"] == Decimal("6")
    assert row["unit_source_value"] == "xa/L"
    assert row["value_source_value"] == "3.000000"
