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

### Requirement: Study question and endpoints are a community proposal
The system SHALL require a Study's research question and endpoints to be published as a **community proposal** — a forum thread open for comments (Rapamycin News / Discourse) — as the act of pre-registration, so that pre-registration serves consensus rather than a private declaration. The questions a Study seeks to answer are themselves subject to community proposal.

> RESOLVED (2026-08-04): pre-registration is **mandatory** and takes the form of a community proposal for comment/consensus; the research questions are themselves subject to community proposal.

#### Scenario: Pre-registration posts a proposal
- **WHEN** a user pre-registers a Study
- **THEN** the system publishes the question and endpoints as a community proposal thread open for comments
- **AND** the Study links bidirectionally to its proposal thread (see `community-and-social`)

#### Scenario: Consensus sought, endpoints frozen
- **WHEN** a Study's proposal is open
- **THEN** comments are collected against the declared question and endpoints
- **AND** the pre-registered endpoints are immutable — changing them requires a new proposal/version, never a silent edit
