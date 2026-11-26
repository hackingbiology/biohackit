"""PhenoAge engine tests (docs/research/phenoage-coefficients.md, Q77 defaults)."""

import math
import re
from dataclasses import fields, replace
from pathlib import Path

import pytest

from core import phenoage
from core.phenoage import (
    PhenoAgeInputs,
    PhenoAgeRefusal,
    PhenoAgeResult,
    compute_phenoage,
    evaluate_phenoage,
    phenoage_from_xb,
)

SAMPLE = PhenoAgeInputs(
    albumin_g_per_l=45.0,
    creatinine_umol_per_l=80.0,
    glucose_mmol_per_l=5.0,
    crp_mg_per_dl=0.1,
    lymphocyte_percent=30.0,
    mcv_fl=90.0,
    rdw_percent=13.0,
    alp_u_per_l=70.0,
    wbc_10e3_per_ul=6.0,
    age_years=40.0,
)


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize(("xb", "expected"), [(-12, 9.375), (-9, 42.647), (-6, 75.920)])
def test_mortality_to_age_matches_d3_vectors(xb: float, expected: float) -> None:
    # docs/research/phenoage-coefficients.md section 1.5 D3 (S2 constants)
    assert phenoage_from_xb(xb) == pytest.approx(expected, abs=0.0005)


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_same_input_same_output() -> None:
    assert compute_phenoage(SAMPLE) == compute_phenoage(SAMPLE)


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_worked_example_step_by_step() -> None:
    xb = (
        -19.9067
        + -0.0336 * 45.0
        + 0.0095 * 80.0
        + 0.1953 * 5.0
        + 0.0954 * math.log(0.1)
        + -0.0120 * 30.0
        + 0.0268 * 90.0
        + 0.3306 * 13.0
        + 0.00188 * 70.0
        + 0.0554 * 6.0
        + 0.0804 * 40.0
    )
    gamma = 0.0076927
    m = 1 - math.exp(-math.exp(xb) * (math.exp(120 * gamma) - 1) / gamma)
    age = 141.50225 + math.log(-0.00553 * math.log(1 - m)) / 0.090165
    result = compute_phenoage(SAMPLE)
    assert isinstance(result, PhenoAgeResult)
    assert result.xb == pytest.approx(xb, rel=1e-12)
    assert result.mortality_score == pytest.approx(m, rel=1e-12)
    assert result.phenoage_years == pytest.approx(age, rel=1e-12)
    assert result.constants_version == "levine2018-S2+Q77"


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize("name", [f.name for f in fields(PhenoAgeInputs)])
def test_missing_input_gives_none_with_reason(name: str) -> None:
    inputs = replace(SAMPLE, **{name: None})
    assert compute_phenoage(inputs) is None
    assert evaluate_phenoage(inputs) == PhenoAgeRefusal(phenoage.REASON_MISSING, name)


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_not_finite_gives_none_with_reason(bad: float) -> None:
    inputs = replace(SAMPLE, glucose_mmol_per_l=bad)
    assert compute_phenoage(inputs) is None
    assert evaluate_phenoage(inputs) == PhenoAgeRefusal(
        phenoage.REASON_NOT_FINITE, "glucose_mmol_per_l"
    )


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize("crp", [0.0, -0.5])
def test_crp_at_or_below_zero_gives_none(crp: float) -> None:
    inputs = replace(SAMPLE, crp_mg_per_dl=crp)
    assert compute_phenoage(inputs) is None
    assert evaluate_phenoage(inputs) == PhenoAgeRefusal(
        phenoage.REASON_CRP_NOT_POSITIVE, "crp_mg_per_dl"
    )


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
@pytest.mark.parametrize("age", [-1000.0, 5000.0])
def test_mortality_outside_open_interval_gives_none(age: float) -> None:
    # age -1000 -> M rounds to 0; age 5000 -> exp overflows or M rounds to 1
    inputs = replace(SAMPLE, age_years=age)
    assert compute_phenoage(inputs) is None
    outcome = evaluate_phenoage(inputs)
    assert isinstance(outcome, PhenoAgeRefusal)
    assert outcome.reason == phenoage.REASON_MORTALITY_OUT_OF_RANGE


# scenario: biomarkers-and-labs::phenoage-from-routine-bloods
def test_module_imports_no_ai_code() -> None:
    source = Path(phenoage.__file__).read_text()
    imports = re.findall(r"^\s*(?:from|import)\s+([\w.]+)", source, re.MULTILINE)
    assert imports
    assert not [
        i for i in imports if re.search(r"\bai\b|llm|anthropic|openai", i, re.I)
    ]
