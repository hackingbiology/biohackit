# Biomarkers & Lab Data — the Blood Layer (M2)

## Purpose

The flagship of Phase 1. Analyte registry with mandatory coding, the deterministic import pipeline, manual entry of equal standing, three ranges per analyte, and completeness/freshness. Standalone value: "upload your past lab reports, get your clinical history in graphs, free." The architecture here is what makes open data possible later.

## Requirements

### Requirement: Coded analyte registry
The system SHALL maintain a biomarker registry where every analyte carries a LOINC code and a UCUM unit, and every stored measurement additionally carries its method/assay and originating laboratory.

#### Scenario: Coding is mandatory for a measurement
- **WHEN** a measurement is persisted
- **THEN** it has a UCUM unit and links to a LOINC-coded analyte
- **AND** without method/assay and lab it is flagged not aggregation-eligible

### Requirement: Three ranges per analyte
The system SHALL store and display three distinct ranges — laboratory reference (method-dependent), longevity-optimal (with cited source), and safety threshold — and never collapse them.

#### Scenario: A value near the optimal edge but within reference
- **WHEN** an ApoB value sits inside the lab reference range but outside the optimal range
- **THEN** the display shows it as reference-normal yet optimal-out
- **AND** the optimal range shows its source

### Requirement: Deterministic pipeline with a hard boundary
The system SHALL make extraction, mapping, and threshold/index computation deterministic and reproducible (same input → same output); the LLM SHALL only produce the plain-language narration, generated once and cached.

#### Scenario: Numbers are reproducible
- **WHEN** the same report is imported twice
- **THEN** the extracted values, mappings, and computed thresholds are identical
- **AND** any LLM narration is fetched from cache keyed on a fingerprint of the underlying data

### Requirement: Import from PDF, photo, and CSV with learned templates
The system SHALL import lab data from PDF, photo, and CSV; on recognising a laboratory's format it SHALL generate a deterministic template so subsequent imports from that lab bypass the LLM.

#### Scenario: Second import from a known lab
- **WHEN** a report matches a previously learned laboratory template
- **THEN** extraction runs deterministically without an LLM call

### Requirement: Manual entry of equal standing
The system SHALL support manual measurement entry as a first-class path, with a sanity check on out-of-range values.

#### Scenario: Typed value gets the same treatment
- **WHEN** a user types a value manually
- **THEN** it is stored with the same provenance fields and a plausibility check
- **AND** it is not treated as inferior to an imported value except where verification status matters (see `community-and-social`)

### Requirement: Human review before persistence
The system SHALL require human confirmation before extracted values enter the system, and SHALL fail loudly on anything not understood.

#### Scenario: Unrecognised line item
- **WHEN** the parser cannot interpret a line
- **THEN** it declares the item and asks, rather than proceeding on an incomplete report
- **AND** the review step shows recognised / not-recognised / inferred status per item

### Requirement: Completeness and freshness indicators
The system SHALL show, per organ system, how complete and how fresh the data is.

#### Scenario: Sparse metabolic panel
- **WHEN** a system has 6 of 13 expected markers, last updated 4 months ago
- **THEN** the UI states "Metabolic: 6/13, last updated 4 months ago"
- **AND** any index computed on sparse data is annotated as such (see `dashboards-and-doctor-view`)

### Requirement: Optional PII obfuscation on import
The system SHALL offer PII obfuscation of imported documents as an option with a reviewable diff; by default the original file is retained **raw** (the user chooses to obfuscate).

#### Scenario: User opts to obfuscate
- **WHEN** a user chooses to obfuscate a report containing name and ID
- **THEN** the PII is obfuscated and the user can see what was removed
- **AND** by default, without that choice, the original file is retained raw

### Requirement: Original report file retained and public raw
The system SHALL retain the original lab report file and make it public by default in its **raw** original format, as part of OpenData.

#### Scenario: Raw original file published
- **WHEN** a user's lab report is public
- **THEN** the raw original-format file (e.g. PDF) is available exactly as uploaded
- **AND** it is part of the OpenData public snapshot (see `analytics-and-open-data`)
