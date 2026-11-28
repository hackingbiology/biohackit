## MODIFIED Requirements

### Requirement: VO2max captured as a biomarker
The system SHALL capture VO2max as a measured biomarker with date and method. The method SHALL be free text and the unit a UCUM string; no code (for example LOINC) and no method list SHALL be stored until one is fetched from its source and cited (Q149).

#### Scenario: VO2max recorded
- **WHEN** a user enters or uploads a VO2max value
- **THEN** it is stored as a biomarker (see `biomarkers-and-labs`) and shown in dashboards

#### Scenario: VO2max has no invented code
- **WHEN** a VO2max value is stored
- **THEN** it carries its date, a free-text method and a unit
- **AND** it carries no code from a code system unless that code was cited from its source

## ADDED Requirements

### Requirement: Activity level is declared, with no MET table
The system SHALL take the activity level used by `nutrition-management` from what the user declares, and SHALL NOT ship a MET table or per-activity MET values (Q143).

#### Scenario: Activity level without MET values
- **WHEN** a user declares strength, cardio, mobility and HIIT
- **THEN** the declared activity level is available to the TDEE computation
- **AND** no MET value is stored or shown
