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

## Open questions carried into the spec (`> OPEN:` markers)

- **O1 Copy bypass** — In the copy flow, is an "I acknowledge the risk" acknowledgement acceptable, or must real baseline *values* be mandatory with no acknowledge-only path? (safety-guardrails / W2)
- **O2 Rapamycin News depth** — link-only, SSO via Discourse Connect, or partnership? (community-and-social)
- **O3 Study endpoint** — pre-registration mandatory to publish, or optional with a quality badge? (studies-nof1)
- **O4 Baseline lineage** — do we also capture a coarse "how did you arrive at this protocol" note for imported regimens? (protocols D5)
- **O5 Dashboard default** — organ-system grid (my choice) vs a single headline number first? (wireframes)
- **O6 Cohort comparison placement** — inside each dashboard tile or a dedicated tab? (wireframes)

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
