# [M02] TG-n part 1: deterministic calculated ratio markers (GET /api/labs/reports/<id>/calculated/)

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: a stored, sourced `core.CalculatedRatioDefinition` (numerator, denominator, unit of each input, Source) and an owner-only API that computes each ratio from one report in code, labels it calculated and lists inputs with dates; a missing input gives not computable with no value. No ratio seeded, no formula in code. One migration (table only), no new dependency.

Spec refs: s01-spec-discovery biomarkers-and-labs "Deterministic calculated markers".

Acceptance: scenarios a-ratio-is-computed-from-its-inputs and a-missing-input-yields-no-value are tested; Q83 records the defaults.
