# M02 Tasks

Ordering: tasks with no new dependency first. Each TG is one implementer run (~60 tool calls). "Req" names the requirement in `openspec/specs/biomarkers-and-labs/spec.md` (main), `openspec/changes/s01-spec-discovery/specs/biomarkers-and-labs/spec.md` (s01), or this change's delta (M02).

## TG1 — Spec (this change)
- [x] proposal.md, tasks.md, spec delta written; questions Q56–Q60 appended to docs/QUESTIONS.md; ecosystem test enforces the link to docs/ecosystem/m02-blood-layer.md

## TG-a — Lab report and result models (no new dependency)
- [ ] `LabReport` and result rows with laboratory, method, device, collected/reported timestamps, value+unit as reported and normalised, FK to `core.Biomarker`; OMOP MEASUREMENT column mapping documented after checking the DDL. Req: M02 "Lab result provenance and OMOP MEASUREMENT alignment"; main "Coded analyte registry"; s01 "Unit conversion between unit systems"; domain-model "Measurement provenance" (implement, do not restate). `LabResult` is a separate model from `core.Measurement` (Q61). Blocked by: Q59, Q61.

## TG-b — Manual entry API (no new dependency)
- [ ] Authenticated API to create a lab report with results by hand, same models and same review/persist path as imports. Req: main "Manual entry of equal standing".

## TG-c — CSV import with review and rollback (stdlib csv)
- [ ] Parse CSV with `csv`, show parsed rows for review, persist only after confirmation, roll back a whole import. Req: main "Import from PDF, photo, and CSV with learned templates" (CSV part), main "Human review before persistence", s01 "Import can be rolled back".

## TG-d — Deterministic PII redaction
- [ ] Rule-based redaction of extracted text before review, with a diff the user sees, optional per Q58. Req: main "Optional PII obfuscation on import". Blocked by: Q58.

## TG-e — Add pdfplumber (dependency)
- [ ] `uv add pdfplumber` after fetching and recording its licence (licence gate); text and table extraction into the review step. Req: main "Import from PDF, photo, and CSV with learned templates" (PDF part).

## TG-f — OCR with pytesseract (dependency)
- [ ] `uv add pytesseract`, licence fetch, Tesseract binary requirement documented; photo import into the review step. Req: same as TG-e (photo part). Blocked by: TG-e.

## TG-g — Original report file retained
- [ ] Store the uploaded file with the report; retention per Q57. Private storage only: the file is never published or exposed in OpenData until Q62 is answered and a requirement covers it. Req: main "Original report file retained and public raw" (retention part). Blocked by: Q57, Q62.

## TG-h — Completeness and freshness indicators
- [ ] Completeness and freshness per organ system from stored results. Req: main "Completeness and freshness indicators". Depends on an organ-system grouping of analytes (not yet defined; record a question when the task starts).

## TG-i — PhenoAge computation
- [ ] Deterministic computation from the standard panel; coefficients entered only with a citation to the original paper. Req: main "Deterministic PhenoAge computation from the standard panel". Blocked by: Q56.

## TG-j — FHIR and OMOP export
- [ ] Hand-written FHIR DiagnosticReport/Observation representation and OMOP MEASUREMENT-shaped export of stored results. Req: M02 "FHIR representation of a stored lab result", M02 "Lab result provenance and OMOP MEASUREMENT alignment". Blocked by: Q55, TG-a.

## TG-k — Extraction benchmark
- [ ] Synthetic report with a verified answer key; measure extraction accuracy of TG-e/TG-f. Req: s01 "Extraction benchmark on a synthetic report". Blocked by: TG-e.
