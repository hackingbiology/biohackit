# STATE — resume entrypoint

- Runner: `gl-auditor@sd-172212:~/biohackit` (migrated 2026-11-17), loop `tools/autodev/run.sh` (cron 03:15 and 15:15, Sonnet, ≤15 USD/week).
- Budget: ≤20% of weekly Claude cap; ledger `tools/autodev/ledger.jsonl`, cap in `tools/autodev/budget.conf`.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- Module: 0 — Foundations
- Step: TG1–TG3 done (core: Intervention, Biomarker, Measurement hypertable; 15 backend tests green); TG4–TG5 pending
- Next action: TG4 — frontend skeleton and auth. Note: the local dev DB has an inconsistent migration history (blocks `makemigrations`), so core migrations were hand-written; use a fresh DB for future makemigrations.
