# [M02] TG-a part 1: LabReport and LabResult models

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (M02 module issue number not verified, Q60)

## Goal
`core.LabReport` and `core.LabResult` (separate from `core.Measurement`, Q61): origin, validation state, laboratory, method, device, collected/reported times, value and unit as reported, normalised value via `terminology.services.normalize_value`, aggregation-eligibility flag. No new dependency. Part 2 (analyte category Q66, DEXA/microbiome rule, OMOP mapping) stays open.

## Spec refs
openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md: 7 of the 9 scenarios of "Lab result provenance and OMOP MEASUREMENT alignment".

## Acceptance
- Tests in backend/tests/test_lab_results.py declare each scenario; gates pass.
