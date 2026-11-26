# [M02] Apply Q63: lab result validation states entered | user_confirmed | source_verified | disputed | retracted

Labels: autodev, feature
Milestone: M02
Parent: unknown (Q60)

## Goal
Replace the default states unreviewed | reviewed with Fabio's five states. Only user_confirmed or source_verified results with a laboratory and a method are aggregation-eligible. Owner-only PATCH endpoint to change the state; data migration 0009.

## Spec refs
openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md "Lab result provenance and OMOP MEASUREMENT alignment" (5 new scenarios); Q63, Q75.

## Acceptance
- States and default as in Q63; eligibility depends on state, laboratory and method.
- Migration maps unreviewed to entered and reviewed to user_confirmed, recomputes eligibility, reversible only when no other state is in use.
- PATCH returns 200 for the owner, 400 naming validation_state for entered, source_verified or leaving retracted, 404 for a non-owner.
