## ADDED Requirements

### Requirement: Import from wearable export files
The system SHALL accept wearable data as an uploaded export file (Apple Health, Google Fit, or CSV from Oura and Whoop) and SHALL NOT require a live connection to a wearable provider. (Source: docs/hackingbiology-project-spec.md § 4.2, § 6 M10, § 8.5. A commercial aggregator is a later decision and is not specified here.)

#### Scenario: Upload an export file
- **WHEN** a user uploads a supported wearable export file
- **THEN** the values it contains are stored as measurements with the wearable as the declared source
- **AND** the review step of "Human review before persistence" applies before storage

#### Scenario: Unreadable entries are declared
- **WHEN** an entry in the file cannot be understood
- **THEN** the system lists it as not recognised and does not drop it silently
