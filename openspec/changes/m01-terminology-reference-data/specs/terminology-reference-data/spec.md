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

#### Scenario: Blank LOINC code
- **WHEN** the LOINC code is empty or whitespace only
- **THEN** persistence fails with a validation error

### Requirement: Three ranges kept separate
The system SHALL store reference, optimal and safety ranges in separate structures and expose them separately.

#### Scenario: Reference-normal but optimal-out
- **WHEN** a value lies inside the reference range and outside the optimal range
- **THEN** the API reports both statuses independently

#### Scenario: Range bounds in analyte unit
- **WHEN** a range row's unit differs from its analyte's unit
- **THEN** persistence fails with a validation error

### Requirement: Optimal range provenance gate
The system SHALL expose an optimal range only if it has source, population, endpoint, evidence grade and last-reviewed date.

#### Scenario: Incomplete provenance
- **WHEN** any of those fields is missing
- **THEN** the range is not returned as optimal

#### Scenario: Complete provenance
- **WHEN** source, population, endpoint, evidence grade and last-reviewed date are all present
- **THEN** the selector returns the range

### Requirement: Ranges are stratified by age band, sex and ancestry
`ReferenceRange` and `OptimalRange` SHALL carry optional `age_min_years` (inclusive), `age_max_years` (exclusive), `sex` and `ancestry`, where null means all. A row applies to a subject only if every non-null stratum field matches; a subject attribute that is unknown (None) matches only rows where that field is null. The selector SHALL return the applicable complete row with the most non-null stratum dimensions (the age band counts as one dimension if either bound is set), and SHALL return none when two or more rows tie at the highest specificity.

#### Scenario: Most specific stratum wins
- **WHEN** an unstratified complete row and a sex-matching complete row exist
- **THEN** the sex-matching row is returned

#### Scenario: Non-matching stratum is excluded
- **WHEN** a row is for another sex or outside the subject's age band
- **THEN** it is never returned

#### Scenario: Unknown subject attribute
- **WHEN** the subject's sex is None
- **THEN** a sex-stratified row is not returned and an unstratified one is

#### Scenario: Tie between equally specific strata
- **WHEN** two complete rows match at the same highest specificity
- **THEN** nothing is returned

#### Scenario: Incomplete specific row does not win
- **WHEN** the most specific matching row lacks provenance
- **THEN** the next most specific complete row is returned

### Requirement: Licence-restricted vocabularies are not bundled
The system SHALL NOT ship SNOMED or the full LOINC table; it SHALL load them only from user-supplied files.

#### Scenario: Seed contents
- **WHEN** the repository seed files are inspected
- **THEN** they contain only openly licensed or explicitly permitted content, with licence noted in `Source`
