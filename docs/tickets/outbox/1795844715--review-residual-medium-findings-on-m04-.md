# [review] Residual medium findings on m04-openspec-change-pills-therapeutics-nutrition-v

Labels: autodev

[
 {
  "file": "openspec/changes/m04-pills-therapeutics-nutrition-exercise/specs/daily-log-and-adherence/spec.md",
  "line": 11,
  "severity": "medium",
  "claim": "The entered amount has no unit requirement, so an exported `quantity` can be paired with a `dose_unit_source_value` from the planned dose that does not match it.",
  "fix": "Add a SHALL: an entered amount is stored with a UCUM unit. It is exported only when its unit equals the unit written to `dose_unit_source_value`; otherwise `quantity` stays empty. Add a scenario for the mismatched-unit case.",
  "confirmed": true,
  "reason": "Line 11 says the unit columns come from the M03 mapping, which takes them from the planned intervention. It also says `quantity` comes from the entered amount. No scenario in the file requires a unit on the entered amount or a match with the planned unit. A user who enters '1' (one capsule) on a 500 mg intervention would export quantity 1 with unit mg."
 }
]
