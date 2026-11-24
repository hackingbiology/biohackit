## ADDED Requirements

### Requirement: Research API answers intervention-by-biomarker queries
The system SHALL offer a documented research endpoint that, given an intervention and a biomarker, returns de-identified cohort data with its methodological caveats attached. (Source: whitepaper § 11 Openness.)

#### Scenario: Ask for an intervention and a biomarker
- **WHEN** a researcher requests the cohort result for an intervention and a biomarker
- **THEN** the response contains de-identified cohort data for that pair
- **AND** the response carries its caveats, including the four attributes required by `scientific-method-and-evidence`

#### Scenario: No identifying data in the response
- **WHEN** the research endpoint returns data
- **THEN** it contains no direct identifier of any contributor
- **AND** it applies the minimum cohort thresholds of "Aggregated research export uses only well-coded data", suppressing or marking not determinable any cohort below them

### Requirement: Open licences declared on published data and content
The system SHALL publish its public dataset snapshot and its content under open licences and SHALL state the licence alongside each published artefact. (Source: docs/foundation.md § 3, "Open by code and by data". The source does not name the licences; see QUESTIONS.md Q16.)

#### Scenario: Snapshot states its licence
- **WHEN** a third party downloads the public snapshot
- **THEN** the download states the open licence that applies to it

#### Scenario: Content states its licence
- **WHEN** a user views published content
- **THEN** the applicable open licence is reachable from that page
