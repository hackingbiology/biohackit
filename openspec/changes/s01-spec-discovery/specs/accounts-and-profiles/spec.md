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

### Requirement: Personal data erasure
The system SHALL let a user delete their account and personal data, and SHALL state what cannot be recalled once public data has been cloned by a third party. (Source: docs/hackingbiology-project-spec.md § 7; whitepaper § 11 on clonable snapshots. See QUESTIONS.md Q21.)

#### Scenario: Erasure on request
- **WHEN** a user requests deletion
- **THEN** their data is removed from the instance and from later public snapshots

#### Scenario: Clones are disclosed
- **WHEN** the user starts a deletion
- **THEN** the system states that copies already cloned by others are outside its control

### Requirement: Consent to public-by-default is explicit and revocable
The system SHALL record one explicit consent to the public-by-default posture at onboarding, SHALL keep per-item withholding available, and SHALL let the user revoke that consent or withhold or unpublish any item at any time. This refines, and does not replace, the public-by-default requirement. (Source: docs/hackingbiology-project-spec.md § 7 Dati, privacy; the default-private part of that source is superseded, see QUESTIONS.md Q21.)

#### Scenario: Onboarding consent is recorded
- **WHEN** a user completes onboarding
- **THEN** the system stores the user's consent to public-by-default sharing with the time it was given
- **AND** the system explains in plain language that items can be withheld individually

#### Scenario: Revocation withdraws the item
- **WHEN** a user revokes consent or withholds an item
- **THEN** the item is removed from the instance's public pages and from later public snapshots
- **AND** the system states that copies already cloned by others are outside its control (see Q21)
