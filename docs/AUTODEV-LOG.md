# Autodev log

One entry per iteration: date · module · what was done · commit.

2026-11-09 · M00 Foundations · wrote OpenSpec change m00-foundations: proposal.md, tasks.md (TG1–TG5), foundations-architecture spec, QUESTIONS.md Q1–Q4, STATE updated · d92b3f2
2026-11-18 · M00 Foundations · TG1 repo layout: Django+Next.js skeleton, Docker Compose, Makefile, CI, env example; ruff/eslint/tsc clean (Django check and docker compose up not run on runner) · see git log
2026-11-19 · M00 Foundations · TG2 backend auth: accounts app (email User, Profile, SocialHandle), JWT register/token/refresh/me, public profile, 10 tests green · see git log
2026-11-19 · M00 Foundations · TG3 core domain stubs (Intervention/Biomarker/Measurement), hypertable migration with composite PK, 5 domain tests, 15 total green · see git log
2026-11-20 · M00b low-friction login · TG1 backend (allauth socialaccount+headless+mfa, DiscourseConnect provider, env-driven providers, code login, passkeys, verified-email linking) + TG3 tests, 26 green · see git log
2026-11-21 · M00b low-friction login · TG2 frontend sign-in (SignInForm: providers/email code/passkey, EN/IT/ZH, plain fetch), jest.config.js fix, 5 jest tests green · see git log
2026-11-21 · M00b low-friction login · archived change into openspec/specs/accounts-and-profiles (Fabio's action list still open) · see git log
