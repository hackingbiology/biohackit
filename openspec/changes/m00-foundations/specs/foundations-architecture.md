# Foundations Architecture (M00)

## Purpose

Specifies the technical skeleton that all subsequent modules build on. This spec covers decisions not derivable from the functional capability specs — stack choices, repo layout, CI/CD, authentication mechanism, and local-dev orchestration.

---

## Requirements

### Requirement: Monorepo with backend and frontend roots
The system SHALL live in a single git repository with `backend/` (Python/Django) and `frontend/` (Next.js/React) as first-class subdirectories at the repo root. No git submodules.

#### Scenario: Fresh-clone dev start
- **WHEN** a developer clones the repository and runs `docker compose up`
- **THEN** all services (database, backend, frontend) start in one command
- **AND** the Next.js PWA is reachable at `http://localhost:3000`
- **AND** the Django API is reachable at `http://localhost:8000/api/`

### Requirement: Technology stack
The system SHALL use the following stack exactly, unless a future OpenSpec change supersedes this spec:

| Layer | Technology | Version floor |
|---|---|---|
| Backend language | Python | 3.12 |
| Backend framework | Django | 5.0 |
| Backend API | Django REST Framework | 3.15 |
| Auth (email/password) | django-allauth | 0.61 |
| Auth (tokens) | djangorestframework-simplejwt | 5.3 |
| Database | PostgreSQL | 16 |
| Time-series | TimescaleDB | 2.14 |
| Backend linting/format | ruff | 0.4 |
| Backend test runner | pytest-django | 4.8 |
| Backend dep management | uv + pyproject.toml | — |
| Frontend framework | Next.js (App Router) | 15 |
| Frontend language | TypeScript | 5.4 (strict) |
| Frontend styles | Tailwind CSS | 4 |
| Frontend package mgr | pnpm | 9 |
| Frontend unit tests | Jest + Testing Library | — |
| Frontend E2E tests | Playwright | 1.44 |
| Container orchestration | Docker Compose | v2 |

#### Scenario: Stack pinned in lockfiles
- **WHEN** a developer installs dependencies
- **THEN** `uv.lock` and `pnpm-lock.yaml` are present and committed; versions are reproducible

### Requirement: CI pipeline on every pull request
The system SHALL run a CI pipeline on every pull request and every push to `main` using GitHub Actions. The pipeline SHALL fail if any linting or test step fails.

#### Scenario: Backend CI passes
- **WHEN** a pull request is opened
- **THEN** the `backend` CI job runs `ruff check` and `ruff format --check`
- **AND** then runs `pytest` with the Django test database
- **AND** the job exits non-zero on any failure, blocking the merge

#### Scenario: Frontend CI passes
- **WHEN** a pull request is opened
- **THEN** the `frontend` CI job runs `eslint` and `tsc --noEmit`
- **AND** then runs `jest --ci`
- **AND** the job exits non-zero on any failure, blocking the merge

### Requirement: JWT authentication
The system SHALL authenticate API requests using short-lived JWT access tokens (15 minutes) and long-lived refresh tokens (7 days). No session cookies for the API.

#### Scenario: JWT token issued and refreshed
- **WHEN** a user POSTs valid credentials to `/api/auth/token/`
- **THEN** the response contains an `access` token (15-min lifetime) and a `refresh` token (7-day lifetime)
- **AND** the client can POST the `refresh` token to `/api/auth/token/refresh/` to obtain a new `access` token without re-entering credentials

#### Scenario: Expired access token is rejected
- **WHEN** a client presents an expired access token
- **THEN** the API returns HTTP 401 with `{"detail": "token_not_valid"}`
- **AND** the client must use the refresh token to obtain a new access token

### Requirement: TimescaleDB hypertable for measurements
The system SHALL create the `core_measurement` PostgreSQL table as a TimescaleDB hypertable partitioned by the `time` column before any measurement data is inserted. This is a migration-time operation, not a runtime operation.

#### Scenario: Hypertable accepts time-range queries
- **WHEN** a row is inserted into `core_measurement`
- **THEN** a query `SELECT * FROM core_measurement WHERE time BETWEEN $1 AND $2` uses the TimescaleDB chunk index and returns correctly

### Requirement: UTC timestamps everywhere
The system SHALL store all timestamps in UTC. The database connection SHALL use `TimeZone = 'UTC'`. Django `USE_TZ = True`. No localtime conversions in the data layer.

#### Scenario: Measurement time is stored as UTC
- **WHEN** a measurement is ingested with a local timestamp
- **THEN** the stored `time` value is in UTC
- **AND** the offset-aware local value is preserved as metadata if provided by the source

### Requirement: AGPL-3.0 license header in every source file
Every new Python and TypeScript/JavaScript source file SHALL include an AGPL-3.0 short-form header comment as the first comment block.

#### Scenario: License header present
- **WHEN** a new `.py` or `.ts`/`.tsx` file is created
- **THEN** the first comment block identifies the project, the license (`AGPL-3.0-or-later`), and links to the full text

### Requirement: Environment configuration via env vars
The system SHALL read all configuration (database URL, secret key, allowed hosts, CORS origins, JWT settings) from environment variables documented in `.env.example`. No secrets committed to the repository.

#### Scenario: Missing required env var is fatal at startup
- **WHEN** Django starts without a required env var (e.g. `SECRET_KEY`)
- **THEN** the process exits immediately with a clear error message
- **AND** it does not start serving requests with an insecure default
