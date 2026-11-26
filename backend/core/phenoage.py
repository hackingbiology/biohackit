"""Deterministic PhenoAge (Levine 2018) engine. Pure arithmetic, no AI/LLM.

Every constant is copied from docs/research/phenoage-coefficients.md (sections
1.2, 1.3, 1.5). Source ids: S1 Levine 2018 (PMC5940111); S2 its supplement SD1
(Table S1 p. 10, formulas pp. 1-2); S3 2019 correction; S4 Kuo 2021.
Q77 (docs/QUESTIONS.md) defaults: nine markers present, no imputation, CRP <= 0
gives no result, S2 mortality-to-age pair (D3), ALP 0.00188 (D2).

Arithmetic is IEEE float (Python ``float``) throughout. Intermediate values are
never rounded, floored or clamped. Inputs are in the S2 Table S1 units.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields

CONSTANTS_VERSION = "levine2018-S2+Q77"

# S2 Table S1 (p. 10): "Constant -19.9067" (D1, Q77 default).
INTERCEPT = -19.9067
# S2 Table S1 (p. 10) weights; units are those of PhenoAgeInputs.
W_ALBUMIN = -0.0336  # g/L
W_CREATININE = 0.0095  # umol/L
W_GLUCOSE = 0.1953  # mmol/L
W_LN_CRP = 0.0954  # on ln(CRP), CRP in mg/dL
W_LYMPHOCYTE_PCT = -0.0120  # %
W_MCV = 0.0268  # fL
W_RDW = 0.3306  # %
# S3/S4 print 0.00188; S2 Table S1 prints its rounding 0.0019 (D2, Q77 default).
W_ALP = 0.00188  # U/L
W_WBC = 0.0554  # 10^3 cells/uL
W_AGE = 0.0804  # years

# S2 p. 2 text: Gompertz gamma (Table S1 prints the rounding 0.0077, D4).
GAMMA = 0.0076927
# S2 p. 2: "t denotes time (here in units of months)".
HORIZON_MONTHS = 120
# S2 pp. 1-2 mortality-to-age constants (D3, Q77 default; S3/S4 use 0.09165).
AGE_OFFSET = 141.50225
AGE_DIVISOR = 0.090165
AGE_LOG_FACTOR = 0.00553

REASON_MISSING = "missing_input"
REASON_NOT_FINITE = "not_finite_input"
REASON_CRP_NOT_POSITIVE = "crp_not_positive"
REASON_MORTALITY_OUT_OF_RANGE = "mortality_score_out_of_range"


@dataclass(frozen=True)
class PhenoAgeInputs:
    """Nine analytes in S2 Table S1 units plus age in years; None = missing."""

    albumin_g_per_l: float | None
    creatinine_umol_per_l: float | None
    glucose_mmol_per_l: float | None
    crp_mg_per_dl: float | None
    lymphocyte_percent: float | None
    mcv_fl: float | None
    rdw_percent: float | None
    alp_u_per_l: float | None
    wbc_10e3_per_ul: float | None
    age_years: float | None


@dataclass(frozen=True)
class PhenoAgeResult:
    phenoage_years: float
    mortality_score: float
    xb: float
    constants_version: str


@dataclass(frozen=True)
class PhenoAgeRefusal:
    """Machine-readable reason no result was produced."""

    reason: str
    field: str | None = None


def _validated(inputs: PhenoAgeInputs) -> dict[str, float] | PhenoAgeRefusal:
    values: dict[str, float] = {}
    for f in fields(inputs):
        value = getattr(inputs, f.name)
        if value is None:
            return PhenoAgeRefusal(REASON_MISSING, f.name)
        if not math.isfinite(value):
            return PhenoAgeRefusal(REASON_NOT_FINITE, f.name)
        values[f.name] = value
    if values["crp_mg_per_dl"] <= 0:
        return PhenoAgeRefusal(REASON_CRP_NOT_POSITIVE, "crp_mg_per_dl")
    return values


def _linear_predictor(v: dict[str, float]) -> float:
    """xb = intercept + sum(weight * value), CRP entering as ln(CRP)."""
    return (
        INTERCEPT
        + W_ALBUMIN * v["albumin_g_per_l"]
        + W_CREATININE * v["creatinine_umol_per_l"]
        + W_GLUCOSE * v["glucose_mmol_per_l"]
        + W_LN_CRP * math.log(v["crp_mg_per_dl"])
        + W_LYMPHOCYTE_PCT * v["lymphocyte_percent"]
        + W_MCV * v["mcv_fl"]
        + W_RDW * v["rdw_percent"]
        + W_ALP * v["alp_u_per_l"]
        + W_WBC * v["wbc_10e3_per_ul"]
        + W_AGE * v["age_years"]
    )


def mortality_score(xb: float) -> float:
    """S2 p. 1: M = 1 - exp(-exp(xb) * (exp(120*gamma) - 1) / gamma)."""
    return 1 - math.exp(-math.exp(xb) * (math.exp(HORIZON_MONTHS * GAMMA) - 1) / GAMMA)


def phenoage_from_mortality(mortality: float) -> float:
    """S2 pp. 1-2: 141.50225 + ln(-0.00553 * ln(1 - M)) / 0.090165."""
    return (
        AGE_OFFSET + math.log(-AGE_LOG_FACTOR * math.log(1 - mortality)) / AGE_DIVISOR
    )


def phenoage_from_xb(xb: float) -> float:
    """PhenoAge in years from the linear predictor (D3 check, doc section 1.5)."""
    return phenoage_from_mortality(mortality_score(xb))


def evaluate_phenoage(inputs: PhenoAgeInputs) -> PhenoAgeResult | PhenoAgeRefusal:
    """Compute PhenoAge, or say why not. No imputation, flooring or clamping."""
    values = _validated(inputs)
    if isinstance(values, PhenoAgeRefusal):
        return values
    xb = _linear_predictor(values)
    try:
        m = mortality_score(xb)
    except OverflowError:
        return PhenoAgeRefusal(REASON_MORTALITY_OUT_OF_RANGE)
    if not 0 < m < 1:
        return PhenoAgeRefusal(REASON_MORTALITY_OUT_OF_RANGE)
    return PhenoAgeResult(phenoage_from_mortality(m), m, xb, CONSTANTS_VERSION)


def compute_phenoage(inputs: PhenoAgeInputs) -> PhenoAgeResult | None:
    """The result, or None when no result is allowed (see evaluate_phenoage)."""
    outcome = evaluate_phenoage(inputs)
    return outcome if isinstance(outcome, PhenoAgeResult) else None
