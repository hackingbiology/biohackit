# [M00] Repo layout and tooling scaffold

Labels: autodev, feature
Milestone: M00 Foundations
Parent: #3

## Goal

Stand up the technical skeleton that every subsequent module builds on:
a Django 5 backend, a Next.js 15 PWA frontend, Docker Compose for local dev,
a Makefile, and a GitHub Actions CI pipeline.

## Spec refs

- `openspec/changes/m00-foundations/specs/foundations-architecture/spec.md`
  - §Requirement: Monorepo with backend and frontend roots
  - §Requirement: Technology stack
  - §Requirement: CI pipeline on every pull request
  - §Requirement: Environment configuration via env vars
  - §Requirement: AGPL-3.0 license header in every source file

## Work

- `backend/` — Django 5 project skeleton (biohackit package, settings via django-environ,
  DRF + simplejwt + allauth wired, whitenoise for static, pyproject.toml with uv)
- `frontend/` — Next.js 15 App Router + TypeScript strict + Tailwind 4 + pnpm
- `docker-compose.yml` — db (TimescaleDB/pg16), backend, frontend services
- `Makefile` — install / migrate / test / lint / dev targets
- `.env.example` — all required env vars documented
- `.github/workflows/ci.yml` — backend (ruff + pytest) and frontend (eslint + jest) jobs

## Acceptance

Scenario: Fresh-clone dev start
- WHEN a developer clones the repository and runs `docker compose up`
- THEN all services start in one command
- AND the Next.js PWA is reachable at http://localhost:3000
- AND the Django API is reachable at http://localhost:8000/api/

Scenario: Stack pinned in lockfiles
- WHEN a developer installs dependencies
- THEN `uv.lock` and `pnpm-lock.yaml` are present and committed; versions are reproducible
