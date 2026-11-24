## ADDED Requirements

### Requirement: Protocol cost is tracked and shown
The system SHALL compute the cost of a protocol per protocol, per intervention and per blood draw, project it per month, and show "what it costs to follow this protocol" on the public protocol page. (Source: docs/hackingbiology-project-spec.md § 6 M4bis. The source names no price source or currency; see QUESTIONS.md Q18.)

#### Scenario: Monthly projection
- **WHEN** a user views a protocol they follow
- **THEN** the system shows the cost per intervention and per draw and a monthly projection
- **AND** each price shows who entered it

#### Scenario: Cost shown publicly
- **WHEN** a visitor views a public protocol
- **THEN** the page shows what it costs to follow
- **AND** no price is a paid placement (see `community-and-social`, "Knowledge is not for sale")
