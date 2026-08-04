# openspec/ — how to read this

This directory is the **functional specification** for biohack.it, written in the OpenSpec convention so it can be reviewed requirement-by-requirement and later drive change proposals.

## Layout

```
openspec/
  project.md                 project context, posture, capability map
  REVIEW-GUIDE.md            start here for a review pass (open questions collated)
  specs/<capability>/spec.md  the capabilities — source of truth
  wireframes/
    navigation.md            information architecture + user journeys (hypotheses)
    wireframes.md            annotated low-fidelity screens (hypotheses)
```

## How a capability reads

```
# <Capability>

## Purpose
Why this exists and where it sits.

## Requirements

### Requirement: <short title>
The system SHALL <a single testable obligation>.

#### Scenario: <case>
- **WHEN** <trigger / precondition>
- **THEN** <observable outcome>
- **AND** <further outcome>
```

Read a requirement as a promise the software makes; read its scenarios as the acceptance tests that prove the promise. A requirement with no scenario is incomplete by convention.

## Markers to look for during review

- `> DECISION:` — a settled choice that reverses or refines spec v0.3; **confirm it**.
- `> OPEN:` — a question deliberately left for us to decide together.

## What is *not* here yet

Non-functional detail (exact schemas, API shapes, infra) and visual design. Wireframes are intentionally low-fidelity hypotheses. Economic figures are out of scope by instruction.
