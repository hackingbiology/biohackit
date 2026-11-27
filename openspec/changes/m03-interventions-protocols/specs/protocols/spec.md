## MODIFIED Requirements

### Requirement: Versioning and change tracking
The system SHALL version every protocol facet, and SHALL record each change as a tracked, timestamped, attributable event with a **mandatory reason**. A protocol in state `Draft` SHALL be edited in place, SHALL create no version and needs no reason; versioning with a mandatory reason SHALL start when the protocol leaves `Draft`.

#### Scenario: A dose change is a tracked event
- **WHEN** a user changes rapamycin from 6 mg/week to 8 mg/week
- **THEN** a new version is created with a change event {field, old, new, timestamp, actor, reason}
- **AND** the change cannot be saved without a reason
- **AND** the prior version remains retrievable and referenceable by measurements taken under it

#### Scenario: Diff between versions
- **WHEN** a user or viewer compares two versions of a protocol
- **THEN** the system SHALL render a field-level diff of interventions, doses, cycles, and measures

#### Scenario: Measurements bind to the version in effect
- **WHEN** a measurement is recorded on a date
- **THEN** it is associated with the protocol version active on that date
- **AND** later edits to the protocol never silently reinterpret past measurements

#### Scenario: A saved draft is editable in place
- **WHEN** a user edits a saved protocol that is still in state `Draft`
- **THEN** the draft is updated in place
- **AND** no version is created and no reason is required

#### Scenario: A measurement dated during Draft is bound to no version
- **WHEN** a measurement is dated while its protocol is in state `Draft`
- **THEN** it is bound to no protocol version
- **AND** it is not re-bound to version 1 when the protocol later leaves `Draft`

## ADDED Requirements

### Requirement: A protocol version is immutable
The system SHALL keep every created `ProtocolVersion` unchanged, including the latest one, so that measurements bound to it keep their meaning. Any change to a created version, including a correction to the latest version, SHALL create a new version with a change event and a mandatory reason. (Source: docs/ecosystem/m03-interventions-protocols.md (f); builds on "Versioning and change tracking", which defines the `Draft` exception.)

#### Scenario: An older version cannot be edited
- **WHEN** a protocol has versions 1 and 2 and a user tries to edit version 1
- **THEN** the edit is refused
- **AND** version 1 is returned unchanged

#### Scenario: Editing the latest version creates a new version
- **WHEN** a protocol has versions 1 and 2 and a user corrects a dose recorded in version 2
- **THEN** version 3 is created with the change event and a reason
- **AND** version 2 is unchanged

#### Scenario: A change without a reason is refused
- **WHEN** a user changes a created version and gives no reason
- **THEN** no new version is created
- **AND** the saved version is unchanged

### Requirement: Protocol export mappings cite their target schema
The system SHALL document the mapping of a tracked intervention to FHIR MedicationStatement and to OMOP DRUG_EXPOSURE, and of a protocol to FHIR PlanDefinition, as export targets and not as storage schemas. OMOP concept ids SHALL stay empty until the OHDSI vocabularies are loaded. (Source: docs/ecosystem/m03-interventions-protocols.md (c).)

#### Scenario: An exported intervention has no invented concept id
- **WHEN** a tracked intervention is exported as an OMOP DRUG_EXPOSURE row
- **THEN** `drug_concept_id` is empty when no vocabulary is loaded
- **AND** the source value is exported as stored
