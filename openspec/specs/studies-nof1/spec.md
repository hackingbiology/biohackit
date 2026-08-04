# N-of-1 Studies

## Purpose

Makes a self-experiment interpretable by forcing the question and the endpoint to be declared before it starts. The container that later composes into distributed, grassroots trials. Pre-registration costs nothing and disarms the main methodological objection in advance.

## Requirements

### Requirement: Study with pre-declared endpoints
The system SHALL model a `Study` with a research question and endpoints declared before T0, an associated protocol, timepoints (T0 baseline, T1…Tn), a per-timepoint test battery, duration, wash-out, stop criteria, and a pre/post statistical comparison.

#### Scenario: Endpoint declared before start
- **WHEN** a user creates a Study
- **THEN** the endpoint must be declared before the study can begin
- **AND** it is timestamped so later results cannot silently redefine success

### Requirement: Timepoints drive the planner
The system SHALL feed a Study's timepoints and test battery into the measurement planner and overlay them on the personal calendar.

#### Scenario: Battery scheduled
- **WHEN** a Study defines T1 at week 8 with a battery
- **THEN** those measures appear as due in the planner at week 8

### Requirement: Pre/post read-out
The system SHALL compute the declared pre/post comparison at completion and present it against the pre-registered endpoint.

#### Scenario: Honest read-out
- **WHEN** a Study completes
- **THEN** the system reports the endpoint result as declared, including a null result
- **AND** insufficient data yields "not determinable" rather than a guessed value

> OPEN: Is endpoint pre-registration mandatory to publish a Study, or optional with a quality badge? (spec v0.3 §11 Q15)
