# M00 Foundations — Tasks

Each task group maps to a ticket (`docs/tickets/outbox/m00-<slug>.md`).
Tick items as they are completed. Never commit red tests.

---

## TG1: Repo layout and tooling
**Ticket:** m00-repo-layout  
**Label:** feature  
**SHALL scenarios covered:** foundations-architecture §Scenario: fresh-clone dev start

- [ ] `backend/` directory with Django project skeleton via `django-admin startproject biohackit backend/`
- [ ] `backend/pyproject.toml` with deps: Django 5.0, djangorestframework, djangorestframework-simplejwt, django-allauth, psycopg[binary], django-environ, django-timescaledb, whitenoise
- [ ] `backend/pytest.ini` / `[tool.pytest.ini_options]` configured; `pytest-django` in dev deps
- [ ] `frontend/` directory with `pnpm create next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"` output committed
- [ ] `frontend/pnpm-lock.yaml` committed
- [ ] `docker-compose.yml` at repo root: services `db` (timescale/timescaledb-ha:pg16) and `backend` and `frontend`; volume `pgdata`
- [ ] `docker-compose.override.yml.example` with per-dev port overrides
- [ ] `Makefile` at repo root with targets: `install`, `migrate`, `test`, `lint`, `dev`
- [ ] `.env.example` documenting all required env vars (DB_URL, SECRET_KEY, ALLOWED_HOSTS, CORS_ORIGINS, JWT_*)
- [ ] `.github/workflows/ci.yml` with jobs `backend` (ruff + pytest) and `frontend` (eslint + jest); trigger: pull_request + push to main
- [ ] AGPL-3.0 license header added to `backend/biohackit/__init__.py` and `frontend/src/app/layout.tsx`

---

## TG2: Backend auth and user model
**Ticket:** m00-backend-auth  
**Label:** feature  
**SHALL scenarios covered:**
- accounts-and-profiles §Scenario: Account needed to contribute
- accounts-and-profiles §Scenario: Power user stands up their own instance
- accounts-and-profiles §Scenario: Onboarding invites sharing
- accounts-and-profiles §Scenario: Stable traits captured specifically
- accounts-and-profiles §Scenario: Social and forum handles linked
- foundations-architecture §Scenario: JWT token issued and refreshed

- [ ] `backend/accounts/` app created (`python manage.py startapp accounts`)
- [ ] Custom `User` model in `accounts/models.py`: email-primary (no username), `is_public` default=True, timestamps
- [ ] `Profile` model FK to `User`: `date_of_birth`, `sex` (ChoiceField M/F/I/X/prefer-not), `ethnicity` (free text, nullable), `height_cm` (DecimalField), `is_public` default=True, `created_at`, `updated_at`
- [ ] `SocialHandle` model FK to `Profile`: `platform` (telegram | wechat | xiaohongshu | rapamycin_news | other), `handle`, `url`
- [ ] `AUTH_USER_MODEL = 'accounts.User'` in settings; migration 0001 committed
- [ ] DRF configured in settings; `DEFAULT_AUTHENTICATION_CLASSES` = simplejwt
- [ ] simplejwt settings: access token 15 min, refresh 7 days
- [ ] allauth configured for email+password; `ACCOUNT_EMAIL_REQUIRED = True`, `ACCOUNT_USERNAME_REQUIRED = False`
- [ ] API endpoints: `POST /api/auth/register/`, `POST /api/auth/token/` (login), `POST /api/auth/token/refresh/`, `GET /api/auth/me/`
- [ ] `GET /api/profiles/<username>/` publicly readable, no auth required
- [ ] Django admin registered for `User`, `Profile`, `SocialHandle`

---

## TG3: Base domain model stubs
**Ticket:** m00-domain-stubs  
**Label:** feature  
**SHALL scenarios covered:**
- domain-model §Scenario: Method and lab are mandatory metadata (Measurement schema)
- domain-model §Scenario: The three ranges stay distinct (Biomarker schema)
- domain-model §Scenario: Pulsed senolytic is representable (Intervention schema)

- [ ] `backend/core/` app created for shared domain models
- [ ] `InterventionSubtype` enum: `substance | exercise | device_therapy | procedure | hormonal | nutrition_fasting`
- [ ] `Intervention` stub model: `name` (CharField), `subtype` (ChoiceField), `cycle_schema` (JSONField, nullable), `created_at`; full business logic deferred to M03
- [ ] `BiomarkerRole` enum: `efficacy | safety | baseline`
- [ ] `Biomarker` stub model: `loinc_code` (CharField, nullable), `name` (CharField), `role` (ChoiceField), `unit_ucum` (CharField, nullable), `created_at`; full three-range fields deferred to M01
- [ ] `Measurement` model: `id` (BigAutoField), `user` FK, `biomarker` FK, `time` (DateTimeField), `value` (DecimalField, max_digits=20, decimal_places=6), `unit_ucum` (CharField), `source` (CharField), `laboratory` (CharField, nullable), `method` (CharField, nullable), `is_aggregation_eligible` (BooleanField, default=False, set True when lab+method present)
- [ ] TimescaleDB `create_hypertable('core_measurement', 'time')` via post-migrate signal or manual migration step
- [ ] migration 0001 for `core` committed
- [ ] `is_aggregation_eligible` auto-set to True in `Measurement.save()` when `laboratory` and `method` are both non-empty

---

## TG4: Frontend skeleton and auth
**Ticket:** m00-frontend-skeleton  
**Label:** feature  
**SHALL scenarios covered:**
- accounts-and-profiles §Scenario: Account needed to contribute
- accounts-and-profiles §Scenario: Onboarding invites sharing

- [ ] Next.js App Router layout in `frontend/src/app/layout.tsx`: `<html lang="en">`, mobile-first meta viewport, Tailwind base styles
- [ ] `frontend/src/lib/api.ts`: typed fetch wrapper pointing to `NEXT_PUBLIC_API_URL`; exports `apiFetch(path, init?)`
- [ ] `frontend/src/lib/auth.ts`: `register(email, password)`, `login(email, password)`, `refreshToken()`, `logout()` — all hit the DRF JWT endpoints; tokens stored in httpOnly cookie via Next.js Route Handler
- [ ] `frontend/src/app/(auth)/sign-up/page.tsx`: email + password fields, calls `register()`, redirects to `/onboarding` on success
- [ ] `frontend/src/app/(auth)/sign-in/page.tsx`: email + password fields, calls `login()`, redirects to `/dashboard` on success
- [ ] `frontend/src/app/onboarding/page.tsx`: placeholder with copy "Welcome — your profile is public by default. Here's why that matters…" + Continue button
- [ ] `frontend/src/middleware.ts`: redirect unauthenticated requests for `/dashboard/*` to `/sign-in`
- [ ] `frontend/src/app/page.tsx`: public homepage with tagline, Sign Up + Sign In CTAs
- [ ] `frontend/src/components/ui/Button.tsx`: accessible button primitive (Tailwind, aria-label support)
- [ ] `frontend/src/components/ui/Input.tsx`: accessible text input primitive (label, error, aria-describedby)
- [ ] PWA manifest at `frontend/public/manifest.json`: name, icons (from brand/), `display: standalone`, `theme_color`

---

## TG5: Tests and CI green
**Ticket:** m00-tests  
**Label:** test  
**SHALL scenarios covered:** all scenarios from TG2 and TG3; CI gate for all subsequent modules

**Backend tests (`backend/tests/`):**

- [ ] `test_accounts.py::test_register_creates_user` — POST /api/auth/register/ → 201, user exists
- [ ] `test_accounts.py::test_register_requires_email` — missing email → 400
- [ ] `test_accounts.py::test_login_returns_jwt` — POST /api/auth/token/ → 200, `access` and `refresh` keys present
- [ ] `test_accounts.py::test_refresh_token` — POST /api/auth/token/refresh/ with valid refresh → 200, new `access`
- [ ] `test_accounts.py::test_public_profile_readable_without_auth` — GET /api/profiles/<slug>/ → 200, no auth header
- [ ] `test_accounts.py::test_profile_biological_attributes` — set date_of_birth, sex, height_cm; retrieve; values match
- [ ] `test_accounts.py::test_social_handles_created` — add telegram and rapamycin_news handles; retrieve profile; both present
- [ ] `test_accounts.py::test_private_write_requires_auth` — POST /api/auth/register/ then GET /api/auth/me/ without token → 401
- [ ] `test_domain.py::test_intervention_cycle_schema_stored` — create Intervention with `cycle_schema = {"pattern": "pulsed", "on_days": [1,2,3]}`; retrieve; schema intact
- [ ] `test_domain.py::test_measurement_aggregation_eligibility` — Measurement with lab+method → is_aggregation_eligible True; without → False
- [ ] `test_domain.py::test_measurement_hypertable_insert` — insert Measurement row; select back by time range; row returned

**Frontend tests (`frontend/src/__tests__/`):**

- [ ] `auth.test.ts`: `register()` calls the correct endpoint with email/password; returns token on 201
- [ ] `auth.test.ts`: `login()` calls token endpoint; returns access+refresh on 200
- [ ] `Button.test.tsx`: renders with correct aria-label; onClick fires
- [ ] `Input.test.tsx`: renders label; error prop shows error text; aria-describedby links to error element

**CI:**

- [ ] `.github/workflows/ci.yml` backend job: checkout, uv install, ruff check, pytest — exits 0
- [ ] `.github/workflows/ci.yml` frontend job: checkout, pnpm install, eslint, jest — exits 0
- [ ] CI runs successfully on a test branch before final commit
