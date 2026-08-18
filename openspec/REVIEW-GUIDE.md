# Review Guide — start here

This is a first, broad functional specification for biohack.it in OpenSpec form, plus navigation and wireframe hypotheses. It is meant to be **reviewed and corrected**, not accepted. Below is the fastest path through it and the exact points where I need your call.

## How to review in ~30 minutes

1. Read [`project.md`](project.md) — posture and capability map (5 min).
2. Skim [`specs/domain-model/spec.md`](specs/domain-model/spec.md) — the entities everything rests on (5 min).
3. Read the three most load-bearing capabilities (10 min):
   - [`specs/protocols`](specs/protocols/spec.md) — create / copy / import-baseline / **versioning**.
   - [`specs/safety-guardrails`](specs/safety-guardrails/spec.md) — the harm-reduction core.
   - [`specs/biomarkers-and-labs`](specs/biomarkers-and-labs/spec.md) — the Blood Layer, Phase 1.
4. Walk [`wireframes/navigation.md`](wireframes/navigation.md) journeys J1–J3, then skim [`wireframes/wireframes.md`](wireframes/wireframes.md) (10 min).
5. Answer the decisions and open questions below.

## Decisions I made from your automode brief — please confirm

| # | Decision | Where | Reverses / refines |
|---|---|---|---|
| D1 | **No local-first.** Server-hosted only. | accounts-and-profiles | spec v0.3 §11 Q28 |
| D2 | **Public by default**, with per-item withholding; UX actively invites sharing. | accounts-and-profiles, project.md | spec v0.3 Principle #2 |
| D3 | **Genomics is public too** (gVCF included), behind heightened consent — reverses Principle #9. | genomics, project.md, agent-access | your review 2026-08-04 |
| D4 | **No economic figures** anywhere in specs/artifacts. | project.md | your instruction |
| D5 | Experienced users **import an already-running protocol**; "in effect since" ≠ "tracked since". | protocols | new (your brief) |
| D6 | **Copy = fork with lineage + safety gate**; beginners cannot activate without baseline. | protocols, safety-guardrails, community | spec §4.1 B |
| D7 | **T0 seeding**: curated protocols (Fabio's first) + invited alpha biohackers → no cold community. | accounts-and-profiles, protocols | your brief |
| D8 | Competitor names **removed from the deck** (comparison to be done separately later). | deck | your instruction |
| D9 | **Content & evidence based on Forever Healthy's work** — Evipedia knowledgebase (CC BY 4.0) via MCP + AI4L (MIT) for AI reviews/queries; new `ai-uses-and-attribution` capability. | ai-uses-and-attribution, evidence-layer, interventions, project.md | your direction |

## Review status (updated 2026-08-04)

**Confirmed:** D1 (no local-first) ✓ — self-hosting a full AGPL instance is a distinct, supported path · D2 (public by default) ✓.

**Added on review (2026-08-04):**
- **Three reference sections added.** `related-initiatives` (highlighted register of similar initiatives, commercial & non), `data-standards-and-typing` (data structures in use and why, for scientific validity), and — in `ai-uses-and-attribution` — technical evaluation of reused OSS/open-data components + upstream notification (be the glue of others' data effort). _(related-initiatives, data-standards-and-typing, ai-uses-and-attribution)_
- **Q7 resolved — everything copyable, informed.** All interventions (peptides / plasmapheresis / IV included) are **one-click copyable**; mitigation = an **informed-decision panel** (adoption + outcomes, evidence corpus & grading, medical/research level, dose provenance, potential impacts, forum links) + the safety gate. _(community-and-social, protocols, safety-guardrails)_
- **Activities restructured.** Split **Pills Management** out of Procurement (now scales to 60–130 pills/day); added **Therapeutics Management** (red light, HBOT, sauna, cold plunge, cryotherapy, plasmapheresis, IV, ozone/EBOO, PEMF — each with typed parameters), **Exercise Reporting** (strength/cardio/mobility/HIIT + VO2max, log-only, not a gym app), and **Nutrition Management** (computed TDEE, eating pattern OMAD/CR/IF, macro split); **removed Claims Validator** (off-topic). _(pills-management, therapeutics-management, exercise-reporting, nutrition-management, procurement-and-inventory)_
- **Raw by default + BETA poll.** Public data (incl. raw lab reports and gVCF) is published **raw**, no forced PII obfuscation; the maximal-openness stance goes to a **community poll on Rapamycin News at the public BETA**. _(analytics-and-open-data, biomarkers-and-labs)_
- **D10 Fully clonable + self-hostable.** OpenData = public profiles + their public data, protocols, treatments, measurements, original lab files, public genomics/gVCF (excl. only withheld); published as a clonable snapshot to seed an independent AGPL instance; aggregated research export stays z-scored/threshold-guarded. _(analytics-and-open-data, accounts-and-profiles, project.md)_

**Resolved open questions:**
- **O1 Copy gate** → baseline values are **required** AND an explicit risk acknowledgment is **also required** (acknowledgment is never a bypass). _(safety-guardrails, W2 updated)_
- **O2 Rapamycin News** → **Discourse Connect SSO** where feasible, else link-only; a partnership is expected. _(community-and-social updated)_
- **O5 Dashboard** → **headline number first** (biological-age Δ, with uncertainty/clock/lab), **then** the organ-system grid; graceful fallback if the clock is missing. _(dashboards-and-doctor-view updated)_
- **O3 Study endpoint** → pre-registration is **mandatory** and takes the form of a **community proposal** (forum thread) for comment/consensus; research questions are themselves subject to community proposal; endpoints frozen once posted. _(studies-nof1 + community-and-social updated)_

- **O4 Baseline lineage** → **yes** — where analytic history is hard to reconstruct, capture a coarse free-text "how you got here" note AND flag the record as `history: synthesized` (not analytic). _(protocols updated)_

- **O6 Cohort comparison** → **both** — inline reference on each tile (A) **and** a dedicated "vs cohort" view (B). Plus: every biomarker reports its **sex/age-normalized percentile**. _(dashboards-and-doctor-view + analytics-and-open-data + wireframes updated)_

**All review questions resolved**, including the percentile reference: it is computed against **published reference distributions** (source declared per marker), not the platform aggregate. No open decisions remain — the next step is the module-by-module OpenSpec deep dive.

## What is intentionally NOT here yet
- Data schemas, API shapes, infrastructure, auth mechanics.
- Visual/UI design (wireframes are low-fi hypotheses).
- The competitive comparison (removed from the deck; to be redone in a dedicated form).
- The 5 remaining companion analyses still in the claude.ai chat (protocolengine, myagingtests ×2, bloodwork, lamplit) — not needed for this spec; retrievable on request.

## After your review — the plan you asked for
Once the specification is settled, we run a **module-by-module deep dive**, each expanded and organised as its own OpenSpec change. This tree is the base those changes will build on.

## Inventory of this deliverable
- `project.md`, `README.md`, this guide.
- 23 capability specs under `specs/` (domain-model, ai-uses-and-attribution, data-standards-and-typing, related-initiatives + 19 modules).
- `wireframes/navigation.md` (IA + 7 journeys), `wireframes/wireframes.md` (7 annotated screens).
