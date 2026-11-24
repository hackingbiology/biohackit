# Ecosystem scan — M00 foundations (retroactive)

Method, decision categories and licence table: [README.md](README.md). Change: `openspec/changes/m00-foundations`. Projects are those in `backend/pyproject.toml`, `frontend/package.json`, the M00 proposal and `docs/getbased-reuse-analysis.md`. All facts were fetched on 2026-11-24 (commands in the README); "last activity" is the GitHub `pushed_at` date. No give-back item was found (see [GIVEBACK.md](GIVEBACK.md)).

Not in scope of this scan: a PWA/service-worker library (none is in `frontend/package.json` today), and dev-only tooling (pytest, ruff, jest, eslint, typescript).

## Backend

### Django
- **URL:** https://github.com/django/django
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-23
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/django/django and pypi.org/pypi/Django/json (license_expression), 2026-11-24

### Django REST framework
- **URL:** https://github.com/encode/django-rest-framework
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Verified:** pypi.org/pypi/djangorestframework/json (license_expression); api.github.com reported `NOASSERTION` for the licence, so PyPI is the source; pushed_at from api.github.com, 2026-11-24

### djangorestframework-simplejwt
- **URL:** https://github.com/jazzband/djangorestframework-simplejwt
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-23
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/jazzband/djangorestframework-simplejwt and pypi.org (license field `MIT`), 2026-11-24

### django-allauth
- **URL:** https://codeberg.org/allauth/django-allauth
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-13
- **Decision:** adopt as dependency
- **Verified:** pypi.org/pypi/django-allauth/json (license_expression, Source URL); api.github.com/repos/pennersr/django-allauth for pushed_at (GitHub repo, not the Codeberg source URL), 2026-11-24

### psycopg
- **URL:** https://github.com/psycopg/psycopg
- **Licence:** LGPL-3.0
- **AGPL-compatible:** yes (LGPL-3.0, used as an unmodified library)
- **Last activity:** 2026-11-23
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/psycopg/psycopg and pypi.org (license_expression `LGPL-3.0-only`), 2026-11-24

### django-environ
- **URL:** https://github.com/joke2k/django-environ
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-09-16
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/joke2k/django-environ and pypi.org (license field `MIT`), 2026-11-24

### django-timescaledb
- **URL:** https://github.com/jamessewell/django-timescaledb
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0), but the PyPI classifier says BSD while its licence text says Apache-2.0; GitHub says Apache-2.0
- **Last activity:** 2025-04-10
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/schlunsen/django-timescaledb (redirects to jamessewell/django-timescaledb) and pypi.org/pypi/django-timescaledb/json, 2026-11-24. Last push is over seven months old; watch for a maintained fork.

### whitenoise
- **URL:** https://github.com/evansd/whitenoise
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-13
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/evansd/whitenoise and pypi.org (license_expression), 2026-11-24

### gunicorn
- **URL:** https://github.com/benoitc/gunicorn
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-12
- **Decision:** adopt as dependency
- **Verified:** pypi.org/pypi/gunicorn/json (license_expression); api.github.com reported `NOASSERTION`, so PyPI is the source; pushed_at from api.github.com, 2026-11-24

## Database

### PostgreSQL
- **URL:** https://github.com/postgres/postgres
- **Licence:** unknown
- **Licence note:** PostgreSQL licence (permissive text in the COPYRIGHT file); GitHub returned no SPDX id (`NOASSERTION`)
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (the licence is not on the fetched GNU list page)
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Provisional:** yes, until the AGPL question is answered (README rule on separate-process servers). Images used: `timescale/timescaledb-ha:pg16` (docker-compose.yml:3, docker-compose.staging.yml:5) and `timescale/timescaledb:latest-pg16` (.github/workflows/ci.yml:14); both bundle PostgreSQL.
- **Verified:** raw.githubusercontent.com/postgres/postgres/master/COPYRIGHT and api.github.com/repos/postgres/postgres (GitHub mirror), 2026-11-24. Runs as a separate server process, not linked into our code.

### TimescaleDB
- **URL:** https://github.com/timescale/timescaledb
- **Licence:** unknown
- **Licence note:** Apache-2.0 outside `tsl/`; Timescale License inside `tsl/` (mixed, no single SPDX id; GitHub returned `NOASSERTION`)
- **AGPL-compatible:** Apache-2.0 part yes; Timescale License part unknown — question in docs/QUESTIONS.md
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Provisional:** yes, until the AGPL question is answered. Images: `timescale/timescaledb-ha:pg16` (docker-compose.yml:3, docker-compose.staging.yml:5) and `timescale/timescaledb:latest-pg16` (.github/workflows/ci.yml:14). Whether those builds include `tsl/` is unknown (docker not available to inspect them).
- **Verified:** raw.githubusercontent.com/timescale/timescaledb/main/LICENSE and api.github.com (`NOASSERTION`), 2026-11-24. Runs as a database extension in a separate server process; M00 uses a hypertable only.

## Frontend

### Next.js
- **URL:** https://github.com/vercel/next.js
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/vercel/next.js and registry.npmjs.org/next (license `MIT`), 2026-11-24

### React
- **URL:** https://github.com/react/react
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/facebook/react (redirects to react/react) and registry.npmjs.org/react, 2026-11-24

### Tailwind CSS
- **URL:** https://github.com/tailwindlabs/tailwindcss
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/tailwindlabs/tailwindcss and registry.npmjs.org/tailwindcss, 2026-11-24

## Process and prior art

### OpenSpec
- **URL:** https://github.com/Fission-AI/OpenSpec
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-24
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/Fission-AI/OpenSpec and registry.npmjs.org/@fission-ai%2Fopenspec (npm package `@fission-ai/openspec`), 2026-11-24

### get-based
- **URL:** https://github.com/elkimek/get-based
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-22
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/elkimek/get-based, 2026-11-24. No get-based code is imported in M00. Component-level reuse (biomarker schema, import pipeline) is analysed in `docs/getbased-reuse-analysis.md` and belongs to later module scans.
