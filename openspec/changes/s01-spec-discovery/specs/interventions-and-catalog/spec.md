## ADDED Requirements

### Requirement: Early partial result during long waits
The system SHALL show what has been understood so far while a long extraction job is still running. (Source: docs/hackingbiology-project-spec.md § 8.5ter.)

#### Scenario: Partial result visible while waiting
- **WHEN** an extraction job runs longer than an interactive request
- **THEN** the user sees the items recognised so far, marked as partial
- **AND** the final result replaces them when the job completes
