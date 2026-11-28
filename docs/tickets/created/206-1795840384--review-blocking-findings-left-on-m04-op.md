# [review] Blocking findings left on m04-openspec-change-pills-therapeutics-nutrition-e

Labels: autodev

[
 {
  "file": "openspec/changes/m04-pills-therapeutics-nutrition-exercise/specs/pills-management/spec.md",
  "line": 61,
  "severity": "high",
  "claim": "The export scenario maps every intake event to a DRUG_EXPOSURE row. Intake events include skipped and missed states, so the export would record exposures that never happened.",
  "fix": "Limit DRUG_EXPOSURE to intake events marked done. Add a scenario: a skipped or missed intake writes no DRUG_EXPOSURE row, and any MedicationAdministration exported has status not-done. For a partial intake, use only a user-entered amount or leave quantity empty.",
  "confirmed": true,
  "reason": "Line 61 reads \"each event maps to a MedicationAdministration and a DRUG_EXPOSURE row\" with no state filter. tasks.md defines intake events with four-state adherence (done, partial, skipped, missed). Exporting non-done events as drug exposures is false data."
 }
]
