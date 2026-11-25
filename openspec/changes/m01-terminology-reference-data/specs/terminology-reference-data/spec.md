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

### Requirement: Full LOINC release is imported from user-supplied files
The system SHALL import the LOINC core table (Loinc.csv) from user-supplied files with `manage.py import_loinc`, idempotently and in one transaction, SHALL link every imported term to a `Source` recording the release version, and SHALL NOT commit any LOINC content to the repository.

#### Scenario: LOINC release absent
- **WHEN** `import_loinc` runs and the release directory or Loinc.csv is absent
- **THEN** the command fails with a non-zero exit and no traceback
- **AND** the message names `data/vendor/loinc/` and how to obtain the release
- **AND** nothing is written

#### Scenario: LOINC import is idempotent
- **WHEN** `import_loinc` runs twice on the same release
- **THEN** the row count and the stored values are the same after both runs

#### Scenario: LOINC import records its version as Source
- **WHEN** `import_loinc` runs with `--release-version <v>`
- **THEN** every imported term links to `Source(name='LOINC', version=<v>, licence, url='https://loinc.org/license/', retrieved_at)`

#### Scenario: Malformed LOINC release aborts the import
- **WHEN** Loinc.csv lacks a required column or has a row with an empty LOINC_NUM
- **THEN** the whole import is rolled back
- **AND** the error names the file and line

### Requirement: LOINC terms are searchable by name and code
The system SHALL return imported LOINC terms that match a query on loinc_num (exact, case-insensitive, trimmed), long_common_name, short_name or component, using Postgres full-text and trigram matching. Results SHALL be paginated and ranked deterministically (exact code match first, then descending relevance, then loinc_num ascending). Only authenticated users SHALL be able to search. The query SHALL be at most 200 characters after trimming, and searches SHALL be rate-limited per user.

#### Scenario: LOINC search by name
- **WHEN** an authenticated user searches for a word contained in a term's long name
- **THEN** that term is returned

#### Scenario: LOINC search tolerates a typo
- **WHEN** an authenticated user searches with a one-letter misspelling of a word in a term's name
- **THEN** the term is still returned through trigram similarity

#### Scenario: LOINC search by exact code
- **WHEN** an authenticated user searches with `q=<loinc_num>`
- **THEN** the term with that code is the first result

#### Scenario: LOINC search is paginated
- **WHEN** an authenticated user searches
- **THEN** the response has `count`, `next`, `previous` and `results`
- **AND** `page_size` is bounded to a maximum

#### Scenario: LOINC search rejects an empty query
- **WHEN** `q` is missing or only whitespace
- **THEN** the response is HTTP 400 with a plain-language message

#### Scenario: LOINC search rejects an overlong query
- **WHEN** `q` is longer than 200 characters after trimming
- **THEN** the response is HTTP 400 with a plain-language message
- **AND** no database search runs

#### Scenario: LOINC search is rate-limited
- **WHEN** an authenticated user exceeds the `loinc_search` throttle rate
- **THEN** the response is HTTP 429

#### Scenario: LOINC search requires authentication
- **WHEN** an anonymous client searches
- **THEN** the response is HTTP 401

#### Scenario: LOINC search returns provenance
- **WHEN** a term is returned
- **THEN** it includes loinc_num, long_common_name, short_name, component, system, property, scale_type, status and source {name, version, licence, url, retrieved_at}
