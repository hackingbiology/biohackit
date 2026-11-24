# [M00c] Staging part B: docker-compose.staging.yml on port 18800
Labels: autodev, feature
Milestone: M00c
Parent: #34

Goal: public, password-less staging stack (gunicorn, production Next server, DEBUG off, noindex, demo account only), single published port 18800.

Spec refs: openspec/changes/m00c-autodev-v2/specs/dev-process/spec.md (Public staging environment).

Acceptance: scenarios dev-process::staging-runs-production-servers, staging-not-indexed, staging-holds-only-demo-data, staging-single-port have tests; gates green.
