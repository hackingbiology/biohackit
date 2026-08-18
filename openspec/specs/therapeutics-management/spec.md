# Therapeutics Management (periodic treatments)

## Purpose

Manages interventions that require a periodic treatment session rather than a pill — red light / photobiomodulation, HBOT (incl. hypoxia-hyperoxia), IHHT (intermittent hypoxia-hyperoxia training), sauna, cold exposure / cold plunge, whole-body cryotherapy, therapeutic plasma exchange (TPE / plasmapheresis), IV infusions (e.g. NAD+, vitamins), ozone / EBOO, PEMF, whole-body vibration, vagus nerve stimulation (tVNS), and others to add — capturing their **typed parameters**, scheduling their sessions, and logging done/not-done. Builds on the Device/Therapy and Procedure intervention subtypes (see `domain-model`).

## Requirements

### Requirement: Model periodic therapy sessions
The system SHALL model periodic therapy interventions — red light / photobiomodulation, HBOT (incl. hypoxia-hyperoxia), IHHT (intermittent hypoxia-hyperoxia training), sauna, cold exposure / cold plunge, whole-body cryotherapy, therapeutic plasma exchange (TPE / plasmapheresis), IV infusions (e.g. NAD+, vitamins), ozone / EBOO, PEMF, whole-body vibration, vagus nerve stimulation (tVNS) — with their parameters and session cadence, and the catalog SHALL be extensible.

#### Scenario: HBOT protocol captured
- **WHEN** a user configures an HBOT hypoxia-hyperoxia protocol
- **THEN** its parameters and session cadence are stored
- **AND** red light, cryotherapy, cold plunge, plasmapheresis and the others are represented the same way

### Requirement: Typed parameters per therapy
The system SHALL type each therapy with its own characteristic parameters — for example red light (wavelength(s), irradiance, duration, distance, body area), HBOT (pressure in ATA, FiO2 profile, duration), IHHT (FiO2 high/low cycle, cycle count, session duration), cryotherapy / cold plunge (temperature, duration), sauna (temperature, humidity, duration), TPE / plasmapheresis (volume exchanged, replacement fluid, frequency), IV infusion (agent, dose, rate), whole-body vibration (frequency, amplitude, duration), tVNS (intensity, site, duration) — so each exposes only what is meaningful for it.

#### Scenario: Parameters differ by therapy
- **WHEN** two different therapies are configured
- **THEN** each exposes only its characteristic parameters
- **AND** a cold plunge's water temperature is never conflated with a red-light wavelength

### Requirement: Extensible therapy catalog
The system SHALL allow new therapy types to be added and configured with parameters and cadence, without changing the model.

#### Scenario: Add a new therapy
- **WHEN** a new periodic therapy is introduced
- **THEN** it can be configured with its parameters and cadence like existing ones

### Requirement: Schedule therapy sessions on the calendar
The system SHALL place therapy sessions on the daily/weekly programming calendar and remind the user.

#### Scenario: Session scheduled and reminded
- **WHEN** a therapy has a due session
- **THEN** it appears on the calendar (see `measurement-planning`) with a reminder

### Requirement: Log sessions done or not
The system SHALL log therapy sessions with four-state adherence (done / partial / skipped / missed), feeding adherence.

#### Scenario: Session logged
- **WHEN** a user completes or misses a therapy session
- **THEN** it is logged with its adherence state (see `daily-log-and-adherence`)
