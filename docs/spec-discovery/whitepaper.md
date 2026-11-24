# Spec discovery register — part A: whitepaper and foundation

Sources compared with `openspec/specs/**`: `whitepaper/whitepaper.src.html` (all sections) and `docs/foundation.md` (all sections). Part B (hackingbiology project spec, get-based reuse analysis, presentation) follows in a later register.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour (vision, organisation, planning, contact details); the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| whitepaper/whitepaper.src.html § Cover | Tagline, title, forum and version line | out-of-scope | — | Branding and event details, not product behaviour |
| whitepaper/whitepaper.src.html § Abstract | A person documents a protocol in a standard machine-readable form | covered | protocols/Create a protocol from scratch | |
| whitepaper/whitepaper.src.html § Abstract | Protocols and outcomes are shared in the open | covered | protocols/Publish with per-facet visibility | |
| whitepaper/whitepaper.src.html § Abstract | Safety is built into copying a protocol | covered | safety-guardrails/Mandatory baseline AND risk acknowledgment before following a protocol | |
| whitepaper/whitepaper.src.html § Abstract | Free, open-source software anyone can run | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | |
| whitepaper/whitepaper.src.html § Abstract | The full functional specification is public | added | community-and-social/Specification is publicly browsable | Also in section 12 and foundation section 4 |
| whitepaper/whitepaper.src.html § 01 The problem | Intervention has outrun measurement; experiments evaporate | out-of-scope | — | Problem statement and motivation |
| whitepaper/whitepaper.src.html § 01 The problem | A shared representation layer makes individual records comparable | covered | data-standards-and-typing/Coding plus provenance make aggregation valid | |
| whitepaper/whitepaper.src.html § 02 The ethical core | The beginner who copies gets safety markers they would not choose | covered | safety-guardrails/Safety markers inherited automatically | |
| whitepaper/whitepaper.src.html § 02 The ethical core | The treating physician gets a legible view of what is taken and why | covered | dashboards-and-doctor-view/Doctor protocol sheet | |
| whitepaper/whitepaper.src.html § 02 The ethical core | The experienced biohacker's results are measured, not claimed | covered | domain-model/Measurement provenance | |
| whitepaper/whitepaper.src.html § 03 The core idea | Three spellings of one regimen resolve to one entity | covered | interventions-and-catalog/Substance resolution on codes, not English strings | |
| whitepaper/whitepaper.src.html § 03 The core idea | Substances keyed to RxNorm, ATC, PubChem and UNII | covered | interventions-and-catalog/Substance catalog metadata | |
| whitepaper/whitepaper.src.html § 03 The core idea | Dose in defined units with a real cycle schema | covered | domain-model/Intervention carries a cycle schema | |
| whitepaper/whitepaper.src.html § 03 The core idea | Biomarkers coded to LOINC and UCUM, lab and method carried with each value | covered | biomarkers-and-labs/Coded analyte registry | |
| whitepaper/whitepaper.src.html § 04 From act to evidence | Interventions versioned with every change | covered | protocols/Versioning and change tracking | |
| whitepaper/whitepaper.src.html § 04 From act to evidence | Measurements carry lab, method and provenance | covered | domain-model/Measurement provenance | |
| whitepaper/whitepaper.src.html § 04 From act to evidence | Individual before/after bound to the active protocol version | covered | studies-nof1/Pre/post read-out | |
| whitepaper/whitepaper.src.html § 04 From act to evidence | Cohort of people on the same protocol, weighted by adherence and completeness | covered | analytics-and-open-data/Cohort aggregation | |
| whitepaper/whitepaper.src.html § 04 From act to evidence | Evidence is an open dataset anyone can interrogate | covered | analytics-and-open-data/Full clonable public snapshot | |
| whitepaper/whitepaper.src.html § 05 What it does | Substances, therapies, exercise and nutrition documented with dose and timing | covered | protocols/Create a protocol from scratch | |
| whitepaper/whitepaper.src.html § 05 What it does | Copy any public protocol with one click | covered | protocols/Copy / fork an existing protocol | |
| whitepaper/whitepaper.src.html § 05 What it does | Reference, optimal and safety ranges per biomarker | covered | biomarkers-and-labs/Three ranges per analyte | |
| whitepaper/whitepaper.src.html § 05 What it does | Biological clocks such as PhenoAge, epigenetic and glycation | covered | biomarkers-and-labs/Biological clocks are first-class biomarkers | |
| whitepaper/whitepaper.src.html § 05 What it does | Upload past lab reports and see the history in graphs | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | |
| whitepaper/whitepaper.src.html § 05 What it does | Publish protocol and outcomes, open by default | covered | protocols/Publish with per-facet visibility | |
| whitepaper/whitepaper.src.html § 05 What it does | Quality from deterministic validation, community review and expert oversight | added | community-and-social/Three layers of quality assurance | |
| whitepaper/whitepaper.src.html § 05 What it does | Follow and copy people whose public biomarkers show results | covered | community-and-social/Follow and copy | |
| whitepaper/whitepaper.src.html § 05 What it does | Community features attach to Rapamycin News | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| whitepaper/whitepaper.src.html § 06 Architecture | Protocol changes are versioned like commits, with a reason | covered | protocols/Versioning and change tracking | |
| whitepaper/whitepaper.src.html § 06 Architecture | A contested claim is discussed in public (issues) | covered | community-and-social/Public claim review | |
| whitepaper/whitepaper.src.html § 06 Architecture | TestingProtocol, TreatmentPlan and Goal kept separate; goals map to Hallmarks of Aging | covered | domain-model/Separation of the three protocol facets | |
| whitepaper/whitepaper.src.html § 06 Architecture | Substance, SafetyRule, Biomarker, Measurement and Dashboard as one structure | covered | domain-model/Safety, adherence and wellness as first-class entities | |
| whitepaper/whitepaper.src.html § 06 Architecture | FHIR, OMOP, LOINC, UCUM and substance vocabularies documented | covered | data-standards-and-typing/Document each standard and its rationale | |
| whitepaper/whitepaper.src.html § 06 Architecture | Evidence content follows Evipedia | covered | ai-uses-and-attribution/Integrate the Evipedia knowledgebase, attributed | |
| whitepaper/whitepaper.src.html § 06 Architecture | AI-generated review text goes through AI4L | covered | ai-uses-and-attribution/AI4L as the framework for AI-generated reviews and evidence queries | |
| whitepaper/whitepaper.src.html § 06 Architecture | Published map of where AI is and is not used | covered | ai-uses-and-attribution/Published AI surfaces map — "what is AI, what is NOT AI" | |
| whitepaper/whitepaper.src.html § 06 Architecture | The model writes words, never numbers | covered | interventions-and-catalog/LLM never writes into constrained columns | |
| whitepaper/whitepaper.src.html § 07 Harm reduction | Mandatory baseline and risk acknowledgement before following | covered | safety-guardrails/Mandatory baseline AND risk acknowledgment before following a protocol | |
| whitepaper/whitepaper.src.html § 07 Harm reduction | Safety markers inherited from every active compound | covered | safety-guardrails/Safety markers inherited automatically | |
| whitepaper/whitepaper.src.html § 07 Harm reduction | Dose plausibility check catches the extra zero | covered | safety-guardrails/Dose sanity check | |
| whitepaper/whitepaper.src.html § 07 Harm reduction | An overdue test is surfaced as a safety gap | covered | measurement-planning/Overdue is a safety signal | |
| whitepaper/whitepaper.src.html § 07 Harm reduction | The platform describes and never prescribes | added | safety-guardrails/Platform describes and never prescribes | Also foundation sections 3 and 7 |
| whitepaper/whitepaper.src.html § 07 Harm reduction | Research-grade and animal-derived doses are marked and gated | covered | safety-guardrails/Heightened acknowledgment for research-level or animal-derived dosing | |
| whitepaper/whitepaper.src.html § 07 Harm reduction | Informed-decision panel before copying; nothing hidden | covered | community-and-social/One-click copyable catalog with an informed-decision panel | |
| whitepaper/whitepaper.src.html § 08 The minimum viable product | Upload existing lab reports and get a biomarker history | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | |
| whitepaper/whitepaper.src.html § 08 The minimum viable product | Extraction, mapping and thresholds are deterministic; model only narrates, once, cached | covered | biomarkers-and-labs/Deterministic pipeline with a hard boundary | |
| whitepaper/whitepaper.src.html § 08 The minimum viable product | Every value carries LOINC, UCUM and method; three ranges each with a source | covered | biomarkers-and-labs/Three ranges per analyte | |
| whitepaper/whitepaper.src.html § 08 The minimum viable product | Useful to a single user with no network | covered | accounts-and-profiles/Onboarding "bring your reports" | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | Limits of self-managed data stated up front | covered | scientific-method-and-evidence/Publicly declared nature and limits | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | Every number carries value, uncertainty, provenance and evidence level | covered | scientific-method-and-evidence/Evidence confidence on every displayed number | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | Findings are phrased as observed, never caused | covered | scientific-method-and-evidence/Observed, never caused | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | Negative results are a first-class contribution | covered | scientific-method-and-evidence/Negative results are first-class | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | Named threats to validity | covered | statistical-methodology/Named threats to validity | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | Under-powered comparisons report not determinable | covered | statistical-methodology/Under-powered comparisons are declared, not hidden | |
| whitepaper/whitepaper.src.html § 09 Intellectual honesty | A study earns the word trial by meeting a published bar | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| whitepaper/whitepaper.src.html § 10 What is unique | Literature prediction and observed cohort on one axis | covered | dashboards-and-doctor-view/Double-column literature vs observed | |
| whitepaper/whitepaper.src.html § 11 Openness | Clonable open-data snapshot sufficient to seed an instance | covered | analytics-and-open-data/Full clonable public snapshot | |
| whitepaper/whitepaper.src.html § 11 Openness | Genomic data and lab originals public behind a heightened consent gate | covered | genomics/Public by default with heightened consent (incl. gVCF) | |
| whitepaper/whitepaper.src.html § 11 Openness | Everything public is open and linked data, coded and linked, sufficient to seed an instance | added | analytics-and-open-data/Public data is published as linked data | Serialisation open, Q24 |
| whitepaper/whitepaper.src.html § 11 Openness | Research API returns de-identified cohort data with caveats for an intervention and biomarker | added | analytics-and-open-data/Research API answers intervention-by-biomarker queries | |
| whitepaper/whitepaper.src.html § 11 Openness | Raw publication put to a community vote when the public beta opens | covered | analytics-and-open-data/Raw-data publication validated by a community poll at BETA | |
| whitepaper/whitepaper.src.html § 11 Openness | OMOP research export | covered | analytics-and-open-data/Researcher access and OMOP export | |
| whitepaper/whitepaper.src.html § 11 Openness | No aim to publish papers | out-of-scope | — | Organisational stance, not software behaviour |
| whitepaper/whitepaper.src.html § 12 Specification and roadmap | Specification published and browsable | added | community-and-social/Specification is publicly browsable | |
| whitepaper/whitepaper.src.html § 12 Specification and roadmap | Staged roadmap and deferred modules | out-of-scope | — | Planning artefact, tracked in docs/ROADMAP.md |
| whitepaper/whitepaper.src.html § 12 Specification and roadmap | Daily log is a quick daily check-off | covered | daily-log-and-adherence/Daily check-off with dose and slot pre-resolved | |
| whitepaper/whitepaper.src.html § 12 Specification and roadmap | Pre-registered N-of-1 studies | covered | studies-nof1/Study with pre-declared endpoints | |
| whitepaper/whitepaper.src.html § 13 Governance and sustainability | Foundation owns software, brand and copyright; cannot relicense away from AGPL-3.0 | added | community-and-social/Stewardship and mission lock are published | |
| whitepaper/whitepaper.src.html § 13 Governance and sustainability | Board mix, grant funding, aligned equity | out-of-scope | — | Organisational and funding matters, not software behaviour |
| whitepaper/whitepaper.src.html § 13 Governance and sustainability | Founder story | out-of-scope | — | Narrative |
| whitepaper/whitepaper.src.html § 14 Participate | Roles open to contributors, contact channels, colophon | out-of-scope | — | Recruitment and contact details; the colophon only states that the specification prevails |
| docs/foundation.md § 1 Why two names, one mission | Software and steward are separate and the steward is the guarantor | added | community-and-social/Stewardship and mission lock are published | |
| docs/foundation.md § 2 Incorporation and ownership | Incorporation seat and ownership of brand and copyright | out-of-scope | — | Legal structure; the user-visible part is the published stewardship statement |
| docs/foundation.md § 2 Incorporation and ownership | Data-protection duties met at the hosting layer, apart from the seat | out-of-scope | — | Hosting jurisdiction is still open in the source; no behaviour is stated |
| docs/foundation.md § 3 What the Foundation guarantees | Never commercial, never a walled garden | added | community-and-social/Knowledge is not for sale | |
| docs/foundation.md § 3 What the Foundation guarantees | Open code and open data, anyone can run an instance | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | |
| docs/foundation.md § 3 What the Foundation guarantees | Public dataset and content carry open licences | added | analytics-and-open-data/Open licences declared on published data and content | |
| docs/foundation.md § 3 What the Foundation guarantees | Harm reduction first; describes, never prescribes | added | safety-guardrails/Platform describes and never prescribes | |
| docs/foundation.md § 3 What the Foundation guarantees | Where AI is and is not used is published | covered | ai-uses-and-attribution/Published AI surfaces map — "what is AI, what is NOT AI" | |
| docs/foundation.md § 3 What the Foundation guarantees | Every reused upstream is attributed and notified | covered | ai-uses-and-attribution/Notify upstreams of their inclusion | |
| docs/foundation.md § 3 What the Foundation guarantees | Full export always; the person owns the record | added | accounts-and-profiles/Full personal data export | |
| docs/foundation.md § 4 Governance | Foundation holds domain, trademark and canonical instance | out-of-scope | — | Legal and organisational |
| docs/foundation.md § 4 Governance | Board of biohackers and software hackers | out-of-scope | — | Organisational |
| docs/foundation.md § 4 Governance | ADRs and specs public from day one | added | community-and-social/Specification is publicly browsable | |
| docs/foundation.md § 4 Governance | Community governance attaches to Rapamycin News | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| docs/foundation.md § 4 Governance | Contested claims are public | covered | community-and-social/Public claim review | |
| docs/foundation.md § 4 Governance | Study proposals are discussed in public | covered | community-and-social/Host study proposals for comment and consensus | |
| docs/foundation.md § 5 Sustainability | Funding by public grants and aligned startup equity | out-of-scope | — | Funding model |
| docs/foundation.md § 5 Sustainability | No supplier can buy influence over which protocols emerge | added | community-and-social/Knowledge is not for sale | |
| docs/foundation.md § 6 Public presence | biohack.it product site and hackingbiology.com organisation site; About links to the Foundation | added | community-and-social/Stewardship and mission lock are published | |
| docs/foundation.md § 7 Risks and mitigations | Mitigations: charter, open licences, mixed board, grants | out-of-scope | — | Organisational mitigations |
| docs/foundation.md § 7 Risks and mitigations | Community can always run its own instance | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | |
| docs/foundation.md § 7 Risks and mitigations | Descriptive-not-prescriptive posture by design; legal review before launch | added | safety-guardrails/Platform describes and never prescribes | The legal review itself is a process step, not software |
| docs/foundation.md § Resolved and still open | Decisions taken and open items (seat, board, grants, hosting jurisdiction) | out-of-scope | — | Status log of organisational decisions |
