## ADDED Requirements

### Requirement: Adherence states have one stored name each
The system SHALL store each intake or session event in exactly one of four states, `done`, `partial`, `skipped`, `missed`, which are the states the main spec calls taken-as-planned, partial-dose, intentionally-skipped and forgotten (Q150), or in no state while the event is still pending. A state SHALL be set only by an explicit user action; the system SHALL NOT infer one, and no rule, schedule or default SHALL set `done` or `partial`.

#### Scenario: A pending event has no state
- **WHEN** an intake is due and the user has not marked it
- **THEN** the event is stored without a state
- **AND** it is not counted as done, skipped or missed by any export

### Requirement: Intake events export only what was taken
The system SHALL export an intake event as an exposure only according to its stored state: `done` and `partial` events describe something taken; `skipped`, `missed` and stateless events describe nothing taken. The export SHALL use the FHIR R4 MedicationAdministration `status` codes `completed`, `stopped` and `not-done` (value set https://hl7.org/fhir/R4/valueset-medication-admin-status.html, fetched 2026-11-28) and the column rules of the M03 OMOP DRUG_EXPOSURE mapping (`docs/omop/drug-exposure-mapping.md`: source-value, unit and route columns). The per-event export SHALL be a new function that reuses those column rules; `drug_exposure_start_date` SHALL come from the date stored on the intake event, never from the protocol version run. `quantity` SHALL come only from an amount the user entered on that event, SHALL be empty when none was entered, and SHALL never be derived from the planned dose (Q152). Because DRUG_EXPOSURE has no status column, the adherence state SHALL be carried by the MedicationAdministration status and by the app; an exported `partial` row without an entered amount is not distinguishable from a `done` row in OMOP columns alone (Q155). An amount entered on an intake event SHALL be stored with a UCUM unit string, and SHALL be exported as `quantity` only when that unit equals the unit the M03 mapping writes to `dose_unit_source_value`; otherwise `quantity` SHALL stay empty and no unit conversion SHALL be attempted (Q158). When the planned intervention is `per_body_weight`, `quantity` SHALL stay empty even if the units match, because the M03 mapping writes a per-weight unit (for example `mg/kg`) to `dose_unit_source_value` and a per-weight amount is not an absolute amount (Q158). Scope is intake events only (Q147).

#### Scenario: A done intake exports one administration and one exposure
- **WHEN** an intake event in state `done` is exported
- **THEN** exactly one MedicationAdministration with status `completed` is produced
- **AND** exactly one DRUG_EXPOSURE row is produced, whose `drug_exposure_start_date` is the date stored on the intake event
- **AND** the M03 mapping supplies only the source-value, unit and route columns, and `quantity` is empty unless the user entered an amount on that event

#### Scenario: Each event is dated by its own day
- **WHEN** two `done` events of the same intervention on different days are exported
- **THEN** the two DRUG_EXPOSURE rows have different `drug_exposure_start_date` values, each equal to its event date

#### Scenario: A skipped or missed intake writes no exposure
- **WHEN** an intake event in state `skipped` or `missed` is exported
- **THEN** no DRUG_EXPOSURE row is written for it
- **AND** if a MedicationAdministration is emitted for it, its status is `not-done`, never `completed`

#### Scenario: A partial intake with an entered amount exports that amount
- **WHEN** an intake event in state `partial` is exported and the user entered an amount on that event
- **THEN** one DRUG_EXPOSURE row is written, dated from the intake event, with `quantity` equal to the entered amount
- **AND** if a MedicationAdministration is emitted its status is `stopped`, never `completed` (Q151)

#### Scenario: A partial intake without an entered amount exports an empty quantity
- **WHEN** an intake event in state `partial` is exported and the user entered no amount on that event
- **THEN** one DRUG_EXPOSURE row is written, dated from the intake event, with `quantity` empty
- **AND** the quantity is never derived from the planned dose (Q152)
- **AND** if a MedicationAdministration is emitted its status is `stopped`, never `completed`

#### Scenario: An entered amount in a different unit exports an empty quantity
- **WHEN** a `partial` or `done` event has an entered amount whose unit differs from the planned unit
- **THEN** the DRUG_EXPOSURE row has an empty `quantity`
- **AND** the amount is not converted

#### Scenario: An entered per-weight amount exports an empty quantity
- **WHEN** a `partial` or `done` event of a `per_body_weight` intervention has an entered amount whose unit equals the stored per-weight unit (for example `mg/kg`)
- **THEN** the DRUG_EXPOSURE row has an empty `quantity`
- **AND** the stored per-weight unit text goes to `dose_unit_source_value` as the M03 mapping writes it

#### Scenario: A state set by a rule exports no exposure
- **WHEN** a rule, schedule or default tries to set an intake event to `done` or `partial`
- **THEN** the state is not stored and the event stays without a state
- **AND** no DRUG_EXPOSURE row is written for it

#### Scenario: An event without a recorded state exports nothing
- **WHEN** an intake event has no stored state
- **THEN** no MedicationAdministration and no DRUG_EXPOSURE row is produced for it
- **AND** the state is not guessed from the planned time, the schedule or neighbouring events

#### Scenario: Other logs are not exported by this change
- **WHEN** a therapy session, an exercise session or a meal is logged
- **THEN** this change exports no FHIR resource and no OMOP row for it (Q147)

### Requirement: Reminders are shown in the app first
The system SHALL show reminders for an intake, a session and a due stock in the app (on the daily log and the calendar). Web Push and email reminders SHALL NOT be sent until a separate change adds each channel with its own consent and an approved dependency (Q144).

#### Scenario: Intake reminder appears in the app
- **WHEN** an intake is due and has no state
- **THEN** the daily log shows a reminder naming the intake
- **AND** no push notification and no email is sent

#### Scenario: Due session appears in the app
- **WHEN** a therapy session is due and has no state
- **THEN** the calendar shows it and the daily log shows an in-app reminder naming the session (Q144)
- **AND** no push notification and no email is sent
