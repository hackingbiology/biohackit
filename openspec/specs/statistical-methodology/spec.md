# Statistical Methodology (cross-cutting)

## Purpose

Governs how the platform reasons about numbers, so that aggregate output is defensible rather than merely computed. It names the threats to validity that self-selected, self-reported longitudinal data carries, separates biological change from analytical noise, and makes uncertainty mandatory. Companion to `scientific-method-and-evidence`, which owns the declared limits and the phrasing discipline; this capability owns the arithmetic behind them.

## Requirements

### Requirement: Named threats to validity
The system SHALL declare, and where possible surface or mitigate, the threats to validity carried by its data — confounding, regression to the mean, healthy-user bias, survivor and drop-out bias, selection at entry, measurement error, and multiple testing.

#### Scenario: A cohort result names its threats
- **WHEN** an aggregate result is produced for a cohort
- **THEN** the applicable threats to validity are stated with the result
- **AND** the result is never presented as if these had been controlled for

### Requirement: Regression to the mean and multiplicity are handled explicitly
The system SHALL account for regression to the mean when a cohort is defined by an extreme baseline, and SHALL correct or declare multiplicity when several biomarkers or interventions are examined together.

#### Scenario: Extreme baseline cohort
- **WHEN** a cohort is selected on an out-of-range baseline value
- **THEN** the expected regression-to-the-mean component is declared alongside the observed change

#### Scenario: Many markers examined at once
- **WHEN** an analysis spans multiple biomarkers or interventions
- **THEN** the number of comparisons is declared and correction is applied or its absence stated

### Requirement: Separate biological change from analytical noise
The system SHALL distinguish intra-individual biological variability and assay drift from genuine change, using the method/assay and laboratory provenance stored with every measurement.

#### Scenario: Laboratory or method changes mid-series
- **WHEN** a series contains measurements from different laboratories or assays
- **THEN** the change point is flagged in the series
- **AND** the comparison uses lab-relative normalisation rather than raw values (see `analytics-and-open-data`)

#### Scenario: Change within known biological variability
- **WHEN** an observed change falls within the analyte's known intra-individual variability
- **THEN** it is presented as indistinguishable from noise, not as an effect

### Requirement: Missing data is declared, never imputed silently
The system SHALL declare missingness and drop-out in any aggregate, and SHALL NOT silently impute values.

#### Scenario: Incomplete follow-up
- **WHEN** participants lack follow-up measurements
- **THEN** the aggregate states how many contributed at each timepoint and how many dropped out
- **AND** any imputation is explicit, labelled, and separable from measured values

### Requirement: Uncertainty and effect size are mandatory
The system SHALL express every reported effect with its uncertainty and in the outcome's native units, and SHALL NOT derive a trend from insufficient data.

#### Scenario: No interval, no effect
- **WHEN** an effect is reported
- **THEN** it carries an uncertainty interval and native units
- **AND** a trend is not computed from two measurements (see `analytics-and-open-data`, "stops instead of guessing")

### Requirement: Under-powered comparisons are declared, not hidden
The system SHALL state when a cohort is too small or too sparse to support a comparison, rather than presenting a precise-looking number.

#### Scenario: Cohort too small
- **WHEN** a comparison falls below the declared minimum cohort or coverage
- **THEN** the system reports "not determinable" with what is missing
