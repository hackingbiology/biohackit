# Nutrition Management

## Purpose

Defines the user's dietary regime so it can be represented, scheduled and logged alongside the rest of the protocol: a computed **TDEE**, the typical eating **schedule/pattern** they intend to follow (OMAD, calorie restriction, intermittent fasting, or conventional breakfast-lunch-dinner), and the typical **macronutrient split** (carbohydrate / protein / fat). Builds on the Nutrition/Fasting intervention subtype (see `domain-model`) and connects to meal-timed intakes in `pills-management`.

## Requirements

### Requirement: Compute TDEE
The system SHALL compute the user's Total Daily Energy Expenditure deterministically from their biological profile and activity level, and SHALL show the formula used.

#### Scenario: TDEE from profile and activity
- **WHEN** the user's biological profile (see `accounts-and-profiles`) and activity level (see `exercise-reporting`) are known
- **THEN** the system computes TDEE deterministically with a declared formula
- **AND** it recomputes when the inputs change

### Requirement: Declare the typical eating schedule/pattern
The system SHALL let the user declare their typical intended eating pattern — OMAD, calorie restriction, intermittent fasting (e.g. 16/8), or conventional breakfast-lunch-dinner — together with the eating window.

#### Scenario: Fasting pattern declared and scheduled
- **WHEN** a user follows 16/8 intermittent fasting
- **THEN** the pattern and eating window are recorded
- **AND** they are reflected in the daily/weekly calendar and inform meal-timed intakes (see `measurement-planning`, `pills-management`)

### Requirement: Typical macronutrient composition
The system SHALL capture the typical macronutrient split — carbohydrate, protein, fat — the user intends to follow.

#### Scenario: Macro split recorded
- **WHEN** a user sets their typical macros
- **THEN** the carbs/protein/fat composition is stored and shown on the profile

### Requirement: Log adherence to the nutrition plan
The system SHALL log adherence to the declared nutrition pattern (followed / deviated) with exceptions, feeding overall adherence.

#### Scenario: Fasting exception logged
- **WHEN** a user breaks their fasting window
- **THEN** the deviation is logged as an exception (see `daily-log-and-adherence`)
