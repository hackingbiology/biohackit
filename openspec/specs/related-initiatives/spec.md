# Related Initiatives (ecosystem landscape)

## Purpose

A clearly highlighted, maintained public register of similar initiatives — commercial and non-commercial — across longevity/biohacking data, protocols, and biomarkers, stating what each does, its data and licensing posture, and biohack.it's relationship to it (reuse, complement, differentiate, or contact). Honesty about the ecosystem is a credibility and acquisition surface, and the basis for being a connector rather than a walled garden. (This is the dedicated home for the landscape that was deliberately kept out of the conference deck.)

## Requirements

### Requirement: Maintain a register of similar initiatives
The system SHALL maintain a register of similar initiatives — commercial and non-commercial — each with what it does, its data/licensing posture, and biohack.it's relationship to it.

#### Scenario: An initiative is recorded with our relationship
- **WHEN** a similar initiative is identified (e.g. Evipedia / Forever Healthy, get-based, ProtocolEngine, MyAgingTests / Clock Foundation, Lamplit, Lucis, TruDiagnostics, GlycanAge, Bryan Johnson / Blueprint)
- **THEN** it is recorded with its description, data/licensing posture, and our relationship
- **AND** the entry declares whether it is commercial or non-commercial

### Requirement: Classify the relationship
The system SHALL classify each initiative's relationship as reuse, complement, differentiate, or contact-upstream.

#### Scenario: Reuse vs differentiate
- **WHEN** an initiative's code or data is reusable under a compatible license
- **THEN** it is classified `reuse` (see `ai-uses-and-attribution`)
- **AND** a proprietary database we only study is classified `differentiate`

### Requirement: Prominently surfaced and current
The system SHALL surface this register as a clearly highlighted public section and keep it current as the field moves.

#### Scenario: Public, living section
- **WHEN** a visitor looks for how biohack.it relates to the rest of the field
- **THEN** the register is prominently accessible and dated
- **AND** it is updated as initiatives change
