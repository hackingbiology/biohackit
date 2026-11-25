## ADDED Requirements

### Requirement: Lab request generated from a pooled draw
The system SHALL generate, from the analytes pooled into one draw, a request the user can take to a laboratory. (Source: docs/hackingbiology-project-spec.md § 4.1 journey C. The source gives no format; see QUESTIONS.md Q20.)

#### Scenario: Request lists the pooled analytes
- **WHEN** a user opens the next planned draw
- **THEN** the system offers a lab request listing the pooled analytes and the pre-analytical requirements
- **AND** the request recommends no brand of laboratory test

### Requirement: Measurement appointments are recorded
The system SHALL let a user record a planned measurement as an appointment with a date and a place, and SHALL close it when the result is recorded. (Source: docs/presentation/biohackit-deck.pdf slide 14; docs/slides/hacking-biology-project-presentation.pdf § page 8, "Scheduling measurements (booking, appointments, recording data)". Booking with a laboratory is not specified.)

#### Scenario: Record an appointment
- **WHEN** a user records an appointment for a planned measurement
- **THEN** it appears on the calendar on that date

#### Scenario: Result closes the appointment
- **WHEN** the result of the measurement is recorded
- **THEN** the appointment is marked done and linked to the measurement
