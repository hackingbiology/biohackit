# STATE — resume entrypoint

- Runner: **autodev v2** (OpenSpec `m00c-autodev-v2`): systemd `biohackit-autodev` as gl-auditor on sd-172212, continuous graph planner→implementer→gates→adversarial review→verify→merge (`tools/autodev2/`). v1 cron runner retired 2026-11-24.
- Definition of done: `docs/TRACEABILITY.md` (`tools/trace/matrix.py`). Daily digest 08:15 in `docs/digest/` + GitHub issue. Staging: http://51.158.36.151:18800.
- Budget: ≤40% of the weekly plan limit, measured from real utilization (`/var/lib/biohackit-usage/usage.json`), paced over the week.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- X01 Ecosystem page done 2026-11-25: public `/ecosystem` renders `frontend/src/content/ecosystem.json`, generated from docs/ecosystem/ by `tools/ecosystem/export_page_data.py` (`--check` plus tests keep it in sync). Remaining x01 task: planner rule (scan precedes each module change).
- M00c TG2 gates C done 2026-11-25: `tools/audit/pip_audit_gate.py` audits `uv export` of backend/uv.lock with `pip-audit==2.10.1` run through `uvx` (isolated tool env). It is not installed in `backend/.venv` because `tools/licence/check_licences.py` scans every distribution of that venv. Fixable vulnerability exits 1; cannot run exits 2. On this branch: 19 packages, no fixable vulnerability. **B2 blocker for the next planner:** B2's last run failed only at the licence gate, because `pnpm licenses list --prod --json` exited 1 after the postcss override changed the lockfile while the shared `frontend/node_modules` did not match (see the node_modules section below and Q34).
- M00c TG2 spec discovery part C done 2026-11-24: registers docs/spec-discovery/getbased-reuse.md and presentation.md (14 ADDED requirements, Q25–Q30), linked-data scenario fix; next: part D (docs/slides/, docs/specs/, docs/analysis/, remaining docs/*.md).
- M00c TG2 spec discovery part B done 2026-11-24: register docs/spec-discovery/project-spec.md (14 ADDED requirements, Q18–Q23), plus part A residuals (linked-data requirement, Q24; register-rows scenario wording); next: part C (docs/getbased-reuse-analysis.md, docs/presentation/).
- M00c TG2 spec discovery part A done 2026-11-24: register docs/spec-discovery/whitepaper.md, change openspec/changes/s01-spec-discovery (8 ADDED requirements, Q16–Q17), test_spec_discovery_register.py.
- M00c TG2 gates A done 2026-11-24: changed-file coverage gate (tools/coverage/changed_coverage.py); remaining gates-hardening sub-items (mypy, pip-audit, pnpm audit, semgrep, openspec validate, Playwright+axe, mutmut) need tools not installed here.
- X01 TG4 done 2026-11-24: integration anchor scan docs/ecosystem/integrations.md (Q14), give-back register test, m01 scan TG column fix; next X01 items: planner rule, Ecosystem docs page.
- X01 licence gate done 2026-11-24: tools/licence/check_licences.py + overrides.toml, `licences` step appended to gates.sh (Q12 open); next X01 item: integration scans for the anchors.
- X01 TG1 done 2026-11-24: docs/ecosystem/ README, GIVEBACK, m00-foundations scan + enforcing test; m01 scan done 2026-11-24 (docs/ecosystem/m01-terminology.md, decisions annotated in m01 tasks); next X01 item: integration scans for the anchors.
- M00c TG2: staging stack written (docker-compose.staging.yml, docs/STAGING.md); next M00c TG2 item is gates hardening.
- Module: 0 — Foundations (with m00b low-friction login prioritised)
- Step: M00 TG1–TG5 done locally (backend 26 pytest, frontend 11 jest, tsc+eslint clean); only the 3 CI-on-GitHub items remain; Fabio must confirm CI green (QUESTIONS 2026-11-23)
- m00b archived 2026-11-21 (openspec/changes/archive/m00b-low-friction-login); Fabio's action list (rapamycin.news secret, OAuth apps) still open.
- Next action: M01 TG3 (coded analyte registry). TG2 done 2026-11-24 (30 pytest green); its migration was hand-written because makemigrations needs a fresh DB — run `makemigrations --check` on a fresh DB to confirm no drift. Earlier note: M01 TG2 (terminology app, Source/Unit models) — M01 spec written 2026-11-23 (openspec/changes/m01-terminology-reference-data). M00 archive still awaits Fabio CI confirmation (tick CI items + archive when confirmed).
- B1 done 2026-11-25: next/eslint-config-next 15.1.0 -> 15.5.29 (docs/security/frontend-advisories.md); B2 pnpm audit gate next; postcss left open (Q33).
- Fix main (no .npmrc) done 2026-11-25: shared node_modules verified (lint, tsc, jest green); see the section at the end of this file.
- Notes: the venv needed `pip --python backend/.venv/bin/python install "django-allauth[mfa,socialaccount]"` (pulls `requests`). The local dev DB has an inconsistent migration history (blocks `makemigrations`); use a fresh DB.

## Shared frontend/node_modules: root cause and rules
- **Symptom:** eslint/tsc/jest failed with MODULE_NOT_FOUND because links in the shared `frontend/node_modules` pointed into task worktrees that had been deleted.
- **Repair (2026-11-25 13:02):** hoisted reinstall at the real path (`/home/gl-auditor/biohackit/frontend`); `node_modules/next` is now a real directory and `.bin/tsc` a relative link. In this worktree lint, type-check and jest (6 suites, 18 tests) pass.
- **Why `.npmrc` was dropped:** attempts v2–v4 committed tests reading `frontend/.npmrc`, but the file never reached the task worktree (backend pytest FileNotFoundError, jest ENOENT); the cause is unconfirmed. No test or Dockerfile line may depend on it; the one optional `.npmrc` check left in `pnpm-build-policy.test.ts` was removed.
- **Rule:** agents never run `pnpm install`, `add` or `remove` inside a worktree (it writes through the symlink into the shared install). Only `lint`, `type-check`, `test:ci`.
- **Orchestrator proposal:** QUESTIONS Q34 (options A/B/C).
