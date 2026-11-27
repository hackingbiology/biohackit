# [review] Residual medium findings on x01-getbased-import-spec-unit-and-calculated-fix

Labels: autodev

[
 {
  "file": "openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md",
  "line": 14,
  "severity": "medium",
  "claim": "The matching scenario's catch-all 'not recognised' (line 15) does not exempt calculatedRatios-group markers, derivedFrom markers or deletedMarkers that have no mapping row. Those markers would block confirm, which contradicts the scenarios at lines 58-61, 72-75 and 82-86.",
  "fix": "Reword lines 14-15 so the catch-all applies only to markers not covered by another scenario. List the exempt cases: a calculatedRatios-group marker, a key with a deny-list row, a marker with derivedFrom, a marker in deletedMarkers. Name the unit-less measured row case separately. Then write: every other marker with no mapping row is listed as not recognised.",
  "confirmed": true,
  "reason": "Read spec.md lines 1-95. Line 15 says 'every other marker, with no row of any kind' is not recognised, and line 14 exempts only deny-list rows and unit-less measured rows. Line 25 makes not recognised rows block confirm. Lines 61 (deleted), 73-75 (calculatedRatios group) and 86 (derivedFrom) say those markers are excluded from the confirm refusal. A marker in one of those groups with no row matches both rules."
 }
]
