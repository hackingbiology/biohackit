# STATE — resume entrypoint

- Runner: `gl-auditor@sd-172212:~/biohackit` (migrated 2026-11-17), loop `tools/autodev/run.sh` (cron 03:15 and 15:15, Sonnet, ≤15 USD/week).
- Budget: ≤20% of weekly Claude cap; ledger `tools/autodev/ledger.jsonl`, cap in `tools/autodev/budget.conf`.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- Module: 0 — Foundations (with m00b low-friction login prioritised)
- Step: M00 TG1–TG4 done; TG5 backend tests green (26), auth.test.ts written but unrun (runner cannot run pnpm/jest, see QUESTIONS); CI items open
- m00b archived 2026-11-21 (openspec/changes/archive/m00b-low-friction-login); Fabio's action list (rapamycin.news secret, OAuth apps) still open.
- Next action: run frontend tests (jest, lint, tsc) once allowed, verify CI green on a branch, then archive M00.
- Notes: the venv needed `pip --python backend/.venv/bin/python install "django-allauth[mfa,socialaccount]"` (pulls `requests`). The local dev DB has an inconsistent migration history (blocks `makemigrations`); use a fresh DB.
