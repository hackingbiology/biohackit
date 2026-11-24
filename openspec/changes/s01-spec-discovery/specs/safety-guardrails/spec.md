## ADDED Requirements

### Requirement: Platform describes and never prescribes
The system SHALL tell a user what to measure and SHALL NOT tell a user what to take or how much; no surface, including AI-generated text, issues a recommendation of a compound or dose. (Source: whitepaper § 07 Harm reduction; docs/foundation.md § 3 and § 7.)

#### Scenario: Monitoring guidance names markers, not treatments
- **WHEN** the platform shows safety guidance for an active compound
- **THEN** it lists the markers to measure and why
- **AND** it does not recommend a compound or a dose

#### Scenario: Dose guidance is a plausibility check only
- **WHEN** a dose is checked
- **THEN** the result is framed as a guardrail against an implausible entry, not as clinical advice
