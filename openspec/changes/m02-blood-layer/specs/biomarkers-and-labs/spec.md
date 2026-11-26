## ADDED Requirements

### Requirement: Lab result provenance and OMOP MEASUREMENT alignment
The system SHALL store each lab result as a `LabResult` row, separate from `core.Measurement`, with its laboratory, method, device (when reported), collected and reported timestamps, the value and unit as reported and the normalised value and unit, linked to a LOINC-coded analyte. A `LabResult` SHALL accept a reported unit for which no conversion exists (it is not rejected as `Measurement` rejects it). The system SHALL keep these fields mappable to the columns of the OMOP MEASUREMENT table. A normalised value and unit SHALL be stored when the reported unit equals the analyte's unit or a stored conversion factor exists for the result's analyte and unit pair, as in `s01-spec-discovery` "Unit conversion between unit systems".

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
The system SHALL represent a stored lab report as a FHIR DiagnosticReport and each of its results as a FHIR Observation, carrying the LOINC code, the value with its unit as reported (as UCUM system and code only when the reported unit is valid UCUM, otherwise as text only), and the laboratory and method when known.

#### Scenario: A report exports as DiagnosticReport with Observations
- **WHEN** a lab report with results is exported as FHIR
- **THEN** one DiagnosticReport references one Observation per result
- **AND** each Observation carries the LOINC code and the as-reported value and unit

#### Scenario: Missing provenance is omitted, not invented
- **WHEN** a result has no method or laboratory
- **THEN** the Observation omits those elements

#### Scenario: Non-UCUM reported unit
- **WHEN** a result's reported unit is not valid UCUM
- **THEN** the Observation carries the reported unit as text only, with no UCUM system or code
