## ADDED Requirements

### Requirement: LLM usage is capped by a monthly credit allowance
The system SHALL meter LLM-backed analyses per user against a visible allowance that regenerates monthly, and SHALL NOT place an LLM call in the interactive path of an ordinary page load. (Source: docs/hackingbiology-project-spec.md § 8.4, § 8.5bis. The source gives no amounts; see QUESTIONS.md Q19.)

#### Scenario: Allowance is visible and enforced
- **WHEN** a user requests an LLM-backed analysis
- **THEN** the remaining allowance is shown before and after
- **AND** when it is exhausted the request is declined with the date it regenerates

#### Scenario: Ordinary pages make no LLM call
- **WHEN** an ordinary page is loaded
- **THEN** any narration shown comes from cache, and no LLM call is made

### Requirement: AI proposals are offered as a block
The system SHALL present AI-generated proposals as a block that the user can accept in full or reject in full, and SHALL NOT apply a proposal without that choice. (Source: docs/hackingbiology-project-spec.md § 8.5ter, § 8.4 item 2.)

#### Scenario: Accept all or reject all
- **WHEN** the system proposes changes
- **THEN** the user can accept all or reject all
- **AND** nothing is applied before the user chooses
