# Analytics & Open Data (M8)

## Purpose

Aggregation across cohorts, honest cross-person comparison, stratification, and the open-data discipline that decides whether researchers cite the dataset or ignore it. OpenData ships as **two products**: a **full clonable public snapshot** (public profiles and their public data, protocols, treatments, measurements) that lets anyone self-host an equivalent instance, and an **aggregated research export** (lab-relative z-scores, cohort thresholds, OMOP). Phase 4.

## Requirements

### Requirement: Defined OpenData scope
The system SHALL define OpenData as everything a user has made public: public user profiles and their public data, defined protocols, treatments/interventions, measurements, **raw original lab report files**, and **public genomic data including the gVCF**. Only withheld per-item data is excluded.

#### Scenario: What is and isn't OpenData
- **WHEN** the OpenData set is assembled
- **THEN** it includes public profiles and their public data, protocols, treatments, measurements, original lab files, and public genomics (incl. gVCF)
- **AND** it excludes only withheld items (see `genomics`, `biomarkers-and-labs`)

### Requirement: Full clonable public snapshot
The system SHALL publish OpenData as a full, clonable snapshot sufficient to seed an independent self-hosted instance, in addition to the aggregated research export.

#### Scenario: Clone the whole public dataset
- **WHEN** a third party downloads the public snapshot
- **THEN** it contains the public profiles, protocols, treatments, measurements, original lab files and public genomics as published
- **AND** it is sufficient to stand up an equivalent instance (see `accounts-and-profiles`)

#### Scenario: One boundary for both products
- **WHEN** either the public snapshot or the aggregated research export is produced
- **THEN** neither includes any withheld item (public genomics, gVCF and original lab files are included, being public)

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

### Requirement: Aggregated research export uses only well-coded data
The system SHALL include in the **aggregated research export** only measurements carrying LOINC + UCUM + declared provenance, and only above minimum cohort thresholds guarding re-identification. (The full public snapshot, by contrast, carries public data as published.)

#### Scenario: Small clean over large dirty
- **WHEN** the aggregated research export runs
- **THEN** it excludes uncoded/unprovenanced measurements
- **AND** it suppresses cohorts too small to protect identity

### Requirement: Researcher access and OMOP export
The system SHALL provide a researcher endpoint (dump + API) and an OMOP CDM export for the research layer.

#### Scenario: OMOP export
- **WHEN** the research export runs
- **THEN** it produces an OMOP-CDM dataset consumable by OHDSI tooling

### Requirement: Sex/age-normalized percentile computation
The system SHALL compute, per biomarker, a percentile normalized for sex and age against **published reference distributions**, and SHALL expose it to dashboards and the doctor view (see `dashboards-and-doctor-view`), declaring the published source used per marker.

> RESOLVED (2026-08-04): the percentile is computed against **published reference distributions**, not the platform's own aggregate; the source is declared per marker.

#### Scenario: Percentile with declared reference
- **WHEN** a percentile is computed for a marker
- **THEN** it is normalized for the user's sex and age band
- **AND** the reference population and its source are declared with the value

#### Scenario: Distinct from cohort comparison
- **WHEN** both a population percentile and a same-protocol cohort comparison exist for a marker
- **THEN** they are computed and presented as two distinct references (population vs peers-on-this-protocol)

### Requirement: Raw-data publication validated by a community poll at BETA
The platform's policy of publishing raw data (raw lab reports, gVCF, and all public data) SHALL be put to a community poll on Rapamycin News when the public BETA testing call opens, to gauge participant opinion, and the outcome SHALL inform the raw-publication policy.

#### Scenario: BETA community poll
- **WHEN** the public BETA testing call opens
- **THEN** a poll on Rapamycin News asks participants their view on publishing raw data of everything
- **AND** the outcome informs the raw-publication policy (see `community-and-social`)

### Requirement: "Stops instead of guessing" in aggregates
The system SHALL declare insufficiency rather than present an approximate synthetic value when coverage is inadequate.

#### Scenario: Not enough coverage
- **WHEN** an organ-system index or projection lacks coverage
- **THEN** the system says "not determinable" instead of an approximate number
