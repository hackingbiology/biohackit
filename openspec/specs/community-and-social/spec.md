# Community & Social (M6)

## Purpose

Following, copying, cohorts, the calculated Evidence Badge, public claim review, two-axis reputation, and data-quality-only gamification — attached to the pre-existing Rapamycin News community rather than launched cold.

## Requirements

### Requirement: Follow and copy
The system SHALL let a user follow another user and copy/subscribe to a public protocol, with copying invoking the protocol fork + safety inheritance path (see `protocols`, `safety-guardrails`).

#### Scenario: Copy enters the safety gate
- **WHEN** a user copies a public protocol
- **THEN** a fork is created and the mandatory baseline/safety gate is applied before activation

### Requirement: Cohorts form around protocols
The system SHALL group users practising the same protocol into a `Cohort` and let a follower compare against it.

#### Scenario: Compare to the cohort
- **WHEN** a user practises a protocol with others
- **THEN** they can see their own trajectory against the cohort's (see `analytics-and-open-data`)

### Requirement: Link to Rapamycin News first, cohorts second
The system SHALL link each protocol/compound to the relevant existing forum thread, and SHALL treat community as an extension of Rapamycin News rather than a cold-launched social feature.

#### Scenario: Thread link on every protocol
- **WHEN** a protocol references a compound discussed on Rapamycin News
- **THEN** the protocol links bidirectionally to that thread

> DECISION: The exact integration (link only / SSO via Discourse Connect / partnership) is spec v0.3 §11 Q3, still OPEN. Confirm the desired depth.

### Requirement: Calculated Evidence Badge
The system SHALL compute reputation from data the system already holds and show its derivation, never a self-declared claim.

#### Scenario: Derivation, not claim
- **WHEN** a protocol has verified measurements
- **THEN** the badge reads e.g. "Rapamycin 6mg/week, 94 days, adherence 91%; ApoB 78→91 (+17%), ALT stable, lymphocytes −18%; 3 measurements, single lab, verified reports"
- **AND** no free-form success claim is shown in its place

### Requirement: Public claim review
The system SHALL make contested claims public, discussed, and traceable — not a private flag to a team.

#### Scenario: Contested claim is visible
- **WHEN** users contest a claim
- **THEN** the item shows "contested by N people, here's why" publicly

### Requirement: Two-axis reputation and specialty discovery
The system SHALL keep verified-credential and data-verification as separate axes and provide discovery by specialty, not popularity.

#### Scenario: Discover by specialty
- **WHEN** a user browses contributors
- **THEN** they can filter by verified specialty distinct from data-quality

### Requirement: Gamification only on data quality
The system SHALL gamify only data quality — adherence streaks, panel completeness, documentation continuity — and SHALL NOT rank users by health outcomes.

#### Scenario: No outcome leaderboard
- **WHEN** gamification is displayed
- **THEN** it rewards logging/completeness
- **AND** there is no "lowest ApoB" or "best biological age" ranking
