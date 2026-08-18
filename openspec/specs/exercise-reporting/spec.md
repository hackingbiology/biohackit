# Exercise Reporting

## Purpose

Lets a user define what their physical activity is and log whether they did it — **not a gym-management app**. Covers strength training, cardio, mobility, whether HIIT is performed, and VO2max. Its job is to make the activity explicit, log done/not-done, and place it in the daily/weekly programming alongside pills and therapeutics.

## Requirements

### Requirement: Define the exercise activity profile
The system SHALL let a user declare their exercise activity — strength training, cardio, mobility, and whether HIIT is performed — at the level of what they do, not per-set gym tracking.

#### Scenario: Activity declared, not micro-managed
- **WHEN** a user sets up their exercise profile
- **THEN** they declare strength, cardio, mobility and HIIT yes/no at an activity level
- **AND** the system does not require per-set/per-rep gym logging

### Requirement: VO2max captured as a biomarker
The system SHALL capture VO2max as a measured biomarker with date and method.

#### Scenario: VO2max recorded
- **WHEN** a user enters or uploads a VO2max value
- **THEN** it is stored as a biomarker (see `biomarkers-and-labs`) and shown in dashboards

### Requirement: Log done or not-done
The system SHALL log whether a planned exercise activity was done, with four-state adherence, without becoming a gym tracker.

#### Scenario: Weekly strength session logged
- **WHEN** a planned strength session is due
- **THEN** the user marks it done / partial / skipped / missed (see `daily-log-and-adherence`)
- **AND** no set-by-set detail is required

### Requirement: Appears in the programming calendar
The system SHALL place exercise activities in the daily/weekly programming calendar alongside pills and therapeutics.

#### Scenario: Exercise on the weekly plan
- **WHEN** the weekly plan is shown
- **THEN** exercise activities appear alongside pill intakes and therapy sessions (see `measurement-planning`)
