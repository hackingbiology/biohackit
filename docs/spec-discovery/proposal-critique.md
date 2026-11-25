# Spec discovery register — part D2b1: proposal critique

Source compared with `openspec/specs/**`: `docs/proposal-critique.html` (7 `<h2>` sections). One row per feature claim about biohack.it. Site-copy rewrites, the critic's opinions, roadmap ordering and success targets are `out-of-scope` unless they describe a product behaviour. Questions for the owner are in `docs/QUESTIONS.md`, not requirements.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/proposal-critique.html § My verdict, in one paragraph | Keep distributed trials as the destination and earn the word by defining what qualifies | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/proposal-critique.html § My verdict, in one paragraph | Raise rigour around statistics, evidence governance and epistemic phrasing | covered | statistical-methodology/Named threats to validity | |
| docs/proposal-critique.html § My verdict, in one paragraph | Verdict on the critique and on the homepage undersell | out-of-scope | — | Opinion about an outside review; not software behaviour |
| docs/proposal-critique.html § The ten criticisms | C1 Homepage explains the project within 30 seconds | out-of-scope | — | Site copy and layout; the owner decides, see Q37 |
| docs/proposal-critique.html § The ten criticisms | C2 Publish the bar a study must clear to be called a distributed trial (pre-registered endpoint, shared protocol version, declared timepoints, adherence floor, minimum cohort, published analysis plan) | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/proposal-critique.html § The ten criticisms | C2 A pile of N-of-1 is not a trial; the platform states what it can and cannot support | covered | scientific-method-and-evidence/Publicly declared nature and limits | |
| docs/proposal-critique.html § The ten criticisms | C3 Confounding, regression to the mean, multiplicity, healthy-user and survivor bias named as a structural component | covered | statistical-methodology/Named threats to validity | |
| docs/proposal-critique.html § The ten criticisms | C3 Regression to the mean and multiplicity handled explicitly | covered | statistical-methodology/Regression to the mean and multiplicity are handled explicitly | |
| docs/proposal-critique.html § The ten criticisms | C3 Missingness declared | covered | statistical-methodology/Missing data is declared, never imputed silently | |
| docs/proposal-critique.html § The ten criticisms | C3 Intra-individual variability, effect size and uncertainty | covered | statistical-methodology/Uncertainty and effect size are mandatory | |
| docs/proposal-critique.html § The ten criticisms | C4 Scientific Advisory Board in the Foundation governance | out-of-scope | — | Governance and people decision; the document itself says it is not a spec problem; see Q37 |
| docs/proposal-critique.html § The ten criticisms | C5 One advisory board with a named clinical-safety seat | out-of-scope | — | Governance and people decision; see Q37 |
| docs/proposal-critique.html § The ten criticisms | C6 Quality stated as deterministic validation, community review and expert oversight | added | community-and-social/Three layers of quality assurance | |
| docs/proposal-critique.html § The ten criticisms | C7 Public by default including genomics, behind a heightened consent gate | covered | genomics/Public by default with heightened consent (incl. gVCF) | |
| docs/proposal-critique.html § The ten criticisms | C7 Community poll on Rapamycin News at public BETA | covered | analytics-and-open-data/Raw-data publication validated by a community poll at BETA | |
| docs/proposal-critique.html § The ten criticisms | C7 Say publicly why maximal openness was chosen and how someone opts out | added | analytics-and-open-data/Public-by-default reasoning and opt-out are stated publicly | |
| docs/proposal-critique.html § The ten criticisms | C8 Every optimal range inspectable down to source, population, endpoint, evidence grade, last reviewed | covered | biomarkers-and-labs/Optimal-range governance | |
| docs/proposal-critique.html § The ten criticisms | C9 Keep the specification whole, ring-fence what is built | out-of-scope | — | Build-ordering decision, not product behaviour; see the MVP rows |
| docs/proposal-critique.html § The ten criticisms | C10 Results matter more than more features | out-of-scope | — | Opinion about priorities |
| docs/proposal-critique.html § The twelve pieces of advice | A1 Category line: open infrastructure for structured human self-experimentation | out-of-scope | — | Site copy |
| docs/proposal-critique.html § The twelve pieces of advice | A2 Pipeline diagram on the homepage | out-of-scope | — | Site layout; see Q37 |
| docs/proposal-critique.html § The twelve pieces of advice | A3 Public Scientific Method page: what can and cannot be inferred | covered | scientific-method-and-evidence/Publicly declared nature and limits | |
| docs/proposal-critique.html § The twelve pieces of advice | A4 One advisory board with scientific and clinical-safety seats | out-of-scope | — | Governance and people decision; see Q37 |
| docs/proposal-critique.html § The twelve pieces of advice | A5 Evidence Constitution: RCT > observational > N-of-1 > anecdote | covered | scientific-method-and-evidence/Evidence hierarchy | |
| docs/proposal-critique.html § The twelve pieces of advice | A6 MVP of Protocol, Blood Layer, Safety and Doctor Sheet | covered | dashboards-and-doctor-view/Doctor protocol sheet | Each of the four is an existing capability; the ordering itself is out-of-scope |
| docs/proposal-critique.html § The twelve pieces of advice | A7 Defer procurement, advanced nutrition, social | out-of-scope | — | Roadmap ordering; the requirements stay in the specification |
| docs/proposal-critique.html § The twelve pieces of advice | A8 Three flagship protocols as demonstrations | covered | protocols/Curated and community origin | Curated seed at T0; the three topics are the proposal's, see Q37 |
| docs/proposal-critique.html § The twelve pieces of advice | A9 Evidence Confidence on every number: value, uncertainty, provenance, evidence level | covered | scientific-method-and-evidence/Evidence confidence on every displayed number | |
| docs/proposal-critique.html § The twelve pieces of advice | A10 Research API returning de-identified, methodologically annotated data for an intervention and a biomarker | added | analytics-and-open-data/Research API answers intervention-by-biomarker queries | |
| docs/proposal-critique.html § The twelve pieces of advice | A11 Publish an early methods paper | out-of-scope | — | Project milestone, not software behaviour |
| docs/proposal-critique.html § The twelve pieces of advice | A12 Negative results as a cultural value | covered | scientific-method-and-evidence/Negative results are first-class | |
| docs/proposal-critique.html § What I would rewrite on the site | Hero copy and category line | out-of-scope | — | Site copy; approval is a question to the owner, Q37 |
| docs/proposal-critique.html § What I would rewrite on the site | Pipeline graphic Intervention to Evidence | out-of-scope | — | Site layout |
| docs/proposal-critique.html § What I would rewrite on the site | Free-text dose spellings resolve to one computable entity (code, dose, interval, pulsed) linked to biomarkers | covered | interventions-and-catalog/Substance resolution on codes, not English strings | Pulsed cycle: domain-model/Intervention carries a cycle schema |
| docs/proposal-critique.html § What I would rewrite on the site | GitHub analogy table (repository, fork, commit, release, CI, issues, telemetry, README, dataset) | out-of-scope | — | Site and slide metaphor; the underlying fork and version behaviour is covered by protocols/Copy / fork an existing protocol |
| docs/proposal-critique.html § What I would rewrite on the site | What this can and cannot tell you block | covered | scientific-method-and-evidence/Publicly declared nature and limits | |
| docs/proposal-critique.html § What I would rewrite on the site | Negative results welcome block | covered | scientific-method-and-evidence/Negative results are first-class | |
| docs/proposal-critique.html § What I would rewrite on the site | Retire "the community is the quality control" for the three-layer wording | added | community-and-social/Three layers of quality assurance | |
| docs/proposal-critique.html § What I would add to the specification | statistical-methodology: named threats to validity with how each is surfaced or mitigated | covered | statistical-methodology/Named threats to validity | |
| docs/proposal-critique.html § What I would add to the specification | statistical-methodology: intra-individual variability and assay drift, lab or method change flagged | covered | statistical-methodology/Separate biological change from analytical noise | |
| docs/proposal-critique.html § What I would add to the specification | statistical-methodology: no effect without an interval, no trend from two points | covered | statistical-methodology/Uncertainty and effect size are mandatory | |
| docs/proposal-critique.html § What I would add to the specification | statistical-methodology: phrasing discipline, never "X causes Y", machine-enforced | covered | scientific-method-and-evidence/Observed, never caused | |
| docs/proposal-critique.html § What I would add to the specification | scientific-method-and-evidence: evidence hierarchy | covered | scientific-method-and-evidence/Evidence hierarchy | |
| docs/proposal-critique.html § What I would add to the specification | scientific-method-and-evidence: what qualifies as a distributed trial | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/proposal-critique.html § What I would add to the specification | scientific-method-and-evidence: negative results first-class | covered | scientific-method-and-evidence/Negative results are first-class | |
| docs/proposal-critique.html § What I would add to the specification | Blood Layer optimal-range governance | covered | biomarkers-and-labs/Optimal-range governance | |
| docs/proposal-critique.html § What I would add to the specification | Explicit, documented Research API with de-identified, methodologically annotated responses | added | analytics-and-open-data/Research API answers intervention-by-biomarker queries | |
| docs/proposal-critique.html § What I would add to the specification | Cross-cutting Evidence Confidence on every displayed number | covered | scientific-method-and-evidence/Evidence confidence on every displayed number | |
| docs/proposal-critique.html § MVP first | Document a protocol: create, copy, import a running regimen, versioned | covered | protocols/Import an already-running protocol (experienced baseline) | Also protocols/Create a protocol from scratch, Copy / fork an existing protocol, Versioning and change tracking |
| docs/proposal-critique.html § MVP first | Upload past lab reports and see history in graphs | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | |
| docs/proposal-critique.html § MVP first | Inherit safety markers with a mandatory baseline | covered | safety-guardrails/Safety markers inherited automatically | Baseline: safety-guardrails/Mandatory baseline AND risk acknowledgment before following a protocol |
| docs/proposal-critique.html § MVP first | Hand the doctor a legible sheet | covered | dashboards-and-doctor-view/Doctor protocol sheet | |
| docs/proposal-critique.html § MVP first | Fast-follow Daily Log and adherence, thirty seconds a day | covered | daily-log-and-adherence/Daily check-off with dose and slot pre-resolved | |
| docs/proposal-critique.html § MVP first | Adherence makes an N-of-1 interpretable | covered | daily-log-and-adherence/Adherence qualifies data downstream | |
| docs/proposal-critique.html § MVP first | Public protocols, follow and copy, N-of-1 studies attached to Rapamycin News | covered | community-and-social/Follow and copy | N-of-1: studies-nof1/Study with pre-declared endpoints |
| docs/proposal-critique.html § MVP first | Cohorts, Research API, first open dataset | covered | analytics-and-open-data/Cohort aggregation | Dataset: analytics-and-open-data/Full clonable public snapshot |
| docs/proposal-critique.html § MVP first | Distributed trials as the destination, pre-registered and endpoint-declared | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/proposal-critique.html § MVP first | Success targets (active users, imported results, published protocols, cohort comparisons, dataset, preprint) | out-of-scope | — | Project targets measured outside the software; not a behaviour |
| docs/proposal-critique.html § MVP first | Deferred: procurement, advanced nutrition, therapeutics scheduling, genomics beyond import, agent access | out-of-scope | — | Roadmap ordering; the requirements remain in the specification |
| docs/proposal-critique.html § What I need from you | Confirm: keep the word distributed trials and publish the bar | out-of-scope | — | Question to the owner, recorded in QUESTIONS.md Q37 with a default |
| docs/proposal-critique.html § What I need from you | Approve the hero copy | out-of-scope | — | Question to the owner, Q37 |
| docs/proposal-critique.html § What I need from you | GitHub table on site, slide or both | out-of-scope | — | Question to the owner, Q37 |
| docs/proposal-critique.html § What I need from you | Keep genomics public by default and publish the reasoning and the BETA poll | added | analytics-and-open-data/Public-by-default reasoning and opt-out are stated publicly | The decision is Q37; publishing the reasoning is the added requirement |
| docs/proposal-critique.html § What I need from you | Advisory board composition and names | out-of-scope | — | Question to the owner, Q37 |
| docs/proposal-critique.html § What I need from you | Confirm the MVP ring-fence of four | out-of-scope | — | Question to the owner, Q37 |
