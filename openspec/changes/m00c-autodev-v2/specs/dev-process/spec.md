## ADDED Requirements

### Requirement: Measurable definition of done
The development process SHALL measure completeness as the share of OpenSpec scenarios covered by at least one passing test that declares the scenario id.

#### Scenario: Matrix generated
- **WHEN** `tools/trace/matrix.py` runs
- **THEN** it lists every scenario of `openspec/specs/**` and of open changes with its covering tests, and reports the covered percentage

#### Scenario: Coverage never regresses
- **WHEN** a task branch would lower the number of covered scenarios
- **THEN** the gates fail and the branch is not merged

### Requirement: Deterministic quality gates
The process SHALL merge to main only when the deterministic gates pass on the rebased branch, and SHALL reject any change that removes or weakens a gate.

#### Scenario: Weakened gate rejected
- **WHEN** a branch deletes a line of `tools/autodev2/gates.sh` or modifies the orchestrator
- **THEN** the merge is refused and a ticket is opened

### Requirement: Adversarial, verified review
Every task SHALL be reviewed by independent read-only reviewer agents, and only findings confirmed by a verifier citing file:line SHALL be acted upon; unresolved confirmed findings SHALL become tickets.

#### Scenario: Unsupported finding dropped
- **WHEN** a reviewer reports a finding whose cited code does not exhibit the problem
- **THEN** the verifier rejects it and no change is made

### Requirement: Budget ceiling
The process SHALL keep its attributed share of the weekly plan limit at or below 40%, paced over the week, and SHALL pause when account-wide utilization reaches 90%.

#### Scenario: Over pace
- **WHEN** the attributed share exceeds the allowed share for the elapsed time
- **THEN** the orchestrator sleeps and resumes when allowed

### Requirement: Daily feedback without blocking
The process SHALL publish one daily digest and SHALL never block on a question, taking a recorded reversible default instead.

#### Scenario: Digest published
- **WHEN** it is 08:15 Europe/Rome and no digest exists for today
- **THEN** a digest with matrix %, merges, failures, defaults taken, questions and budget is committed and filed as a `digest` issue
