## ADDED Requirements

### Requirement: Lab result provenance and OMOP MEASUREMENT alignment
The system SHALL store each lab result as a `LabResult` row, separate from `core.Measurement`, with its source (its `LabReport` and the report's origin: manual entry or a named import), a validation state, its laboratory, method, device (when reported), collected and reported timestamps, the value and unit as reported and the normalised value and unit, linked to a LOINC-coded analyte. A `LabResult` SHALL accept a reported unit for which no conversion exists (it is not rejected as `Measurement` rejects it). The system SHALL keep these fields mappable to the columns of the OMOP MEASUREMENT table. A normalised value and unit SHALL be stored when the reported unit equals the analyte's unit or a stored conversion factor exists for the result's analyte and unit pair, as in `s01-spec-discovery` "Unit conversion between unit systems". A blood-analyte `LabResult` persisted without a laboratory or method SHALL be stored and flagged as not aggregation-eligible, as domain-model "Measurement provenance" requires of `Measurement`. For a `LabResult` whose analyte is a body-composition (DEXA) or microbiome analyte, the system SHALL ask for the missing laboratory or method before storing it, as in `s01-spec-discovery` "Body composition and microbiome results are accepted as measurements", scenario "Result without provenance" (Q66). The validation state values are not defined by domain-model or code; the default is `unreviewed` | `reviewed` (Q63).

#### Scenario: A result records its source
- **WHEN** a lab result is persisted
- **THEN** it references its `LabReport` and the report's origin (manual entry or a named import)
- **AND** it carries a validation state

#### Scenario: A result without laboratory or method is not aggregation-eligible
- **WHEN** a blood-analyte `LabResult` is persisted without a laboratory or method
- **THEN** it is still stored
- **AND** it is flagged as not aggregation-eligible

#### Scenario: A DEXA or microbiome result without provenance is not stored
- **WHEN** a user submits a DEXA or microbiome `LabResult` without a laboratory or method
- **THEN** the system asks for the missing provenance before it is stored
- **AND** no `LabResult` row is created until it is supplied

#### Scenario: A stored result keeps the reported value
- **WHEN** a lab result is persisted
- **THEN** the as-reported value and unit are stored on the result

#### Scenario: Reported unit equals the analyte unit
- **WHEN** a result's reported unit equals the analyte's unit
- **THEN** the normalised value equals the reported value, with no conversion factor needed

#### Scenario: A stored factor yields the normalised value
- **WHEN** a result's unit differs from the analyte's unit and a conversion factor is stored for the result's analyte and unit pair
- **THEN** the normalised value and unit are stored using that factor

#### Scenario: No conversion factor leaves the normalised value empty
- **WHEN** a result's unit differs from the analyte's unit and no conversion factor is stored for the result's analyte and unit pair
- **THEN** the normalised value and unit are left empty
- **AND** the result is still persisted with the as-reported value and unit

#### Scenario: Collected and reported times are distinct
- **WHEN** a report states both a collection time and a report time
- **THEN** both are stored separately on the result
- **AND** a missing one is stored as empty, never filled with the other

#### Scenario: A result maps to OMOP MEASUREMENT
- **WHEN** a stored result is exported in OMOP MEASUREMENT shape
- **THEN** every exported column has a documented source field
- **AND** a column with no source field is left empty

### Requirement: FHIR representation of a stored lab result
The system SHALL represent a stored lab report as a FHIR DiagnosticReport and each of its results as a FHIR Observation, carrying the LOINC code, the value with its unit as reported (as UCUM system `http://unitsofmeasure.org` and code only when the reported unit is valid UCUM, otherwise as text only), and the laboratory and method when known. In this requirement a reported unit is valid UCUM if and only if the reported unit string exactly equals the `ucum_code` of a stored terminology `Unit` row.

#### Scenario: A report exports as DiagnosticReport with Observations
- **WHEN** a lab report with results is exported as FHIR
- **THEN** one DiagnosticReport references one Observation per result
- **AND** each Observation carries the LOINC code and the as-reported value and unit

#### Scenario: Observation carries laboratory and method when known
- **WHEN** a result has a laboratory and a method and is exported as FHIR
- **THEN** the Observation carries the laboratory and the method

#### Scenario: Missing provenance is omitted, not invented
- **WHEN** a result has no method or laboratory
- **THEN** the Observation omits those elements

#### Scenario: Reported unit matches a stored UCUM unit
- **WHEN** a result's reported unit string exactly equals the `ucum_code` of a stored terminology `Unit`
- **THEN** the Observation carries system `http://unitsofmeasure.org` and that code

#### Scenario: Non-UCUM reported unit
- **WHEN** a result's reported unit string equals no stored terminology `Unit.ucum_code`
- **THEN** the Observation carries the reported unit as text only, with no UCUM system or code

### Requirement: Lab report import can be rolled back
The system SHALL let a user roll back a lab report import. Rolling back SHALL remove every `LabResult`, the `LabReport` and the retained original report file stored with it, all created by that import, and SHALL leave `LabResult` rows from other imports and from manual entry untouched. This applies `s01-spec-discovery` "Import can be rolled back" to `LabResult`.

#### Scenario: Rollback removes the import's results and report
- **WHEN** a user rolls back an import that created a `LabReport` with results
- **THEN** that `LabReport` and all its `LabResult` rows are removed

#### Scenario: Rollback leaves other results untouched
- **WHEN** a user rolls back one import
- **THEN** `LabResult` rows from other imports and from manual entry remain unchanged

#### Scenario: Rollback removes the retained original
- **WHEN** a user rolls back an import whose original report file was retained
- **THEN** that stored file is removed together with the `LabReport`, so no uploaded document is left behind
