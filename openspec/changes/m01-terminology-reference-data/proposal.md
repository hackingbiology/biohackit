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

## Decisions update (Fabio, 2026-11-24)
- **D-LOINC (supersedes "subset only"):** the platform SHALL carry the **complete** LOINC release, as broad and detailed as published: all terms (~100k+), the official long names, the consumer names, the panels and forms, the answer lists, the LOINC Part hierarchy, and the linguistic variants. Variants for **it-IT and zh-CN** are required for i18n. The LOINC licence allows free redistribution with the copyright and licence notice and with the content unmodified. The release zip must be downloaded with a free loinc.org account, which Fabio holds. It is placed in `data/vendor/loinc/` (git-ignored) and loaded by an idempotent, versioned importer that records the LOINC version as `Source`. The curated "standard panel" subset remains as a *featured* flag, not as a limit.
- **D-SNOMED:** the full SNOMED CT is not bundled, because of its affiliate licence: it is free only in member territories and it cannot be shipped in an AGPL repo or open-data export. Instead:
  - bundle the **SNOMED CT Global Patient Set (GPS)**, the free set usable anywhere, after the runner has verified its licence text;
  - support a "bring your own SNOMED" importer for licensed operators;
  - keep SNOMED codes as optional cross-references only, never as the primary key: lab tests use LOINC, diagnoses use ICD-11 (WHO), substances use RxNorm/ATC/UNII.
- **D-OPTIMAL:** optimal ranges by age, sex and (where evidence exists) ancestry are a dedicated **research programme R1**; see docs/ROADMAP.md. M01 delivers only the stratified structure (age band, sex, ancestry, source, evidence grade) and the provenance gate.
