# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError

from .models import Unit, UnitConversion

if TYPE_CHECKING:
    from core.models import Biomarker


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


def normalize_value(
    value: object,
    unit: str,
    target_unit: str,
    biomarker: "Biomarker | None" = None,
) -> Normalized:
    """Deterministic: stored factors only. Prefers an analyte-specific conversion."""
    amount = Decimal(str(value))
    src, dst = _unit(unit), _unit(target_unit)
    if src == dst:
        return Normalized(amount, unit, amount, target_unit, None)
    qs = UnitConversion.objects.filter(from_unit=src, to_unit=dst)
    conv = None
    if biomarker is not None:
        conv = qs.filter(biomarker=biomarker).first()
    conv = conv or qs.filter(biomarker__isnull=True).first()
    if conv is None:
        raise ValidationError(f"No conversion {unit} -> {target_unit}")
    return Normalized(amount, unit, amount * conv.factor, target_unit, conv.source_id)
