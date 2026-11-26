# [M02] TG-b: manual lab entry API with plausibility flag

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: authenticated `POST /api/labs/reports/` (origin=manual) and owner-only GET, using the same LabReport/LabResult save path as imports, plus a deterministic plausibility flag from stored cited ReferenceRange rows (Q70).

Spec refs: biomarkers-and-labs "Manual entry of equal standing" / "Typed value gets the same treatment".

Acceptance: typed value equals a directly created LabResult in provenance, validation state, eligibility and normalisation; one invalid result stores nothing (400 naming field); within/outside/not_checked tests; auth and ownership tests; no new dependency, no seeded ranges.
