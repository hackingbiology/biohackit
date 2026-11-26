# SPDX-License-Identifier: AGPL-3.0-or-later
"""Calculated quotient markers for one stored LabReport (M02 TG-n part 1). Deterministic.

Each stored CalculatedRatioDefinition names two Biomarkers and the UCUM unit each must
be in. Inputs are bound as in phenoage_binding: one report, disputed and retracted
results skipped, a value used as reported when its unit matches, otherwise converted
only by a stored UnitConversion. No formula, constant or code is written here. No AI,
nothing is stored.
"""

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_EVEN, Context, Decimal
from typing import Any

from django.core.exceptions import ValidationError

from terminology.models import Source
from terminology.services import normalize_value

from .models import Biomarker, CalculatedRatioDefinition, LabReport, LabResult
from .phenoage_binding import EXCLUDED_STATES

# Division precision: 28 significant digits, half-even. Explicit so the result does
# not depend on the ambient decimal context. The value is never rounded for display.
DIVISION_CONTEXT = Context(prec=28, rounding=ROUND_HALF_EVEN)

NUMERATOR = "numerator"
DENOMINATOR = "denominator"


def _iso(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _source_dict(source: Source) -> dict[str, str]:
    return {"name": source.name, "version": source.version, "url": source.url}


def _in_unit(
    result: LabResult, target: str
) -> tuple[Decimal, bool, Source | None] | None:
    """Value in the target unit, whether converted, the conversion's Source; or None."""
    if result.reported_unit == target:
        return result.reported_value, False, None
    if result.normalised_value is not None and result.normalised_unit == target:
        return result.normalised_value, True, result.normalised_source
    try:
        converted = normalize_value(
            result.reported_value, result.reported_unit, target, result.biomarker
        )
    except ValidationError:
        return None
    if converted.source_id is None:
        return converted.value, True, None
    return converted.value, True, Source.objects.get(pk=converted.source_id)


def _bind(
    report: LabReport, role: str, biomarker: Biomarker, unit_code: str
) -> tuple[dict[str, Any] | None, str | None]:
    """The input description and None, or None and a machine-readable reason."""
    candidates = list(
        LabResult.objects.filter(report=report, biomarker=biomarker)
        .exclude(validation_state__in=EXCLUDED_STATES)
        .select_related("biomarker")
        .order_by("pk")
    )
    if not candidates:
        return None, f"missing_input:{role}"
    if len(candidates) > 1:
        return None, f"ambiguous_input:{role}"
    result = candidates[0]
    found = _in_unit(result, unit_code)
    if found is None:
        return None, f"unit_not_convertible:{role}"
    return {
        "role": role,
        "lab_result_id": result.pk,
        "loinc_code": biomarker.loinc_code,
        "value_used": str(found[0]),
        "unit_used": unit_code,
        "reported_value": str(result.reported_value),
        "reported_unit": result.reported_unit,
        "collected_at": _iso(result.collected_at),
        "reported_at": _iso(result.reported_at),
        "converted": found[1],
        "conversion_source": None if found[2] is None else _source_dict(found[2]),
    }, None


def _compute_one(
    report: LabReport, definition: CalculatedRatioDefinition
) -> dict[str, Any]:
    head: dict[str, Any] = {
        "name": definition.name,
        "calculated": True,
        "source": _source_dict(definition.source),
    }
    bound = [
        _bind(
            report, NUMERATOR, definition.numerator, definition.numerator_unit.ucum_code
        ),
        _bind(
            report,
            DENOMINATOR,
            definition.denominator,
            definition.denominator_unit.ucum_code,
        ),
    ]
    reasons = [reason for _, reason in bound if reason is not None]
    inputs = [item for item, _ in bound if item is not None]
    if not reasons and Decimal(inputs[1]["value_used"]) == 0:
        reasons.append("denominator_zero")
    if reasons:
        return {**head, "status": "not_computable", "value": None, "reasons": reasons}
    value = DIVISION_CONTEXT.divide(
        Decimal(inputs[0]["value_used"]), Decimal(inputs[1]["value_used"])
    )
    return {
        **head,
        "status": "computed",
        "value": str(value),
        "unit_note": (
            f"{inputs[0]['unit_used']} / {inputs[1]['unit_used']} "
            "(quotient of the two input values in these units)"
        ),
        "inputs": inputs,
    }


def compute_ratios(report: LabReport) -> list[dict[str, Any]]:
    """Every stored ratio definition (by name) computed from this report's results."""
    definitions = CalculatedRatioDefinition.objects.select_related(
        "numerator", "denominator", "numerator_unit", "denominator_unit", "source"
    ).order_by("name")
    return [_compute_one(report, d) for d in definitions]
