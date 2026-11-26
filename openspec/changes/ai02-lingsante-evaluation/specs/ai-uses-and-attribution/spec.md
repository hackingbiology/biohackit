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

### Requirement: Model governance record before adoption
Before any AI model is enabled for users, the project SHALL publish a governance record for it, covering technical, legal, ethical and political dimensions, and SHALL record the adoption decision and its rationale publicly. The record SHALL cover at least:
- origin;
- licence;
- jurisdiction;
- data flows;
- training-data transparency;
- behavioural audit;
- regulatory fit;
- supply-chain safety;
- alternatives.

#### Scenario: Governance record complete
- **WHEN** a model is proposed for enablement
- **THEN** `docs/research/model-governance/<model>.md` exists, with each dimension either filled from cited sources or marked unknown, and the decision (adopt / adopt with limits / reject) is in docs/ecosystem and the AI surfaces map

#### Scenario: Behavioural audit across languages
- **WHEN** the behavioural audit runs
- **THEN** the same probe set is answered in it, en and zh by the candidate and by at least two comparison models from different jurisdictions, and differences are reported. The probes cover medical accuracy, refusals, censorship or topic avoidance, commercial steering (e.g. towards products or services) and safety on supplements and doses.

#### Scenario: No silent provider choice
- **WHEN** a user-facing feature uses a model
- **THEN** the feature names the model and its origin, and where practical the instance operator can switch to an alternative model
