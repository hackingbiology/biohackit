# M01 Terminology & Reference Data — OpenSpec Change Proposal

**Author:** autodev · **Date:** 2026-11-23 · **Module issue:** #4
**Capabilities in scope:** `data-standards-and-typing`, `biomarkers-and-labs` (registry, three ranges, range governance)

## Goal
Give the platform a standards-coded, provenance-carrying reference layer that M02 (lab ingestion) and later modules build on:

- **Terminology tables** with an explicit `Source` registry (name, version, licence, URL, retrieved-at): LOINC, UCUM units, RxNorm/ATC, PubChem/UNII.
- **Coded analyte registry**: `Biomarker` extended so every analyte carries a LOINC code and a UCUM unit, plus a unit-conversion table (deterministic, per-analyte factors with source).
- **Three ranges per analyte** (`ReferenceRange` laboratory/method-dependent, `OptimalRange`, `SafetyThreshold`) — never collapsed; optimal ranges require source, population, endpoint, evidence grade and last-reviewed date or they are not displayable.
- **Seed loader**: management command `seed_reference` loading CSV/JSON seed files; refuses any row with no `source`. Idempotent.
- **Validation helpers**: UCUM unit validation, value normalisation (as-reported and normalised both kept).

## Out of scope
Lab import (M02), interventions catalog (M03), PhenoAge computation (M02), AI narration (M07).

## Scientific-data policy
No value is invented. Seed rows are limited to what can be cited from public sources (LOINC codes with official long names, UCUM codes from the UCUM spec). Licence-restricted vocabularies (SNOMED, full LOINC table) are NOT bundled: the loader accepts a user-supplied file. Optimal ranges are seeded only with a citation; where none can be verified, the range is left empty (therefore not displayed) and a question is raised.

## Decisions taken (defaults; Fabio may reverse)
| # | Decision | Default |
|---|---|---|
| D1 | LOINC distribution | Small curated subset (standard panel incl. PhenoAge inputs) with LOINC licence notice; full table via user-supplied file |
| D2 | Optimal ranges in seed | None invented; structure + validator only until sources are supplied/approved |
| D3 | Location | new Django app `backend/terminology/` |
| D4 | SNOMED | Not bundled (licence); field reserved |
