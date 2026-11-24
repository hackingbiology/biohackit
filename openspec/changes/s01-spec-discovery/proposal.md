# Change: s01 — Spec discovery

## Why
The whitepaper, the Foundation evaluation and the project spec promise features that no requirement in `openspec/specs/**` states. The traceability matrix only measures what is specified, so unspecified promises are invisible to the definition of done.

## What changes
Part A compares `whitepaper/whitepaper.src.html` and `docs/foundation.md` with the existing specs. The result is the register `docs/spec-discovery/whitepaper.md`: every feature is `covered` by an existing requirement, `added` here, or `out-of-scope` with a reason. Part A added eight requirements in four capabilities; open details are in `docs/QUESTIONS.md` (Q16, Q17).

Part B compares `docs/hackingbiology-project-spec.md` and records the result in `docs/spec-discovery/project-spec.md`. It adds fourteen requirements, in eight further capabilities and three already touched, with open details in Q18–Q23. It also closes a part A gap: the whitepaper § 11 "open and linked data" promise becomes `analytics-and-open-data/Public data is published as linked data` (Q24).

Part C compares `docs/getbased-reuse-analysis.md` and `docs/presentation/biohackit-deck.pdf` (registers `docs/spec-discovery/getbased-reuse.md` and `docs/spec-discovery/presentation.md`). It adds fourteen requirements: calculated markers, Bortz clock, unit conversion, cycle-phase ranges, import rollback and a parser benchmark (`biomarkers-and-labs`); trend alerts, the intervention overlay and the protected sharing link (`dashboards-and-doctor-view`); lifestyle context cards (`accounts-and-profiles`); the AI verdict shape and the provider choice (`ai-uses-and-attribution`); measurement appointments (`measurement-planning`); consumer DNA files (`genomics`, a new capability in this change). Open details are Q25–Q30. It also fixes a part B finding: the linked-data scenario now links public entities only. Part D (`docs/slides/`, `docs/specs/`, `docs/analysis/`, remaining `docs/*.md`) will append here.

## Impact
- New requirements in `safety-guardrails`, `accounts-and-profiles`, `community-and-social`, `analytics-and-open-data`, `daily-log-and-adherence`, `biomarkers-and-labs`, `procurement-and-inventory`, `evidence-layer`, `ai-uses-and-attribution`, `measurement-planning`, `interventions-and-catalog`, `dashboards-and-doctor-view`, and `genomics`.
- No code changes; implementation tasks are listed in `tasks.md`.
