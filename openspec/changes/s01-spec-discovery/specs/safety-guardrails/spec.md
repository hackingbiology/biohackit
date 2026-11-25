## ADDED Requirements

### Requirement: Platform describes and never prescribes
The system SHALL tell a user what to measure and SHALL NOT tell a user what to take or how much; no surface, including AI-generated text, issues a recommendation of a compound or dose. (Source: whitepaper § 07 Harm reduction; docs/foundation.md § 3 and § 7.)

#### Scenario: Monitoring guidance names markers, not treatments
- **WHEN** the platform shows safety guidance for an active compound
- **THEN** it lists the markers to measure and why
- **AND** it does not recommend a compound or a dose

#### Scenario: Dose guidance is a plausibility check only
- **WHEN** a dose is checked
- **THEN** the result is framed as a guardrail against an implausible entry, not as clinical advice
- **AND** a dose with `animal-derived` provenance (see "Posology provenance (human vs animal)") keeps its marking and the heightened acknowledgment applies (see `interventions-and-catalog`)

### Requirement: LLM-assisted curation requires human review
The system SHALL treat any safety rule, interaction or mapping proposed by an LLM as a proposal only, generated offline in batch, and SHALL NOT make it live until a named curator approves it. (Source: docs/hackingbiology-project-spec.md § 8.3 and § 8.4.)

#### Scenario: Proposals are not live
- **WHEN** an LLM proposes a safety rule, interaction or mapping
- **THEN** it is stored as a proposal that no user-facing check uses

#### Scenario: Curator approval and provenance
- **WHEN** a curator approves a proposal
- **THEN** it goes live and records the curator and its AI origin as provenance

#### Scenario: Numeric thresholds need a source
- **WHEN** an LLM proposal contains a numeric threshold
- **THEN** it cannot be approved until a cited source is attached
