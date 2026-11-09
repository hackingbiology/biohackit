# M00 Foundations — OpenSpec Change Proposal

**Author:** autodev  
**Date:** 2026-11-09  
**Module issue:** #3  
**Capabilities in scope:** `accounts-and-profiles`, `domain-model` (foundation subset), `data-standards-and-typing` (typing infrastructure only)

---

## Goal

Stand up the technical skeleton that every subsequent module builds on:

- **Monorepo** with `backend/` (Django 5) and `frontend/` (Next.js 15 PWA).
- **Database:** PostgreSQL 16 + TimescaleDB 2.x, `pgcrypto` extension; migrations committed.
- **CI:** GitHub Actions runs on every PR — ruff + pytest (backend) and ESLint + Jest (frontend); no red tests merge.
- **Auth:** JWT-based API auth (djangorestframework-simplejwt) with allauth for email+password registration; OAuth stubs for a later iteration.
- **User + Profile models** implementing the accounts-and-profiles SHALL scenarios that gate all subsequent work (server-required account, public-by-default, biological attributes, social handles).
- **Domain model stubs** for Intervention, Biomarker, and Measurement — just enough schema for M01+ to build on; no business logic yet.
- **TimescaleDB hypertable** for `Measurement` declared and migrated (empty).
- **Next.js PWA shell** — App Router, TypeScript strict, Tailwind 4, mobile-first baseline; sign-in / sign-up pages wired to the JWT API.

## What this enables

| Unlocks | Needed by |
|---|---|
| Authenticated user + profile | every subsequent module |
| `Biomarker` stub table | M01 terminology tables extend it |
| `Measurement` hypertable | M02 lab ingestion writes into it |
| CI pipeline | all future green-gate requirements |
| Public-by-default profile + data model | M07 (evidence), M09 (community) |

## Decisions taken (defaults; Fabio may reverse)

| # | Decision | Default | Rationale |
|---|---|---|---|
| D1 | Email-only auth (no username) | email-primary | Simpler, less confusion; allauth supports it |
| D2 | OAuth providers in M00 | stubbed, not live | Avoids secret management complexity at scaffold; enabled in M13 hardening |
| D3 | Frontend package manager | pnpm | Speed + disk efficiency in CI |
| D4 | Python dependency management | uv + pyproject.toml | Fast, reproducible, modern |
| D5 | Local dev orchestration | Docker Compose | Single `docker compose up` → PG + TimescaleDB + Django + Next.js |
| D6 | Backend linting | ruff (lint + format) | Replaces flake8 + black in one tool |
| D7 | Frontend testing | Jest + Playwright | Jest for unit/component, Playwright for critical E2E paths |
| D8 | TimescaleDB setup | in M00 migrations | Avoids a painful later migration; hypertable is empty until M02 |
| D9 | UTC everywhere | yes | No timezone ambiguity in measurements or logs |
| D10 | AGPL-3.0 header | in every new source file | License compliance from day one |

## Open questions flagged to Fabio

See `docs/QUESTIONS.md` entries dated 2026-11-09, M00.

## Spec delta

A new spec `foundations-architecture.md` is added to this change's `specs/` to capture the technical architecture not covered by the functional specs. No existing spec file is modified; the functional requirements in `accounts-and-profiles` and `domain-model` are already correct.

## Acceptance

This module is done when:

1. `docker compose up` starts cleanly on a fresh clone.
2. `make test` (backend) passes all tests listed in `tasks.md` TG5.
3. `make lint` exits 0 (ruff + ESLint).
4. The Next.js sign-up and sign-in pages work end-to-end against the JWT API.
5. A newly registered user has a public-by-default profile with biological attribute fields.
6. The `Measurement` hypertable exists and accepts an insert.
7. CI passes on a fresh PR branch.
