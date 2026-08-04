# Claims Validator (M12)

## Purpose

Paste a product page URL; the system checks its claims against the Evidence Layer. No personal data, negligible marginal cost, high acquisition value — harm reduction upstream, catching the beginner at the supplement before the protocol. Phase 2.

## Requirements

### Requirement: Validate a product page against evidence
The system SHALL accept a product-page URL and verify its stated claims against `EvidenceClaim` records, returning per-claim support with graded confidence and study counts.

#### Scenario: Overstated claim flagged
- **WHEN** a page claims a benefit the evidence does not support
- **THEN** the validator marks that claim unsupported with the evidence it checked against
- **AND** no personal data is required to run it

### Requirement: No regulatory exposure
The system SHALL present results as informational, anchored to cited literature, without diagnosis or personalised recommendation.

#### Scenario: Informational framing
- **WHEN** results are shown
- **THEN** they cite sources and avoid personalised medical advice
