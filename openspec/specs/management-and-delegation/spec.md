# Management & Delegation (Mentor / Longevity Doctor / Clinic)

## Purpose

Supports a third-party **managing user** — a Biohacking Mentor / Longevity Doctor / Longevity Clinic — who supervises and manages one or more users' protocols: administering, measuring, and monitoring on their behalf. Kept deliberately lean: a user signs up on their own and may then assign a manager; if assigned, it is indicated. Builds on existing hooks — TreatmentPlan `Physician-Assigned`, attributable change events, the doctor view, and the verified-credential reputation axis — so it is additive rather than a rewrite.

## Requirements

### Requirement: Managing-user role
The system SHALL support a managing-user role — Biohacking Mentor / Longevity Doctor / Longevity Clinic — able to manage one or more users as a roster.

#### Scenario: A manager holds a roster
- **WHEN** a managing user is set up
- **THEN** they can hold a roster of one or more managed users
- **AND** the role carries the verified-credential axis (see `accounts-and-profiles`)

### Requirement: Self-signup, then assign a manager
The system SHALL let a user sign up on their own and then assign — and revoke — a manager who follows them; assignment is the user's choice and never required to use the platform.

#### Scenario: User assigns and can revoke a manager
- **WHEN** a self-registered user assigns a manager
- **THEN** a managed-by relationship is created, revocable by the user at any time
- **AND** using the platform without a manager remains fully possible

### Requirement: Management scope — administer, measure, monitor
The system SHALL let an assigned manager administer (author/adjust the managed user's TreatmentPlan as `Physician-Assigned`), measure (enter/import measurements), and monitor (view dashboards), within what the user has granted.

#### Scenario: Manager adjusts a managed protocol
- **WHEN** a manager edits a managed user's TreatmentPlan
- **THEN** the change is applied as `Physician-Assigned` with a mandatory reason (see `protocols`)
- **AND** it is attributed to the manager, not the user

### Requirement: Manager actions are attributed
The system SHALL attribute every managing action to the manager in the tracked change/measurement history, visible to the managed user.

#### Scenario: Who did what is clear
- **WHEN** a manager performs an action on a managed user
- **THEN** the history records the manager as actor
- **AND** the managed user can see what their manager did

### Requirement: An assigned manager is indicated
The system SHALL indicate, on the managed user's profile and dashboard, that a manager is assigned and who they are.

#### Scenario: Assignment is shown
- **WHEN** a user has an assigned manager
- **THEN** the profile and dashboard indicate the manager (name + credential)
- **AND** revoking the assignment is reflected everywhere it was shown

> OPEN (kept lean for now): fine-grained permission scopes, and who owns the safety-gate risk acknowledgment when a manager assigns a protocol (managed user vs manager). To be detailed later without blocking the MVP relationship.
