# [M00c] Spec discovery part B: gap register for docs/hackingbiology-project-spec.md
Labels: autodev, spec
Milestone: M00c
Parent: #34

## Goal
Compare `docs/hackingbiology-project-spec.md` with `openspec/specs/**`, record every feature in `docs/spec-discovery/project-spec.md`, and add each unspecified one as an ADDED requirement in `openspec/changes/s01-spec-discovery`. Also close two residual part A review findings (register-rows scenario wording, whitepaper linked-data promise).

## Spec refs
- `dev-process::register-rows-resolve`, `dev-process::unspecified-feature-captured`
- `openspec/changes/s01-spec-discovery` (14 requirements from this source, plus `Public data is published as linked data`)

## Acceptance
- Every row of the register cites the source and resolves (`backend/tests/test_spec_discovery_register.py`).
- Open choices are in `docs/QUESTIONS.md` Q18–Q24 with a reversible default.
- Part C (`docs/getbased-reuse-analysis.md`, `docs/presentation/`) remains.
