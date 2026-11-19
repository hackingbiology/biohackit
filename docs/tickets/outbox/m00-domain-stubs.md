# [M00] Base domain model stubs

Labels: autodev, feature
Milestone: M00 Foundations
Parent: #3

## Goal

`core` app with the minimal shared domain: Intervention (with cycle schema), Biomarker (with role)
and Measurement (provenance fields) stored in a TimescaleDB hypertable. Business logic is deferred
to M01 (three ranges, standards) and M03 (interventions).

## Spec refs

- `openspec/specs/domain-model` (Intervention carries a cycle schema; Biomarker with role; Measurement provenance)
- `openspec/changes/m00-foundations/tasks.md` TG3; QUESTIONS Q4 (hypertable now)

## Acceptance

- Pulsed senolytic is representable: `cycle_schema={"pattern":"pulsed","on_days":[1,2,3]}` round-trips intact
- Method and lab are mandatory metadata: Measurement without laboratory AND method is `is_aggregation_eligible=False`
- Biomarker roles efficacy | safety | baseline exist (three-range fields land in M01)
- `core_measurement` is a hypertable on `time` and range queries return inserted rows
