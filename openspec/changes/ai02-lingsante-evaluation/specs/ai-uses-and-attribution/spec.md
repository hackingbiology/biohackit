## ADDED Requirements

### Requirement: Model-agnostic extraction proposals verified verbatim
Any AI model used to read lab reports SHALL only propose rows, and the system SHALL accept a proposed value or unit only if deterministic code finds it verbatim in the document text; accepted rows start in the `entered` state.

#### Scenario: Hallucinated value rejected
- **WHEN** a model proposes the value "5.4" for an analyte but "5.4" does not occur in the report text
- **THEN** the row is rejected and never stored

#### Scenario: Verified proposal needs user confirmation
- **WHEN** a proposed value and unit are found verbatim
- **THEN** the row is stored as `entered` with the model name and version recorded, and is excluded from statistics until the user confirms it

### Requirement: Comparable model evaluation
The project SHALL evaluate candidate medical models with a reproducible harness on non-personal sample reports and publish per-model accuracy before any model is enabled.

#### Scenario: Evaluation report published
- **WHEN** the harness runs for a model
- **THEN** it records precision and recall of verified rows per language (it, en, zh) in docs/research/model-evaluation.md
