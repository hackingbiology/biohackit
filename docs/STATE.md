# STATE — resume entrypoint

- Runner: `gl-auditor@sd-172212:~/biohackit` (migrated 2026-11-17), loop `tools/autodev/run.sh` (cron 03:15 and 15:15, Sonnet, ≤15 USD/week).
- Budget: ≤20% of weekly Claude cap; ledger `tools/autodev/ledger.jsonl`, cap in `tools/autodev/budget.conf`.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- Module: 0 — Foundations (with m00b low-friction login prioritised)
- Step: M00 TG1–TG3 done; m00b TG1 (backend) + TG3 (tests) done, 26 backend tests green; m00b TG2 (frontend sign-in page, 5 jest tests green) done, so m00b agent tasks are complete; M00 TG4 (remaining items) and TG5 pending
- Next action: archive the m00b change (Fabio's action list stays open), then finish M00 TG4 (sign-up page → SignInForm, logout via headless, middleware session check, Button/Input tests) and TG5.
- Notes: the venv needed `pip --python backend/.venv/bin/python install "django-allauth[mfa,socialaccount]"` (pulls `requests`). The local dev DB has an inconsistent migration history (blocks `makemigrations`); use a fresh DB.
