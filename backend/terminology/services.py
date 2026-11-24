# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError

from .models import Unit, UnitConversion


@dataclass(frozen=True)
class Normalized:
    reported_value: Decimal
    reported_unit: str
    value: Decimal
    unit: str
    source_id: int | None


def _unit(code: str) -> Unit:
    try:
        return Unit.objects.get(ucum_code=code)
    except Unit.DoesNotExist:
        raise ValidationError(f"Unknown UCUM unit: {code!r}") from None


def normalize_value(value, unit: str, target_unit: str, biomarker=None) -> Normalized:
    """Deterministic: stored factors only. Prefers an analyte-specific conversion."""
    value = Decimal(str(value))
    src, dst = _unit(unit), _unit(target_unit)
    if src == dst:
        return Normalized(value, unit, value, target_unit, None)
    qs = UnitConversion.objects.filter(from_unit=src, to_unit=dst)
    conv = None
    if biomarker is not None:
        conv = qs.filter(biomarker=biomarker).first()
    conv = conv or qs.filter(biomarker__isnull=True).first()
    if conv is None:
        raise ValidationError(f"No conversion {unit} -> {target_unit}")
    return Normalized(value, unit, value * conv.factor, target_unit, conv.source_id)
