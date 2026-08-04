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
