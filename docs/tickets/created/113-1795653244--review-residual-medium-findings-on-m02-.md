# [review] Residual medium findings on m02-tg1b-spec-review-fixes

Labels: autodev

[
 {
  "file": "openspec/changes/m02-blood-layer/specs/biomarkers-and-labs/spec.md",
  "line": 11,
  "severity": "medium",
  "claim": "The M02 scenario says a LabResult without laboratory or method is still stored and flagged, but proposal.md and Q64 put microbiome and DEXA results into LabResult and say s01 applies, while s01 'Result without provenance' says the system asks for the missing provenance before storing.",
  "fix": "Settle the conflict in the M02 delta. Either limit 'still stored and flagged' to blood analytes and have microbiome and DEXA LabResults follow s01 'Result without provenance', or record in proposal.md and Q64 that s01 'Result without provenance' is overridden for LabResult and needs a MODIFIED requirement. List the outcome in TG-a.",
  "confirmed": true,
  "reason": "M02 spec.md:11-14 says a LabResult without lab or method is still stored and flagged. s01 spec.md:77-79 says a microbiome result without lab or method is not stored until the provenance is supplied. proposal.md:53 says microbiome and DEXA lab results are stored as LabResult and that the s01 requirements apply to LabResult. The Relation to s01 note does not mention or resolve this clash. A microbiome LabResult without lab or method is therefore both stored and not stored under the two specs."
 }
]
