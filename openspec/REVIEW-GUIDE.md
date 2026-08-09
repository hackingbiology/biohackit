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
| D3 | **Genomics stays structurally private** even under D2. | genomics, project.md | unchanged (Principle #9) |
| D4 | **No economic figures** anywhere in specs/artifacts. | project.md | your instruction |
| D5 | Experienced users **import an already-running protocol**; "in effect since" ≠ "tracked since". | protocols | new (your brief) |
| D6 | **Copy = fork with lineage + safety gate**; beginners cannot activate without baseline. | protocols, safety-guardrails, community | spec §4.1 B |
| D7 | **T0 seeding**: curated protocols (Fabio's first) + invited alpha biohackers → no cold community. | accounts-and-profiles, protocols | your brief |
| D8 | Competitor names **removed from the deck** (comparison to be done separately later). | deck | your instruction |

## Review status (updated 2026-08-04)

**Confirmed:** D1 (no local-first) ✓ · D2 (public by default) ✓.

**Resolved open questions:**
- **O1 Copy gate** → baseline values are **required** AND an explicit risk acknowledgment is **also required** (acknowledgment is never a bypass). _(safety-guardrails, W2 updated)_
- **O2 Rapamycin News** → **Discourse Connect SSO** where feasible, else link-only; a partnership is expected. _(community-and-social updated)_
- **O5 Dashboard** → **headline number first** (biological-age Δ, with uncertainty/clock/lab), **then** the organ-system grid; graceful fallback if the clock is missing. _(dashboards-and-doctor-view updated)_
- **O3 Study endpoint** → pre-registration is **mandatory** and takes the form of a **community proposal** (forum thread) for comment/consensus; research questions are themselves subject to community proposal; endpoints frozen once posted. _(studies-nof1 + community-and-social updated)_

- **O4 Baseline lineage** → **yes** — where analytic history is hard to reconstruct, capture a coarse free-text "how you got here" note AND flag the record as `history: synthesized` (not analytic). _(protocols updated)_

- **O6 Cohort comparison** → **both** — inline reference on each tile (A) **and** a dedicated "vs cohort" view (B). Plus: every biomarker reports its **sex/age-normalized percentile**. _(dashboards-and-doctor-view + analytics-and-open-data + wireframes updated)_

**All eight review questions are resolved.** One non-blocking design detail remains (`> OPEN:` in analytics-and-open-data): which reference population underlies the sex/age percentile (published references vs platform aggregate). Remaining work is design fidelity, not decisions.

## What is intentionally NOT here yet
- Data schemas, API shapes, infrastructure, auth mechanics.
- Visual/UI design (wireframes are low-fi hypotheses).
- The competitive comparison (removed from the deck; to be redone in a dedicated form).
- The 5 remaining companion analyses still in the claude.ai chat (protocolengine, myagingtests ×2, bloodwork, lamplit) — not needed for this spec; retrievable on request.

## After your review — the plan you asked for
Once the specification is settled, we run a **module-by-module deep dive**, each expanded and organised as its own OpenSpec change. This tree is the base those changes will build on.

## Inventory of this deliverable
- `project.md`, `README.md`, this guide.
- 17 capability specs under `specs/` (domain-model + 16 modules).
- `wireframes/navigation.md` (IA + 7 journeys), `wireframes/wireframes.md` (7 annotated screens).
