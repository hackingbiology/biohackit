# M01 Tasks

## TG1 — Spec (this change)
- [x] proposal.md, tasks.md, spec delta written; questions appended to docs/QUESTIONS.md

## TG2 — Terminology app & sources
- [x] `terminology` Django app; `Source` model (name, version, licence, url, retrieved_at)
- [x] `Unit` (UCUM code, display) and `UnitConversion` (from, to, factor, biomarker nullable, source) models
- [x] `normalize_value()` deterministic helper; keeps as-reported value+unit
- [x] Tests: unknown unit rejected; conversion deterministic; row without source rejected

## TG3 — Coded analyte registry
- [ ] Extend `Biomarker`: loinc_code required+unique, ucum unit FK, long name, system/specimen, source FK
- [ ] Migration for existing stub rows; Measurement validated against analyte unit
- [ ] Tests: persisting a measurement without LOINC/UCUM fails; lab+method missing ⇒ not aggregation-eligible

## TG4 — Three ranges & governance
- [ ] `ReferenceRange` (lab/method, population, low, high, source), `OptimalRange` (source, population, endpoint, evidence_grade, last_reviewed), `SafetyThreshold` (source)
- [ ] Selector `displayable_optimal_range()` returns None unless all provenance fields present
- [ ] API read endpoint exposing the three ranges separately with provenance
- [ ] Tests for every SHALL scenario in the spec delta

## TG5 — Seed loader & data
- [ ] `seed_reference` management command, idempotent, refuses rows lacking source
- [ ] Seed files under `backend/terminology/seed/` with per-row source (UCUM units; LOINC subset for standard panel)
- [ ] Tests: loader idempotent; unsourced row aborts
