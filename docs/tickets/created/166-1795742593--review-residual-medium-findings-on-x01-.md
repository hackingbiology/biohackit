# [review] Residual medium findings on x01-getbased-archive-format-and-import-spec-b

Labels: autodev

[
 {
  "file": "openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md",
  "line": 4,
  "severity": "medium",
  "claim": "No scenario requires the unit on a mapping row to cite the get-based catalogue unit at a commit, so a wrong unit can be attached to a correct number.",
  "fix": "Add a scenario: each mapping row records the get-based catalogue unit with a path and commit citation. The importer stores the value only in that unit, or converts it through UCUM. A row with no cited unit is shown as 'not recognised: unit not verified'.",
  "confirmed": true,
  "reason": "Q93 (QUESTIONS.md:276) says the unit is a column of the mapping row and the archive carries no unit or catalogue version. Line 4 and the scenarios I grepped contain no requirement that the unit cite or match the get-based catalogue. The scenarios I did not read are lines 5-59 and 69 onward, so the grep may have missed one. A mismatched unit would store wrong data that looks complete, which conflicts with frozen criterion 2."
 },
 {
  "file": "openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md",
  "line": 66,
  "severity": "medium",
  "claim": "The calculated-ratios scenario contradicts itself: it excludes keys 'marked as calculated in the mapping table' but also says the mapping table refuses rows for those keys.",
  "fix": "Allow a deny-list row in the mapping table (no Biomarker, cited reason) that marks a key as 'not imported: calculated'. Have the table refuse only measured mapping rows for those keys. Reword lines 66-68 and Q99 to match.",
  "confirmed": true,
  "reason": "Line 66 says a key can be 'marked as calculated in the mapping table'. Line 68 and Q99 (QUESTIONS.md:288) say the table 'refuses rows for those keys'. Both cannot hold. Only the calculatedRatios group prefix remains as a trigger, so any other calculated key without derivedFrom cannot be expressed. That conflicts with the requirement that calculated markers are never stored as measured."
 }
]
