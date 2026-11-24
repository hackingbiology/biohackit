## ADDED Requirements

### Requirement: Reminders for intake, due tests and restock
The system SHALL remind a user of an intake due, a measurement coming due and a stock about to run out. (Source: docs/hackingbiology-project-spec.md § 4.2 Touchpoint. The source names no channel; see QUESTIONS.md Q22.)

#### Scenario: Intake reminder
- **WHEN** an intake in the user's plan is due
- **THEN** the user receives a reminder naming the intake

#### Scenario: Measurement and restock reminders
- **WHEN** a measurement is coming due or a stock is projected to run out
- **THEN** the user receives a reminder naming the measurement or the stock
- **AND** an overdue measurement is worded as a safety signal per `measurement-planning`
