# M03 Tasks

Ordering: tasks with no new dependency first. Each TG is one implementer run (~60 tool calls). "Req" names a requirement in `openspec/specs/interventions-and-catalog/spec.md` (main-IC), `openspec/specs/protocols/spec.md` (main-P), `openspec/changes/s01-spec-discovery/specs/interventions-and-catalog/spec.md` (s01), or this change's deltas (M03). Scan decisions (a)-(g) are in `docs/ecosystem/m03-interventions-protocols.md`. No group seeds a dose, code, peptide or synonym without a cited source; a row without one is not written.

## TG1 — Spec (this change)
- [x] proposal.md, tasks.md, spec deltas written; questions Q108–Q112 appended to docs/QUESTIONS.md; the scan is cited by section (a)-(g)

## TG-a — Substance model with code columns (no new dependency)
- [x] (Done with the Q105/Q106 defaults and Q116, no format check. Follow-up, left out and not built: substance interactions and safety markers from main-IC "Substance catalog metadata".) `Substance` model: names, class, code columns for RxCUI, PubChem CID, UNII and ATC as code strings only, each with source and fetch date; `Provisional` marking per Q105/Q106; no row seeded; no bulk file. Req: M03 "Substance codes are stored as cited code strings"; main-IC "Substance catalog metadata" (implement, do not restate). Scan (a). Blocked by: Q105, Q106 (what may be stored beyond code strings).

## TG-b — Synonym table and review queue (no new dependency)
- [x] (Done 2026-11-27 with defaults Q108: hand-entered cited reviewed synonyms, nothing bulk-loaded; Q117: difflib cutoff 0.8; Q118: language does not filter.) Synonym table with language, source and reviewer per synonym; exact lookup after case/whitespace normalisation; an unresolved name becomes `ambiguous` in a review queue. No synonym seeded. Req: M03 "Synonyms carry provenance and resolve only by exact match"; main-IC "Substance resolution on codes, not English strings" (scenarios "Italian input resolves", "Unresolved substance is surfaced, not dropped"). Scan (b); Wikidata and RapidFuzz only as candidate proposers, not resolvers. Blocked by: Q108 (source of it/zh synonyms).

## TG-c — Input-output diff and constrained columns (no new dependency)
- [x] (Done 2026-11-27 with defaults Q120: duplicates; Q121: max 200 entries; Q122: a correction creates no synonym; Q123: erased reviewer = unreviewed; Q124: retention; Q125: throttle rates.) Diff "N submitted, M recognised, K not understood" at the end of extraction; closed enums filled by code after validation, free text to a notes field, out-of-enum proposals `ambiguous`, no silent truncation. Req: main-IC "Input↔output diff at end of extraction", "LLM never writes into constrained columns". Depends on: TG-b.

## TG-d — Posology provenance and weight-relative gating (no new dependency)
- [x] Per-posology tag `human-derived` or `animal-derived` with a source; a weight-relative posology without a tag is not accepted as a dose; an animal-derived per-weight dose is never converted to an absolute dose. Req: main-IC "Posology provenance (human vs animal)"; s01 "Weight-relative posology is gated on posology provenance". Depends on: TG-a.
  - Done 2026-11-27: `basis`, `provenance`, `provenance_source` on intervention items; per-weight without provenance saves in Draft but is refused on leaving Draft or any later edit; API shows `absolute_dose: null`; OMOP `quantity` stays empty; `ActivationAcknowledgment` (migration 0002) gates activation of research-level or animal-derived protocols (Draft, Paused, already-running import). Defaults Q126-Q129. Left out: the dose sanity check and the mandatory baseline gate (no cited thresholds stored, Q126).

## TG-e — Route, formulation and multi-ingredient products (no new dependency)
- [x] Route and formulation per intake item; declared ingredients of a product; sum of an ingredient across products from declared amounts only, an ingredient without a label amount is not summed. Req: s01 "Route and formulation are recorded per intake item", "Multi-ingredient products list their declared ingredients". Depends on: TG-a.
  - Done 2026-11-27: `route` (closed plain-word list, Q130), `formulation`, `product_id` and `units_per_day` on intervention items; `Product` and `ProductIngredient` (migration substances 0005, nothing seeded) with an owner-only API; `GET /api/protocols/<id>/ingredient-totals/` (Decimal, same unit string only, label-contents-total, null amounts listed not summed); route exported as OMOP `route_source_value`. Defaults Q130-Q132. Left out: the intake schedule, the restock projection (the second AND of "Topical item is distinguished from oral") and the dose sanity check on the sum (no cited thresholds, Q126).

## TG-f — Protocol and ProtocolVersion models (no new dependency unless Q109 says so)
- [x] First sub-task: compare a plain `ProtocolVersion` model with django-simple-history, django-reversion and django-pghistory; re-fetch each licence and activity from GitHub/PyPI first; check pghistory against TimescaleDB; record the result in docs/ecosystem/. Default (Q109): plain model.
- [x] Part 1: `Protocol` (draft saved incrementally, states `Draft|Active|Paused|Completed`, origin `curated|community`, level `medical|research`, `in_effect_since` vs `tracked_since`, `history: synthesized|analytic`); `ProtocolVersion` with change events {field, old, new, timestamp, actor, reason}, reason mandatory; field-level diff of two versions with stdlib `difflib`; every created version is immutable (a protocol in state `Draft` is edited in place and has no version; a version is created when it leaves `Draft` or changes afterwards, even to correct the latest, with a reason); owner-only API under `/api/protocols/` (docs/api-protocols.md); import of an already-running protocol. Req: main-P "Create a protocol from scratch", "Import an already-running protocol", "Versioning and change tracking" (diff, dose change, Draft in place), "Protocol states" (states exist; the overdue effect is not built); M03 "A protocol version is immutable". Scan (f). Defaults: Q109, Q114.
- [ ] Part 2: `forked_from` lineage with source protocol and version ("Copy / fork an existing protocol"); measurements bound to the version in effect on their date; a measurement dated during `Draft` bound to no version (Q113); the Paused overdue effect. Depends on: TG-k visibility (Q112) and a measurement-planning link.

## TG-g — Queued, resumable extraction job (dependency)
- [ ] Evaluate Procrastinate: re-fetch licence and activity from GitHub/PyPI, read its job locking, retry and Django integration, and check it against `Django>=5.0,<6.0` in `backend/pyproject.toml`; then implement an idempotent resumable job with partial results. Celery and django-q2 stay learn-from only. Req: main-IC "Long extraction jobs are queued and resumable"; s01 "Early partial result during long waits". Scan (e). Blocked by: Q110 (approval to add a dependency, as Q74).

## TG-h — Evipedia seeding and enrichment
- [ ] Link substances to Evipedia review ids and PMIDs only; no review text; attribution as the main spec states. Synonyms from Evipedia only if an alias tool is confirmed (re-read the MCP README first); otherwise Q108 applies. Req: M03 "Evipedia content is stored as identifiers"; main-IC "Seed and enrich the catalog from Evipedia" (MODIFIED in this change: names enter as unreviewed candidates). Scan (d). Blocked by: Q15, Q108.

## TG-i — Principal peptides seed
- [ ] Seed the principal peptides as ordinary substances only for names listed in a source that is cited per row (with its codes and synonyms from TG-a and TG-b). No peptide row is seeded without a cited source; BPC-157, ipamorelin and semaglutide in the main spec are examples, not a seed list. Req: main-IC "Principal peptides present in the catalog". Blocked by: Q111, TG-a, TG-b.

## TG-j — Export mappings (FHIR, OMOP)
- [x] OMOP DRUG_EXPOSURE mapping document and function for a tracked intervention: fetch the OMOP CDM DDL and record its commit SHA, check column names against it; concept ids empty until the vocabularies are loaded. Follows docs/omop/measurement-mapping.md. Req: M03 "Protocol export mappings cite their target schema". Scan (c).
- [ ] FHIR MedicationStatement (intervention) and PlanDefinition (protocol) mapping, written by hand against the spec. Req: same. Blocked by: Q55 (FHIR licence).

## TG-k — Visibility, origin and level
- [x] Publish with per-facet visibility (public by default on publish, per-item withhold, genomic elements behind heightened consent), `curated` vs `community` origin shown wherever a protocol appears, `medical` vs `research` level shown. A curated seed protocol is written only from a cited source (no invented protocol). Req: main-P "Publish with per-facet visibility", "Curated and community origin". Blocked by: Q112 (default visibility of a draft and of unpublished facets); depends on: TG-f.
  - Done 2026-11-27: `Publication` (migration 0003) pins a version; per-item withhold by key (`measures[1]`), `genomic` flag never public (Q134); owner `publish`/`unpublish` with mandatory reason and a change event each; anonymous throttled `/api/public/protocols/`; `origin` and `level` in every serializer. Defaults Q133-Q135. Left out: any curated seed (no cited source), per-facet withhold, the genomics heightened consent itself. No dependency.

## TG-l — Browser pages (later)
- [ ] Substance search, review queue, protocol builder and version diff pages; EN first, IT/ZH fall back to EN as in M02; WCAG 2.2 AA; Playwright + axe check (Q34). Depends on: TG-b, TG-f. Blocked by: Q34.
