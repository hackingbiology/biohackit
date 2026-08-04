# Domain Model (cross-cutting)

## Purpose

Defines the entities every other capability builds on, and the one relation that carries the whole system. This capability owns no screens; it constrains all the others. Derived from `docs/hackingbiology-project-spec.md` §5, extended with the protocol-lifecycle clarifications of 2026-08-04.

The load-bearing relation:

```
Substance → SafetyRule → Biomarker → Measurement → Dashboard
```

"What you take" and "how you are" are the same structure read from two sides.

## Requirements

### Requirement: Separation of the three protocol facets
The system SHALL model what-I-measure, what-I-take, and what-I-want as three distinct, independently versioned entities — `TestingProtocol`, `TreatmentPlan`, and `Goal` — rather than a single fused "protocol" record.

#### Scenario: A treatment changes without disturbing the measurement plan
- **WHEN** a user edits a dose inside their `TreatmentPlan`
- **THEN** the change creates a new `TreatmentPlan` version
- **AND** the associated `TestingProtocol` and `Goal` are untouched and keep their own version history

#### Scenario: Goals map to hallmarks
- **WHEN** a user declares a `Goal`
- **THEN** the system SHALL let them map it onto one or more Hallmarks of Aging (Schmauck-Medina 2022 framework)
- **AND** the user's top three goals are flagged as weighted for later analysis

### Requirement: Protocol as public composite
The system SHALL expose `Protocol` as a read-facing composite of a `TestingProtocol` + `TreatmentPlan` + `Goal`, carrying an origin of `curated` or `community`, that is the unit which is published, followed, forked, and copied.

#### Scenario: Publishing composes the facets
- **WHEN** a user publishes a `Protocol`
- **THEN** the composite references specific versions of its three facets
- **AND** it records origin, author, license posture, and any forked-from lineage

### Requirement: Intervention carries a cycle schema
The system SHALL represent every `Intervention` with an explicit cycle schema — `pattern` (continuous | pulsed | titration | on-off), `on_days`/`off_days`, cycle length, cycles per year, titration steps — not merely a frequency.

#### Scenario: Pulsed senolytic is representable
- **WHEN** a user records "dasatinib 100 mg, days 1–3 of each month"
- **THEN** the intervention stores pattern=pulsed with on_days=[1,2,3] over a monthly cycle
- **AND** the pattern is never flattened to "Monthly" with the cycle relegated to free text

### Requirement: Intervention subtypes
The system SHALL support intervention subtypes with their own fields: Substance, Exercise, Device/Therapy, Procedure, Hormonal, and Nutrition/Fasting.

#### Scenario: A procedure differs from a pill
- **WHEN** the intervention is a Procedure (e.g. IV infusion, plasmapheresis)
- **THEN** it carries operator, site, consent and a distinct risk profile
- **AND** the system does not treat it as interchangeable with an oral Substance

### Requirement: Biomarker with role and three ranges
The system SHALL model `Biomarker` with a role (`efficacy` | `safety` | `baseline`), a collection modality, and three distinct ranges per analyte — laboratory reference, longevity-optimal, and safety threshold.

#### Scenario: The three ranges stay distinct
- **WHEN** a biomarker value is displayed
- **THEN** the reference range, the optimal range, and the safety threshold are shown as three different things
- **AND** they are never collapsed into a single band

### Requirement: Measurement provenance
The system SHALL store each `Measurement` with date, source, laboratory, method/assay, unit (UCUM), and validation state.

#### Scenario: Method and lab are mandatory metadata
- **WHEN** a measurement is persisted
- **THEN** it retains its method/assay and originating laboratory
- **AND** a measurement missing these is flagged as not aggregation-eligible

### Requirement: Safety, adherence and wellness as first-class entities
The system SHALL model `SafetyRule`, `AdherenceLog` (four states: taken-as-planned | partial | intentionally-skipped | forgotten), and `WellnessCheck`, and treat them as core, not optional.

#### Scenario: Adherence qualifies an N-of-1 result
- **WHEN** a cohort result is computed
- **THEN** each contribution carries its adherence percentage
- **AND** a low-adherence contribution can be down-weighted or excluded (see `analytics-and-open-data`)

### Requirement: Cohort and Study
The system SHALL model `Cohort` (the set of people practising the same protocol) and `Study` (a self-experiment container with pre-declared endpoints and timepoints).

#### Scenario: Cohort forms around a protocol
- **WHEN** two or more people practise the same published `Protocol`
- **THEN** they belong to its `Cohort`
- **AND** the cohort is the unit of comparison and analytics
