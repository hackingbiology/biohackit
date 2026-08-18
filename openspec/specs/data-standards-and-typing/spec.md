# Data Standards & Typing (scientific validity)

## Purpose

A dedicated section documenting the data structures and standards in use and **why** — the backbone that makes biohack.it's data typed, comparable across people and labs, aggregatable, and scientifically credible. It consolidates the coding and typing discipline otherwise scattered across the modules, for scientific and technical reviewers.

## Requirements

### Requirement: Document each standard and its rationale
The system SHALL document each data standard in use and why it is used — HL7 FHIR (internal clinical vocabulary), OMOP CDM (research export), LOINC + UCUM (analytes and units), RxNorm / ATC / AIFA (drugs), PubChem / ChEBI / UNII (molecules), CPIC / PharmGKB (pharmacogenomics), the Hallmarks of Aging framework, and gVCF (genomics).

#### Scenario: Rationale is explicit
- **WHEN** a standard is adopted
- **THEN** the section states what it is used for and why it matters for validity
- **AND** alternatives considered are noted where relevant

### Requirement: Typing discipline for scientific validity
The system SHALL enforce typing discipline — closed enums populated by deterministic code, free text kept separate, and entities resolved to codes — so data is typed rather than free-form.

#### Scenario: Typed, not free-form
- **WHEN** data is persisted
- **THEN** coded fields resolve to their vocabularies and free text is separate (see `interventions-and-catalog`, `biomarkers-and-labs`)
- **AND** untyped/unresolved entries are marked ambiguous, never left as silent free text

### Requirement: Coding plus provenance make aggregation valid
The system SHALL treat coding (LOINC/UCUM/…) plus method/lab provenance as the precondition for cross-person / cross-lab comparability and open-data validity.

#### Scenario: Only comparable data aggregates
- **WHEN** data is aggregated or released for research
- **THEN** comparison uses coded, provenance-carrying values (lab-relative z-scores) (see `analytics-and-open-data`)
- **AND** uncoded data is excluded from the aggregated research export

### Requirement: Published and maintained as a dedicated section
The system SHALL publish this rationale as a dedicated, maintained section for scientific and technical reviewers.

#### Scenario: Reviewer-facing section
- **WHEN** a scientist or engineer evaluates the platform
- **THEN** the data-standards-and-typing section explains the model and its validity basis
