# M01 Tasks

## TG1 — Spec (this change)
- [x] proposal.md, tasks.md, spec delta written; questions appended to docs/QUESTIONS.md

## TG2 — Terminology app & sources
- [x] `terminology` Django app; `Source` model (name, version, licence, url, retrieved_at)
- [x] `Unit` (UCUM code, display) and `UnitConversion` (from, to, factor, biomarker nullable, source) models
- [x] `normalize_value()` deterministic helper; keeps as-reported value+unit
- [x] Tests: unknown unit rejected; conversion deterministic; row without source rejected

## TG3 — Coded analyte registry
- [x] Extend `Biomarker`: loinc_code required+unique, ucum unit FK, long name, system/specimen, source FK
- [x] Migration for existing stub rows; Measurement validated against analyte unit
- [x] Tests: persisting a measurement without LOINC/UCUM fails; lab+method missing ⇒ not aggregation-eligible

## TG4 — Three ranges & governance
  - Scan decision: no open reference-range dataset with a stated licence was found (Q11); ranges stay structure-only, no import
- [x] (models done; API in part B) `ReferenceRange` (lab/method, population, low, high, source), `OptimalRange` (source, population, endpoint, evidence_grade, last_reviewed), `SafetyThreshold` (source)
- [x] Selector `displayable_optimal_range()` returns None unless all provenance fields present
- [x] API read endpoint exposing the three ranges separately with provenance
- [x] Tests for every SHALL scenario in the spec delta

## TG5 — Seed loader & data
- [x] `seed_reference` management command, idempotent, refuses rows lacking source (part A: loader + format; data rows in part B)
- [ ] Seed files under `backend/terminology/seed/` with per-row source (UCUM units; LOINC subset for standard panel)
- [ ] Validate UCUM codes (seed rows and `services.resolve_unit`) with the `ucumvert` package (MIT, docs/ecosystem/m01-terminology.md) instead of a custom parser, with a test; re-check the licences of its `lark`/`pint` dependencies when adding it; each seed row's `Source` records the UCUM licence name and URL (Q9); keep `Source`/`Unit` column names alignable with OMOP `VOCABULARY`/`CONCEPT`
- [x] Tests: loader idempotent; unsourced row aborts

## TG-LOINC Full LOINC import (Fabio 2026-11-24)
- [ ] (part A: core table; part C1: ConsumerName + LinguisticVariants it-IT/zh-CN) Importer `manage.py import_loinc <dir>`: Loinc table, ConsumerName, Panels&Forms, AnswerList, Part/LinkageFile, LinguisticVariants (it-IT, zh-CN at least); idempotent upsert, records `Source(name=LOINC, version)`; licence notice stored and shown in UI/exports
- [ ] Scan decision: model LOINC tables so they map onto OMOP `CONCEPT` / `CONCEPT_RELATIONSHIP` (Part hierarchy as relationships); the release stays user-supplied until Q10 is answered; no Python LOINC loader was verified, so the importer is our own
- [ ] (part B: search over long/short/component names + API done; consumer/variant names follow their import)
- [ ] part C2: search over consumer names and linguistic variants
- [ ] (part A: core table + synthetic fixture) Test with a tiny synthetic fixture in LOINC file format (no real table in git); if `data/vendor/loinc/` is absent, the importer exits cleanly with instructions
- [x] (part B2) Search hardening: q longer than 200 characters rejected with HTTP 400 and a plain-language message; LoincSearchView has DRF ScopedRateThrottle scope `loinc_search` (rate in settings, Q51 default); pg_trgm.word_similarity_threshold appended to any existing DATABASE_URL `options` instead of replacing them
## TG-SNOMED
  - Scan decision: Snowstorm (Apache-2.0) and HAPI FHIR are read as references for RF2 / CodeSystem handling only; not adopted
- [ ] Verify GPS licence text and URL (record in Source); if redistribution allowed, importer for GPS; generic BYO-SNOMED RF2 importer; SNOMED codes are optional cross-refs only
## TG-STRATA
- [x] `OptimalRange`/`ReferenceRange` stratified by age band, sex, ancestry (nullable = all), with evidence grade; selector picks the most specific stratum with complete provenance (selection rule and fields; API wiring and the profile-derived Subject deferred)
