# [M02] TG-a: LabReport and lab result models with provenance

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (M02 module issue number not verified, Q60)

## Goal
Add LabReport and result models with laboratory, method, device, collected/reported timestamps, value and unit as reported and normalised, linked to `core.Biomarker`, alignable with OMOP MEASUREMENT. No new dependency.

## Spec refs
openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md: "Lab result provenance and OMOP MEASUREMENT alignment"; openspec/specs/biomarkers-and-labs/spec.md: "Coded analyte registry". Blocked by Q59 (default taken).

## Acceptance
- Tests declaring each scenario of the requirement with `scenario: biomarkers-and-labs::<slug>`.
- OMOP column mapping checked against the DDL and documented.
- Gates pass.
