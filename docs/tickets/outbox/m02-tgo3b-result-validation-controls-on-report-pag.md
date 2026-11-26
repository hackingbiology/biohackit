# [M02] TG-o part 3: validation controls on the report page

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: on `/labs/reports/<id>` the owner can confirm, dispute or withdraw each result through the existing `PATCH /api/labs/results/<id>/validation/`. Withdraw asks first and cannot be undone. `source_verified` is never offered. Frontend only: no backend change, no new dependency, no migration.

Spec refs: m02-blood-layer TG-o; biomarkers-and-labs "Lab result provenance and OMOP MEASUREMENT alignment"; Q63, Q75, Q86, Q87, Q89.

Acceptance:
- `pnpm --dir frontend lint`, `typecheck`, `test` and `build` pass.
- Scenarios `the-owner-confirms-a-result`, `a-retracted-result-is-kept-but-excluded` and `source-verification-cannot-be-self-declared` are declared in `lab-report-validation.test.tsx`.
- No change under `backend/`, no change to `package.json` or the lockfile.
