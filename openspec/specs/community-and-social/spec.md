# Community & Social (M6)

## Purpose

Following, copying, cohorts, the calculated Evidence Badge, public claim review, two-axis reputation, and data-quality-only gamification — attached to the pre-existing Rapamycin News community rather than launched cold.

## Requirements

### Requirement: Follow and copy
The system SHALL let a user follow another user and copy/subscribe to a public protocol, with copying invoking the protocol fork + safety inheritance path (see `protocols`, `safety-guardrails`).

#### Scenario: Copy enters the safety gate
- **WHEN** a user copies a public protocol
- **THEN** a fork is created and the mandatory baseline/safety gate is applied before activation

### Requirement: One-click copyable catalog with an informed-decision panel
The system SHALL keep every intervention — including the most sensitive (peptides, plasmapheresis, IV) — in the public catalog, one-click copyable, with nothing documentable-but-not-copyable, and SHALL present an informed-decision panel at the point of copy.

> RESOLVED (2026-08-04): resolves spec v0.3 §11 Q7 — everything is copyable; the mitigation is informed choice plus the safety gate, not exclusion from the catalog.

#### Scenario: Informed one-click copy
- **WHEN** a user chooses to copy any protocol, including a peptide / plasmapheresis / IV one
- **THEN** before activation an informed-decision panel surfaces: how many others practise it and their outcomes (adoption + Evidence Badge), the evidence corpus and grading, the medical/research level and dose provenance, the potential impacts, and Rapamycin News links for deeper discussion
- **AND** the copy then proceeds through the safety gate (baseline + heightened acknowledgment for research/animal-derived), with nothing withheld from the copyable catalog

### Requirement: Cohorts form around protocols
The system SHALL group users practising the same protocol into a `Cohort` and let a follower compare against it.

#### Scenario: Compare to the cohort
- **WHEN** a user practises a protocol with others
- **THEN** they can see their own trajectory against the cohort's (see `analytics-and-open-data`)

### Requirement: Integrate with Rapamycin News (Discourse Connect where feasible)
The system SHALL integrate community with the existing Rapamycin News (Discourse) — via Discourse Connect SSO where feasible, falling back to bidirectional links otherwise — and SHALL treat community as an extension of it rather than a cold-launched social feature.

> RESOLVED (2026-08-04): Discourse Connect SSO ideally; else link-only. A form of partnership with Rapamycin News is expected.

#### Scenario: SSO where feasible, link as fallback
- **WHEN** Discourse Connect SSO is available
- **THEN** identity is shared via Discourse Connect and protocol↔thread links are bidirectional
- **AND** where SSO is not available, bidirectional links are still established

#### Scenario: Thread link on every protocol
- **WHEN** a protocol references a compound discussed on Rapamycin News
- **THEN** the protocol links bidirectionally to that thread

### Requirement: Host study proposals for comment and consensus
The system SHALL host N-of-1 Study proposals (research question + endpoints) as community threads open for comment, and SHALL surface the proposal discussion alongside the Study.

#### Scenario: Proposal collects community input
- **WHEN** a Study is pre-registered (see `studies-nof1`)
- **THEN** its question and endpoints appear as a community proposal thread open for comment
- **AND** the resulting discussion is visible from the Study, and the Study from the thread

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
