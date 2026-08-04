# Measurement Planning (M3 — Scheduling & Measurement Planner)

## Purpose

The engine that turns active interventions into "what to measure, when, and why". Computes the panel, sets phase-dependent cadence, pools analytes into a single blood draw, and treats `Overdue` as a safety signal rather than a calendar nag.

## Requirements

### Requirement: The panel is computed, not chosen
The system SHALL derive the required panel from the protocol as `Safety Core + Δ safety-rule markers of active substances + Δ efficacy markers of goals + optional deep-dives`.

#### Scenario: Adding a nephrotoxic compound expands the panel
- **WHEN** a user adds a compound with a renal safety rule
- **THEN** the relevant renal markers are added to the computed panel with a stated reason
- **AND** the panel updates as interventions change

### Requirement: Phase-dependent cadence
The system SHALL schedule denser measurement during initiation/titration and sparser during maintenance, per intervention phase.

#### Scenario: Titration cadence
- **WHEN** an intervention is in titration
- **THEN** its safety markers are scheduled at a tighter cadence than in maintenance

### Requirement: Analyte pooling into one draw
The system SHALL pool analytes due within a near window into a single blood draw (set-cover), respecting pre-analytic requirements (fasting, wash-outs, timing).

#### Scenario: Fewer needles
- **WHEN** several analytes fall due within the same window
- **THEN** the planner proposes one draw covering them
- **AND** it honours conflicting pre-analytic constraints or splits when it must

### Requirement: Overdue is a safety signal
The system SHALL compute `Overdue` for due measurements and SHALL express it in safety terms tied to the responsible intervention, not as a generic reminder.

#### Scenario: Overdue framed against the drug
- **WHEN** a liver panel is overdue while a hepatically-relevant compound is active
- **THEN** the system states "rapamycin active for 94 days, liver panel overdue by 34"
- **AND** this links to the corresponding SafetyRule (see `safety-guardrails`)

#### Scenario: Overdue pauses with the protocol
- **WHEN** the protocol is `Paused`
- **THEN** Overdue accrual for its measures pauses

### Requirement: Planner views
The system SHALL provide calendar, year, and table views, filterable by type × status, with any Study timeline overlaid on the personal calendar.

#### Scenario: Study overlay
- **WHEN** a user has an active N-of-1 Study
- **THEN** its timepoints appear on the personal calendar alongside routine measures
