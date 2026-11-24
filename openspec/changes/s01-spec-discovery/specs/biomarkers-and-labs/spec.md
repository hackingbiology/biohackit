## ADDED Requirements

### Requirement: Import from wearable export files
The system SHALL accept wearable data as an uploaded export file (Apple Health, Google Fit, or CSV from Oura and Whoop) and SHALL NOT require a live connection to a wearable provider. (Source: docs/hackingbiology-project-spec.md § 4.2, § 6 M10, § 8.5. A commercial aggregator is a later decision and is not specified here.)

#### Scenario: Upload an export file
- **WHEN** a user uploads a supported wearable export file
- **THEN** the values it contains are stored as measurements with the wearable as the declared source
- **AND** the review step of "Human review before persistence" applies before storage

#### Scenario: Unreadable entries are declared
- **WHEN** an entry in the file cannot be understood
- **THEN** the system lists it as not recognised and does not drop it silently

### Requirement: Deterministic calculated markers
The system SHALL compute from stored measurements, by deterministic closed formulas with unit handling, the derived markers HOMA-IR, BUN/creatinine, free water deficit, TG/HDL, LDL/HDL, ApoB/ApoA-I, NLR, PLR, De Ritis and hs-CRP/HDL, and SHALL show each as calculated with the inputs it used. (Source: docs/getbased-reuse-analysis.md § A3. The source names the markers but not the formulas; see QUESTIONS.md Q26.)

#### Scenario: A ratio is computed from its inputs
- **WHEN** all inputs of a calculated marker are present with compatible units
- **THEN** the marker is computed by code, without an LLM, and labelled as calculated
- **AND** the inputs and their dates are listed

#### Scenario: A missing input yields no value
- **WHEN** an input of a calculated marker is missing
- **THEN** the marker is shown as not computable and no approximate value is produced

### Requirement: Deterministic Bortz clock computation
The system SHALL compute the Bortz (2023) biological-age clock deterministically from stored measurements, alongside PhenoAge, and SHALL show a breakdown by component when both clocks are combined. (Source: docs/getbased-reuse-analysis.md § A3. The source does not list the inputs; see QUESTIONS.md Q26.)

#### Scenario: Clock computed with its component breakdown
- **WHEN** the inputs of the Bortz clock are present
- **THEN** the clock value is computed by code and labelled with its method
- **AND** the contribution of each component is shown

#### Scenario: Insufficient inputs
- **WHEN** an input of the clock is missing
- **THEN** the clock is declared not computable rather than estimated

### Requirement: Unit conversion between unit systems
The system SHALL convert a measurement between SI and US conventional units using a documented conversion table, and SHALL keep the originally reported value and unit alongside the converted one. (Source: docs/getbased-reuse-analysis.md § A1, `UNIT_CONVERSIONS`.)

#### Scenario: A US-unit result is shown in SI
- **WHEN** a measurement was reported in a US conventional unit and the user views it in SI
- **THEN** the converted value is shown with its UCUM unit
- **AND** the original value and unit remain retrievable

#### Scenario: No conversion known
- **WHEN** the table has no conversion for an analyte and unit pair
- **THEN** the value is shown in its reported unit and is not converted

### Requirement: Cycle-phase-dependent ranges
The system SHALL support reference ranges that depend on the menstrual-cycle phase for estradiol, progesterone, LH and FSH, and SHALL select the range from the phase recorded for the measurement. (Source: docs/getbased-reuse-analysis.md § A1, `PHASE_RANGES`. The source gives no range values; see QUESTIONS.md Q30.)

#### Scenario: Range follows the recorded phase
- **WHEN** a measurement of one of these analytes has a cycle phase recorded
- **THEN** it is compared with the range of that phase and the phase is named

#### Scenario: No phase recorded
- **WHEN** no phase is recorded for the measurement
- **THEN** the result is shown without a phase-dependent verdict and the user is invited to record the phase

### Requirement: Import can be rolled back
The system SHALL let a user undo a persisted report import as one action, removing the measurements that import created. (Source: docs/getbased-reuse-analysis.md § A2, "persistenza con rollback".)

#### Scenario: Undo an import
- **WHEN** a user rolls back an import
- **THEN** every measurement created by that import is removed
- **AND** measurements from other imports and manual entries are untouched

### Requirement: Extraction benchmark on a synthetic report
The system SHALL provide a benchmark that runs the report parser on a synthetic report with a verified answer key and reports accuracy and speed per model or parser, so that extraction changes can be compared. (Source: docs/getbased-reuse-analysis.md § A2, `import-benchmarks.js`. This project's report and key are authored here, not copied.)

#### Scenario: Benchmark compares parsers
- **WHEN** the benchmark runs
- **THEN** it reports, per parser or model, the share of answer-key results extracted correctly and the elapsed time

#### Scenario: Benchmark data is synthetic
- **WHEN** the benchmark report is inspected
- **THEN** it contains no real person's data and marks every value as synthetic
