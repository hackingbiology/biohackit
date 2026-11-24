## ADDED Requirements

### Requirement: Ecosystem scan before building
Before a module's OpenSpec change is written or implemented, the project SHALL publish an ecosystem scan for that module listing candidate external projects with verified licence, activity and fit, and a reuse decision for each.

#### Scenario: Module change cites its scan
- **WHEN** an OpenSpec change for module Mxx exists
- **THEN** `docs/ecosystem/mxx*.md` exists and the change's proposal links it

#### Scenario: Scan entries are verified
- **WHEN** a scan lists a project
- **THEN** the entry has URL, licence, AGPL compatibility, last-activity date and decision, each either verified from the source or marked unknown

### Requirement: Licence-compatible reuse
The project SHALL only merge third-party code under AGPL-3.0-compatible licences and SHALL record the licence of every reused dataset and schema.

#### Scenario: Incompatible dependency rejected
- **WHEN** a dependency with an AGPL-incompatible licence is added
- **THEN** the gates fail

### Requirement: Give-back register
The project SHALL maintain a register of contributions back to upstream projects and SHALL perform outward contributions only after owner approval.

#### Scenario: Proposed upstream contribution
- **WHEN** work produces something useful upstream (bug fix, mapping, dataset)
- **THEN** a give-back entry is added and proposed in the daily digest, and nothing is posted externally until approved
