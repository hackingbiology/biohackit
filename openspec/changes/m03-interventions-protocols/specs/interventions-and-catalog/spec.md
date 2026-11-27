## MODIFIED Requirements

### Requirement: Seed and enrich the catalog from Evipedia
The system SHALL, when Evipedia exposes interventions and alternate names through a confirmed tool (Q108), seed and enrich its substance/intervention catalog from them (see `ai-uses-and-attribution`), to bootstrap coverage and multilingual entity resolution. Where no such tool is confirmed, the catalog SHALL NOT assume Evipedia as a source. Evipedia names SHALL enter the synonym table as unreviewed candidates with the Evipedia identifier as source, and SHALL resolve a submitted name only after a reviewer has approved them.

#### Scenario: Alternate names aid resolution
- **WHEN** the catalog is seeded or enriched from Evipedia through a confirmed tool
- **THEN** Evipedia intervention names and synonyms enter the synonym table as unreviewed candidates with the Evipedia identifier as source
- **AND** a candidate resolves a submitted name only after review
- **AND** Forever Healthy is attributed under the content terms confirmed in Q15

## ADDED Requirements

### Requirement: Substance codes are stored as cited code strings
The system SHALL store each external substance identifier (RxCUI, PubChem CID, UNII, ATC) as a code string together with its source and fetch date, and SHALL NOT store a bulk RxNorm, ATC/DDD, UNII or PubChem release, nor PubChem synonym or depositor text, until the licence questions Q105 and Q106 are answered. An identifier without a cited source SHALL NOT be stored. (Source: docs/ecosystem/m03-interventions-protocols.md (a).)

#### Scenario: A code is stored with its source and fetch date
- **WHEN** an RxCUI is recorded for a substance
- **THEN** the row holds the code string, the source it came from and the date it was fetched
- **AND** a code without a source is refused

#### Scenario: No bulk terminology file is stored
- **WHEN** the catalog is seeded
- **THEN** only identifier code strings with source and date are written
- **AND** no RxNorm release file, ATC tree, DDD table or UNII file is stored

### Requirement: Synonyms carry provenance and resolve only by exact match
The system SHALL store each synonym with its language, source and reviewer, and SHALL resolve a submitted name only by exact match (after case and whitespace normalisation) on a reviewed synonym. Fuzzy or trigram matching, if used, SHALL only propose a candidate to the review queue and SHALL NOT resolve. (Source: docs/ecosystem/m03-interventions-protocols.md (b).)

#### Scenario: A synonym without a reviewer does not resolve
- **WHEN** a synonym exists with no reviewer
- **THEN** a name matching it is marked `ambiguous` and queued for review
- **AND** it is not resolved to the substance

#### Scenario: A near-match is proposed, not resolved
- **WHEN** a submitted name is close to, but not equal to, a reviewed synonym
- **THEN** the name is marked `ambiguous` and the candidate is shown to the reviewer
- **AND** the entry is not attached to the candidate substance

### Requirement: Evipedia content is stored as identifiers
The system SHALL store, for Evipedia-derived catalog data, review identifiers and PubMed PMIDs, and SHALL NOT store Evipedia review text until the content licence is confirmed (Q15). Where Evipedia offers no alias tool, the synonym table SHALL be filled from reviewed entries with a cited source (Q108). (Source: docs/ecosystem/m03-interventions-protocols.md (d).)

#### Scenario: An Evipedia link keeps no review text
- **WHEN** a substance is linked to an Evipedia review
- **THEN** the review identifier and PMIDs are stored
- **AND** no review text is stored
