# biohack.it — Project Context (OpenSpec)

> **Naming.** **HackingBiology** is the organization (a non-profit). **biohack.it** is the software and the initiative.

## What this is

biohack.it is an open-source (AGPL-3.0), free, server-hosted platform where biohackers **document their protocol** in a structured way (what they take and do — dose, timing, cycles), **measure its efficacy and safety through biomarkers**, and **share the protocol and its outcomes publicly**. The social mechanic is "copy-trading for health": follow and copy the people who get results, seeing their public biomarkers. The ethical core is harm reduction for beginners.

The source of truth for scope and rationale is [`docs/hackingbiology-project-spec.md`](../docs/hackingbiology-project-spec.md) (v0.3) and the companion analyses in `docs/`. This `openspec/` tree translates that vision into a reviewable **functional specification**: capabilities → requirements → scenarios.

## Product posture (decisions that shape every capability)

These are settled directions. Where one supersedes spec v0.3, it is flagged so Fabio can confirm on review.

- **Server-hosted, not local-first.** The individual layer runs on the server. There is no browser-only mode.
  - _Supersedes the "local-first mode" open question (spec v0.3 §11 Q28) — resolved: no local-first (confirmed by Fabio 2026-08-04)._
  - **Self-hosting is a different, supported thing:** the software is AGPL, so a technically capable user may stand up their own full instance and seed it from the public OpenData snapshot.
- **Fully clonable — open by code and by data.** Everything public — public profiles and their public data, defined protocols, treatments/interventions, and measurements — is **OpenData**, published as a clonable snapshot sufficient to run an independent instance. Withheld per-item data is never included; public genomic data (including the gVCF) and original lab report files are included under the same public-by-default rule. See `specs/analytics-and-open-data`.
- **Public by default.** A profile, its protocol and its biomarker outcomes are meant to be public and shared. The UX actively invites sharing rather than defaulting to private.
  - _Supersedes spec v0.3 Service Principle #2 ("public by choice, never by default"). Kept from #2: per-marker granularity still exists for the few things a user withholds._
- **Raw by default, validated by the community.** Public data is published **raw** (raw lab reports and gVCF included) — no forced obfuscation. This maximal-openness stance will be put to a community poll on Rapamycin News when the public BETA opens. See `specs/analytics-and-open-data`.
- **Genomics is public too.** Reversing spec v0.3 Principle #9: genomic data — including the gVCF — is public by default like other data, behind a heightened, explicit consent gate (it is maximally identifying and effectively irreversible once public). See `specs/genomics`.
- **The platform describes, never prescribes** (Principle #3). It suggests *what to measure*, never *what to take or how much*.
- **Deterministic where it counts.** Extraction, mapping, threshold and index computation are deterministic and reproducible; the LLM only produces narration, generated once and cached. *The LLM writes words, never numbers* (Principle, M2/M8).
- **Built on Forever Healthy's work.** Evidence content structure follows **Evipedia** (Forever Healthy, CC BY 4.0), integrated via its MCP; AI-generated reviews and evidence queries use the **AI4L** audit-based-prompting framework (MIT). Where AI is and isn't used is published as an AI surfaces map. See `specs/ai-uses-and-attribution`.
- **Fails loudly** (Principle #6) and **stops instead of guessing** (Principle #8).
- **No chicken-and-egg.** At T0 the team seeds **content-curated protocols** (starting from Fabio's own) and invites a first cohort of **alpha-tester biohackers** with real profiles. Community features attach to Rapamycin News, which already exists.
- **Protocols are living objects.** They are created from scratch, copied/forked from others, or imported from an already-running regimen; they **change over time and every change is versioned and tracked**.
- **No economic figures** appear in specs or artifacts (per Fabio, 2026-08-04). Cost *tracking as a user feature* may exist; investment/opex numbers do not.

## Capability map

Each capability lives under `specs/<capability>/spec.md`. Module codes (M1–M13) refer to `docs/hackingbiology-project-spec.md` §6.

| Capability | Module(s) | Phase |
|---|---|---|
| `domain-model` | cross-cutting (§5) | 0 |
| `ai-uses-and-attribution` | cross-cutting (AI, provenance, previous work) | 0 |
| `accounts-and-profiles` | onboarding, seeding | 1 |
| `protocols` | M1 | 1 |
| `interventions-and-catalog` | M1/M4 (§5, §8.5quater) | 1 |
| `biomarkers-and-labs` (Blood Layer) | M2 | 1 |
| `measurement-planning` | M3 | 2 |
| `safety-guardrails` | M7 | 1–2 |
| `daily-log-and-adherence` | M13 | 1 |
| `dashboards-and-doctor-view` | M5 | 1 |
| `community-and-social` | M6 | 2 |
| `studies-nof1` | Study (§5) | 2 |
| `procurement-and-inventory` | M4 (supply) | 3 |
| `pills-management` | M4 (daily intake) | 3 |
| `therapeutics-management` | Device/Therapy | 2–3 |
| `exercise-reporting` | Exercise | 1–2 |
| `nutrition-management` | Nutrition/Fasting | 1 |
| `evidence-layer` | M11 | 0/3 |
| `analytics-and-open-data` | M8 | 4 |
| `genomics` | M9 | 2 |
| `agent-access` | (getbased B6) | 3 |

## Conventions

- **Requirements** use SHALL/MUST; each has at least one `#### Scenario:` with `WHEN/THEN/AND` steps.
- **`> DECISION:`** blockquotes mark choices that need Fabio's confirmation.
- **`> OPEN:`** blockquotes mark questions left open for review.
- Screens and flows are hypotheses in `wireframes/` — explicitly for revision together.

## Tech context (from spec §8, not re-decided here)

Backend Python/Django · PostgreSQL (+TimescaleDB) · Next.js/React PWA · HL7 FHIR internal vocabulary, OMOP export · LOINC + UCUM for analytes · RxNorm/ATC/PubChem/UNII for substances · Discourse (Rapamycin News) for community · component reuse from `get-based` (AGPL) · external evidence from **Evipedia** (Forever Healthy, CC BY 4.0) via `evipedia-mcp` · AI review generation via **AI4L** (MIT, audit-based prompting).
