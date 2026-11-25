# [M01] TG4 part A: range models and provenance gate

Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

Goal: ReferenceRange, OptimalRange, SafetyThreshold models (Source required, bounds in analyte unit), `displayable_optimal_range()`, `range_status()`, and the two TG3 residual fixes. The API endpoint is part B.
Spec: openspec/changes/m01-terminology-reference-data (Three ranges kept separate; Optimal range provenance gate; Analyte registry requires LOINC and UCUM).
Acceptance: a test per scenario, mutmut gate clean, gates.sh passes.
