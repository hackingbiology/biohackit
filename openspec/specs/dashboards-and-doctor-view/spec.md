# Dashboards & Doctor View (M5)

## Purpose

The public dashboard and the physician-facing output. Organ-system decomposition, biological-age delta shown honestly, the doctor protocol sheet, and the double-column "literature vs observed" comparison that no competitor can build.

## Requirements

### Requirement: Public dashboard grouped by biomarker family
The system SHALL present dashboards grouped by biomarker family (lipids, glucose, kidney, liver, inflammation, hormones, body composition, biological age), each stating why the group is monitored.

#### Scenario: Group shows its rationale
- **WHEN** a viewer opens the kidney group
- **THEN** it shows the markers and the reason they are monitored (which active compound requires them)

### Requirement: Organ-system view unifies efficacy and safety
The system SHALL provide an organ-system view where the same panel that shows efficacy also shows safety gaps.

#### Scenario: Efficacy and safety in one tile
- **WHEN** the renal tile shows a trend
- **THEN** it can simultaneously show "you take a nephrotoxic compound and have not measured creatinine in 8 months"

### Requirement: Headline metric first, then organ-system grid
The system SHALL lead the personal dashboard with a single headline metric — the biological-vs-chronological age delta — shown with its uncertainty interval and the clock and laboratory declared, followed by the organ-system grid. It SHALL NOT use this metric as a reputation or ranking metric.

> RESOLVED (2026-08-04): headline number first, then the organ-system grid.

#### Scenario: Headline then grid
- **WHEN** the dashboard loads and a biological age is available
- **THEN** the biological-age delta is shown first as the headline, with its uncertainty interval, clock, and lab
- **AND** the organ-system grid follows below

#### Scenario: Graceful fallback when the clock is missing
- **WHEN** no biological age is available
- **THEN** the headline falls back to a data-coverage summary (systems covered / freshness)
- **AND** the organ-system grid still renders in full

### Requirement: Biological clocks surfaced as a group
The system SHALL present the available biological clocks — computed (PhenoAge) and uploaded (epigenetic, glycation) — as a dashboard group, each with its method/provider and uncertainty; the headline biological-age delta uses a declared default clock.

#### Scenario: Multiple clocks shown honestly
- **WHEN** more than one biological clock is available
- **THEN** the dashboard shows each clock with its method/provider and uncertainty interval
- **AND** the headline names which clock and lab it uses, and clocks are not presented as comparable across providers

### Requirement: Doctor protocol sheet
The system SHALL generate a "protocol sheet" for a physician: everything taken, doses, timing, since when, markers monitored with rationale, trends, and open alerts — as a public link and a PDF.

#### Scenario: Handover artifact
- **WHEN** a user chooses "prepare for my doctor"
- **THEN** the system generates the sheet as link + PDF
- **AND** it is legible without a platform account

### Requirement: Double-column literature vs observed
The system SHALL, per intervention, place side by side what the literature predicts (Evidence Layer) and what the biomarkers of people practising it show (cohort).

#### Scenario: Prediction beside reality
- **WHEN** an intervention has both literature evidence and a cohort
- **THEN** the view shows "literature predicts X; the N people who did it show Y"
- **AND** the comparison uses the Outcome↔Biomarker link (see `evidence-layer`, `analytics-and-open-data`)

### Requirement: Cohort comparison — inline reference AND dedicated view
The system SHALL surface cohort comparison in BOTH forms: (A) a lightweight inline reference on each dashboard tile, AND (B) a dedicated "vs cohort" view with distribution, percentile, stratification, sample size (n), and adherence weighting.

> RESOLVED (2026-08-04): both A and B.

#### Scenario: Inline reference on the tile
- **WHEN** a biomarker's protocol has a cohort large enough to compare
- **THEN** its dashboard tile shows a lightweight "you vs cohort" reference (e.g. vs cohort median)
- **AND** the tile links into the dedicated "vs cohort" view

#### Scenario: Dedicated view shows the distribution honestly
- **WHEN** the user opens the "vs cohort" view for a biomarker
- **THEN** it shows the cohort distribution with n, stratification, and adherence weighting
- **AND** it declares "not determinable" when the cohort is too small rather than implying precision

### Requirement: Per-biomarker sex/age-normalized percentile
The system SHALL, for every biomarker measurement, report the percentile it falls in, normalized for sex and age against **published reference distributions**, alongside the reference / optimal / safety ranges, and SHALL declare the published source used.

#### Scenario: Percentile shown per marker
- **WHEN** a biomarker value is displayed
- **THEN** it shows its sex/age-normalized percentile with the reference population declared
- **AND** this is distinct from the cohort comparison (population percentile vs same-protocol peers)

#### Scenario: Insufficient reference data
- **WHEN** the reference population is insufficient to place a percentile for that sex/age
- **THEN** the system declares "not determinable" rather than showing a guessed percentile
