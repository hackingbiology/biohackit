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

### Requirement: Backend dependencies have no fixable known vulnerability
The gates SHALL fail when pip-audit reports a vulnerability with a fix version in the runtime packages locked in `backend/uv.lock`, and SHALL fail when the audit cannot run.

#### Scenario: Fixable backend vulnerability rejected
- **WHEN** pip-audit reports a vulnerability that has a fix version for a locked runtime package
- **THEN** the gate exits 1 and prints the package, version, advisory id and fix versions

#### Scenario: Backend audit cannot run
- **WHEN** uv or uvx is missing, the lock export fails, pip-audit exits with an error, or its output is not JSON
- **THEN** the gate prints that it cannot run and exits 2

#### Scenario: Unfixed backend advisory reported
- **WHEN** pip-audit reports a vulnerability with no fix version
- **THEN** the gate prints it as unfixed and does not fail on it

### Requirement: Frontend dependencies have no fixable known vulnerability
The gates SHALL fail when `pnpm audit --prod` reports a high or critical advisory with a patched version in the production dependencies of `frontend/`, SHALL accept no ignore or waiver list, and SHALL fail when the audit cannot run.

#### Scenario: Fixable frontend vulnerability rejected
- **WHEN** pnpm audit reports a high or critical advisory that has a patched version for a production dependency
- **THEN** the gate exits 1 and prints the module, version, advisory id and patched range

#### Scenario: Frontend audit cannot run
- **WHEN** pnpm is missing, the audit exits with an error, or its output is not JSON
- **THEN** the gate prints that it cannot run and exits 2

#### Scenario: Unfixed frontend advisory reported
- **WHEN** pnpm audit reports a high or critical advisory with no patched version
- **THEN** the gate prints it as unfixed and does not fail on it

#### Scenario: Frontend audit waiver rejected
- **WHEN** `frontend/package.json` declares a `pnpm.auditConfig` entry such as `ignoreCves` or `ignoreGhsas`
- **THEN** the gate prints that waivers are forbidden and exits 1

### Requirement: OpenSpec documents are structurally valid
The gates SHALL fail when the pinned OpenSpec CLI reports an invalid specification or change under `openspec/`, and SHALL fail when the validator cannot run or its result cannot be read.

#### Scenario: Invalid specification rejected
- **WHEN** the OpenSpec validator reports a specification or change as invalid
- **THEN** the gate exits 1 and prints the id and type of each invalid item with its messages

#### Scenario: Specification validator cannot run
- **WHEN** pnpm is missing, the CLI exits with an error, times out, or prints output that is not the expected JSON, or reports no items
- **THEN** the gate prints that it cannot run and exits 2

#### Scenario: Valid specifications pass
- **WHEN** the validator reports every item as valid
- **THEN** the gate prints the item count and exits 0

### Requirement: Strict type checking on new backend apps
The gates SHALL fail on any mypy error in an app listed in `tools/mypy/strict_apps.txt`, and SHALL fail when the type check cannot run.

#### Scenario: Type error in strict app rejected
- **WHEN** mypy in strict mode reports an error in a listed app
- **THEN** the gate prints each error as file:line:message and exits 1

#### Scenario: Type checker cannot run
- **WHEN** uv is missing, the environment build fails, mypy crashes or times out, its output cannot be parsed, or strict_apps.txt is missing, empty or lists a path that does not exist
- **THEN** the gate prints that it cannot run and exits 2

#### Scenario: Strict apps type-clean
- **WHEN** mypy reports no error for every listed app
- **THEN** the gate prints the checked app list and exits 0

### Requirement: Mutation testing on deterministic numeric code
The gates SHALL fail when mutmut leaves a surviving mutant in a module listed in `tools/mutmut/targets.txt` that is not listed with a reason in `tools/mutmut/accepted_survivors.txt`, and SHALL fail when the mutation run cannot complete.

#### Scenario: Surviving mutant rejected
- **WHEN** mutmut leaves a surviving mutant in a listed module and the mutant is not in the accepted survivors file
- **THEN** the gate prints the module, the mutant id and its diff and exits 1

#### Scenario: Mutation run cannot complete
- **WHEN** uv is missing, the environment build fails, mutmut crashes or times out, its results cannot be read, targets.txt is missing, empty or lists a path that does not exist, or an accepted survivor has no reason
- **THEN** the gate prints that it cannot run and exits 2

#### Scenario: All mutants killed
- **WHEN** every mutant in every listed module is killed or accepted with a reason
- **THEN** the gate prints each target with its killed and total counts and exits 0

### Requirement: Architecture documentation reflects the repository
The architecture page SHALL be generated from `docs/architecture.md`, SHALL cite for every built component a repository path that exists, and SHALL list planned but unbuilt parts separately, each citing an existing OpenSpec requirement.

#### Scenario: Architecture components exist
- **WHEN** a built component in `docs/architecture.md` cites a repository path that does not exist, or a specified-not-built row cites a requirement that is not in openspec
- **THEN** the test fails naming the row

#### Scenario: Architecture page in sync
- **WHEN** `frontend/src/content/architecture.json` differs from the export of `docs/architecture.md`
- **THEN** the test fails and `tools/docs/export_architecture.py --check` exits 1

### Requirement: User guide describes only built features
The user guide page SHALL be generated from `docs/user-guide.md`, SHALL cite for every built step a frontend route file that exists, and SHALL list planned features separately under "Coming later", each citing an existing OpenSpec requirement.

#### Scenario: User guide steps exist
- **WHEN** a built step in `docs/user-guide.md` cites a route file that does not exist, or a "Coming later" row cites a requirement that is not in `openspec/specs/**` or an open change
- **THEN** the test fails naming the row

#### Scenario: User guide page in sync
- **WHEN** `frontend/src/content/user-guide.json` differs from the export of `docs/user-guide.md`
- **THEN** the test fails and `tools/docs/export_user_guide.py --check` exits 1

### Requirement: Changelog reflects merged work
The changelog page SHALL be generated from `docs/CHANGELOG.md`. Every entry SHALL cite a commit that exists in the repository history and an OpenSpec change that exists under `openspec/changes/` (open or archive) or whose capability exists in `openspec/specs/`.

#### Scenario: Changelog entries resolve
- **WHEN** an entry in `docs/CHANGELOG.md` cites a commit that is not in the repository history or an OpenSpec change that does not exist
- **THEN** the test fails naming the entry

#### Scenario: Changelog page in sync
- **WHEN** `frontend/src/content/changelog.json` differs from the export of `docs/CHANGELOG.md`
- **THEN** the test fails and `tools/docs/export_changelog.py --check` exits 1

### Requirement: API reference reflects the backend routes
The API reference page SHALL be generated from `docs/api-*.md`. Every route under `/api/` in the Django URLconf SHALL be documented there with its method(s), and every documented endpoint SHALL resolve to a route.

#### Scenario: API routes documented
- **WHEN** a route under `/api/` has no documented entry, or a documented `METHOD path` does not resolve to a route
- **THEN** the test fails naming the path

#### Scenario: API reference page in sync
- **WHEN** `frontend/src/content/api-reference.json` differs from the export of `docs/api-*.md`
- **THEN** the test fails and `tools/docs/export_api_reference.py --check` exits 1
