# Pills Management (M4 — daily intake orchestration)

## Purpose

Orchestrates the daily intake of pills and supplements: which to take, when, how to distribute them across the day, spacing between them, whether with or away from meals, and what a substance needs for absorption (e.g. dietary fat). Links to procurement for restock. This is the daily-intake half split out of the original M4; purchase and inventory live in `procurement-and-inventory`, and the schedule surfaces in the daily log and the programming calendar.

## Requirements

### Requirement: Daily intake schedule across slots
The system SHALL allocate intakes into day slots optimising bioavailability and avoiding interference and toxicity summation (mineral separation, competing compounds, hepatic load), using a constraint solver rather than an LLM.

#### Scenario: Competing compounds separated
- **WHEN** two compounds should not be co-administered
- **THEN** the schedule places them in separated slots with a stated reason
- **AND** the allocation is deterministic and explainable

### Requirement: Meal timing and absorption requirements
The system SHALL model each substance's meal constraints — with-meal, away-from-meals, and any co-ingested substance required for absorption (e.g. dietary fat for fat-soluble compounds) — and reflect them in the schedule.

#### Scenario: Fat-soluble compound with a fatty meal
- **WHEN** a fat-soluble compound is scheduled
- **THEN** it is placed with a meal containing sufficient fat
- **AND** a compound requiring an empty stomach is placed away from meals

### Requirement: Spacing and distance rules
The system SHALL honour required spacing/distance between compounds (competition, absorption windows) and pre/post-meal distances, or flag an unresolvable conflict.

#### Scenario: Distance respected or flagged
- **WHEN** a compound must be taken a set distance from another or from food
- **THEN** the schedule enforces that distance
- **AND** it flags the conflict when the constraints cannot all be met

### Requirement: Restock link to procurement
The system SHALL link pill scheduling to procurement so that low stock triggers a restock action (see `procurement-and-inventory`).

#### Scenario: Running low triggers reorder
- **WHEN** scheduled consumption will exhaust a compound's stock within its lead time
- **THEN** the system raises a restock action via procurement

### Requirement: Feeds the daily log and calendar
The system SHALL surface the resolved pill schedule in the daily log and the programming calendar.

#### Scenario: Schedule appears where the user acts
- **WHEN** the daily schedule is computed
- **THEN** each intake appears in the daily log with dose and slot (see `daily-log-and-adherence`)
- **AND** on the daily/weekly calendar alongside therapies and exercise (see `measurement-planning`)
