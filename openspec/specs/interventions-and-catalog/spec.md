# Interventions & Substance Catalog

## Purpose

The catalog of substances and the entity-resolution discipline that keeps a multilingual, `.it` project from silently ignoring what users enter. Owns `Substance` records, external coding, synonyms, and the input→output diff. Extends spec v0.3 §8.5quater.

## Requirements

### Requirement: Substance resolution on codes, not English strings
The system SHALL resolve every substance to external identifiers (RxNorm / ATC / PubChem / UNII) via a multilingual synonym table, never on raw English strings.

#### Scenario: Italian input resolves
- **WHEN** a user enters "rapamicina"
- **THEN** the system resolves it to the same entity as "rapamycin"/"sirolimus" via synonyms
- **AND** the resolved entity carries its external codes for downstream safety and aggregation

#### Scenario: Unresolved substance is surfaced, not dropped
- **WHEN** a substance cannot be resolved to a code
- **THEN** the entry is marked `ambiguous` and queued for review
- **AND** it is never silently discarded or matched to the wrong entity

### Requirement: LLM never writes into constrained columns
The system SHALL populate closed enums by deterministic code after validation; free text goes to a separate wide notes field; out-of-enum proposals are marked `ambiguous`.

#### Scenario: Over-long model output does not corrupt persistence
- **WHEN** the extractor proposes a value that does not fit a constrained field
- **THEN** the value is routed to review as `ambiguous`
- **AND** the insert neither truncates silently nor loses sibling entries

### Requirement: Input↔output diff at end of extraction
The system SHALL always show the diff between what the user submitted and what was recognised.

#### Scenario: 8 in, 5 recognised
- **WHEN** a user submits eight substances and five resolve
- **THEN** the system shows "8 submitted, 5 recognised, 3 not understood" with the three listed
- **AND** the user can correct or confirm the three before anything is committed

### Requirement: Substance catalog metadata
The system SHALL store per `Substance`: name(s), external identifiers, class, known interactions, and associated safety markers.

#### Scenario: Safety markers travel with the substance
- **WHEN** a substance with known safety markers is added to a plan
- **THEN** its associated safety biomarkers become candidates for the measurement plan (see `safety-guardrails`)

### Requirement: Long extraction jobs are queued and resumable
The system SHALL run long parsing/extraction jobs in an idempotent queue with resume, never as an interactive request that can time out with quota consumed and no result.

#### Scenario: Job survives a timeout
- **WHEN** an extraction job exceeds an interactive limit
- **THEN** it continues in the queue and its partial progress is retained
- **AND** re-running is idempotent rather than duplicating entries

### Requirement: Seed and enrich the catalog from Evipedia
The system SHALL seed and enrich its substance/intervention catalog from Evipedia's interventions and their alternate names (see `ai-uses-and-attribution`), to bootstrap coverage and multilingual entity resolution.

#### Scenario: Alternate names aid resolution
- **WHEN** the catalog is seeded or enriched from Evipedia
- **THEN** Evipedia intervention names and synonyms populate the synonym table alongside RxNorm/ATC/PubChem/UNII
- **AND** Forever Healthy is attributed (CC BY 4.0)

### Requirement: Posology provenance (human vs animal)
The system SHALL record, per intervention posology, whether the dosing derives from `human` or `animal` experimentation, with its source, so extrapolated dosing is never presented as established.

#### Scenario: Animal-derived dose is marked
- **WHEN** a dose is extrapolated from animal studies
- **THEN** the posology is tagged `animal-derived` with its source
- **AND** a dose from human trials is tagged `human-derived` (see `evidence-layer`)

### Requirement: Principal peptides present in the catalog
The system SHALL include the principal, commonly-used peptides as known substances in the catalog (resolved to codes and synonyms), so peptide-first users find them — handled as ordinary substances, without a peptide-specific subsystem.

#### Scenario: A common peptide is already present
- **WHEN** a user searches for a common peptide (e.g. BPC-157, ipamorelin, semaglutide)
- **THEN** it is present as a known substance with its codes/synonyms and evidence link
- **AND** peptides are treated like any other substance, not a separate subsystem
