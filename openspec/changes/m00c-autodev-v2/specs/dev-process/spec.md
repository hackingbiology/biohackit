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

### Requirement: Reproducible backend dependencies
Every runtime dependency declared in backend/pyproject.toml SHALL have a matching package entry in backend/uv.lock.

#### Scenario: Lockfile in sync
- **WHEN** a dependency is declared in pyproject.toml
- **THEN** uv.lock contains a `[[package]]` with that normalized name, and the `biohackit` package's dependencies list references it

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

### Requirement: Public staging environment
The process SHALL provide a public, password-less staging stack on port 18800 that runs production servers, is not indexed by search engines, holds only demo data and publishes a single port.

#### Scenario: Staging runs production servers
- **WHEN** docker-compose.staging.yml is started
- **THEN** the backend runs gunicorn with DEBUG false and a required SECRET_KEY, and the frontend runs the production Next server with `/api` and `/_allauth` rewritten to the backend

#### Scenario: Staging not indexed
- **WHEN** any page or API response is requested from staging
- **THEN** it carries the header `X-Robots-Tag: noindex`

#### Scenario: Staging holds only demo data
- **WHEN** the staging seed runs, once or repeatedly
- **THEN** it creates at most one demo account from DEMO_USERNAME and DEMO_PASSWORD and no measurements, ranges, doses or other health values

#### Scenario: Staging single port
- **WHEN** the staging stack is up
- **THEN** only port 18800 is published on the host and neither the database nor the backend publishes a port

### Requirement: Changed backend code is tested
The gates SHALL fail when any backend Python source file changed on the branch (excluding tests/, migrations/ and manage.py) has line coverage below 90% under the backend test suite.

#### Scenario: Under-tested change rejected
- **WHEN** a changed backend source file has less than 90% line coverage or is absent from the coverage report
- **THEN** the coverage gate fails and names the file and its percentage

#### Scenario: Excluded and unchanged files ignored
- **WHEN** the only changed backend files are tests, migrations, manage.py or non-Python files
- **THEN** the coverage gate passes without running coverage

#### Scenario: Deleted file not required
- **WHEN** a backend source file is deleted on the branch
- **THEN** it is not checked

### Requirement: Specification discovery is traceable
Every feature promised by a project document SHALL be recorded in a register under `docs/spec-discovery/` that maps it to a requirement, and every feature without a requirement SHALL be added to an open OpenSpec change.

#### Scenario: Register rows resolve
- **WHEN** a register row has status covered or added
- **THEN** the source file exists, a covered row's `<capability>/<Requirement title>` exists in `openspec/specs/**`, and an added row's requirement exists in an open change's specs

#### Scenario: Unspecified feature captured
- **WHEN** a register row has status added
- **THEN** its requirement is in an open change and not yet in `openspec/specs/**`

### Requirement: Frontend framework has no fixable high or critical advisory
The frontend SHALL pin a `next` version that satisfies the patched range of every high or critical advisory recorded for it in `docs/security/frontend-advisories.md`.

#### Scenario: Patched framework pinned
- **WHEN** the frontend lockfile is read
- **THEN** the resolved `next` version satisfies the patched range of every advisory listed in docs/security/frontend-advisories.md, and package.json and the lockfile agree
