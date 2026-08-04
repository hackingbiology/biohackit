# Daily Log & Adherence (M13)

## Purpose

The thirty-seconds-a-day surface that keeps the platform alive between blood draws, and the source of the adherence signal that makes an N-of-1 interpretable and weights a cohort contribution. Phase 1.

## Requirements

### Requirement: Daily check-off with dose and slot pre-resolved
The system SHALL present a daily check-off of intakes with dose and time-slot already resolved from the plan.

#### Scenario: One-tap logging
- **WHEN** a user opens the daily log
- **THEN** each due intake shows its resolved dose and slot
- **AND** the user marks it without re-entering dose

### Requirement: Four-state adherence
The system SHALL record adherence in four states: taken-as-planned | partial-dose | intentionally-skipped | forgotten, and compute daily and cumulative adherence.

#### Scenario: Intentional skip is distinct from forgotten
- **WHEN** a user marks a dose intentionally-skipped
- **THEN** it is stored distinctly from "forgotten"
- **AND** both feed the adherence percentage that qualifies results

### Requirement: Wellness check
The system SHALL capture a daily subjective wellness check — mood 1–5, energy 1–5, sleep hours, sleep quality 1–5, free notes.

#### Scenario: High-frequency series with zero cost
- **WHEN** a user submits a wellness check
- **THEN** it is stored as a high-frequency series usable in dashboards
- **AND** it requires no purchase or lab

### Requirement: Adherence qualifies data downstream
The system SHALL make adherence available to analytics so a low-adherence contribution can be down-weighted or excluded.

#### Scenario: 35% adherence flagged
- **WHEN** a contribution has 35% adherence
- **THEN** analytics can exclude or down-weight it versus a 95% contribution (see `analytics-and-open-data`)
