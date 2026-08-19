# Scientific Method & Evidence (cross-cutting)

## Purpose

States publicly what this data can and cannot support, so credibility comes from declared limits rather than from claimed rigour. It carries the project's honest position — **self-managed, self-declared, self-selected experimentation, not a clinical trial** — the evidence hierarchy that ranks what we hold, the bar a study must clear before the words *distributed trial* are used, and the cultural commitment to negative results.

The honest comparison is not against a controlled trial, which this loses and does not try to win. It is against what exists today: a dose written in prose, a screenshot of a lab report, a spreadsheet nobody else can open.

## Requirements

### Requirement: Publicly declared nature and limits
The system SHALL publish, as a first-class page, that its data is self-managed, self-declared and self-selected, without randomisation, blinding or controlled conditions, and that participants change protocols mid-course, measure irregularly and drop out.

#### Scenario: Limits are stated before claims
- **WHEN** a visitor or researcher encounters the platform's results
- **THEN** the declared nature and limits are available and linked from where results are shown
- **AND** the stated comparison is against unstructured practice (prose, screenshots, spreadsheets), never against a controlled trial

### Requirement: Evidence hierarchy
The system SHALL declare and apply an evidence hierarchy — controlled trial > observational > N-of-1 > anecdote — and SHALL state when an N-of-1 is genuinely informative and when it is not.

#### Scenario: A claim is placed in the hierarchy
- **WHEN** evidence supports a statement on the platform
- **THEN** its level in the hierarchy is shown alongside it (see `evidence-layer`)
- **AND** self-reported data is never presented at the level of controlled evidence

### Requirement: Qualification bar for a distributed trial
The system SHALL publish the criteria a study must meet before it is described as a distributed trial — pre-registered endpoint, shared protocol version, declared timepoints, adherence floor, minimum cohort size, published analysis plan — and SHALL apply the term only to studies that meet them.

> RESOLVED (2026-08-19): distributed trials are kept as the stated destination; the word is earned by publishing the bar rather than avoided. Nothing *starts* as a trial — a study becomes trial-like only when enough people run the same protocol with endpoints declared in advance.

#### Scenario: The term is applied only when earned
- **WHEN** a study does not meet every published criterion
- **THEN** it is presented as a self-experiment or a cohort observation, not as a distributed trial
- **AND** the unmet criteria are visible

### Requirement: Observed, never caused
The system SHALL phrase aggregate findings as observation, not causation — "among qualifying users exposed to X, the observed change was Y" — and SHALL NOT state or imply that an intervention caused an outcome.

#### Scenario: Aggregate output is phrased as observation
- **WHEN** a cohort result is rendered anywhere in the product or exports
- **THEN** it is expressed as an observed change in a self-selected group
- **AND** causal phrasing is not produced by any surface, including AI-generated narration

### Requirement: Evidence confidence on every displayed number
The system SHALL accompany every meaningful number it displays or exports with four things — **value, uncertainty, provenance and evidence level** — and SHALL suppress or mark as not-determinable any number that cannot carry them.

#### Scenario: A number without its confidence is not shown
- **WHEN** a computed or measured value is rendered anywhere in the product, the doctor sheet, or an export
- **THEN** it carries its uncertainty, where it came from, and the strength of evidence behind it
- **AND** if any of those is unavailable, the value is marked not-determinable rather than displayed bare

#### Scenario: Evidence confidence travels into exports
- **WHEN** data leaves the platform through open data or the research API
- **THEN** the same four attributes travel with each value (see `analytics-and-open-data`)

### Requirement: Negative results are first-class
The system SHALL accept, display and encourage null and negative outcomes as valid contributions, with the same standing as positive ones.

#### Scenario: A null result is contributed
- **WHEN** a user reports that an intervention produced no detectable change
- **THEN** the result is recorded and shown as a legitimate outcome
- **AND** it counts toward cohort aggregation and reputation for data quality (see `community-and-social`)
