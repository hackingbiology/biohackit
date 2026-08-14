# Evidence Layer (M11)

## Purpose

Grades literature into structured, comparable claims and — crucially — links each outcome to a biomarker, which is what lets the platform compare prediction with observation. Bootstrapped on the longevity subset first.

## Requirements

### Requirement: Evipedia as the primary evidence source
The system SHALL use Forever Healthy's Evipedia knowledgebase as its primary source of intervention evidence reviews (via `ai-uses-and-attribution`), and SHALL run its own AI4L-audited ingestion only for interventions Evipedia does not cover.

#### Scenario: Base on Evipedia, extend where absent
- **WHEN** evidence for an intervention is needed
- **THEN** the platform first uses the Evipedia review (conclusion, grading, PMIDs), attributed to Forever Healthy
- **AND** it runs its own AI4L-audited ingestion only where Evipedia has no coverage

### Requirement: Structured evidence claims
The system SHALL ingest literature (Europe PMC / PubMed / preprints) and extract, in batch, `EvidenceClaim` records of intervention × outcome × study.

#### Scenario: Batch extraction offline
- **WHEN** literature is ingested
- **THEN** claims are extracted in batch offline, not in an interactive request

### Requirement: Confidence separate from effect size
The system SHALL grade confidence with GRADE-inspired weighted factors and report effect size separately, in the outcome's native units.

#### Scenario: No percentages from absolutes
- **WHEN** an effect size is stored
- **THEN** it is in native units, not a percentage derived from absolute values
- **AND** confidence is a separate field from effect size

### Requirement: Directional evidence with study counts
The system SHALL record directional evidence with explicit counts of favourable, null, and unfavourable studies.

#### Scenario: The nulls are counted
- **WHEN** evidence for a compound is summarised
- **THEN** favourable/null/unfavourable counts are all shown

### Requirement: Outcome↔Biomarker link
The system SHALL map outcomes to biomarkers so literature predictions can be compared with observed cohort biomarkers.

#### Scenario: Enables the double column
- **WHEN** an outcome maps to a biomarker
- **THEN** the dashboard double-column can align literature and cohort (see `dashboards-and-doctor-view`)

### Requirement: Alerts on evidence change
The system SHALL alert users when evidence for a compound they use materially changes.

#### Scenario: New unfavourable evidence
- **WHEN** significant new evidence lands for an active compound
- **THEN** affected users are alerted
