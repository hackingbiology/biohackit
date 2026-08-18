# Therapeutics Management (periodic treatments)

## Purpose

Manages interventions that require a periodic treatment session rather than a pill — red light therapy, hyperbaric oxygen therapy (HBOT, including hypoxia-hyperoxia), sauna, cold exposure, and others to add — capturing their parameters, scheduling their sessions, and logging done/not-done. Builds on the Device/Therapy intervention subtype (see `domain-model`).

## Requirements

### Requirement: Model periodic therapy sessions
The system SHALL model periodic therapy interventions (red light, HBOT incl. hypoxia-hyperoxia, sauna, cold exposure) with their parameters (dose, duration, protocol) and session cadence.

#### Scenario: HBOT protocol captured
- **WHEN** a user configures an HBOT hypoxia-hyperoxia protocol
- **THEN** its parameters and session cadence are stored
- **AND** red light and other therapies are represented the same way

### Requirement: Extensible therapy catalog
The system SHALL allow new therapy types to be added and configured with parameters and cadence, without changing the model.

#### Scenario: Add a new therapy
- **WHEN** a new periodic therapy is introduced
- **THEN** it can be configured with its parameters and cadence like existing ones

### Requirement: Schedule therapy sessions on the calendar
The system SHALL place therapy sessions on the daily/weekly programming calendar and remind the user.

#### Scenario: Session scheduled and reminded
- **WHEN** a therapy has a due session
- **THEN** it appears on the calendar (see `measurement-planning`) with a reminder

### Requirement: Log sessions done or not
The system SHALL log therapy sessions with four-state adherence (done / partial / skipped / missed), feeding adherence.

#### Scenario: Session logged
- **WHEN** a user completes or misses a therapy session
- **THEN** it is logged with its adherence state (see `daily-log-and-adherence`)
