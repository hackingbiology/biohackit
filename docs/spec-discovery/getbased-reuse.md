# Spec discovery register — part C: getbased reuse analysis

Source compared with `openspec/specs/**`: `docs/getbased-reuse-analysis.md` (4 August 2026, all sections). Method as in `docs/spec-discovery/whitepaper.md`: every user-facing or system feature the document promises or recommends taking gets one row. Reuse and implementation notes that are not product features are `out-of-scope` with a reason; the reuse decisions themselves are recorded in `docs/ecosystem/integrations.md` (get-based section).

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour of this product, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/getbased-reuse-analysis.md § 0 Il fatto che cambia tutto | getbased is AGPL-3.0-or-later, so its code can be reused | out-of-scope | — | Licence fact; reuse decisions are recorded in docs/ecosystem/integrations.md (get-based section) |
| docs/getbased-reuse-analysis.md § 1 Cos'è | Five lenses: Labs, Genome, Body, Light, Insight | out-of-scope | — | Description of another product; the Light lens is excluded in § 3 Tier C |
| docs/getbased-reuse-analysis.md § 1 Cos'è | Local-first storage with end-to-end encrypted optional sync | out-of-scope | — | getbased design; the local-first question is Q28 in docs/QUESTIONS.md |
| docs/getbased-reuse-analysis.md § 1 Cos'è | Several AI providers including local models and a user-supplied endpoint | added | ai-uses-and-attribution/Choice of AI provider including a local model | Providers not named, Q28 |
| docs/getbased-reuse-analysis.md § 1 Cos'è | Project status, stack and layered architecture of getbased | out-of-scope | — | Facts about another project; verified facts live in docs/ecosystem/ |
| docs/getbased-reuse-analysis.md § 2 Il disallineamento architetturale | Individual versus collective premise; reuse at component level | out-of-scope | — | Architecture rationale; biohack.it is server-hosted (accounts-and-profiles) |
| docs/getbased-reuse-analysis.md § 3 Tier A A1 | Catalogue of coded biomarkers with reference ranges | covered | biomarkers-and-labs/Coded analyte registry | Seeding from the getbased catalogue is a data task under M01 |
| docs/getbased-reuse-analysis.md § 3 Tier A A1 | Reference and optimal range per marker | covered | biomarkers-and-labs/Three ranges per analyte | |
| docs/getbased-reuse-analysis.md § 3 Tier A A1 | Unit conversions between SI and US units | added | biomarkers-and-labs/Unit conversion between unit systems | |
| docs/getbased-reuse-analysis.md § 3 Tier A A1 | Cycle-phase-dependent ranges for four hormones | added | biomarkers-and-labs/Cycle-phase-dependent ranges | Values open, Q30 |
| docs/getbased-reuse-analysis.md § 3 Tier A A2 | Report import: text extraction, parsing, mapping, review, persistence | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | |
| docs/getbased-reuse-analysis.md § 3 Tier A A2 | PII obfuscation before AI parsing, with a diff viewer | covered | biomarkers-and-labs/Optional PII obfuscation on import | |
| docs/getbased-reuse-analysis.md § 3 Tier A A2 | Review modal with filters and mapping | covered | biomarkers-and-labs/Human review before persistence | |
| docs/getbased-reuse-analysis.md § 3 Tier A A2 | Persistence with rollback | added | biomarkers-and-labs/Import can be rolled back | |
| docs/getbased-reuse-analysis.md § 3 Tier A A2 | Benchmark of parsers on a synthetic report with an answer key | added | biomarkers-and-labs/Extraction benchmark on a synthetic report | |
| docs/getbased-reuse-analysis.md § 3 Tier A A3 | PhenoAge computed from the panel | covered | biomarkers-and-labs/Deterministic PhenoAge computation from the standard panel | |
| docs/getbased-reuse-analysis.md § 3 Tier A A3 | Bortz clock combined with PhenoAge, with component breakdown | added | biomarkers-and-labs/Deterministic Bortz clock computation | Inputs open, Q26 |
| docs/getbased-reuse-analysis.md § 3 Tier A A3 | Calculated ratio markers (HOMA-IR, NLR, De Ritis and others) | added | biomarkers-and-labs/Deterministic calculated markers | Formulas open, Q26 |
| docs/getbased-reuse-analysis.md § 3 Tier A A4 | Trend alerts on slope, sudden jumps and critical values | added | dashboards-and-doctor-view/Trend alerts | Thresholds open, Q25 |
| docs/getbased-reuse-analysis.md § 3 Tier A A5 | Chart bands for reference and optimal range | covered | biomarkers-and-labs/Three ranges per analyte | Drawn in the overlay requirement below |
| docs/getbased-reuse-analysis.md § 3 Tier A A5 | Intervention and drug timeline overlaid on the biomarker chart | added | dashboards-and-doctor-view/Intervention timeline overlaid on biomarker chart | |
| docs/getbased-reuse-analysis.md § 3 Tier A A6 | Curated SNP set and APOE haplotype | covered | genomics/Actionable interpretation focus | The SNP list is a data task |
| docs/getbased-reuse-analysis.md § 3 Tier A A6 | Raw-data files from six consumer DNA providers | added | genomics/Import of consumer DNA test files | |
| docs/getbased-reuse-analysis.md § 3 Tier A A6 | Genome parsed only in the browser, nothing on the server | out-of-scope | — | Conflicts with public-by-default genomics (genomics spec); parsing location is part of Q28 |
| docs/getbased-reuse-analysis.md § 3 Tier B B1 | Published AI surfaces map with "what is NOT AI" | covered | ai-uses-and-attribution/Published AI surfaces map — "what is AI, what is NOT AI" | |
| docs/getbased-reuse-analysis.md § 3 Tier B B2 | Verdict cache keyed on a data fingerprint, with a regenerate prompt | added | ai-uses-and-attribution/AI verdict shape with insufficient-data state | Per-verdict cost figures are getbased's and are not adopted |
| docs/getbased-reuse-analysis.md § 3 Tier B B3 | Verdict shape: colour, short tip, detail, regenerate; grey for insufficient data | added | ai-uses-and-attribution/AI verdict shape with insufficient-data state | |
| docs/getbased-reuse-analysis.md § 3 Tier B B4 | Coverage planner: which systems are under-tested and what to measure | covered | measurement-planning/The panel is computed, not chosen | |
| docs/getbased-reuse-analysis.md § 3 Tier B B4 | Completeness indicator per domain | covered | biomarkers-and-labs/Completeness and freshness indicators | |
| docs/getbased-reuse-analysis.md § 3 Tier B B5 | Nine context cards with a coherence note against goals | added | accounts-and-profiles/Lifestyle context cards | |
| docs/getbased-reuse-analysis.md § 3 Tier B B6 | Read-only revocable token for the user's own agent | covered | agent-access/Revocable read-only token | |
| docs/getbased-reuse-analysis.md § 3 Tier B B6 | Agent interface over MCP | covered | agent-access/MCP gateway over encrypted context | |
| docs/getbased-reuse-analysis.md § 3 Tier B B7 | First-class manual entry with out-of-range sanity check | covered | biomarkers-and-labs/Manual entry of equal standing | |
| docs/getbased-reuse-analysis.md § 3 Tier B B8 | Temporary password-protected profile link, no account for the recipient | added | dashboards-and-doctor-view/Time-limited password-protected sharing link | Lifetime open, Q27 |
| docs/getbased-reuse-analysis.md § 3 Tier B B9 | Multi-provider AI with a local option | added | ai-uses-and-attribution/Choice of AI provider including a local model | Q28 |
| docs/getbased-reuse-analysis.md § 3 Tier B B9 | Optional Bitcoin and Cashu payment | out-of-scope | — | The source says to keep it optional; no payment feature is decided |
| docs/getbased-reuse-analysis.md § 3 Tier C | Local-first as the only storage option | out-of-scope | — | Declared not to be taken; self-hosting is specified in accounts-and-profiles |
| docs/getbased-reuse-analysis.md § 3 Tier C | Zero-bundler front end with cross-layer window calls | out-of-scope | — | Implementation style not taken; the stack is frozen in docs/ROADMAP.md |
| docs/getbased-reuse-analysis.md § 3 Tier C | Product recommendation surface with affiliate disclosure | out-of-scope | — | Declared not to be taken; see community-and-social "Knowledge is not for sale" |
| docs/getbased-reuse-analysis.md § 3 Tier C | Light and Sun lens | out-of-scope | — | Declared out of scope; possible future optional module |
| docs/getbased-reuse-analysis.md § 4 Il buco da colmare | LOINC, UCUM and method mapping on top of the inherited catalogue | covered | biomarkers-and-labs/Coded analyte registry | |
| docs/getbased-reuse-analysis.md § 4 Il buco da colmare | Contribute the mapping back upstream | covered | ai-uses-and-attribution/Notify upstreams of their inclusion | Give-back proposals live in docs/ecosystem/GIVEBACK.md; nothing is posted without approval |
| docs/getbased-reuse-analysis.md § 5 Tre strategie | Fork, vendor the data and port the algorithms, or complement | out-of-scope | — | A reuse decision, recorded in docs/ecosystem/, not product behaviour |
| docs/getbased-reuse-analysis.md § 6 Effetto sul piano e sul budget | Budget reallocation to the collective layer | out-of-scope | — | Planning, tracked in docs/ROADMAP.md |
| docs/getbased-reuse-analysis.md § 6 Effetto sul piano e sul budget | AGPL compatibility audit of everything imported | covered | ai-uses-and-attribution/Previous-work and license register | Enforced by the licence gate (tools/licence/) |
| docs/getbased-reuse-analysis.md § 7 Nota operativa | Warning about data left in a shared browser | out-of-scope | — | Operational note about the analyst's browser |
| docs/getbased-reuse-analysis.md § 8 Nuove domande aperte | Options 1 to 3, local-first mode, MCP on the roadmap, upstream mapping | out-of-scope | — | Open decisions, not behaviour; Q28 records the local-first question and MCP access is covered by agent-access |
