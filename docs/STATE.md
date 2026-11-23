# STATE — resume entrypoint

- Runner: `gl-auditor@sd-172212:~/biohackit` (migrated 2026-11-17), loop `tools/autodev/run.sh` (cron 03:15 and 15:15, Sonnet, ≤15 USD/week).
- Budget: ≤20% of weekly Claude cap; ledger `tools/autodev/ledger.jsonl`, cap in `tools/autodev/budget.conf`.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- Module: 0 — Foundations (with m00b low-friction login prioritised)
- Step: M00 TG1–TG5 done locally (backend 26 pytest, frontend 11 jest, tsc+eslint clean); only the 3 CI-on-GitHub items remain; Fabio must confirm CI green (QUESTIONS 2026-11-23)
- m00b archived 2026-11-21 (openspec/changes/archive/m00b-low-friction-login); Fabio's action list (rapamycin.news secret, OAuth apps) still open.
- Next action: M01 TG2 (terminology app, Source/Unit models) — M01 spec written 2026-11-23 (openspec/changes/m01-terminology-reference-data). M00 archive still awaits Fabio CI confirmation (tick CI items + archive when confirmed).
- Notes: the venv needed `pip --python backend/.venv/bin/python install "django-allauth[mfa,socialaccount]"` (pulls `requests`). The local dev DB has an inconsistent migration history (blocks `makemigrations`); use a fresh DB.
