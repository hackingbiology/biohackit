## ADDED Requirements

### Requirement: Intake cadence is typed
The system SHALL store the cadence of each intake as a typed value: a mode, times per day, days of the week and an interval in days (the shape used by get-based, see `docs/ecosystem/m03-interventions-protocols.md`), and SHALL compute due dates from it deterministically.

#### Scenario: Every second day
- **WHEN** an intake has an interval of two days and a start date
- **THEN** it is due on the start date and every second day after it
- **AND** the same cadence and start date always give the same due dates

## MODIFIED Requirements

### Requirement: Daily intake schedule across slots
The system SHALL allocate intakes into day slots optimising bioavailability and avoiding interference and toxicity summation (mineral separation, competing compounds, hepatic load), using a constraint solver rather than an LLM. Until a solver dependency is approved (Q140), the allocation SHALL use a deterministic method written in the repository that returns the same schedule for the same input and states a reason for each separation. A third-party solver SHALL NOT be added without approval (Q140).

#### Scenario: Competing compounds separated
- **WHEN** two compounds should not be co-administered
- **THEN** the schedule places them in separated slots with a stated reason
- **AND** the allocation is deterministic and explainable

#### Scenario: Same input, same schedule
- **WHEN** the allocation runs twice on an identical set of intakes, constraints and slots
- **THEN** both runs return the same schedule
- **AND** every separation of two compounds names the constraint that caused it

### Requirement: Meal timing and absorption requirements
The system SHALL model each substance's meal constraints — with-meal, away-from-meals, and any co-ingested substance required for absorption (e.g. dietary fat for fat-soluble compounds) — and reflect them in the schedule. A meal SHALL count as containing fat only when the user or the plan marks it so; the system SHALL NOT infer fat content from a food database and SHALL NOT apply a fat amount threshold unless one is entered with a cited source (Q154).

#### Scenario: Fat-soluble compound with a fatty meal
- **WHEN** a fat-soluble compound is scheduled
- **THEN** it is placed with a meal marked as containing fat
- **AND** a compound requiring an empty stomach is placed away from meals

#### Scenario: No meal marked as containing fat
- **WHEN** a fat-soluble compound is scheduled and no meal is marked as containing fat
- **THEN** the schedule flags the missing meal instead of choosing one

### Requirement: Spacing and distance rules
The system SHALL honour required spacing/distance between compounds (competition, absorption windows) and pre/post-meal distances, or flag an unresolvable conflict. A constraint SHALL be enforced only if it is stored with a cited source; the system SHALL NOT ship any constraint, distance or duration as seeded data (Q154), and a constraint without a source SHALL be listed as unsourced and not enforced.

#### Scenario: Distance respected or flagged
- **WHEN** a compound must be taken a set distance from another or from food, and the constraint has a cited source
- **THEN** the schedule enforces that distance
- **AND** it flags the conflict when the constraints cannot all be met

#### Scenario: Unsourced constraint is listed, not enforced
- **WHEN** a user enters a required distance between two compounds without a source
- **THEN** the schedule does not treat it as a rule
- **AND** it is shown in a list of unsourced constraints

#### Scenario: No constraint is seeded
- **WHEN** the system is installed
- **THEN** it contains no spacing, competition or absorption constraint until one is entered with a source
