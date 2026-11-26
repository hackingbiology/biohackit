# [review] Residual medium findings on m02-tg1-blood-layer-openspec-change

Labels: autodev

[
 {
  "file": "openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md",
  "line": 4,
  "severity": "medium",
  "claim": "LabResult lacks the source, validation state and aggregation-eligibility rules that domain-model requires of every Measurement.",
  "fix": "Require LabResult to store its source (the import or manual entry, and its LabReport) and a validation state. Add a scenario: a result persisted without a laboratory or method is flagged as not aggregation-eligible.",
  "confirmed": true,
  "reason": "The delta requirement at line 4 lists laboratory, method, device, timestamps, values and units, but has no source, validation state or eligibility flag. domain-model 'Measurement provenance' (openspec/specs/domain-model/spec.md:62-68) puts those rules on `Measurement` only. tasks.md TG-a says to implement it without restating it, on a model the requirement does not name."
 },
 {
  "file": "openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md",
  "line": 34,
  "severity": "medium",
  "claim": "The FHIR requirement depends on deciding whether a reported unit is valid UCUM, but the repo has no validator and TG-j does not list a blocker.",
  "fix": "Define 'valid UCUM' in the spec as 'matches a stored terminology Unit ucum_code', or add a UCUM validation TG as a blocker of TG-j.",
  "confirmed": true,
  "reason": "The spec at lines 34 and 45-47 gates the UCUM system and code on 'valid UCUM'. tasks.md TG-j lists only 'Blocked by: Q55, TG-a'. I did not re-check backend/terminology/services.py for a validator, so the missing-validator part is taken from the finding. The spec itself gives no validity rule."
 },
 {
  "file": "openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md",
  "line": 4,
  "severity": "medium",
  "claim": "A LabResult model separate from core.Measurement conflicts with s01 requirements on rollback and on keeping results in one time-series model, and no MODIFIED requirement covers it.",
  "fix": "Add MODIFIED requirements, or a delta note, so that s01 'Import can be rolled back' and the same-time-series requirement name LabResult. Alternatively let LabResult feed Measurement rows.",
  "confirmed": true,
  "reason": "The delta line 4 and proposal D10 make LabResult separate from Measurement, and the delta has no MODIFIED section. tasks.md TG-c adds rollback for imports. The finding cites s01 rollback ('measurements that import created') and the s01 same-time-series requirement for blood analytes. I did not open the s01 spec to confirm that wording, so it is taken from the finding. Rollback and DEXA results would then target a different model from blood results."
 }
]
