# M02 Tasks

Ordering: tasks with no new dependency first. Each TG is one implementer run (~60 tool calls). "Req" names the requirement in `openspec/specs/biomarkers-and-labs/spec.md` (main), `openspec/changes/s01-spec-discovery/specs/biomarkers-and-labs/spec.md` (s01), or this change's delta (M02).

## TG1 — Spec (this change)
- [x] proposal.md, tasks.md, spec delta written; questions Q56–Q60 appended to docs/QUESTIONS.md; ecosystem test enforces the link to docs/ecosystem/m02-blood-layer.md
- [x] TG1b: three review findings fixed in the spec (LabResult source/validation/eligibility, UCUM definition, rollback and s01 relation); Q63, Q64
- [x] TG1c: blood-only stored-and-flagged rule; DEXA/microbiome follow s01 Result without provenance; Q66

## TG-a — Lab report and result models (no new dependency)
- [x] (part 1: LabReport/LabResult models, source/origin, validation state, provenance fields, as-reported + normalised value, aggregation eligibility; part 1b: the reported value is never rounded, a value the column cannot hold exactly (more than 6 decimals, more than 14 integer digits, NaN/Infinity) is rejected with ValidationError and nothing is stored; part 2 done: `Biomarker.category` + `category_source` (Q66, NULL = blood, no seeded categories) and `LabResult.save` refuses a DEXA/microbiome result without laboratory or method; part 3 done: docs/omop/measurement-mapping.md + `core.omop.lab_result_to_omop_measurement`, DDL v5.4.0 checked, Q69) `LabReport` and result rows with laboratory, method, device, collected/reported timestamps, value+unit as reported and normalised, FK to `core.Biomarker`; OMOP MEASUREMENT column mapping documented after checking the DDL. Req: M02 "Lab result provenance and OMOP MEASUREMENT alignment"; main "Coded analyte registry"; s01 "Unit conversion between unit systems"; domain-model "Measurement provenance" (implement, do not restate). `LabResult` is a separate model from `core.Measurement` (Q61). Also implements M02 scenarios "A result records its source" and "A result without laboratory or method is not aggregation-eligible" (source = LabReport + origin, validation states `entered` | `user_confirmed` | `source_verified` | `disputed` | `retracted` (Q63; eligible only when confirmed), eligibility flag), Q63, and Q64 (DEXA/microbiome as LabResult). Also implements M02 scenario "A DEXA or microbiome result without provenance is not stored" and the analyte category per Q66. Blocked by: Q59, Q61, Q63, Q66.

## TG-b — Manual entry API (no new dependency)
- [x] (done: `POST /api/labs/reports/`, owner-only `GET /api/labs/reports/<id>/`, one transaction, `core.plausibility`, docs/api-labs.md, Q70) Authenticated API to create a lab report with results by hand, same models and same review/persist path as imports. Req: main "Manual entry of equal standing". Part 2: input bounds and O(n) trailing-zero strip, review 1795662883.

## TG-c — CSV import with review and rollback (stdlib csv)
- [x] (part 1 done 2026-11-26: preview, confirm, DELETE rollback of results and report; the retained original file and its scenario "Rollback removes the retained original" stay with TG-g) Parse CSV with `csv`, show parsed rows for review, persist only after confirmation, roll back a whole import. Req: main "Import from PDF, photo, and CSV with learned templates" (CSV part), main "Human review before persistence", M02 "Lab report import can be rolled back" (LabResult, LabReport and retained original file, scenario "Rollback removes the retained original"; s01 "Import can be rolled back" applies to LabResult).

## TG-d — Deterministic PII redaction
- [ ] Rule-based redaction of extracted text before review, with a diff the user sees, optional per Q58. Req: main "Optional PII obfuscation on import". Blocked by: Q58.
  - Part 1 done 2026-11-26 (stays unchecked): opt-in exact-term redaction for the CSV import (`core/redaction.py`, `redact_terms` on preview/confirm, diff in the preview, Q72; default off per Q58). Still pending: redaction of PDF/OCR text (TG-e/TG-f) and what is retained of the original (TG-g).
  - Part 1b done 2026-11-26 (stays unchecked): a laboratory or method cell that overflows only because of redaction gives `400` naming `redact_terms`; matching is linear (`str.find`); bounds and redaction both see the stripped cell.

## TG-e — Add pdfplumber (dependency)
- [ ] `uv add pdfplumber` after fetching and recording its licence (licence gate); text and table extraction into the review step. Req: main "Import from PDF, photo, and CSV with learned templates" (PDF part).

## TG-f — OCR with pytesseract (dependency)
- [ ] `uv add pytesseract`, licence fetch, Tesseract binary requirement documented; photo import into the review step. Req: same as TG-e (photo part). Blocked by: TG-e.

## TG-g — Original report file retained
- [ ] Store the uploaded file with the report; retention per Q57; a rollback of the import removes the file (M02 scenario "Rollback removes the retained original", Q65). Private storage only: the file is never published or exposed in OpenData until Q62 is answered and a requirement covers it. Req: main "Original report file retained and public raw" (retention part). Blocked by: Q57, Q62.
  - Part 1 done 2026-11-26 (stays unchecked): CSV import only. The confirmed CSV is kept as a private file with its `LabReport` (`original_file`, `original_sha256`, `original_size`, migration 0010, `PRIVATE_MEDIA_ROOT`), kept without automatic expiry (Q57), deleted on rollback via `transaction.on_commit` (Q65), never served. Default: with `redact_terms` the original is NOT retained (Q76). PDF/photo retention depends on TG-e/TG-f; the Q62 public-raw part is still open.

## TG-h — Completeness and freshness indicators
- [ ] Completeness and freshness per organ system from stored results. Req: main "Completeness and freshness indicators". Depends on an organ-system grouping of analytes (not yet defined; record a question when the task starts).

## TG-i — PhenoAge computation
- [x] Research (2026-11-26, Fabio's Q56 answer): compare PhenoAge and Bortz coefficients/constants/units/transformations across the original papers (with supplements and errata) and maintained implementations (biolearn, pyaging, get-based, others found); record them in docs/research/phenoage-coefficients.md; adopt a well-maintained AGPL-compatible library as the engine if one exists, checked against the papers (paper prevails unless an erratum says otherwise); no numbers in code before this comparison. Done: the document exists; recommendation is to hand-write PhenoAge against the original supplement (no suitable library); Bortz stays blocked on Q78 (the reference repository has no licence); open constant choice in Q77.
- [ ] Deterministic computation from the standard panel; coefficients entered only with a citation to the original paper, following docs/research/phenoage-coefficients.md and the Q77 default. Req: main "Deterministic PhenoAge computation from the standard panel".
  - Part 1 done 2026-11-26 (stays unchecked): pure engine in backend/core/phenoage.py (S2 constants + Q77 defaults, nine analytes in S2 units, no result on missing/non-finite/CRP <= 0/M outside (0, 1)), tests in backend/tests/test_phenoage.py. Pending (part 2): binding to stored LabResults by LOINC code (codes fetched from loinc.org) with stored unit conversions only, and an owner-only API.
  - Part 2 done 2026-11-26 (stays unchecked): `core/phenoage_binding.py` + `GET /api/labs/reports/<id>/phenoage/`, tests in test_phenoage_binding.py. Open: loinc.org returned 403, so no LOINC code is verified and the map is empty (every request refuses `analyte_not_mapped`, Q79); storing the result and a cross-report view are later tasks.
  - Part 2b done 2026-11-26 (stays unchecked): age_years too large for a float (e.g. 1e400) is a 400 naming age_years; review 1795694970

## TG-j — FHIR and OMOP export
- [x] TG-j part 1 (2026-11-26): hand-written FHIR DiagnosticReport/Observation Bundle (`core/fhir.py`, docs/fhir/lab-report-mapping.md, `GET /api/labs/reports/<id>/fhir/`, Q73); the five FHIR scenarios are tested. The OMOP export endpoint is still to decide, so the item below stays open.
  - Part 2 done 2026-11-26: owner-only `GET /api/labs/reports/<id>/omop/` (`LabReportOmopView`, retracted excluded, concept ids null, Q69/Q80), tests in test_lab_omop_export.py.
- [x] Hand-written FHIR DiagnosticReport/Observation representation and OMOP MEASUREMENT-shaped export of stored results. Req: M02 "FHIR representation of a stored lab result" (valid UCUM = exact match with a stored `Unit.ucum_code`; no UCUM validator blocker), M02 "Lab result provenance and OMOP MEASUREMENT alignment". Blocked by: Q55, TG-a.

## TG-l — Unit conversion view (no new dependency)
- [ ] Owner-only view of a stored result in a requested UCUM unit using stored UnitConversion rows only; reported value and unit always returned; no conversion known → reported value shown unconverted. Req: s01 "Unit conversion between unit systems". Part 1 = API; SI/US labelling of units waits on Q81.
  - Part 1 done 2026-11-26 (stays unchecked): `GET /api/labs/results/<id>/convert/?unit=<ucum>` (`LabResultConvertView`), tests in test_lab_unit_conversion_view.py; Q81.

## TG-m — Result against its three ranges (no new dependency)
- [ ] Owner-only view of a stored LabResult against reference range, optimal range and safety threshold, kept separate, each with its provenance and a deterministic status. Req: main "Three ranges per analyte", main "Optimal-range governance" (inspection part; the contested-range scenario waits on community-and-social).
  - Part 1 done 2026-11-26 (stays unchecked): `GET /api/labs/results/<id>/ranges/` (`LabResultRangesView`, `core/result_ranges.py`), tests in test_lab_result_ranges.py; Q82.

## TG-k — Extraction benchmark
- [ ] Synthetic report with a verified answer key; measure extraction accuracy of TG-e/TG-f. Req: s01 "Extraction benchmark on a synthetic report". Blocked by: TG-e.
