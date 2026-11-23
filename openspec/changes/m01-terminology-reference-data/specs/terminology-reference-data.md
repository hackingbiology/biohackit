# Terminology & Reference Data (delta)

## ADDED Requirements

### Requirement: Every reference row carries its source
The system SHALL store a `Source` (name, version, licence, URL, retrieval date) for every terminology, unit, conversion and range row, and SHALL refuse to persist or seed a row without one.

#### Scenario: Unsourced seed row
- **WHEN** the seed loader reads a row with no source
- **THEN** it aborts with an error naming the row
- **AND** nothing from that file is committed

### Requirement: Units are UCUM and conversions deterministic
The system SHALL validate units against stored UCUM codes and convert values with stored, sourced factors only, retaining the as-reported value and unit next to the normalised one.

#### Scenario: Conversion
- **WHEN** a value is normalised twice from the same input
- **THEN** results are identical and both as-reported and normalised values are kept

#### Scenario: Unknown unit
- **WHEN** a unit is not a known UCUM code
- **THEN** it is rejected (never silently stored as free text)

### Requirement: Analyte registry requires LOINC and UCUM
The system SHALL require a LOINC code and a UCUM unit on every analyte, and a measurement SHALL link to such an analyte.

#### Scenario: Missing code
- **WHEN** an analyte or measurement lacks LOINC or UCUM unit
- **THEN** persistence fails with a validation error

### Requirement: Three ranges kept separate
The system SHALL store reference, optimal and safety ranges in separate structures and expose them separately.

#### Scenario: Reference-normal but optimal-out
- **WHEN** a value lies inside the reference range and outside the optimal range
- **THEN** the API reports both statuses independently

### Requirement: Optimal range provenance gate
The system SHALL expose an optimal range only if it has source, population, endpoint, evidence grade and last-reviewed date.

#### Scenario: Incomplete provenance
- **WHEN** any of those fields is missing
- **THEN** the range is not returned as optimal

### Requirement: Licence-restricted vocabularies are not bundled
The system SHALL NOT ship SNOMED or the full LOINC table; it SHALL load them only from user-supplied files.

#### Scenario: Seed contents
- **WHEN** the repository seed files are inspected
- **THEN** they contain only openly licensed or explicitly permitted content, with licence noted in `Source`
