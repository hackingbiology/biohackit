# [X01] get-based archive importer, part 2a: cited marker mapping and owner-only preview
Labels: autodev, feature
Milestone: M02 Blood layer
Parent: #38

## Goal
A stored, cited mapping table from get-based marker keys to LOINC-coded Biomarkers (`GetbasedMarkerMapping`, migration 0013, nothing seeded) and `POST /api/labs/imports/getbased/preview/`, which classifies every marker of one chosen profile of a plain-JSON export (single-client export or all-clients bundle, version 2) and stores nothing.

## Spec refs
`openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md`, requirement "Import of a get-based archive" (scenarios: preview before anything is saved; markers matched through a cited mapping or not recognised; mapping row cites the get-based catalogue unit; exactly one profile is imported; unknown archive format version rejected; identity and non-lab data are never stored; deleted markers; calculated ratios). Format: `docs/ecosystem/getbased-archive-format.md`. Defaults: Q100.

## Acceptance
- Model rules and DB check constraints for measured and deny-list rows; unit citation is all-or-none with a 40-hex commit.
- Preview statuses with exact reasons, per-value provenance flags, summary counts, `can_confirm`.
- labcharts-backup, migration archive and versions other than 2 are refused with 400.
- LabReport and LabResult counts unchanged; identity, chat, nutrition and wallet never in the response or the logs.
- Later parts: confirm, provenance fields on LabResult, undo, labcharts-backup, migration archive.
