## ADDED Requirements

### Requirement: Three layers of quality assurance
The system SHALL ensure the quality of shared protocols and data through three layers: deterministic validation, community review, and expert oversight. (Source: whitepaper § 05 What it does. The source names the layers only; see QUESTIONS.md Q17.)

#### Scenario: A shared item passes through all three layers
- **WHEN** a protocol or dataset is shared publicly
- **THEN** deterministic validation rules apply to it
- **AND** the community can review it (see Public claim review)
- **AND** an expert-oversight mechanism exists that can flag it

### Requirement: Knowledge is not for sale
The system SHALL NOT sell protocols, biomarkers, safety rules or the open dataset, and SHALL NOT allow a supplier to buy influence over which protocols emerge, are ranked or are shown. (Source: docs/foundation.md § 3 and § 5; complements `procurement-and-inventory`.)

#### Scenario: No paid placement
- **WHEN** protocols or interventions are listed or ranked
- **THEN** no supplier payment affects the listing or ranking

#### Scenario: Open data is not a product
- **WHEN** the open dataset or the knowledge content is offered
- **THEN** it is offered without charge and without exclusive access for any party

### Requirement: Stewardship and mission lock are published
The system SHALL publish, in its About section, that the Hacking Biology Foundation stewards biohack.it, the guarantees the Foundation gives (never commercial, open code and data, harm reduction first, transparency of method, data belongs to the person) and a link to the Foundation's site. (Source: docs/foundation.md § 1, § 3, § 6; whitepaper § 13.)

#### Scenario: About section states the steward and its guarantees
- **WHEN** a visitor opens the About section
- **THEN** it names the Foundation as steward and lists the guarantees
- **AND** it states that the software is licensed AGPL-3.0

#### Scenario: About links to the organisation site
- **WHEN** a visitor follows the Foundation link in the About section
- **THEN** it leads to the Foundation's own site

### Requirement: Specification is publicly browsable
The system SHALL publish its functional specification, and its architecture decision records, in the open and browsable from the product site. (Source: whitepaper § Abstract and § 12; docs/foundation.md § 4.)

#### Scenario: Browse the specification
- **WHEN** a visitor opens the specification section of the site
- **THEN** the capabilities, requirements and scenarios are listed and readable without signing in

#### Scenario: Specification tracks the repository
- **WHEN** a requirement changes in the repository
- **THEN** the published specification reflects the change
