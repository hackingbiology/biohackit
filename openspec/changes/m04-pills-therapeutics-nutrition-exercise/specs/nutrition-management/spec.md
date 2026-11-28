## MODIFIED Requirements

### Requirement: Compute TDEE
The system SHALL compute the user's Total Daily Energy Expenditure deterministically from their biological profile and activity level, and SHALL show the formula used. The formula and any activity factor SHALL be stored with a cited source; when none is stored, or an input is missing, the system SHALL show no TDEE number and say which input or source is missing (Q143, Q153).

#### Scenario: TDEE from profile and activity
- **WHEN** the user's biological profile (see `accounts-and-profiles`) and activity level (see `exercise-reporting`) are known
- **THEN** the system computes TDEE deterministically with a declared formula
- **AND** it recomputes when the inputs change

#### Scenario: No source, no number
- **WHEN** no formula with a cited source is stored, or the profile or activity level is missing
- **THEN** no TDEE value is shown
- **AND** the user is told which input or source is missing

## ADDED Requirements

### Requirement: No food composition data is stored without settled terms
The system SHALL NOT store or seed any record of USDA FoodData Central, Open Food Facts or Ciqual. If a user picks a food from FoodData Central, only its id and the fetch date MAY be kept (Q141). A lookup in Open Food Facts, if offered, SHALL be started by the user, shown with attribution and not stored (Q142). Nothing from Ciqual is used (Q145).

#### Scenario: No food record is stored
- **WHEN** a user declares a macronutrient split or an eating pattern
- **THEN** no food composition record from an external database is stored or seeded
- **AND** the split is the user's declared carbohydrate, protein and fat shares

#### Scenario: Picked food keeps an id only
- **WHEN** a user picks a FoodData Central food
- **THEN** only its id and the date of the fetch are stored
- **AND** no nutrient value from it is stored
