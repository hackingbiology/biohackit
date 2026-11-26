# [M02] TG-h part 1: completeness and freshness per organ system API

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: `core.OrganSystemPanel` (sourced, nothing seeded) and owner-only `GET /api/labs/completeness/` giving n of m expected markers and the newest collection date per panel.

Spec refs: main biomarkers-and-labs "Completeness and freshness indicators" (sparse-metabolic-panel); m02-blood-layer TG-h; Q84.

Acceptance: backend/tests/test_lab_completeness.py passes; trace matrix covers the scenario; one migration; gates pass.
