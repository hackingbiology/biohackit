# [X01] get-based archive importer, part 2b: confirm, per-value provenance and undo
Labels: autodev, feature
Milestone: M02 Blood layer
Parent: #38

## Goal
`POST /api/labs/imports/getbased/confirm/` stores a previewed single-client export or all-clients bundle (version 2) as one `LabReport` with its results, each keeping get-based's per-value provenance, all stored `entered`. Undo reuses `DELETE /api/labs/reports/<id>/`. Backend only.

## Spec refs
`openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md`, requirement "Import of a get-based archive" (scenarios: confirm refused while a row is not recognised; undo of a confirmed import; origin of the import is recorded; AI-read, may-be-AI, origin-not-shown and origin-unknown flags; per-value markerSources is kept; calculated values are not stored as measured; edited values are labelled). Defaults: Q101, Q102.

## Acceptance
- 400 listing the rows while any is not recognised; counts unchanged. Calculated and deleted rows do not block and are counted.
- Every result `entered`, `aggregation_eligible` false, `collected_at` empty; provenance fields round-trip verbatim.
- Report records origin, format name, version 2 and file name; DB checks reject partial fields.
- Undo removes the report, results and provenance only. Identity, chat, nutrition and wallet appear nowhere.
- Later parts: labcharts-backup, migration archive.
