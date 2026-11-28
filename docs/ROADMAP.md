# biohack.it — Autonomous build roadmap

Mandate (Fabio, 2026-11-09): build the whole platform end-to-end, autonomously, for weeks,
until *everything* is done; then Fabio starts using it as first user.

## Non-negotiable criteria (frozen — never relax)
1. **OpenSpec first.** Every module: write/refresh the spec as an OpenSpec change
   (`openspec/changes/<id>/{proposal.md,tasks.md,specs/...}`) BEFORE code. Code follows spec;
   any deviation updates the spec in the same commit.
2. **Very high scientific quality of the database.** Standards-coded (LOINC+UCUM, RxNorm/ATC/
   PubChem/UNII, SNOMED where licensed, FHIR vocab, OMOP export), provenance on every value
   (source, method, device, timestamp, unit-as-reported vs normalized), reference ranges with
   source + population, evidence graded. No invented data: every seed row cites a source.
3. **Very high end-user accessibility.** Plain language first, WCAG 2.2 AA, mobile-first PWA,
   i18n-ready (EN first, IT/ZH next), every number explained in one sentence.
4. **AI4L everywhere it fits — words, never numbers.** AI4L audit-based prompting for all
   narration, reviews, explanations, summaries; deterministic code for every number,
   threshold, mapping and statistic. Every AI output labelled + cached + listed in the AI
   surfaces map (`ai-uses-and-attribution`).
5. Stack (project.md): Django + PostgreSQL/TimescaleDB · Next.js PWA · FHIR/OMOP · AGPL-3.0.
6. Tests for every requirement scenario (SHALL ⇒ test). CI green before moving on.

## Module order (dependency-driven)
| # | Module | Capabilities | Status |
|---|---|---|---|
| 0 | Foundations: repo layout, Django+PG+Next skeleton, CI, auth | accounts-and-profiles, domain-model, data-standards-and-typing | todo |
| 1 | Terminology & reference data (LOINC/UCUM/RxNorm…) with provenance | data-standards-and-typing, biomarkers-and-labs | todo |
| 2 | Blood Layer: lab ingestion (CSV/PDF/manual), normalization, ranges | biomarkers-and-labs | spec written |
| 3 | Interventions catalog + protocols | interventions-and-catalog, protocols | spec written |
| 4 | Pills / therapeutics / nutrition / exercise | pills-management, therapeutics-management, nutrition-management, exercise-reporting | spec written |
| 5 | Daily log & adherence, measurement planning | daily-log-and-adherence, measurement-planning | todo |
| 6 | n-of-1 studies + statistics + scientific method | studies-nof1, statistical-methodology, scientific-method-and-evidence | todo |
| 7 | Evidence layer (Evipedia MCP) + AI4L narration | evidence-layer, ai-uses-and-attribution | todo |
| 8 | Safety guardrails | safety-guardrails | todo |
| 9 | Dashboards + doctor view | dashboards-and-doctor-view | todo |
| 10 | Genomics | genomics | todo |
| 11 | Procurement/inventory, management & delegation, agent access | procurement-and-inventory, management-and-delegation, agent-access | todo |
| 12 | Community, analytics & open data (OMOP/FHIR export, consent, de-id) | community-and-social, analytics-and-open-data | todo |
| 13 | Hardening: a11y audit, security review, i18n, docs, first-user onboarding | all | todo |

Fabio reviews each module's spec in `docs/QUESTIONS.md`; work does not block on him —
reasonable defaults are taken and flagged, and reversed if he disagrees.

## Research programmes (cross-module)

### R1 — Optimal ranges by age, sex, ancestry (Fabio 2026-11-24: a macro research theme)
- **Goal:** for each analyte, give optimal ranges (distinct from lab reference ranges and safety thresholds), stratified by age, sex and, where the evidence supports it, ancestry.
- **Method:**
  1. Run a multi-LLM literature search with AI4L audit-based prompting, using Forever Healthy's Evipedia as the primary knowledgebase.
  2. **LLMs only propose candidate sources.** Every number must be extracted from a cited primary source (study, guideline, cohort), with population, endpoint (all-cause mortality, CVD, …) and evidence grade, and must be checked by a human before it is shown. This follows the frozen rule "the LLM writes words, never numbers".
  3. Where sources disagree, show the range of the evidence, not an average invented by us.
- **Deliverables:**
  - an OpenSpec change `r1-optimal-ranges`;
  - a research dataset with full provenance (CC BY 4.0);
  - a review UI to approve candidates;
  - outreach to Forever Healthy for a data partnership.
- **Gate:** no optimal range is displayable without complete provenance (M01 gate).
