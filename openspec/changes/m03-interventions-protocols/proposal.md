# M03 Interventions Catalog and Protocols — OpenSpec Change Proposal

**Author:** autodev · **Date:** 2026-11-27 · **Module issue:** unknown (no M03 issue found in docs/tickets/created)
**Capabilities in scope:** `interventions-and-catalog` (substances, codes, synonyms, extraction diff, posology provenance, Evipedia seeding) and `protocols` (protocol and version model, fork, states, visibility, origin, level)

## Goal
Give the project a substance catalog that resolves names (Italian, English, Chinese) to external codes without guessing, and a protocol object whose every change is a tracked, attributable version event:

- **Substance model** with code columns (RxCUI, PubChem CID, UNII, ATC) held as code strings, each with source and fetch date.
- **Synonym table**: exact lookup only; an unresolved name goes to a review queue, never dropped, never fuzzy-matched.
- **Extraction guardrails**: input-output diff, constrained columns the LLM never writes, posology provenance (human or animal).
- **Protocols**: draft, states, fork lineage, versions with a mandatory reason, a diff between versions, measurements bound to the version in effect, visibility per facet, curated or community origin, medical or research level.
- **Export mappings** to FHIR MedicationStatement / PlanDefinition and OMOP DRUG_EXPOSURE.

Most behaviour is already a requirement in `openspec/specs/interventions-and-catalog/spec.md`, `openspec/specs/protocols/spec.md` or `openspec/changes/s01-spec-discovery/specs/interventions-and-catalog/spec.md`. Tasks implement those; the delta of this change adds only what the scan decisions need.

## Ecosystem scan
Reuse decisions: [docs/ecosystem/m03-interventions-protocols.md](../../../docs/ecosystem/m03-interventions-protocols.md) (change `x01-ecosystem-reuse`; facts fetched 2026-11-27). Section by section, with its "Decisions for the M03 OpenSpec change" block (line 169 onward):

- **(a) Codes:** identifiers only. RxCUI through the RxNav API and PubChem CID through PUG REST, stored as code strings with source and fetch date, Provisional until Q105. ATC and UNII: learn-from only, no WHO or FDA file stored (Q105, Q106). No bulk release is committed. Delta requirement "Substance codes are stored as cited code strings".
- **(b) Multilingual resolution:** exact lookup in our own synonym table with a source and reviewer per synonym. Wikidata (CC0) and RapidFuzz (MIT) are learn-from only candidate sources for the review queue, never for silent resolution. Delta requirement "Synonyms carry provenance and resolve only by exact match".
- **(c) Models:** FHIR MedicationStatement / PlanDefinition / CarePlan and OMOP DRUG_EXPOSURE are export mapping targets, not storage schemas. FHIR is learn-from only until Q55; the OMOP DDL is reuse schema and is checked as in M02. Delta requirement "Protocol export mappings cite their target schema".
- **(d) Evipedia:** learn-from only; store review IDs and PMIDs, not review text, until Q15. The scan found no alias tool in the MCP, so the synonym source is open (Q108, default: reviewed manual entry with a cited source). Delta requirement "Evipedia content is stored as identifiers" and a MODIFIED "Seed and enrich the catalog from Evipedia" (Evipedia names enter as unreviewed candidates).
- **(e) Queue:** no library adopted. Procrastinate (PostgreSQL-based, MIT) is the first candidate; Celery and django-q2 are learn-from only. Adoption needs approval (Q110) and a check against the scenario "Job survives a timeout".
- **(f) Versioning and diff:** no library adopted. A plain version model is compared with django-simple-history, django-reversion and django-pghistory in a task (Q109); diff with stdlib `difflib` (assessment, not fetched). Delta requirement "A protocol version is immutable".
- **(g) get-based:** learn-from only (period and schedule model, review-before-apply draft, evidence record with a PMID); nothing imported.

## Out of scope
Pills, therapeutics, nutrition and exercise tracking (M04), daily log and adherence (M05), n-of-1 analysis (M06), AI narration (M07), community discovery (`community-and-social`), genomic consent.

## Scientific-data policy
No dose, code, synonym, peptide, URL or citation is invented. Every code string, synonym and dose is stored with a cited source; a row without one is not seeded. This change seeds nothing: seeding tasks are blocked until a source is cited (Q111 for the peptide list).

## Decisions taken (defaults; Fabio may reverse)
| # | Decision | Default |
|---|---|---|
| D1 | Code storage | code strings with source and fetch date; no bulk RxNorm/ATC/UNII/PubChem file (Q105, Q106) |
| D2 | Synonym source for it/zh | reviewed manual entry with a cited source; no alias tool assumed in the Evipedia MCP (Q108) |
| D3 | Resolution | exact match on reviewed synonyms; fuzzy tools only propose to the review queue |
| D4 | Version model | plain `ProtocolVersion` model, `Draft` edited in place with no version; every created version immutable (Q109) |
| D5 | Queue | not adopted; Procrastinate evaluated first, needs approval (Q110) |
| D6 | Principal peptides | list only from a cited source; none seeded now (Q111) |
| D7 | Protocol visibility | main spec rule (public by default, per-item withhold) applies on publish; a draft is private (Q112) |
| D8 | Evipedia | identifiers and PMIDs only (Q15) |
| D9 | Exports | FHIR hand-written against the spec, blocked by Q55; OMOP DRUG_EXPOSURE concept ids empty until vocabularies are loaded |
