# Spec discovery register — part C: conference deck

Source compared with `openspec/specs/**`: `docs/presentation/biohackit-deck.pdf` (21 slides, each read as an image). One row per feature claim; slides that carry only the speaker's biography, contacts or calls to action are `out-of-scope`.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/presentation/biohackit-deck.pdf § slide 1 | Title: open infrastructure for structured self-experimentation; AGPL-3.0, non-profit | added | community-and-social/Stewardship and mission lock are published | Licence of the code is fixed in docs/ROADMAP.md |
| docs/presentation/biohackit-deck.pdf § slide 2 | Speaker biography | out-of-scope | — | Not a product feature |
| docs/presentation/biohackit-deck.pdf § slide 3 | The gap: protocols live in spreadsheets; no shared representation layer | out-of-scope | — | Problem statement; the answer is the domain-model capability |
| docs/presentation/biohackit-deck.pdf § slide 4 | Compose a custom protocol from a database of interventions | covered | protocols/Create a protocol from scratch | |
| docs/presentation/biohackit-deck.pdf § slide 4 | Report health KPIs back; link to existing forum threads | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| docs/presentation/biohackit-deck.pdf § slide 5 | Three free-text spellings resolve to one coded entity (RxNorm, dose, interval) | covered | interventions-and-catalog/Substance resolution on codes, not English strings | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Document: substances, therapies, exercise, nutrition with dose, timing and cycle schemas | covered | domain-model/Intervention carries a cycle schema | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Copy any public protocol with one click | covered | community-and-social/One-click copyable catalog with an informed-decision panel | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Biomarkers with reference, optimal and safety ranges | covered | biomarkers-and-labs/Three ranges per analyte | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Biological clocks: PhenoAge, epigenetic, glycation | covered | dashboards-and-doctor-view/Biological clocks surfaced as a group | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Upload past lab reports and get history in graphs | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Open by default: publish protocol and outcomes | covered | accounts-and-profiles/Public-by-default profile | |
| docs/presentation/biohackit-deck.pdf § slide 6 | Quality from three layers: deterministic validation, community review, expert oversight | added | community-and-social/Three layers of quality assurance | Experts undefined, Q17 |
| docs/presentation/biohackit-deck.pdf § slide 6 | Built on the existing community, not a forum rebuilt | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| docs/presentation/biohackit-deck.pdf § slide 7 | Intervention versioned with every change | covered | protocols/Versioning and change tracking | |
| docs/presentation/biohackit-deck.pdf § slide 7 | Measurements coded with LOINC and UCUM, with lab, method and provenance | covered | biomarkers-and-labs/Coded analyte registry | |
| docs/presentation/biohackit-deck.pdf § slide 7 | Individual effect bound to the protocol version active at the time | covered | protocols/Versioning and change tracking | Scenario "Measurements bind to the version in effect" |
| docs/presentation/biohackit-deck.pdf § slide 7 | Cohort weighted by adherence and data completeness | covered | daily-log-and-adherence/Adherence qualifies data downstream | |
| docs/presentation/biohackit-deck.pdf § slide 7 | Evidence as an open dataset that researchers can interrogate | covered | analytics-and-open-data/Researcher access and OMOP export | |
| docs/presentation/biohackit-deck.pdf § slide 8 | Fork, commit with reason, release: copy, dose change with reason, protocol version | covered | protocols/Copy / fork an existing protocol | Reason on change: protocols/Versioning and change tracking |
| docs/presentation/biohackit-deck.pdf § slide 8 | Issues as a contested claim discussed in public | covered | community-and-social/Public claim review | |
| docs/presentation/biohackit-deck.pdf § slide 8 | Safety monitoring as continuous checks: baseline, inherited markers, overdue | covered | safety-guardrails/Safety markers inherited automatically | |
| docs/presentation/biohackit-deck.pdf § slide 8 | README as the doctor sheet | covered | dashboards-and-doctor-view/Doctor protocol sheet | |
| docs/presentation/biohackit-deck.pdf § slide 8 | Dataset as the open research output | covered | analytics-and-open-data/Full clonable public snapshot | |
| docs/presentation/biohackit-deck.pdf § slide 9 | Three audiences: experienced biohacker, beginner who copies, treating physician | out-of-scope | — | Personas; their needs map to rows below |
| docs/presentation/biohackit-deck.pdf § slide 9 | Physician gets a legible, complete view of what is taken and why | covered | dashboards-and-doctor-view/Doctor protocol sheet | |
| docs/presentation/biohackit-deck.pdf § slide 10 | Mandatory baseline and explicit risk acknowledgment before following | covered | safety-guardrails/Mandatory baseline AND risk acknowledgment before following a protocol | |
| docs/presentation/biohackit-deck.pdf § slide 10 | Safety markers inherited from every active compound | covered | safety-guardrails/Safety markers inherited automatically | |
| docs/presentation/biohackit-deck.pdf § slide 10 | Dose sanity check catches the extra zero | covered | safety-guardrails/Dose sanity check | |
| docs/presentation/biohackit-deck.pdf § slide 10 | Overdue is a safety gap, stated with days active and days overdue | covered | measurement-planning/Overdue is a safety signal | |
| docs/presentation/biohackit-deck.pdf § slide 11 | TestingProtocol, TreatmentPlan and Goal kept apart; goals map to hallmarks | covered | domain-model/Separation of the three protocol facets | |
| docs/presentation/biohackit-deck.pdf § slide 11 | Chain Substance, SafetyRule, Biomarker, Measurement, Dashboard | covered | domain-model/Safety, adherence and wellness as first-class entities | |
| docs/presentation/biohackit-deck.pdf § slide 12 | Upload past lab reports and get a free clinical baseline first | covered | accounts-and-profiles/Onboarding "bring your reports" | |
| docs/presentation/biohackit-deck.pdf § slide 12 | The LLM writes words, never numbers; narration generated once and cached | covered | biomarkers-and-labs/Deterministic pipeline with a hard boundary | |
| docs/presentation/biohackit-deck.pdf § slide 12 | LOINC, UCUM and method on every value; three ranges each with its source | covered | biomarkers-and-labs/Three ranges per analyte | |
| docs/presentation/biohackit-deck.pdf § slide 13 | AI reuses the AI4L framework for reviews | covered | ai-uses-and-attribution/AI4L as the framework for AI-generated reviews and evidence queries | |
| docs/presentation/biohackit-deck.pdf § slide 13 | Evipedia MCP as the evidence source | covered | evidence-layer/Evipedia as the primary evidence source | |
| docs/presentation/biohackit-deck.pdf § slide 13 | AI evaluates safety profiles and biomarkers; optimises scheduling for bioavailability | out-of-scope | — | AI scheduling conflicts with the constraint-solver rule (pills-management/Spacing and distance rules); safety and biomarker values are deterministic and AI only writes words about them; open, Q29 |
| docs/presentation/biohackit-deck.pdf § slide 13 | AI produces dosing algorithm proposals | out-of-scope | — | Conflicts with "Platform describes and never prescribes"; open, Q29 |
| docs/presentation/biohackit-deck.pdf § slide 14 | Scheduling for supplements, pharmaceuticals and interventions | covered | pills-management/Daily intake schedule across slots | |
| docs/presentation/biohackit-deck.pdf § slide 14 | Scheduling measurements: booking, appointments, recording data | added | measurement-planning/Measurement appointments are recorded | Laboratory booking not specified |
| docs/presentation/biohackit-deck.pdf § slide 14 | Book log for fasting adherence and nutrition exceptions | covered | nutrition-management/Log adherence to the nutrition plan | |
| docs/presentation/biohackit-deck.pdf § slide 14 | Supply organisation: when to buy what and from where | covered | procurement-and-inventory/Projected need from protocol | |
| docs/presentation/biohackit-deck.pdf § slide 15 | Distributed clinical trial is only a possible destination, with a qualification bar | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/presentation/biohackit-deck.pdf § slide 15 | Every number carries value, uncertainty, provenance and evidence level, or is not shown | covered | scientific-method-and-evidence/Evidence confidence on every displayed number | |
| docs/presentation/biohackit-deck.pdf § slide 15 | Observed, never caused | covered | scientific-method-and-evidence/Observed, never caused | |
| docs/presentation/biohackit-deck.pdf § slide 15 | Negative results are welcome | covered | scientific-method-and-evidence/Negative results are first-class | |
| docs/presentation/biohackit-deck.pdf § slide 15 | Clock Foundation as a similar, non-open initiative | covered | related-initiatives/Maintain a register of similar initiatives | |
| docs/presentation/biohackit-deck.pdf § slide 16 | Everything public released as a clonable, coded and linked snapshot that can seed an instance | added | analytics-and-open-data/Public data is published as linked data | Serialisation open, Q24 |
| docs/presentation/biohackit-deck.pdf § slide 16 | Original measurement documents uploaded and public so the extraction can be redone | covered | biomarkers-and-labs/Original report file retained and public raw | |
| docs/presentation/biohackit-deck.pdf § slide 16 | HL7 FHIR internally, OMOP for research export, LOINC/UCUM, RxNorm | covered | data-standards-and-typing/Document each standard and its rationale | OMOP export: analytics-and-open-data/Researcher access and OMOP export |
| docs/presentation/biohackit-deck.pdf § slide 17 | Specification browsable publicly and open to community review | added | community-and-social/Specification is publicly browsable | |
| docs/presentation/biohackit-deck.pdf § slide 17 | Count of capabilities and requirements | out-of-scope | — | A figure that changes with every merge; the matrix in docs/TRACEABILITY.md is authoritative |
| docs/presentation/biohackit-deck.pdf § slide 17 | Six capability areas: protocols, blood layer, safety, community, open data, AI and evidence | covered | domain-model/Protocol as public composite | Area names only; each is specified in its own capability |
| docs/presentation/biohackit-deck.pdf § slide 18 | Roadmap: foundations, MVP, adherence, public protocols, open data, trials | out-of-scope | — | Planning, tracked in docs/ROADMAP.md |
| docs/presentation/biohackit-deck.pdf § slide 18 | Daily log in thirty seconds | covered | daily-log-and-adherence/Daily check-off with dose and slot pre-resolved | |
| docs/presentation/biohackit-deck.pdf § slide 18 | Next: procurement, advanced nutrition, therapeutics scheduling, genomics, MCP agent access | covered | agent-access/Revocable read-only token | The other items have their own capabilities (procurement-and-inventory, nutrition-management, therapeutics-management, genomics) |
| docs/presentation/biohackit-deck.pdf § slide 19 | Five contributor roles and calls to join | out-of-scope | — | Recruitment, not software |
| docs/presentation/biohackit-deck.pdf § slide 20 | Contacts, QR codes and references | out-of-scope | — | Contact details are not software behaviour |
| docs/presentation/biohackit-deck.pdf § slide 21 | Fork it, self-host it, own your data | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | |
| docs/presentation/biohackit-deck.pdf § slide 21 | Own your data: full export | added | accounts-and-profiles/Full personal data export | |
