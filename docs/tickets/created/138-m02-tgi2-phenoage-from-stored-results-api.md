# [M02] TG-i part 2: PhenoAge from a user's stored lab results through an owner-only API
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: connect the PhenoAge engine to stored LabResults by LOINC code, with stored unit conversions only, behind an owner-only endpoint.
Spec refs: openspec/changes/m02-blood-layer TG-i; scenario biomarkers-and-labs::phenoage-from-routine-bloods; Q56, Q63, Q75, Q77, Q79.
Acceptance: API equals the engine; refusals for missing, ambiguous, unconvertible, excluded; owner-only; nothing stored. Follow-up: verify LOINC codes (loinc.org returned 403) and fill the map.
