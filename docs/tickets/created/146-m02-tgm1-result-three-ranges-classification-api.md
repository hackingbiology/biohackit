# [M02] TG-m part 1: a stored lab result against its three ranges (GET /api/labs/results/<id>/ranges/)

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: owner-only API returning reference range, optimal range (only if `displayable_optimal_range` passes) and safety threshold as three separate objects, each with provenance and a computed status (inside, below, above, not_comparable, no_range). No new dependency, no migration, no seeded data.

Spec refs: biomarkers-and-labs "Three ranges per analyte", "Optimal-range governance" (inspection part).

Acceptance: scenarios a-value-near-the-optimal-edge-but-within-reference and inspecting-an-optimal-range are tested; Q82 records the defaults.
