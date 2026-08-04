# Analytics & Open Data (M8)

## Purpose

Aggregation across cohorts, honest cross-person comparison, stratification, and the open-data release discipline that decides whether researchers cite the dataset or ignore it. Phase 4.

## Requirements

### Requirement: Cohort aggregation
The system SHALL aggregate outcomes across a cohort practising the same protocol, weighting contributions by adherence and data completeness.

#### Scenario: Adherence-weighted aggregate
- **WHEN** a cohort aggregate is computed
- **THEN** low-adherence and sparse contributions are down-weighted or excluded by a declared rule

### Requirement: Compare on z-score, not raw value
The system SHALL compare people using the z-score relative to the originating laboratory's range, not the raw value.

#### Scenario: Cross-lab comparison
- **WHEN** two users measured the same analyte at different labs
- **THEN** comparison uses lab-relative z-scores

### Requirement: Release only well-coded data
The system SHALL release open data only for measurements carrying LOINC + UCUM + declared provenance, and only above minimum cohort thresholds guarding re-identification.

#### Scenario: Small clean over large dirty
- **WHEN** the open-data export runs
- **THEN** it excludes uncoded/unprovenanced measurements
- **AND** it suppresses cohorts too small to protect identity

### Requirement: Researcher access and OMOP export
The system SHALL provide a researcher endpoint (dump + API) and an OMOP CDM export for the research layer.

#### Scenario: OMOP export
- **WHEN** the research export runs
- **THEN** it produces an OMOP-CDM dataset consumable by OHDSI tooling

### Requirement: "Stops instead of guessing" in aggregates
The system SHALL declare insufficiency rather than present an approximate synthetic value when coverage is inadequate.

#### Scenario: Not enough coverage
- **WHEN** an organ-system index or projection lacks coverage
- **THEN** the system says "not determinable" instead of an approximate number
