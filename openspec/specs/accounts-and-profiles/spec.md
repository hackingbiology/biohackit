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

> RESOLVED (2026-08-04): confirmed — server-hosted, no local-first. Self-hosting a full instance is a different, supported path (below).

### Requirement: Self-hosting a full instance (distinct from local-first)
The system SHALL be self-hostable as a full instance under AGPL-3.0 by a technically capable user, seedable from the public OpenData snapshot; this is distinct from a per-user local-first mode, which does not exist.

#### Scenario: Power user stands up their own instance
- **WHEN** a technical user deploys the AGPL software and imports the public OpenData snapshot
- **THEN** they obtain a running server instance populated with the public protocols, treatments, measurements and public profiles
- **AND** this is a full instance, not a browser-only local-first mode

### Requirement: Public-by-default profile
The system SHALL make a user's profile, protocols and biomarker outcomes public by default, and SHALL present sharing as the expected path while allowing per-item withholding.

#### Scenario: Onboarding invites sharing
- **WHEN** a user completes onboarding
- **THEN** the UI explicitly invites them to make their protocol and outcomes public and explains the collective benefit
- **AND** the user can withhold specific items, but is not defaulted into a fully private profile

> RESOLVED (2026-08-04): confirmed — public by default (supersedes spec v0.3 Principle #2). Genomics is public too, gVCF included, behind heightened consent (reverses Principle #9; see `genomics`).

### Requirement: Required biological profile
The system SHALL require the user to configure their biological attributes — date of birth (for age), sex, ethnicity, height, and other stable or slowly-changing traits — as specifically as possible, used for sex/age normalization and stratification.

#### Scenario: Stable traits captured specifically
- **WHEN** a user sets up their profile
- **THEN** they configure date of birth, sex, ethnicity, height and other stable traits as specifically as possible
- **AND** these feed sex/age-normalized percentiles and cohort stratification (see `dashboards-and-doctor-view`, `analytics-and-open-data`)

### Requirement: Strong invitation to link social and forum identities
The system SHALL strongly invite the user to configure their social and community identities — Telegram, WeChat, Xiaohongshu (RED / "Little Red Book"), other social profiles, and their Rapamycin News forum nickname — surfaced on the public profile.

#### Scenario: Social and forum handles linked
- **WHEN** a user completes onboarding
- **THEN** they are strongly invited to add Telegram, WeChat, Xiaohongshu (RED) and their Rapamycin News nickname
- **AND** these appear on the public-by-default profile and link community identity (see `community-and-social`)

### Requirement: Onboarding "bring your reports"
The system SHALL onboard users around importing lab reports they already have, targeting first value within ten minutes at zero spend, with a persistent multi-step progress indicator.

#### Scenario: First chart within minutes
- **WHEN** a new user uploads a past lab report during onboarding
- **THEN** the system parses and charts it (see `biomarkers-and-labs`)
- **AND** the empty state teaches ("upload a report you already have"), never sells a test
- **AND** the original report file is retained and is public by default in its raw original format (see `biomarkers-and-labs`, `analytics-and-open-data`)

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
