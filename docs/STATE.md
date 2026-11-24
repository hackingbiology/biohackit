# STATE — resume entrypoint

- Runner: **autodev v2** (OpenSpec `m00c-autodev-v2`): systemd `biohackit-autodev` as gl-auditor on sd-172212, continuous graph planner→implementer→gates→adversarial review→verify→merge (`tools/autodev2/`). v1 cron runner retired 2026-11-24.
- Definition of done: `docs/TRACEABILITY.md` (`tools/trace/matrix.py`). Daily digest 08:15 in `docs/digest/` + GitHub issue. Staging: http://51.158.36.151:18800.
- Budget: ≤40% of the weekly plan limit, measured from real utilization (`/var/lib/biohackit-usage/usage.json`), paced over the week.
- Plan: `docs/ROADMAP.md`. Questions for Fabio: `docs/QUESTIONS.md`. Log: `docs/AUTODEV-LOG.md`.

## Current
- Module: 0 — Foundations (with m00b low-friction login prioritised)
- Step: M00 TG1–TG5 done locally (backend 26 pytest, frontend 11 jest, tsc+eslint clean); only the 3 CI-on-GitHub items remain; Fabio must confirm CI green (QUESTIONS 2026-11-23)
- m00b archived 2026-11-21 (openspec/changes/archive/m00b-low-friction-login); Fabio's action list (rapamycin.news secret, OAuth apps) still open.
- Next action: M01 TG3 (coded analyte registry). TG2 done 2026-11-24 (30 pytest green); its migration was hand-written because makemigrations needs a fresh DB — run `makemigrations --check` on a fresh DB to confirm no drift. Earlier note: M01 TG2 (terminology app, Source/Unit models) — M01 spec written 2026-11-23 (openspec/changes/m01-terminology-reference-data). M00 archive still awaits Fabio CI confirmation (tick CI items + archive when confirmed).
- Notes: the venv needed `pip --python backend/.venv/bin/python install "django-allauth[mfa,socialaccount]"` (pulls `requests`). The local dev DB has an inconsistent migration history (blocks `makemigrations`); use a fresh DB.
