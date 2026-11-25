## ADDED Requirements

### Requirement: Early partial result during long waits
The system SHALL show what has been understood so far while a long extraction job is still running. (Source: docs/hackingbiology-project-spec.md § 8.5ter.)

#### Scenario: Partial result visible while waiting
- **WHEN** an extraction job runs longer than an interactive request
- **THEN** the user sees the items recognised so far, marked as partial
- **AND** the final result replaces them when the job completes

### Requirement: Weight-relative posology is gated on posology provenance
The system SHALL accept a posology expressed per unit of body weight only together with its posology provenance tag (`human-derived` or `animal-derived`, with source, see "Posology provenance (human vs animal)"), and SHALL display it as the per-weight value exactly as recorded, with its provenance. The system SHALL NOT multiply a per-weight value by the user's body weight, because it never issues a personalised dosage; the user enters their own absolute amount, which passes the "Dose sanity check". Any weight-relative posology that is `animal-derived` falls under "Heightened acknowledgment for research-level or animal-derived dosing" in `safety-guardrails`. (Source: docs/reference/hb-protocol-structure.xlsx, sheet Pharmacy, column C.)

#### Scenario: Weight-relative posology without provenance is not accepted as a dose
- **WHEN** a weight-relative posology is entered without a posology provenance tag
- **THEN** no absolute dose is computed or shown
- **AND** the user is asked to record the provenance and its source

#### Scenario: Animal-derived per-weight dose is not converted to an absolute human dose
- **WHEN** a weight-relative posology has provenance `animal-derived`
- **THEN** no absolute human dose is computed or shown
- **AND** only the per-weight value is shown, with the `animal-derived` marking and its source
- **AND** activating a protocol that contains it requires the heightened acknowledgment from `safety-guardrails`

#### Scenario: Human-derived per-weight value is shown as recorded
- **WHEN** a weight-relative posology has provenance `human-derived` with a source
- **THEN** the per-weight value is shown as recorded with its provenance and source
- **AND** no absolute dose is computed from the user's body weight
- **AND** an absolute amount the user enters passes the dose sanity check before it is accepted

### Requirement: Route and formulation are recorded per intake item
The system SHALL record, per item of a regimen, its route (for example oral or topical) and its formulation (for example liposomal or a named form), so topical and differently formulated products are distinguished from plain oral intake. A route or formulation never implies an amount. (Source: docs/reference/hb-protocol-structure.xlsx, sheet Pharmacy, rows 2-8 and 22.)

#### Scenario: Topical item is distinguished from oral
- **WHEN** an item such as a skin or scalp preparation is added to a regimen
- **THEN** it is recorded with route `topical` and shown separately from oral items
- **AND** it appears in the intake schedule and restock projection like any other item

### Requirement: Multi-ingredient products list their declared ingredients
The system SHALL let a product (for example a blend or a multivitamin) list its ingredients, each resolved as a substance with the amount per unit declared on the product label and the label as its source. A summed daily intake of one ingredient across products SHALL be computed by code from those declared amounts, shown as a sum of label contents and never as a recommended posology; any posology of a user's regimen still carries its posology provenance tag (see "Posology provenance (human vs animal)"). The sum SHALL pass the "Dose sanity check" in `safety-guardrails`. (Source: docs/reference/hb-protocol-structure.xlsx, sheet Pharmacy, rows 231-307.)

#### Scenario: Same ingredient in two products is summed from declared amounts
- **WHEN** two products in the regimen both declare the same ingredient on their labels
- **THEN** the system shows the sum per day, computed deterministically from the declared amounts and the daily number of units, with each label as source
- **AND** the sum is labelled as a total of label contents, not as a posology

#### Scenario: An ingredient without a label amount is not summed
- **WHEN** a product lists an ingredient without a declared amount
- **THEN** that ingredient is listed without an amount and contributes nothing to any sum
- **AND** the system does not estimate the missing amount
