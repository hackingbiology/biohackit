# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from terminology.models import Source, Unit, UnitConversion
from terminology.services import normalize_value


@pytest.fixture
def src(db):
    return Source.objects.create(
        name="UCUM", version="2.1", licence="UCUM licence", url="https://ucum.org",
        retrieved_at=date(2026, 11, 24),
    )


@pytest.fixture
def units(src):
    a = Unit.objects.create(ucum_code="mg/dL", display="mg/dL", source=src)
    b = Unit.objects.create(ucum_code="g/L", display="g/L", source=src)
    UnitConversion.objects.create(from_unit=a, to_unit=b, factor=Decimal("0.01"), source=src)
    return a, b


def test_unsourced_row_rejected(db):
    with pytest.raises(ValidationError):
        Unit(ucum_code="mg/dL", display="x").save()


def test_unknown_unit_rejected(units):
    with pytest.raises(ValidationError):
        normalize_value(1, "furlongs", "g/L")


def test_conversion_deterministic_keeps_reported(units):
    r1 = normalize_value("150", "mg/dL", "g/L")
    r2 = normalize_value("150", "mg/dL", "g/L")
    assert r1 == r2
    assert r1.value == Decimal("1.5")
    assert (r1.reported_value, r1.reported_unit) == (Decimal("150"), "mg/dL")


def test_missing_conversion_rejected(units, src):
    Unit.objects.create(ucum_code="mmol/L", display="mmol/L", source=src)
    with pytest.raises(ValidationError):
        normalize_value(1, "mg/dL", "mmol/L")
