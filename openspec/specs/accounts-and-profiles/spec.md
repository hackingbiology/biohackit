# Accounts & Profiles

## Purpose

Registration, the public profile, onboarding journeys, and the T0 seeding of curated content and invited alpha testers. Server-hosted; no local-first mode. Public-by-default posture starts here.

## Requirements

### Requirement: Server-hosted account
The system SHALL require a server-hosted account to create or share protocols and measurements; there is no browser-only/local-first mode.

#### Scenario: Account needed to contribute
- **WHEN** a visitor wants to save a protocol or a measurement
- **THEN** the system requires registration/sign-in
- **AND** read access to public profiles and protocols does not require an account

> DECISION: This resolves spec v0.3 §11 Q28 (local-first) as **no**. Confirm.

### Requirement: Public-by-default profile
The system SHALL make a user's profile, protocols and biomarker outcomes public by default, and SHALL present sharing as the expected path while allowing per-item withholding.

#### Scenario: Onboarding invites sharing
- **WHEN** a user completes onboarding
- **THEN** the UI explicitly invites them to make their protocol and outcomes public and explains the collective benefit
- **AND** the user can withhold specific items, but is not defaulted into a fully private profile

> DECISION: Supersedes spec v0.3 Principle #2 ("public by choice, never by default"). Genomics remains structurally private (see `genomics`).

### Requirement: Context attributes
The system SHALL let a profile declare optional context attributes (age, sex, and other self-declared attributes) used for stratification, with the user controlling which are public.

#### Scenario: Attribute used for cohort stratification
- **WHEN** a user declares age and sex
- **THEN** those attributes are available to cohort stratification (see `analytics-and-open-data`)
- **AND** the user can mark any attribute as withheld from the public profile

### Requirement: Onboarding "bring your reports"
The system SHALL onboard users around importing lab reports they already have, targeting first value within ten minutes at zero spend, with a persistent multi-step progress indicator.

#### Scenario: First chart within minutes
- **WHEN** a new user uploads a past lab report during onboarding
- **THEN** the system parses and charts it (see `biomarkers-and-labs`)
- **AND** the empty state teaches ("upload a report you already have"), never sells a test

### Requirement: Two independent reputation axes
The system SHALL model reputation as two separate axes — verified professional credential (who you are) and data verification (what your measurements show) — and SHALL never fuse them into one score.

#### Scenario: A physician without data, a biohacker with data
- **WHEN** a physician verifies a credential but has no measurements
- **THEN** their credential axis is populated and their data-verification axis is empty
- **AND** discovery can filter by specialty/credential separately from data quality

### Requirement: T0 alpha-tester seeding
The system SHALL support inviting a first cohort of biohackers as alpha testers with real, attributed profiles, so that curated content and early community protocols coexist at launch.

#### Scenario: Invited alpha tester publishes
- **WHEN** an invited alpha biohacker accepts and imports their running protocol
- **THEN** their profile and protocol become part of the seeded, browsable library
- **AND** the platform never presents an empty community at launch (curated + Fabio + alphas)
