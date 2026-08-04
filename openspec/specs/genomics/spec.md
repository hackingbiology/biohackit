# Genomics (M9 — deliberately minimal)

## Purpose

No processing of raw genomic data. Import of selected interpreted variants only, focused on the actionable. The one category that is structurally non-shareable: there must be no code path that publishes it.

## Requirements

### Requirement: No raw genomic processing
The system SHALL NOT process raw genomic files; it SHALL import only selected interpreted variants/reports and link out to external resources.

#### Scenario: Link out, not process
- **WHEN** a user has raw genomic data
- **THEN** the system links to external resources rather than ingesting the raw file

### Requirement: Actionable focus
The system SHALL limit genomic content to the actionable — pharmacogenomics (CYP metaboliser status; APOE) — and exclude the rest from scope.

#### Scenario: Actionable variant imported
- **WHEN** an actionable pharmacogenomic variant is imported
- **THEN** it can inform safety context
- **AND** non-actionable variants are out of scope

### Requirement: Structurally non-shareable
The system SHALL have no code path that publishes genomic data — no setting, no sharing surface, no possible error.

#### Scenario: No publish path exists
- **WHEN** any sharing or export runs
- **THEN** genomic-derived data is never included
- **AND** there is no UI toggle that could expose it
