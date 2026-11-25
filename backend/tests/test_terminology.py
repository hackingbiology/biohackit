# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from terminology.models import Source, Unit, UnitConversion
from terminology.services import normalize_value, range_status


@pytest.fixture
def src(db):
    return Source.objects.create(
        name="UCUM",
        version="2.1",
        licence="UCUM licence",
        url="https://ucum.org",
        retrieved_at=date(2026, 11, 24),
    )


@pytest.fixture
def units(src):
    a = Unit.objects.create(ucum_code="mg/dL", display="mg/dL", source=src)
    b = Unit.objects.create(ucum_code="g/L", display="g/L", source=src)
    UnitConversion.objects.create(
        from_unit=a, to_unit=b, factor=Decimal("0.01"), source=src
    )
    return a, b


def test_unsourced_row_rejected(db):
    with pytest.raises(ValidationError):
        Unit(ucum_code="mg/dL", display="x").save()


# scenario: terminology-reference-data::unknown-unit
def test_unknown_unit_rejected(units):
    with pytest.raises(ValidationError):
        normalize_value(1, "furlongs", "g/L")


# scenario: terminology-reference-data::conversion
def test_conversion_deterministic_keeps_reported(units):
    r1 = normalize_value("150", "mg/dL", "g/L")
    r2 = normalize_value("150", "mg/dL", "g/L")
    assert r1 == r2
    assert r1.value == Decimal("1.5")
    assert (r1.unit, r1.source_id) == ("g/L", UnitConversion.objects.get().source_id)
    assert (r1.reported_value, r1.reported_unit) == (Decimal("150"), "mg/dL")


# scenario: terminology-reference-data::unknown-unit
def test_unknown_unit_message_names_the_unit(units):
    with pytest.raises(ValidationError, match="Unknown UCUM unit: 'furlongs'"):
        normalize_value(1, "furlongs", "g/L")


# scenario: terminology-reference-data::conversion
def test_same_unit_is_identity_without_source(units):
    r = normalize_value("150", "mg/dL", "mg/dL")
    assert (r.value, r.unit, r.source_id) == (Decimal("150"), "mg/dL", None)
    assert (r.reported_value, r.reported_unit) == (Decimal("150"), "mg/dL")


# scenario: terminology-reference-data::conversion
def test_analyte_specific_conversion_preferred(units, src):
    from core.models import Biomarker

    a, b = units
    bm = Biomarker.objects.create(
        name="X", role="efficacy", loinc_code="TEST-1", unit=a, source=src
    )
    UnitConversion.objects.create(
        from_unit=a, to_unit=b, factor=Decimal("0.5"), source=src, biomarker=bm
    )
    assert normalize_value("10", "mg/dL", "g/L", bm).value == Decimal("5.0")
    assert normalize_value("10", "mg/dL", "g/L").value == Decimal("0.10")


# scenario: terminology-reference-data::conversion
def test_conversion_selected_by_source_unit(units, src):
    from core.models import Biomarker

    mg_dl, g_l = units
    other = Source.objects.create(
        name="Synthetic test source",
        version="0",
        licence="test only",
        url="https://example.invalid/test",
        retrieved_at=date(2026, 11, 24),
    )
    mmol = Unit.objects.create(ucum_code="mmol/L", display="mmol/L", source=src)
    # Synthetic test-only factors, not reference data.
    UnitConversion.objects.create(
        from_unit=mmol, to_unit=g_l, factor=Decimal("2"), source=other
    )
    generic = UnitConversion.objects.get(from_unit=mg_dl)

    from_mmol = normalize_value("10", "mmol/L", "g/L")
    assert from_mmol.value == Decimal("20")
    assert from_mmol.source_id == other.pk
    from_mg = normalize_value("10", "mg/dL", "g/L")
    assert from_mg.value == Decimal("0.10")
    assert from_mg.source_id == generic.source_id

    bm = Biomarker.objects.create(
        name="Y", role="efficacy", loinc_code="TEST-2", unit=g_l, source=src
    )
    UnitConversion.objects.create(
        from_unit=mmol, to_unit=g_l, factor=Decimal("3"), source=other, biomarker=bm
    )
    assert normalize_value("10", "mmol/L", "g/L", bm).value == Decimal("30")
    assert normalize_value("10", "mg/dL", "g/L", bm).value == Decimal("0.10")


def test_missing_conversion_rejected(units, src):
    Unit.objects.create(ucum_code="mmol/L", display="mmol/L", source=src)
    with pytest.raises(ValidationError, match="No conversion mg/dL -> mmol/L"):
        normalize_value(1, "mg/dL", "mmol/L")


@pytest.mark.parametrize(
    ("value", "low", "high", "expected"),
    [
        ("0.9", "1", "2", "below"),
        ("1", "1", "2", "within"),
        ("1.5", "1", "2", "within"),
        ("2", "1", "2", "within"),
        ("2.1", "1", "2", "above"),
        ("-5", None, "2", "within"),
        ("2.1", None, "2", "above"),
        ("99", "1", None, "within"),
        ("0.9", "1", None, "below"),
        ("0", None, None, "within"),
    ],
)
def test_range_status(value, low, high, expected):
    def d(x):
        return None if x is None else Decimal(x)

    assert range_status(Decimal(value), d(low), d(high)) == expected
