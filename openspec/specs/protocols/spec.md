# Protocols (M1 — Protocol Builder & Library)

## Purpose

The authoring, versioning, and lifecycle of protocols: created from scratch, **copied/forked** from another user, or **imported from an already-running regimen**. Protocols are living objects — they change, and every change is tracked. Covers the curated vs community origin and the T0 seeding that removes the chicken-and-egg problem. Discovery and the social act of following are specified in `community-and-social`; this capability owns the object and its history.

## Requirements

### Requirement: Create a protocol from scratch
The system SHALL let a user author a `Protocol` by composing a `TestingProtocol`, a `TreatmentPlan`, and one or more `Goal`s, in a builder that does not require all three to be complete before saving a draft.

#### Scenario: Draft saved incrementally
- **WHEN** a user adds a single intervention and saves
- **THEN** the protocol persists as a `Draft`
- **AND** the system surfaces what is still missing (e.g. "no efficacy markers yet") without blocking the save

#### Scenario: System proposes the measurement side
- **WHEN** a user adds interventions to a `TreatmentPlan`
- **THEN** the system SHALL propose the efficacy and safety biomarkers implied by those interventions (see `safety-guardrails`, `measurement-planning`)
- **AND** the proposals are shown as an Accept-All / Reject-All block, never auto-applied

### Requirement: Import an already-running protocol (experienced baseline)
The system SHALL support an onboarding path for an experienced biohacker who is **already running a protocol**, capturing the current regimen and its historical baseline rather than assuming a clean start. Where the analytic history is hard to reconstruct, the system SHALL accept a coarse free-text lineage note and SHALL flag the record as starting from a summarized, non-analytic history.

> RESOLVED (2026-08-04): record `in_effect_since` ≠ `tracked_since`; where reconstruction is hard, accept a coarse "how you got here" note AND flag the record as `history: synthesized` (versus `analytic`).

#### Scenario: Baseline capture for someone mid-protocol
- **WHEN** a new experienced user declares interventions they are already taking
- **THEN** the system records `in_effect_since` separately from `tracked_since` and marks the protocol `Active` from import
- **AND** it invites (does not require) backfilling past measurements and prior changes as history

#### Scenario: Synthesized history when reconstruction is hard
- **WHEN** the user cannot reconstruct the analytic history of how the protocol evolved
- **THEN** the system accepts a coarse free-text lineage note ("how you arrived here")
- **AND** it flags the protocol/baseline as `history: synthesized` (not `analytic`) so downstream analytics can distinguish it (see `analytics-and-open-data`)

### Requirement: Copy / fork an existing protocol
The system SHALL let a user copy another user's public `Protocol`, producing a new protocol that records its `forked_from` lineage (source protocol + version).

#### Scenario: Forking preserves lineage and safety
- **WHEN** a user copies a public protocol
- **THEN** the new protocol references the source protocol and the exact source version
- **AND** the inherited safety markers and mandatory baseline travel with it (see `safety-guardrails`)

#### Scenario: Fork then diverge
- **WHEN** the user edits their fork
- **THEN** changes apply only to their copy
- **AND** the lineage link to the source is retained for later comparison

### Requirement: Versioning and change tracking
The system SHALL version every protocol facet, and SHALL record each change as a tracked, timestamped, attributable event with a **mandatory reason**.

#### Scenario: A dose change is a tracked event
- **WHEN** a user changes rapamycin from 6 mg/week to 8 mg/week
- **THEN** a new version is created with a change event {field, old, new, timestamp, actor, reason}
- **AND** the change cannot be saved without a reason
- **AND** the prior version remains retrievable and referenceable by measurements taken under it

#### Scenario: Diff between versions
- **WHEN** a user or viewer compares two versions of a protocol
- **THEN** the system SHALL render a field-level diff of interventions, doses, cycles, and measures

#### Scenario: Measurements bind to the version in effect
- **WHEN** a measurement is recorded on a date
- **THEN** it is associated with the protocol version active on that date
- **AND** later edits to the protocol never silently reinterpret past measurements

### Requirement: Curated and community origin
The system SHALL tag each protocol with origin `curated` (authored/vetted by the HackingBiology team) or `community`, and SHALL make origin visible wherever a protocol is shown.

#### Scenario: Curated seed exists at T0
- **WHEN** the platform launches
- **THEN** a set of team-curated protocols (including Fabio's own) SHALL be present as `curated`
- **AND** a first cohort of invited alpha-tester profiles can publish `community` protocols on top of them (see `accounts-and-profiles`)

### Requirement: Publish with per-facet visibility
The system SHALL let a user publish a protocol public-by-default, while allowing specific measures or interventions to be withheld per-item.

#### Scenario: Public by default, withhold one marker
- **WHEN** a user publishes a protocol
- **THEN** the protocol and its outcomes are public unless the user explicitly withholds an item
- **AND** genomic elements follow the same public-by-default rule, behind heightened consent (see `genomics`)

### Requirement: Protocol states
The system SHALL support protocol lifecycle states `Draft | Active | Paused | Completed` and SHALL reflect state in discovery and dashboards.

#### Scenario: Pausing stops overdue accrual
- **WHEN** a user sets a protocol to `Paused`
- **THEN** measurement-plan Overdue calculations for that protocol pause (see `measurement-planning`)
- **AND** the pause is itself a tracked change event

### Requirement: Protocol level classification (medical | research)
The system SHALL classify a protocol by level — `medical` (established, clinician-grade) or `research` (experimental) — and display the level wherever the protocol appears, so a follower sees what kind of protocol they are copying.

#### Scenario: Research-level protocol is labelled
- **WHEN** a protocol contains experimental interventions
- **THEN** it is classified and displayed as `research` level
- **AND** a `medical`-level protocol is labelled distinctly, with the acknowledgment implication handled in `safety-guardrails`
