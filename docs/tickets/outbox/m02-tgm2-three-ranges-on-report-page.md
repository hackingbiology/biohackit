# [M02] TG-m part 2: three ranges on the report page

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

## Goal
`/labs/reports/<id>` shows each result against its laboratory reference range, longevity-optimal range and safety threshold, separately, with status in words, source, and the optimal range's provenance in one interaction. Uses the existing `GET /api/labs/results/<id>/ranges/`. Frontend only.

## Spec refs
main biomarkers-and-labs "Three ranges per analyte", "Optimal-range governance"; change m02-blood-layer TG-m; Q88.

## Acceptance
- `frontend/src/components/ResultRanges.tsx` and `frontend/src/__tests__/lab-result-ranges.test.tsx` declare both scenarios.
- No backend, package.json or lockfile change.
- Gates pass.
