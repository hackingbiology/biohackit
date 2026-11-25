# STATE — resume entrypoint

- Runner: **autodev v2** (OpenSpec `m00c-autodev-v2`): systemd `biohackit-autodev` as gl-auditor on sd-172212, continuous graph planner→implementer→gates→adversarial review→verify→merge (`tools/autodev2/`). v1 cron runner retired 2026-11-24.
- Definition of done: `docs/TRACEABILITY.md` (`tools/trace/matrix.py`). Daily digest 08:15 in `docs/digest/` + GitHub issue. Staging: http://51.158.36.151:18800.
- Budget: ≤40% of the weekly plan limit, measured from real utilization (`/var/lib/biohackit-usage/usage.json`), paced over the week.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
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
- Notes: the venv needed `pip --python backend/.venv/bin/python install "django-allauth[mfa,socialaccount]"` (pulls `requests`). The local dev DB has an inconsistent migration history (blocks `makemigrations`); use a fresh DB.
