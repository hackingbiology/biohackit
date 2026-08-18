# Genomics (M9 — minimal interpretation, public by default)

## Purpose

No heavy re-analysis pipeline: the platform imports selected interpreted variants and, where provided, retains the raw **gVCF**, focused on the actionable. Like all other data on biohack.it, genomic data — including the gVCF — is **public by default** and part of OpenData, behind a heightened, explicit consent step because it is maximally identifying.

## Requirements

### Requirement: Accept genomic data including gVCF
The system SHALL accept genomic data — interpreted variants/reports and, where provided, the raw gVCF — store it, and treat it as publishable data.

#### Scenario: gVCF stored and publishable
- **WHEN** a user provides a gVCF
- **THEN** the system stores it and treats it as publishable, public-by-default data
- **AND** deep re-analysis (variant calling from raw reads) is out of scope

### Requirement: Actionable interpretation focus
The system SHALL surface genomic interpretation limited to the actionable — pharmacogenomics (CYP metaboliser status; APOE) — while retaining the raw gVCF for sharing and export.

#### Scenario: Actionable variant surfaced, raw retained
- **WHEN** an actionable pharmacogenomic variant is present
- **THEN** it can inform safety context
- **AND** non-actionable interpretation stays out of scope even though the raw gVCF is retained and shareable

### Requirement: Public by default with heightened consent (incl. gVCF)
The system SHALL make genomic data — including the gVCF — public by default like other data, gated by an explicit heightened-consent step stating its identifiability, the exposure of biological relatives, and the effective irreversibility of publication.

#### Scenario: Heightened consent before genomics goes public
- **WHEN** a user's genomic data (incl. gVCF) is set public
- **THEN** the system requires an explicit heightened-consent acknowledgment covering identifiability, relatives, and irreversibility
- **AND** once consented, the data is part of OpenData like other public data (see `analytics-and-open-data`)

> DECISION (2026-08-04): reverses spec v0.3 Principle #9 — genomics is public by default, gVCF included. FLAG for Fabio: genomic data is maximally identifying (of the user and their biological relatives), is a GDPR Art. 9 special category, and public release is effectively irreversible. The heightened-consent gate is the mitigation — confirm it is sufficient.
