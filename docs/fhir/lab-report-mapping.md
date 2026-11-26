# FHIR export of a stored lab report: element mapping

Code: `backend/core/fhir.py` (`lab_report_to_fhir_bundle`, `render_fhir_json`). Hand-written, no
HL7 library and no new dependency (Q55). Spec: M02 "FHIR representation of a stored lab result".

## Spec checked

FHIR R4, v4.0.1, fetched 2026-11-26 from hl7.org:

- https://hl7.org/fhir/R4/diagnosticreport.html
- https://hl7.org/fhir/R4/observation.html
- https://hl7.org/fhir/R4/datatypes.html (Quantity, CodeableConcept, Coding)
- https://hl7.org/fhir/R4/organization.html
- https://hl7.org/fhir/R4/bundle.html
- https://hl7.org/fhir/R4/valueset-diagnostic-report-status.html
- https://hl7.org/fhir/R4/valueset-observation-status.html

Only the first part of the long pages was read by the fetch tool; every element used below was
seen in what was read. `resourceType` is the FHIR JSON type marker.

## Form: collection Bundle

A `Bundle` of `type: collection` holds the DiagnosticReport, one Observation per result and one
Organization per distinct laboratory. Reason: `Bundle.entry.fullUrl` may be a `urn:uuid`, so
references resolve inside one document, and an Organization can be shared by several
Observations (contained resources could not be nested). The urn:uuid values are
`uuid5` of the table and primary key, so the output is stable.

## Elements

| Resource.element | Source |
|---|---|
| Bundle.resourceType, Bundle.type | fixed `Bundle`, `collection` |
| Bundle.entry, entry.fullUrl, entry.resource | one per resource; fullUrl = uuid5 of `LabReport.pk`, `LabResult.pk` or report pk + laboratory |
| DiagnosticReport.resourceType | fixed |
| DiagnosticReport.status | fixed `unknown`: required 1..1, nothing stored says it (Q73) |
| DiagnosticReport.code (`text`) | fixed label "Laboratory report": required 1..1, no stored code is invented (Q73) |
| DiagnosticReport.result | one reference per `LabResult` of the report, ordered by pk |
| Observation.resourceType | fixed |
| Observation.status | fixed `unknown`: required 1..1 (Q73) |
| Observation.code (`coding.system`, `coding.code`) | `http://loinc.org`, `Biomarker.loinc_code` |
| Observation.valueQuantity (`value`) | `LabResult.reported_value`, exact decimal, not rounded. Trailing zeros of the 6-decimal column are dropped (7 is written `7`, not `7.000000`); the lab's original text precision (e.g. `7.0`) is not stored, so it cannot be reproduced |
| Observation.valueQuantity.system, `code` | `http://unitsofmeasure.org`, `Unit.ucum_code` via `reported_unit_ref`; only when `reported_unit` exactly equals a stored `ucum_code` |
| Observation.valueQuantity.unit | `LabResult.reported_unit`, only when no stored `ucum_code` matches |
| Observation.effectiveDateTime | `LabResult.collected_at` (UTC), only when set |
| Observation.issued | `LabResult.reported_at` (UTC), only when set; kept separate from effectiveDateTime |
| Observation.method (`text`) | `LabResult.method`, only when non-empty |
| Observation.performer | reference to an Organization, only when `LabResult.laboratory` is non-empty (Q73) |
| Organization.resourceType, Organization.name | fixed; `LabResult.laboratory` (which `LabResult.save` fills from `LabReport.laboratory` when the result has none) |

Not emitted, no source field: DiagnosticReport.subject, issued, performer, category, effective[x],
Observation.subject, specimen, device, interpretation, referenceRange, comparator. The stored
`device`, normalised value and validation state have no mapping yet.

`Quantity.value` is a decimal; the endpoint writes it as a JSON number with the stored digits
(`render_fhir_json`), never as a string or a float.
