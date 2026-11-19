# STATE — resume entrypoint

- Runner: `gl-auditor@sd-172212:~/biohackit` (migrated 2026-11-17), loop `tools/autodev/run.sh` (cron 03:15 and 15:15, Sonnet, ≤15 USD/week).
- Budget: ≤20% of weekly Claude cap; ledger `tools/autodev/ledger.jsonl`, cap in `tools/autodev/budget.conf`.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- Module: 0 — Foundations
- Step: TG1, TG2 done (accounts: User/Profile/SocialHandle, JWT endpoints, 10 tests green); TG3–TG5 pending
- Next action: TG3 — core app domain stubs (Intervention, Biomarker, Measurement + hypertable). Verify `docker compose up` when possible.
