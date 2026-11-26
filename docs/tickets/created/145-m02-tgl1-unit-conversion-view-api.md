# [M02] TG-l part 1: owner-only unit conversion view of a stored lab result
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: `GET /api/labs/results/<id>/convert/?unit=<ucum>` shows a stored result in a requested UCUM unit using only stored, sourced `UnitConversion` rows; the reported value and unit are always returned; no conversion known shows the reported value unconverted.

Spec refs: s01 "Unit conversion between unit systems"; m02-blood-layer TG-l; Q81.

Acceptance: scenarios `biomarkers-and-labs::a-us-unit-result-is-shown-in-si` and `biomarkers-and-labs::no-conversion-known` tested in backend/tests/test_lab_unit_conversion_view.py; docs/api-labs.md updated; no dependency, no migration.
