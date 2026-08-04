# Safety Guardrails (M7)

## Purpose

The module that justifies the project. Baseline gating before following a protocol, automatically inherited safety markers, dose plausibility, interaction and critical-value alerts, and escalation with a ready protocol sheet. Describes what to monitor; never prescribes what to take.

## Requirements

### Requirement: Mandatory baseline AND risk acknowledgment before following a protocol
The system SHALL require BOTH (a) the required baseline safety markers to be recorded — by import or manual entry — AND (b) an explicit, logged risk acknowledgment, before a user can set a copied/followed protocol to `Active`. Neither substitutes for the other.

> RESOLVED (2026-08-04): baseline values are required *and* an acknowledgment is required; acknowledgment is never a bypass for missing baseline.

#### Scenario: Beginner cannot start blind
- **WHEN** a beginner copies a protocol containing an off-label compound
- **THEN** the system blocks activation until the required baseline markers are recorded
- **AND** the user has also explicitly acknowledged the risk (recorded, timestamped)
- **AND** the required safety markers for that compound are already attached

#### Scenario: Acknowledgment alone is not enough
- **WHEN** a user acknowledges the risk but has not recorded the required baseline
- **THEN** activation remains blocked
- **AND** the UI states which baseline markers are still missing

### Requirement: Safety markers inherited automatically
The system SHALL attach a substance's associated safety markers to the user's measurement plan whenever that substance becomes active — safety is not opt-in.

#### Scenario: Inheriting on copy
- **WHEN** a protocol is copied
- **THEN** its safety markers travel with it into the follower's plan (see `protocols`)

### Requirement: Dose sanity check
The system SHALL compare an entered dose against tolerable upper limit, usual therapeutic dose, and maximum reported-in-literature dose, and flag it on three levels: outside-common-use / above-upper-limit / potentially-toxic. This is numeric plausibility validation, not clinical advice.

#### Scenario: The extra zero
- **WHEN** a user enters vitamin D3 at 100,000 IU/day
- **THEN** the system flags it as potentially toxic and asks for confirmation
- **AND** the same applies to e.g. selenium 2000 mcg or rapamycin 30 mg/day

### Requirement: Interaction and critical-value alerts
The system SHALL raise interaction warnings between active substances and alerts on critical out-of-range measured values, with declared confidence where interaction data is uncertain.

#### Scenario: Interaction warned with confidence
- **WHEN** two active substances have a known interaction
- **THEN** the system warns and states the confidence/source of the interaction claim

### Requirement: Escalation with a ready sheet
The system SHALL provide an explicit "consult a physician" escalation that produces the protocol sheet ready to hand over (see `dashboards-and-doctor-view`).

#### Scenario: Critical value escalates
- **WHEN** a measured value crosses a safety threshold
- **THEN** the system escalates with the protocol sheet pre-generated
- **AND** it never issues a personalised dosage or diagnosis
