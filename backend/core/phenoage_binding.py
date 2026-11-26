# SPDX-License-Identifier: AGPL-3.0-or-later
"""Binds one stored LabReport to PhenoAgeInputs (M02 TG-i part 2). Deterministic.

Each analyte is picked by the LOINC code of its Biomarker. A value is used as is
when its UCUM unit equals the S2 Table S1 unit; otherwise only a stored
UnitConversion may convert it (never a factor written here). No AI, no storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError

from terminology.services import normalize_value

from .models import LabReport, LabResult, LabResultValidation
from .phenoage import PhenoAgeInputs, PhenoAgeRefusal

REASON_NOT_MAPPED = "analyte_not_mapped"
REASON_AMBIGUOUS = "ambiguous_analyte"
REASON_UNIT_NOT_CONVERTIBLE = "unit_not_convertible"

# S2 Table S1 unit of each PhenoAgeInputs analyte field (UCUM spelling).
S2_UNITS: dict[str, str] = {
    "albumin_g_per_l": "g/L",
    "creatinine_umol_per_l": "umol/L",
    "glucose_mmol_per_l": "mmol/L",
    "crp_mg_per_dl": "mg/dL",
    "lymphocyte_percent": "%",
    "mcv_fl": "fL",
    "rdw_percent": "%",
    "alp_u_per_l": "U/L",
    "wbc_10e3_per_ul": "10*3/uL",
}

# LOINC code per field. Every code must appear in the table of
# docs/research/phenoage-coefficients.md (section 1.7) with its loinc.org URL and
# fetch date. loinc.org answered HTTP 403 to every fetch on 2026-11-26, so no code
# could be verified and none is written (Q79): every analyte is "analyte_not_mapped".
LOINC_BY_FIELD: dict[str, str] = {}

EXCLUDED_STATES = frozenset(
    {LabResultValidation.RETRACTED, LabResultValidation.DISPUTED}
)


@dataclass(frozen=True)
class UsedInput:
    field: str
    lab_result_id: int
    value: float
    unit: str
    converted: bool


@dataclass(frozen=True)
class Binding:
    inputs: PhenoAgeInputs
    used: list[UsedInput]


def _in_target_unit(result: LabResult, target: str) -> tuple[Decimal, bool] | None:
    """Value in the S2 unit and whether a conversion was applied, or None."""
    if result.reported_unit == target:
        return result.reported_value, False
    if result.normalised_value is not None and result.normalised_unit == target:
        return result.normalised_value, True
    try:
        converted = normalize_value(
            result.reported_value, result.reported_unit, target, result.biomarker
        )
    except ValidationError:
        return None
    return converted.value, True


def _bind_field(
    field: str, candidates: list[LabResult]
) -> tuple[float, UsedInput] | PhenoAgeRefusal:
    if not candidates:
        return PhenoAgeRefusal("missing_input", field)
    if len(candidates) > 1:
        return PhenoAgeRefusal(REASON_AMBIGUOUS, field)
    result = candidates[0]
    target = S2_UNITS[field]
    found = _in_target_unit(result, target)
    if found is None:
        return PhenoAgeRefusal(REASON_UNIT_NOT_CONVERTIBLE, field)
    number = float(found[0])
    return number, UsedInput(field, result.pk, number, target, found[1])


def inputs_from_report(
    report: LabReport, age_years: float
) -> Binding | PhenoAgeRefusal:
    """Inputs for the engine from one report, or the first refusal (field order)."""
    values: dict[str, float | None] = {}
    used: list[UsedInput] = []
    for field in S2_UNITS:
        code = LOINC_BY_FIELD.get(field)
        if code is None:
            return PhenoAgeRefusal(REASON_NOT_MAPPED, field)
        candidates = list(
            LabResult.objects.filter(report=report, biomarker__loinc_code=code)
            .exclude(validation_state__in=EXCLUDED_STATES)
            .select_related("biomarker")
            .order_by("pk")
        )
        bound = _bind_field(field, candidates)
        if isinstance(bound, PhenoAgeRefusal):
            return bound
        values[field] = bound[0]
        used.append(bound[1])
    return Binding(PhenoAgeInputs(age_years=age_years, **values), used)
