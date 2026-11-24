# [M01] Terminology app: Source, Unit, UnitConversion, normalize_value
Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

## Goal
Create the `terminology` Django app with sourced `Source`, `Unit` (UCUM) and `UnitConversion` models and a deterministic `normalize_value()` helper that keeps the as-reported value and unit.

## Spec refs
`openspec/changes/m01-terminology-reference-data/specs/terminology-reference-data.md` — "Every reference row carries its source", "Units are UCUM and conversions deterministic".

## Acceptance
- Row without source is rejected (unsourced row).
- Unknown unit is rejected, never stored as free text.
- Normalising the same input twice gives identical results; as-reported and normalised values are both kept.
