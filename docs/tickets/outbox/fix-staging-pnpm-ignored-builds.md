# [M00c] Fix staging: frontend image fails at pnpm install with ERR_PNPM_IGNORED_BUILDS

Labels: autodev, feature
Milestone: M00c
Parent: unknown (see docs/tickets/created/40-m00c-tg2-staging-b-compose.md)

Goal: pin pnpm and declare which dependency build scripts may run so the staging frontend image builds.

Spec refs: dev-process::staging-runs-production-servers

Acceptance:
- `packageManager` pins an exact pnpm version
- build-script policy covers sharp and unrs-resolver
- clean temp `pnpm install --frozen-lockfile` exits 0
- regression test in frontend/src/__tests__/pnpm-build-policy.test.ts
