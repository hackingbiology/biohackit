# [M02] TG-j part 1: FHIR DiagnosticReport/Observation export of a stored lab report

Labels: autodev, feature
Milestone: M02
Parent: unknown (Q60)

## Goal
Deterministic hand-written FHIR R4 export of a stored lab report, with an owner-only GET endpoint.

## Spec refs
openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md "FHIR representation of a stored lab result" (5 scenarios); Q55, Q73.

## Acceptance
- Five scenarios covered by tests in backend/tests/test_lab_fhir.py.
- UCUM system/code only on an exact stored Unit.ucum_code match; laboratory and method omitted when unknown.
- docs/fhir/lab-report-mapping.md lists the FHIR version, URLs and element sources.
- No dependency, no migration; gates green.
