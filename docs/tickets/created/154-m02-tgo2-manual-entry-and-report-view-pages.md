# [M02] TG-o part 2: manual entry and report view pages

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: two lab pages on staging. `/labs/new` lets a signed-in user type a lab report by hand; `/labs/reports/<id>` shows one stored report with validation state, aggregation eligibility and range check in words. Frontend only: no backend change, no new dependency, no migration.

Spec refs: m02-blood-layer TG-o; main biomarkers-and-labs "Manual entry of equal standing", "Human review before persistence"; s01 "Import can be rolled back"; Q70, Q75, Q86, Q87.

Acceptance:
- `pnpm --dir frontend lint`, `type-check` and `test:ci` pass.
- The scenario `biomarkers-and-labs::typed-value-gets-the-same-treatment` is declared in `lab-manual-entry.test.tsx` and `lab-report-view.test.tsx`.
- `reported_value` is sent as the exact typed string.
- No change under `backend/`, no change to `package.json` or the lockfile.
