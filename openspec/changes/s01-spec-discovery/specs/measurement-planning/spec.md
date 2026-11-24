## ADDED Requirements

### Requirement: Lab request generated from a pooled draw
The system SHALL generate, from the analytes pooled into one draw, a request the user can take to a laboratory. (Source: docs/hackingbiology-project-spec.md § 4.1 journey C. The source gives no format; see QUESTIONS.md Q20.)

#### Scenario: Request lists the pooled analytes
- **WHEN** a user opens the next planned draw
- **THEN** the system offers a lab request listing the pooled analytes and the pre-analytical requirements
- **AND** the request recommends no brand of laboratory test
