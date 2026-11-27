## ADDED Requirements

### Requirement: A protocol version is immutable
The system SHALL keep every created `ProtocolVersion` unchanged, including the latest one, so that measurements bound to it keep their meaning. A protocol in state `Draft` SHALL be edited in place and SHALL create no version. A `ProtocolVersion` SHALL be created when the protocol leaves `Draft` or is changed afterwards, and any such change, including a correction to the latest version, SHALL create a new version with a change event and a mandatory reason. (Source: docs/ecosystem/m03-interventions-protocols.md (f); builds on "Versioning and change tracking".)

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

#### Scenario: A saved draft is editable in place
- **WHEN** a user edits a saved protocol that is still in state `Draft`
- **THEN** the draft is updated in place
- **AND** no version is created

### Requirement: Protocol export mappings cite their target schema
The system SHALL document the mapping of a tracked intervention to FHIR MedicationStatement and to OMOP DRUG_EXPOSURE, and of a protocol to FHIR PlanDefinition, as export targets and not as storage schemas. OMOP concept ids SHALL stay empty until the OHDSI vocabularies are loaded. (Source: docs/ecosystem/m03-interventions-protocols.md (c).)

#### Scenario: An exported intervention has no invented concept id
- **WHEN** a tracked intervention is exported as an OMOP DRUG_EXPOSURE row
- **THEN** `drug_concept_id` is empty when no vocabulary is loaded
- **AND** the source value is exported as stored
