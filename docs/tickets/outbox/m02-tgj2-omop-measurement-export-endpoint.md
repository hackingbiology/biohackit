# [M02] TG-j part 2: OMOP MEASUREMENT export endpoint
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: owner-only `GET /api/labs/reports/<id>/omop/` exporting a stored report as OMOP MEASUREMENT-shaped rows via `core.omop.lab_result_to_omop_measurement`; retracted excluded; concept ids stay null (Q69, Q80).

Spec: m02-blood-layer, biomarkers-and-labs "Lab result provenance and OMOP MEASUREMENT alignment".

Acceptance: tests in backend/tests/test_lab_omop_export.py; docs/api-labs.md; gates pass.
