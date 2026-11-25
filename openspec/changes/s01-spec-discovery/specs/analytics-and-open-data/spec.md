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
The system SHALL publish its public dataset snapshot and its content under open licences and SHALL state the licence alongside each published artefact. (Source: docs/foundation.md § 3, "Open by code and by data"; docs/slides/hacking-biology-project-presentation.pdf § page 9, AGPL-3.0 software and a Creative Commons licence for material. The source does not name the licences; see QUESTIONS.md Q16.)

#### Scenario: Snapshot states its licence
- **WHEN** a third party downloads the public snapshot
- **THEN** the download states the open licence that applies to it

#### Scenario: Content states its licence
- **WHEN** a user views published content
- **THEN** the applicable open licence is reachable from that page

### Requirement: Analytics pipeline works on pseudonymised data
The system SHALL run cohort analytics on pseudonymised records, with identifiers held apart from the analytic data. (Source: docs/hackingbiology-project-spec.md § 7.)

#### Scenario: Analytics input carries no direct identifier
- **WHEN** a cohort analysis runs
- **THEN** its input records carry a pseudonym and no name or contact detail

### Requirement: Public data is published as linked data
The system SHALL publish everything public as linked data, with its entities coded and linked to each other and to external vocabularies, sufficient to seed an independent instance. (Source: whitepaper § 11 Openness, "Open & linked data". The source names no serialisation; see QUESTIONS.md Q24.)

#### Scenario: Entities are coded and linked
- **WHEN** a third party reads the public dataset
- **THEN** each public entity carries its standard codes and a link to every public entity it references, and no identifier or link for a withheld entity
- **AND** the dataset contains no reference to a withheld item

#### Scenario: Linked data seeds an instance
- **WHEN** an independent instance imports the linked data
- **THEN** it reproduces the public entities and their links without access to the origin instance
