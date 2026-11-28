## ADDED Requirements

### Requirement: Therapy parameters have a unit and no unsourced default
The system SHALL store each typed therapy parameter with a unit and SHALL NOT supply a default value or a permitted range for it unless one is stored with a cited source (Q148). Parameters of a therapy without a cited source SHALL be entered by the user as free values.

#### Scenario: No default dose or range
- **WHEN** a therapy type is created
- **THEN** its parameters have names and units but no default value and no permitted range
- **AND** a value or range appears only where a source is stored with it

#### Scenario: Value stored with its unit
- **WHEN** a user enters a parameter value for a session type
- **THEN** the value is stored together with its unit
- **AND** a value without a unit is refused

### Requirement: Therapy sessions follow a typed cadence
The system SHALL store a therapy's session cadence in the same typed form as an intake cadence (mode, days of the week, interval in days) and compute due sessions from it deterministically.

#### Scenario: Weekly sessions
- **WHEN** a therapy has a cadence of two named days of the week
- **THEN** a session is due on each of those days
- **AND** sessions appear in the calendar with an in-app reminder (Q144)
