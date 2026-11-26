# Ecosystem scan — M02 Blood Layer

Method, decision categories and licence table: [README.md](README.md). Capability: `biomarkers-and-labs` (no OpenSpec change for M02 exists yet; this scan precedes it). Areas: PDF text extraction, OCR, CSV import, FHIR lab resources, OMOP MEASUREMENT, PhenoAge / biological clocks, PII redaction, get-based components. Facts were fetched on 2026-11-26 from the GitHub API and PyPI; "last activity" is the GitHub `pushed_at` date. Anything that could not be fetched is `unknown`. Our own assessments (not fetched facts) are marked "assessment". No dependency is added by this scan.

## PDF/table text extraction

### pdfplumber
- **URL:** https://github.com/jsvine/pdfplumber
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-21
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/jsvine/pdfplumber and pypi.org/pypi/pdfplumber/json (classifier "MIT License", version 0.11.11), 2026-11-26
- **Licence note:** assessment: extracts text and tables with coordinates from text-based lab PDFs, the first step of the import pipeline. Its own dependencies were not checked; the licence gate (`tools/licence/check_licences.py`) must pass when it is added in an M02 task.

### pypdf
- **URL:** https://github.com/py-pdf/pypdf
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-25
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/py-pdf/pypdf (licence `NOASSERTION`) and pypi.org/pypi/pypdf/json (license_expression `BSD-3-Clause`, version 7.1.1), 2026-11-26
- **Licence note:** the licence comes from PyPI because GitHub reported `NOASSERTION`. Assessment: plain text extraction without table geometry; pdfplumber is the better fit, so this is a fallback to reconsider only.

### PyMuPDF
- **URL:** https://github.com/pymupdf/PyMuPDF
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-24
- **Decision:** reject
- **Verified:** api.github.com/repos/pymupdf/PyMuPDF, 2026-11-26
- **Licence note:** compatible by licence, but a second licensing regime for the same capability adds nothing over pdfplumber; the GitHub licence field was not cross-checked against a commercial dual-licence statement, which was not fetched.

## OCR for photographed reports

### Tesseract OCR
- **URL:** https://github.com/tesseract-ocr/tesseract
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-11-25
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/tesseract-ocr/tesseract, 2026-11-26
- **Licence note:** a native binary run as a separate process; assessment: its accuracy on phone photos of lab reports was not measured, so M02 must test it on synthetic reports before relying on it.

### pytesseract
- **URL:** https://github.com/madmaze/pytesseract
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-11-02
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/madmaze/pytesseract and pypi.org/pypi/pytesseract/json (licence text "Apache License 2.0", version 0.3.13), 2026-11-26
- **Licence note:** thin Python wrapper around the Tesseract binary above.

### EasyOCR
- **URL:** https://github.com/JaidedAI/EasyOCR
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-11-13
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/JaidedAI/EasyOCR, 2026-11-26
- **Licence note:** assessment: a deep-learning engine whose install pulls a large ML stack; heavier than Tesseract for the same job, so kept as an alternative to compare, not adopted.

## CSV import

### pandas
- **URL:** https://github.com/pandas-dev/pandas
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-25
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/pandas-dev/pandas and pypi.org/pypi/pandas/json (license_expression `BSD-3-Clause`, version 3.1.1), 2026-11-26
- **Licence note:** assessment: lab CSVs are small; the standard-library `csv` module, already used by `import_loinc`, avoids a large dependency. Revisit only if a task needs heavy tabular transforms.

## FHIR lab resources (DiagnosticReport, Observation)

### HL7 FHIR specification
- **URL:** https://github.com/HL7/fhir
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q55)
- **Last activity:** 2026-11-25
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/HL7/fhir (licence `NOASSERTION`) and raw.githubusercontent.com/HL7/fhir/master/LICENSE (says the source is covered by multiple licences, and that the specification itself is under a different licence), 2026-11-26
- **Licence note:** DiagnosticReport and Observation definitions are read only to design our export mapping; no definition text or file is copied until Q55 is answered.
- **Provisional:** yes, until Q55 is answered; nothing from this repository is imported.

### fhir.resources
- **URL:** https://github.com/nazrulworld/fhir.resources
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-09-14
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/nazrulworld/fhir.resources (licence `NOASSERTION`), raw.githubusercontent.com/nazrulworld/fhir.resources/main/LICENSE and pypi.org/pypi/fhir.resources/json (version 8.3.0 uploaded 2026-07-03, classifier "BSD License"), 2026-11-24
- **Licence note:** same verdict as docs/ecosystem/m01-terminology.md and integrations.md; cited, not re-decided. Pydantic FHIR models; M02 builds DiagnosticReport/Observation JSON by hand against the spec until Q9 is answered.
- **Provisional:** yes, fhir.resources is not used until Fabio answers Q9; the default is that it is not a dependency.

## OMOP CDM MEASUREMENT table

### OMOP CDM DDL
- **URL:** https://github.com/OHDSI/CommonDataModel
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-10-28
- **Decision:** reuse schema or dataset
- **Verified:** api.github.com/repos/OHDSI/CommonDataModel and raw.githubusercontent.com/OHDSI/CommonDataModel/main/DESCRIPTION (`License: Apache License 2.0`), 2026-11-24
- **Licence note:** same verdict as m01-terminology.md and integrations.md; cited, not re-decided. The MEASUREMENT table is the alignment target for lab results Column names checked against the v5.4.0 DDL (commit dd85c0d30bb3dd4bd16c5dbef7dbf9dd93075fa2, https://raw.githubusercontent.com/OHDSI/CommonDataModel/v5.4.0/inst/ddl/5.4/postgresql/OMOPCDM_postgresql_5.4_ddl.sql, 2026-11-26); mapping in docs/omop/measurement-mapping.md.

## PhenoAge / biological-age implementations

### pyaging
- **URL:** https://github.com/lucascamillomd/pyaging
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-22
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/lucascamillomd/pyaging and pypi.org/pypi/pyaging/json (license_expression `MIT`, version 0.6.3; project_urls point to this repository), 2026-11-26
- **Licence note:** assessment: a clock library built around epigenetic and omics data with a large dependency set. Its model files and data licences were not checked. Our PhenoAge is a closed-form formula over routine blood markers, with the published coefficients to be taken from the paper (Levine 2018) when M02 is specified, not from memory; this library is read for method only.
- **Engine decision (Q56 research, 2026-11-26):** not adopted as the computation engine; hand-write against the original paper. Source read: raw.githubusercontent.com/lucascamillomd/pyaging at commit db77b4bc263c82bfd2d5330029f232c71f2b33ec. It does carry the clinical formula (`PhenoAge` class), but it requires torch >= 2.2.0 and downloads the weights at runtime, and its current mortality-to-age constants (141.50 and 0.09165, from Kuo 2021) differ from the original supplement (141.50225 and 0.090165), which moves a result by 1 to 2 years. Details: docs/research/phenoage-coefficients.md (D3).

### biolearn
- **URL:** https://github.com/bio-learn/biolearn
- **Licence:** unknown
- **AGPL-compatible:** unknown — a "new BSD" licence without a clause count cannot be assigned an SPDX id; question in docs/QUESTIONS.md (Q55)
- **Last activity:** 2026-07-11
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/bio-learn/biolearn (licence `NOASSERTION`) and pypi.org/pypi/biolearn/json (licence text "new BSD", classifier "OSI Approved", version 0.9.1), 2026-11-26
- **Licence note:** the clause count (2 or 3) was not determined, so no SPDX id is claimed. Read for method only; no code is imported.
- **Engine decision (Q56 research, 2026-11-26):** not adopted. At commit 0d714f5a0c0ad5743b6315f3edab1f86112d394f (raw.githubusercontent.com/bio-learn/biolearn) its `PhenoAge` is the DNA-methylation clock; only a clinical unit registry exists, no blood-chemistry formula was found. Details: docs/research/phenoage-coefficients.md (D7).

### get-based (PhenoAge and Bortz, calculated markers)
- **URL:** https://github.com/elkimek/get-based
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-22
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/elkimek/get-based, 2026-11-26 (the same entry is in m00-foundations.md, verified 2026-11-24)
- **Licence note:** `docs/getbased-reuse-analysis.md` §A3 says get-based has PhenoAge and Bortz as deterministic closed formulas. That statement comes from the analysis document; the source file was not read in this scan. Code is not copied here: the backend is Python and each coefficient needs a citation, so M02 verifies it against the paper.
- **Engine decision (Q56 research, 2026-11-26):** the source file was read (raw.githubusercontent.com/elkimek/get-based at commit 3fba237f89f004cad915fa5c7767aaf9efe1d9d6, `js/data-calculated-markers.ts` lines 336-437): PhenoAge uses the original supplement's constants; its Bortz variant omits 4 of the 25 biomarkers, rounds the coefficients and caps inputs without a cited source. It is TypeScript, so it cannot be a Python engine. Still learn-from only. Details: docs/research/phenoage-coefficients.md (E1-E4).

### Bortz blood-age reference repository (bortzjd/bloodmarker_BA_estimation)
- **URL:** https://github.com/bortzjd/bloodmarker_BA_estimation
- **Licence:** unknown
- **AGPL-compatible:** no — no licence file (GitHub reports none) and the paper claims the code and models as Humanity Inc IP; treated as not usable until Q78 is answered
- **Last activity:** 2023-09-29
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/bortzjd/bloodmarker_BA_estimation (`license: null`, `pushed_at` 2023-09-29, commit 789db0ec99853a8278bcc5036b5f419de4b96c89) and raw.githubusercontent.com at that commit, 2026-11-26
- **Licence note:** it holds the authors' coefficients and means for the Full ENC model (Data/coefficients_and_means.csv) and an R example. The coefficients are cited in docs/research/phenoage-coefficients.md for comparison only; no Bortz number enters code until Q78 is answered.

### mcp-phenoage-clock
- **URL:** https://github.com/199-mcp/mcp-phenoage-clock
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2025-05-31
- **Decision:** reject
- **Verified:** api.github.com/repos/199-mcp/mcp-phenoage-clock and raw.githubusercontent.com at commit 67bbb0440839ffcd49c8a6d17bbf8f2136729ce0, 2026-11-26
- **Licence note:** rejected as a source: it accepts albumin in g/dL, creatinine in mg/dL, glucose in mg/dL and CRP in mg/L and applies them to coefficients defined for g/L, umol/L, mmol/L and mg/dL without a conversion (`src/phenoage.ts` lines 81-91 and 99-108). Details: docs/research/phenoage-coefficients.md (D5).

### BioAge (R package)
- **URL:** https://github.com/dayoonkwon/BioAge
- **Licence:** GPL-3.0
- **AGPL-compatible:** unknown — the GPL-3.0 row of the README table is `unknown`; question in docs/QUESTIONS.md
- **Last activity:** 2026-04-02
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/dayoonkwon/BioAge and raw.githubusercontent.com at commit b1f9fc02f086cd4aa74185f2335ab1366082e7fe, 2026-11-26
- **Licence note:** an R package that refits the PhenoAge model on supplied data instead of applying the published constants, so it cannot serve as a computation engine in a Python backend.

## PII detection and redaction

### Microsoft Presidio
- **URL:** https://github.com/data-privacy-stack/presidio
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-24
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/data-privacy-stack/presidio (the old microsoft/presidio name redirects there) and pypi.org/pypi/presidio-analyzer/json (license_expression `MIT`, version 2.2.366), 2026-11-26
- **Licence note:** assessment: it detects PII with NLP models and a language model download, which is heavy for the first step. M02 first uses deterministic pattern redaction before any text reaches an AI step; whether Presidio's recall justifies its size is to be measured on synthetic reports before adopting it. Its own dependencies were not checked.

## get-based lab import components

### get-based import pipeline (pdf-import.js and satellites)
- **URL:** https://github.com/elkimek/get-based
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-22
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/elkimek/get-based, 2026-11-26
- **Licence note:** `docs/getbased-reuse-analysis.md` §A2 names `pdf-import.js` and seven satellite modules: text extraction, PII obfuscation with a diff viewer, AI parsing, schema mapping, a review modal and rollback, plus a benchmark on a synthetic report. We take the design (review step before persistence, rollback, a benchmark with a verified answer key); the JavaScript is not imported. The module files were not read in this scan.

## Decisions for the M02 OpenSpec change

No dependency is added in this task: adoption happens in M02 tasks, each with a licence-gate pass.

- **PDF/table text extraction:** adopt pdfplumber as dependency (MIT, tables with coordinates); pypdf learn-from only, PyMuPDF rejected.
- **OCR for photographed reports:** adopt Tesseract with pytesseract as dependency (Apache-2.0); accuracy on photos to be tested on synthetic reports first; EasyOCR learn-from only.
- **CSV import:** learn-from only for pandas; use the standard-library `csv` module, as `import_loinc` does.
- **FHIR lab resources:** learn-from only; the spec licence is unknown (Q55) and fhir.resources waits for Q9, so DiagnosticReport/Observation are built by hand against the spec.
- **OMOP MEASUREMENT:** reuse schema (OMOP CDM DDL, Apache-2.0) as the alignment target for lab results.
- **PhenoAge / biological clocks:** learn-from only for pyaging, biolearn and get-based; coefficients come from the original paper with a citation, computed by deterministic code. Q56 research done 2026-11-26 (docs/research/phenoage-coefficients.md): no library is adopted as the engine; PhenoAge is hand-written against the original supplement, and Bortz waits for the licence question (Q78).
- **PII redaction:** learn-from only for Presidio; start with deterministic redaction, decide on Presidio after a measurement.
- **get-based import components:** learn-from only; reuse the pipeline design (review modal, rollback, benchmark), not the JavaScript.
