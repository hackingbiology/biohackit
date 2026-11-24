## ADDED Requirements

### Requirement: Full personal data export
The system SHALL let a person export their complete record at any time, because the individual, not the platform, owns it. (Source: docs/foundation.md § 3, "Data belongs to the person".)

#### Scenario: Export everything I stored
- **WHEN** a signed-in user requests an export of their data
- **THEN** the system provides all of that user's stored records in a machine-readable form
- **AND** the export does not depend on the user's records being public

#### Scenario: Export is always available
- **WHEN** a user has any stored data
- **THEN** the export action is offered
