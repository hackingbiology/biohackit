# M02 Blood Layer — OpenSpec Change Proposal

**Author:** autodev · **Date:** 2026-11-26 · **Module issue:** unknown (not verified; Q60 asks Fabio)
**Capabilities in scope:** `biomarkers-and-labs` (lab ingestion, review, provenance, completeness, PhenoAge, export)

## Goal
Deliver "upload your past lab reports, get your clinical history in graphs" on top of the M01 coded registry:

- **Lab report and result models** with provenance (laboratory, method, device, collected and reported timestamps, value and unit as reported and as normalised), linked to the `core.Biomarker` LOINC/UCUM registry and alignable with OMOP MEASUREMENT.
- **Ingestion**: manual entry of equal standing, CSV, then PDF and photo, always with a human review step before persistence and a rollback.
- **Deterministic PII redaction**, original report file retained, completeness/freshness indicators, PhenoAge.
- **Export** of a stored lab result as FHIR DiagnosticReport/Observation and as OMOP MEASUREMENT.

Most behaviour is already a requirement in `openspec/specs/biomarkers-and-labs/spec.md` or in `openspec/changes/s01-spec-discovery`. Tasks implement those; the delta adds only what is new.

## Ecosystem scan
Reuse decisions: [docs/ecosystem/m02-blood-layer.md](../../../docs/ecosystem/m02-blood-layer.md) (change `x01-ecosystem-reuse`). Restated:

- **pdfplumber** (PDF text and tables) and **pytesseract/Tesseract** (OCR) are adopted in later task groups, each as its own task with a licence-gate pass. pypdf and EasyOCR: learn-from only; PyMuPDF rejected.
- **CSV**: standard-library `csv` (as `import_loinc` does); pandas learn-from only.
- **FHIR DiagnosticReport/Observation**: written by hand against the spec (spec licence unknown, Q55; fhir.resources waits for Q9).
- **OMOP MEASUREMENT**: alignment target (OMOP CDM DDL); column names are checked against the DDL when the model task is done.
- **PhenoAge**: coefficients from the original paper with a citation, computed by deterministic code; pyaging, biolearn and get-based learn-from only.
- **PII redaction**: deterministic first; Presidio learn-from only until measured.
- **get-based pipeline**: reuse the design (review step, rollback, benchmark with answer key), not its JavaScript.

## Out of scope
Wearables, genomics, interventions catalog (M03), AI narration of results (M07), research programme R1 (optimal ranges by stratum).

## Scientific-data policy
No value, range, coefficient or code is invented. PhenoAge coefficients are entered only with a citation to the original paper (Q56). Analyte codes come from the M01 registry. Extraction results are stored as reported with provenance; normalisation uses stored conversion factors only.

## Decisions taken (defaults; Fabio may reverse)
| # | Decision | Default |
|---|---|---|
| D1 | PDF/OCR libraries | pdfplumber and pytesseract, each added in its own task after a licence fetch |
| D2 | CSV | stdlib `csv`, no pandas |
| D3 | FHIR | hand-written against the spec, no `fhir.resources` (Q55, Q9) |
| D4 | OMOP | MEASUREMENT as alignment target only; no OMOP tables created |
| D5 | PhenoAge coefficients | from the original paper only, cited (Q56) |
| D6 | Original report retention | kept until the user deletes it (Q57) |
| D7 | PII redaction | off by default, as the main spec requires; the user may opt in and sees a reviewable diff. What the retained original is after opt-in is not decided here (Q58) |
| D8 | Location | results in `backend/core`; import code in a new app named in TG-a (Q59) |
| D9 | Publication of originals | the main spec makes the raw original public by default, which conflicts with redaction being off. Default: the original stays private until the user explicitly publishes it; no MODIFIED requirement is made yet (Q62) |
| D10 | Lab result model | `LabResult` is separate from `core.Measurement` because `Measurement` rejects unconvertible units (Q61) |
| D11 | Validation state values | domain-model names a validation state but defines no values; Fabio chose `entered` \| `user_confirmed` \| `source_verified` \| `disputed` \| `retracted` (Q63, 2026-11-26) |
| D12 | Valid UCUM | exact match with a stored terminology `Unit.ucum_code`. Full UCUM grammar validation (ucumvert, m01 TG5 B1) can widen the definition later |

## UCUM system URL
`http://unitsofmeasure.org` is copied from the FHIR R4 UCUM page, https://hl7.org/fhir/R4/ucum.html (fetched 2026-11-26): "The URI http://unitsofmeasure.org identifies UCUM codes".

## Relation to s01
`s01-spec-discovery` "Import can be rolled back" (removing the measurements an import created) and "Body composition and microbiome results ... same time series model as blood analytes" apply to `LabResult` for lab-reported results. The delta adds "Lab report import can be rolled back" for `LabResult`. DEXA and microbiome lab results are stored as `LabResult`; `core.Measurement` stays for self-tracked values (Q64). s01 "Result without provenance" applies to DEXA and microbiome `LabResult`s; the stored-and-flagged rule applies to blood analytes only (Q66). `s01-spec-discovery` is not edited.
