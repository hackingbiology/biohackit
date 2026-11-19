# [M00] Write OpenSpec change for Foundations module
Labels: autodev, spec
Milestone: M00 — Foundations
Parent: #3

## Goal

Author the OpenSpec change (`openspec/changes/m00-foundations/`) for Module 0 — Foundations — which is the prerequisite to any implementation work. This change defines the technical skeleton (repo layout, stack, CI, auth, base models) for the entire platform.

## Spec references

- `openspec/changes/m00-foundations/proposal.md` — purpose, decisions, acceptance criteria
- `openspec/changes/m00-foundations/tasks.md` — five implementation task groups (TG1–TG5)
- `openspec/changes/m00-foundations/specs/foundations-architecture.md` — new technical architecture spec (stack, CI, JWT, hypertable, UTC, AGPL headers, env-var config)

Existing functional specs referenced but not modified:
- `openspec/specs/accounts-and-profiles/spec.md`
- `openspec/specs/domain-model/spec.md`
- `openspec/specs/data-standards-and-typing/spec.md`

## Acceptance

- [ ] `openspec/changes/m00-foundations/proposal.md` present and complete
- [ ] `openspec/changes/m00-foundations/tasks.md` present with TG1–TG5, all items unchecked
- [ ] `openspec/changes/m00-foundations/specs/foundations-architecture.md` present with SHALL scenarios covering stack, CI, JWT, hypertable, UTC, AGPL, env config
- [ ] `docs/QUESTIONS.md` has four M00 entries with defaults
- [ ] `docs/STATE.md` updated: step = "OpenSpec change written"; next = "implement TG1"
