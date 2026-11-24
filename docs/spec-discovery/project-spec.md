# Spec discovery register — part B: hackingbiology project spec

Source compared with `openspec/specs/**`: `docs/hackingbiology-project-spec.md` (v0.3, all sections). Part C (`docs/getbased-reuse-analysis.md`, `docs/presentation/`) follows in a later register.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour (vision, planning, stack choice, open question) or superseded by a recorded decision; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/hackingbiology-project-spec.md § 0 Nota di lettura | Reading guide: three levels and the open-questions list | out-of-scope | — | Document structure |
| docs/hackingbiology-project-spec.md § 1 Executive summary | Biohacker documents a protocol in a structured way | covered | protocols/Create a protocol from scratch | |
| docs/hackingbiology-project-spec.md § 1 Executive summary | Protocol and results shared publicly; follow and copy people with results | covered | community-and-social/Follow and copy | |
| docs/hackingbiology-project-spec.md § 1 Executive summary | Aggregate of protocols with baseline and follow-up is open data | covered | analytics-and-open-data/Cohort aggregation | |
| docs/hackingbiology-project-spec.md § 1 Executive summary | The beginner who copies gets monitoring of kidney and liver | covered | safety-guardrails/Safety markers inherited automatically | |
| docs/hackingbiology-project-spec.md § 1 Executive summary | Non-profit corporate form | out-of-scope | — | Legal structure |
| docs/hackingbiology-project-spec.md § 2 Il problema | Competitor landscape table and the infrastructure gap | out-of-scope | — | Problem statement and market analysis |
| docs/hackingbiology-project-spec.md § 3.1 Biohacker esperto | Scheduling of measurements and purchases; dashboard that answers the doctor | covered | measurement-planning/Phase-dependent cadence | |
| docs/hackingbiology-project-spec.md § 3.1 Biohacker esperto | Qualified peer feedback on one's trends | covered | community-and-social/Cohorts form around protocols | |
| docs/hackingbiology-project-spec.md § 3.2 Principiante | Follow an existing protocol and inherit its safety markers | covered | safety-guardrails/Safety markers inherited automatically | |
| docs/hackingbiology-project-spec.md § 3.3 Comunità | Every protocol and compound has its thread; platform feeds the forum | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| docs/hackingbiology-project-spec.md § 3.4 Medici curanti | Doctor is the recipient of a readable output, not a user | covered | dashboards-and-doctor-view/Doctor protocol sheet | |
| docs/hackingbiology-project-spec.md § 3.5 Ricerca e pratica clinica | Honest declaration of data reliability and its limits | covered | scientific-method-and-evidence/Publicly declared nature and limits | |
| docs/hackingbiology-project-spec.md § 3.6 Critica medica | Clinical objections collected, published and used as a backlog | added | community-and-social/Medical objections are collected as a public backlog | |
| docs/hackingbiology-project-spec.md § 3.7 Laboratori di analisi | Labs as a source of reports to import | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | Future lab partnership is not software behaviour |
| docs/hackingbiology-project-spec.md § 3.8 Fornitori | No commercial integration with suppliers in the initial phase | covered | procurement-and-inventory/No monetised procurement initially | |
| docs/hackingbiology-project-spec.md § 3.9 Market player | Market players may integrate, never rank; commercial content labelled | added | community-and-social/Knowledge is not for sale | Labelling scenario added to the requirement |
| docs/hackingbiology-project-spec.md § 4.1 Journey A | Import baseline, declare interventions, system proposes missing markers, calendar | covered | accounts-and-profiles/Onboarding "bring your reports" | |
| docs/hackingbiology-project-spec.md § 4.1 Journey B | Mandatory baseline and safety checklist before starting a copied protocol | covered | safety-guardrails/Mandatory baseline AND risk acknowledgment before following a protocol | |
| docs/hackingbiology-project-spec.md § 4.1 Journey B | Compare with the cohort practising the same protocol | covered | dashboards-and-doctor-view/Cohort comparison — inline reference AND dedicated view | |
| docs/hackingbiology-project-spec.md § 4.1 Journey C | Due analytes pooled into one draw | covered | measurement-planning/Analyte pooling into one draw | |
| docs/hackingbiology-project-spec.md § 4.1 Journey C | A request for the laboratory is generated | added | measurement-planning/Lab request generated from a pooled draw | Format open, Q20 |
| docs/hackingbiology-project-spec.md § 4.1 Journey C | Upload PDF, parse, human validation, values fill the dashboards | covered | biomarkers-and-labs/Human review before persistence | |
| docs/hackingbiology-project-spec.md § 4.1 Journey D | Protocol sheet for the doctor: public link and PDF | covered | dashboards-and-doctor-view/Doctor protocol sheet | |
| docs/hackingbiology-project-spec.md § 4.1 Journey E | Publish, thread, followers, cohort, versioned revision | covered | protocols/Versioning and change tracking | |
| docs/hackingbiology-project-spec.md § 4.2 Touchpoint | Responsive web app, mobile for daily adherence | out-of-scope | — | Platform choice (PWA), fixed in docs/ROADMAP.md criteria 3 and 5 |
| docs/hackingbiology-project-spec.md § 4.2 Touchpoint | Public profile and protocol pages indexable | added | community-and-social/Public profile and protocol pages are indexable | |
| docs/hackingbiology-project-spec.md § 4.2 Touchpoint | Bidirectional protocol and forum thread link | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| docs/hackingbiology-project-spec.md § 4.2 Touchpoint | Reminders for intake, due test, restock | added | daily-log-and-adherence/Reminders for intake, due tests and restock | Channel open, Q22 |
| docs/hackingbiology-project-spec.md § 4.2 Touchpoint | Open data endpoint (dump and API) | covered | analytics-and-open-data/Full clonable public snapshot | |
| docs/hackingbiology-project-spec.md § 4.2 Touchpoint | Import from Apple Health, Google Fit, CSV | added | biomarkers-and-labs/Import from wearable export files | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 1 | The person owns the data; full export always | added | accounts-and-profiles/Full personal data export | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 2 | Public by choice, never by default; per-marker granularity | out-of-scope | — | Superseded: RESOLVED 2026-08-04 in accounts-and-profiles ("Public-by-default profile") |
| docs/hackingbiology-project-spec.md § 4.3 Principio 3 | The platform describes, never prescribes | added | safety-guardrails/Platform describes and never prescribes | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 4 | Safety is not opt-in | covered | safety-guardrails/Safety markers inherited automatically | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 5 | Every claim has a source; evidence graded by type | covered | scientific-method-and-evidence/Evidence hierarchy | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 6 | The system fails loudly and never proceeds silently on an incomplete protocol | covered | interventions-and-catalog/Input↔output diff at end of extraction | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 7 | Value in the first ten minutes at zero spend | covered | accounts-and-profiles/Onboarding "bring your reports" | |
| docs/hackingbiology-project-spec.md § 4.3 Principio 8 | Stops instead of guessing when coverage is insufficient | covered | analytics-and-open-data/"Stops instead of guessing" in aggregates | Individual trends: statistical-methodology/Uncertainty and effect size are mandatory |
| docs/hackingbiology-project-spec.md § 4.3 Principio 9 | Genomic data structurally never shareable | out-of-scope | — | Superseded: genomics is public behind heightened consent (accounts-and-profiles RESOLVED note; genomics spec) |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Person/Profile with context attributes and visibility | covered | accounts-and-profiles/Required biological profile | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | TestingProtocol, TreatmentPlan and Goal kept separate; goals map to hallmarks | covered | domain-model/Separation of the three protocol facets | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Protocol is the public composite with origin, fork and thread | covered | domain-model/Protocol as public composite | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Intervention with cycle schema (pattern, on/off days, titration) | covered | domain-model/Intervention carries a cycle schema | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Intervention subtypes incl. procedure, hormonal, nutrition | covered | domain-model/Intervention subtypes | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Substance catalog entity with identifiers, class, interactions | covered | interventions-and-catalog/Substance catalog metadata | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Biomarker with role, ranges and collection modality | covered | domain-model/Biomarker with role and three ranges | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Measurement with date, source, lab, method, unit, validation state | covered | domain-model/Measurement provenance | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | MeasurementPlan with explicit reason | covered | measurement-planning/Phase-dependent cadence | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | SafetyRule: if X, monitor Y with cadence Z and alert threshold | covered | domain-model/Safety, adherence and wellness as first-class entities | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Inventory and Purchase with lots, expiry, lead time | covered | procurement-and-inventory/Inventory with lots and expiry | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | DaySchedule under interaction and bioavailability constraints | covered | pills-management/Daily intake schedule across slots | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Cohort and Study (endpoints before start, washout, stop criteria) | covered | studies-nof1/Study with pre-declared endpoints | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | AdherenceLog with four states and cumulative adherence | covered | daily-log-and-adherence/Four-state adherence | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Adherence qualifies N-of-1 and weights cohort contributions | covered | daily-log-and-adherence/Adherence qualifies data downstream | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | WellnessCheck: mood, energy, sleep, notes | covered | daily-log-and-adherence/Wellness check | |
| docs/hackingbiology-project-spec.md § 5 Modello di dominio | Chain Substance, SafetyRule, Biomarker, Measurement, Dashboard | covered | domain-model/Safety, adherence and wellness as first-class entities | |
| docs/hackingbiology-project-spec.md § 6 M1 | Create, version, fork, publish; curated and community catalog; diff between versions | covered | protocols/Copy / fork an existing protocol | |
| docs/hackingbiology-project-spec.md § 6 M1 | Curated and community origin | covered | protocols/Curated and community origin | |
| docs/hackingbiology-project-spec.md § 6 M2 | LOINC and UCUM mandatory; method and lab stored per measurement | covered | biomarkers-and-labs/Coded analyte registry | |
| docs/hackingbiology-project-spec.md § 6 M2 | Three ranges per analyte | covered | biomarkers-and-labs/Three ranges per analyte | |
| docs/hackingbiology-project-spec.md § 6 M2 | Hard boundary: deterministic numbers, LLM writes words once, cached | covered | biomarkers-and-labs/Deterministic pipeline with a hard boundary | |
| docs/hackingbiology-project-spec.md § 6 M2 | Import from PDF, photo, CSV; manual entry of equal standing; review; loud failure | covered | biomarkers-and-labs/Manual entry of equal standing | |
| docs/hackingbiology-project-spec.md § 6 M2 | Completeness and freshness per system | covered | biomarkers-and-labs/Completeness and freshness indicators | |
| docs/hackingbiology-project-spec.md § 6 M2 | The panel is computed from safety core, safety rules and goals | covered | measurement-planning/The panel is computed, not chosen | |
| docs/hackingbiology-project-spec.md § 6 M3 | Cadence dense at start, sparse at maintenance; pooling; pre-analytical requirements | covered | measurement-planning/Phase-dependent cadence | |
| docs/hackingbiology-project-spec.md § 6 M3 | Overdue is a safety signal tied to safety rules | covered | measurement-planning/Overdue is a safety signal | |
| docs/hackingbiology-project-spec.md § 6 M3 | Two-axis filters, three views, study timelines on the calendar | covered | measurement-planning/Planner views | |
| docs/hackingbiology-project-spec.md § 6 M4 | Projected need, batch purchase, stock, restock alerts | covered | procurement-and-inventory/Projected need from protocol | |
| docs/hackingbiology-project-spec.md § 6 M4 | Slots that optimise bioavailability and avoid toxicity summation | covered | pills-management/Spacing and distance rules | |
| docs/hackingbiology-project-spec.md § 6 M5 | Public view grouped by biomarker family with reasons | covered | dashboards-and-doctor-view/Public dashboard grouped by biomarker family | |
| docs/hackingbiology-project-spec.md § 6 M5 | Biological-age delta shown with uncertainty, clock and lab; not used for ranking | covered | dashboards-and-doctor-view/Headline metric first, then organ-system grid | |
| docs/hackingbiology-project-spec.md § 6 M5 | Organ-system view shows efficacy and safety together | covered | dashboards-and-doctor-view/Organ-system view unifies efficacy and safety | |
| docs/hackingbiology-project-spec.md § 6 M5 | Double-column literature versus cohort | covered | dashboards-and-doctor-view/Double-column literature vs observed | |
| docs/hackingbiology-project-spec.md § 6 M4bis | Cost per protocol, intervention and draw; monthly projection; public cost | added | procurement-and-inventory/Protocol cost is tracked and shown | Price source open, Q18 |
| docs/hackingbiology-project-spec.md § 6 M6 | Profiles, follow, copy, cohorts | covered | community-and-social/Cohorts form around protocols | |
| docs/hackingbiology-project-spec.md § 6 M6 | Reputation on data completeness, not on winning results | covered | community-and-social/Two-axis reputation and specialty discovery | |
| docs/hackingbiology-project-spec.md § 6 M6 | Link to existing threads before cohorts; no cold-launched social features | out-of-scope | — | Delivery order, tracked in docs/ROADMAP.md; the integration itself is specified |
| docs/hackingbiology-project-spec.md § 6 M6 | Public, discussed and traceable claim review | covered | community-and-social/Public claim review | |
| docs/hackingbiology-project-spec.md § 6 M6 | Evidence Badge computed from the data, with derivation visible | covered | community-and-social/Calculated Evidence Badge | |
| docs/hackingbiology-project-spec.md § 6 M6 | Two reputation axes, never fused; discovery by specialty | covered | accounts-and-profiles/Two independent reputation axes | |
| docs/hackingbiology-project-spec.md § 6 M6 | Gamification only on data quality; no outcome leaderboards | covered | community-and-social/Gamification only on data quality | |
| docs/hackingbiology-project-spec.md § 6 M7 | Baseline gating, inherited markers, critical alerts, interaction warnings, escalation | covered | safety-guardrails/Interaction and critical-value alerts | |
| docs/hackingbiology-project-spec.md § 6 M7 | Escalation to see a doctor with the protocol sheet ready | covered | safety-guardrails/Escalation with a ready sheet | |
| docs/hackingbiology-project-spec.md § 6 M7 | Dose sanity check on three levels | covered | safety-guardrails/Dose sanity check | |
| docs/hackingbiology-project-spec.md § 6 M8 | Cohort aggregation, stratification, anonymised open data, researcher endpoint | covered | analytics-and-open-data/Cohort aggregation | |
| docs/hackingbiology-project-spec.md § 6 M8 | Release only data with LOINC, UCUM and provenance | covered | analytics-and-open-data/Aggregated research export uses only well-coded data | |
| docs/hackingbiology-project-spec.md § 6 M8 | Compare people on z-score against the origin lab range | covered | analytics-and-open-data/Compare on z-score, not raw value | |
| docs/hackingbiology-project-spec.md § 6 M9 | Genomics minimal: no raw processing, actionable pharmacogenomics only | covered | genomics/Actionable interpretation focus | |
| docs/hackingbiology-project-spec.md § 6 M10 | Wearables: file import first; aggregator decided later | added | biomarkers-and-labs/Import from wearable export files | Aggregator choice and price are not software behaviour |
| docs/hackingbiology-project-spec.md § 6 M13 | Daily check-off with dose and slot pre-resolved | covered | daily-log-and-adherence/Daily check-off with dose and slot pre-resolved | |
| docs/hackingbiology-project-spec.md § 6 M11 | Evidence claims extracted from literature | covered | evidence-layer/Structured evidence claims | |
| docs/hackingbiology-project-spec.md § 6 M11 | Confidence separate from effect size in native units | covered | evidence-layer/Confidence separate from effect size | |
| docs/hackingbiology-project-spec.md § 6 M11 | Directional evidence with counts of favourable, null, unfavourable studies | covered | evidence-layer/Directional evidence with study counts | |
| docs/hackingbiology-project-spec.md § 6 M11 | Alerts when evidence on a compound in use changes | covered | evidence-layer/Alerts on evidence change | |
| docs/hackingbiology-project-spec.md § 6 M11 | Outcome to Biomarker link | covered | evidence-layer/Outcome↔Biomarker link | |
| docs/hackingbiology-project-spec.md § 6 M12 | Claims Validator for a pasted product URL | added | evidence-layer/Claims Validator | |
| docs/hackingbiology-project-spec.md § 7 Dati, privacy | Explicit, granular, revocable consent to publish | added | accounts-and-profiles/Consent to public-by-default is explicit and revocable | Default-private per-item opt-in is superseded by public-by-default (accounts-and-profiles RESOLVED 2026-08-04); only one onboarding consent plus per-item withholding and revocation is added. Clones are out of reach, Q21 |
| docs/hackingbiology-project-spec.md § 7 Dati, privacy | Pseudonymised analytics | added | analytics-and-open-data/Analytics pipeline works on pseudonymised data | Default-private part superseded by the public-by-default decision; hosting jurisdiction is open in docs/foundation.md |
| docs/hackingbiology-project-spec.md § 7 Dati, privacy | Right to export and to erasure implemented | added | accounts-and-profiles/Personal data erasure | Export part is covered by "Full personal data export" |
| docs/hackingbiology-project-spec.md § 7 Dispositivo medico | Design registers and shows; no personalised dosing, diagnosis or therapy advice | added | safety-guardrails/Platform describes and never prescribes | Legal opinion before launch is a process step |
| docs/hackingbiology-project-spec.md § 7 Contenuto della comunità | Moderation, disclaimer and a policy on what is not publishable | added | community-and-social/Moderation policy for community-contributed protocols | Content of the policy open, Q23 |
| docs/hackingbiology-project-spec.md § 7 Open data | Aggregate release with minimum cohort thresholds against re-identification | covered | analytics-and-open-data/Aggregated research export uses only well-coded data | |
| docs/hackingbiology-project-spec.md § 7 Open data | Open licence, documented and versioned schema | added | analytics-and-open-data/Open licences declared on published data and content | |
| docs/hackingbiology-project-spec.md § 8 Analisi tecnica | Budget, PWA, monolith, no Kubernetes, forum not built | out-of-scope | — | Stack and budget constraints, tracked in docs/ROADMAP.md and docs/ecosystem/ |
| docs/hackingbiology-project-spec.md § 8.1 Stack proposto | Backend, DB, frontend, auth, community, dashboard, deploy choices | out-of-scope | — | Technology choices, not behaviour; the stack is frozen in docs/ROADMAP.md criterion 5 |
| docs/hackingbiology-project-spec.md § 8.2 Modello dati | FHIR as internal vocabulary, OMOP export | covered | data-standards-and-typing/Document each standard and its rationale | |
| docs/hackingbiology-project-spec.md § 8.2 Modello dati | OMOP CDM export for the research level | covered | analytics-and-open-data/Researcher access and OMOP export | |
| docs/hackingbiology-project-spec.md § 8.3 Vocabolari | LOINC, UCUM, RxNorm, ATC, PubChem, UNII on substances and analytes | covered | interventions-and-catalog/Substance catalog metadata | |
| docs/hackingbiology-project-spec.md § 8.3 Vocabolari | Interactions need own curation, LLM-assisted, with declared confidence | covered | safety-guardrails/Interaction and critical-value alerts | Licence choices for interaction sources are tracked in docs/ecosystem/ |
| docs/hackingbiology-project-spec.md § 8.3 Vocabolari | Pharmacogenomics and literature anchoring | covered | genomics/Actionable interpretation focus | |
| docs/hackingbiology-project-spec.md § 8.3 Vocabolari | Hallmark-of-aging mapping and seed from the existing workbook | out-of-scope | — | Seed content is a data task under M01; mapping of goals to hallmarks is covered in domain-model |
| docs/hackingbiology-project-spec.md § 8.4 Uso dell'LLM | Report parsing with learned deterministic templates, human confirmation | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | |
| docs/hackingbiology-project-spec.md § 8.4 Uso dell'LLM | Curation assistance in batch with mandatory human review | added | safety-guardrails/LLM-assisted curation requires human review | |
| docs/hackingbiology-project-spec.md § 8.4 Uso dell'LLM | Scheduling by constraint solver, not an LLM | covered | pills-management/Spacing and distance rules | Solver choice is an implementation detail |
| docs/hackingbiology-project-spec.md § 8.4 Uso dell'LLM | No LLM in the interactive path of each page | added | ai-uses-and-attribution/LLM usage is capped by a monthly credit allowance | |
| docs/hackingbiology-project-spec.md § 8.5 Wearable e genomica | Wearable file import now, aggregator later | added | biomarkers-and-labs/Import from wearable export files | |
| docs/hackingbiology-project-spec.md § 8.5 Wearable e genomica | No VCF processing; link out and import of interpreted reports | out-of-scope | — | Superseded: genomics spec accepts genomic data including gVCF |
| docs/hackingbiology-project-spec.md § 8.5bis Tetto a crediti | Monthly credit allowance for LLM analyses | added | ai-uses-and-attribution/LLM usage is capped by a monthly credit allowance | Amounts open, Q19 |
| docs/hackingbiology-project-spec.md § 8.5quater Due regole | LLM never writes constrained columns; out-of-enum marks ambiguous | covered | interventions-and-catalog/LLM never writes into constrained columns | |
| docs/hackingbiology-project-spec.md § 8.5quater Due regole | Entities resolve on codes with multilingual synonyms | covered | interventions-and-catalog/Substance resolution on codes, not English strings | |
| docs/hackingbiology-project-spec.md § 8.5quater Due regole | Input versus output diff after extraction | covered | interventions-and-catalog/Input↔output diff at end of extraction | |
| docs/hackingbiology-project-spec.md § 8.5quater Due regole | Long jobs queued, idempotent, resumable | covered | interventions-and-catalog/Long extraction jobs are queued and resumable | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | Four-step onboarding with persistent progress | covered | accounts-and-profiles/Onboarding "bring your reports" | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | Quick actions with title and subtitle | added | dashboards-and-doctor-view/Quick actions on the dashboard | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | Legend of recognised, not recognised, inferred | covered | biomarkers-and-labs/Human review before persistence | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | AI proposals as a block with Accept All and Reject All | added | ai-uses-and-attribution/AI proposals are offered as a block | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | Wizard with mandatory human review | covered | biomarkers-and-labs/Human review before persistence | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | Early partial result during long waits | added | interventions-and-catalog/Early partial result during long waits | |
| docs/hackingbiology-project-spec.md § 8.5ter Pattern di interfaccia | Empty state that teaches, not sells | covered | accounts-and-profiles/Onboarding "bring your reports" | |
| docs/hackingbiology-project-spec.md § 8.5quinquies Riuso di getbased | Reuse of the getbased catalog, pipeline, algorithms and charts | out-of-scope | — | Reuse decision recorded in docs/ecosystem/; analysed in part C (docs/getbased-reuse-analysis.md) |
| docs/hackingbiology-project-spec.md § 8.5quinquies Riuso di getbased | Published AI surfaces map | covered | ai-uses-and-attribution/Published AI surfaces map — "what is AI, what is NOT AI" | |
| docs/hackingbiology-project-spec.md § 8.5quinquies Riuso di getbased | Fingerprint-keyed cache of AI verdicts; grey means insufficient data | covered | biomarkers-and-labs/Deterministic pipeline with a hard boundary | |
| docs/hackingbiology-project-spec.md § 8.5quinquies Riuso di getbased | Read-only revocable agent token over MCP | covered | agent-access/Revocable read-only token | |
| docs/hackingbiology-project-spec.md § 8.5quinquies Riuso di getbased | Not taken: local-first as the only option | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | |
| docs/hackingbiology-project-spec.md § 8.5quinquies Riuso di getbased | Contribute the LOINC/UCUM mapping upstream | covered | ai-uses-and-attribution/Notify upstreams of their inclusion | Give-back proposals live in docs/ecosystem/GIVEBACK.md |
| docs/hackingbiology-project-spec.md § 8.6 Open source | AGPL-3.0 software; open licences for content and datasets | added | analytics-and-open-data/Open licences declared on published data and content | Licence choice open, Q16 |
| docs/hackingbiology-project-spec.md § 8.6 Open source | Public repo, public ADRs, open seed data | added | community-and-social/Specification is publicly browsable | |
| docs/hackingbiology-project-spec.md § 9 Roadmap | Phases 0 to 5 | out-of-scope | — | Planning artefact, tracked in docs/ROADMAP.md |
| docs/hackingbiology-project-spec.md § 9 Roadmap | Phase 5 distributed trials of pre-registered studies | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/hackingbiology-project-spec.md § 10 Rischi principali | Risk and mitigation table | out-of-scope | — | Each mitigation maps to a row above; the table is a planning artefact |
| docs/hackingbiology-project-spec.md § 11 Domande aperte | Thirty open questions (visibility, funding, Rapamycin News relation, scope, contacts) | out-of-scope | — | Open decisions, not behaviour; recorded in docs/QUESTIONS.md as they become blocking |
| docs/hackingbiology-project-spec.md § 11 Domande aperte | Creator coaching commission as funding candidate | out-of-scope | — | Funding model; the spec bars selling protocols, biomarkers, safety rules and data |
| docs/hackingbiology-project-spec.md § 12 Panorama competitivo | Competitor comparison and the strategic verdict | out-of-scope | — | Market analysis |
