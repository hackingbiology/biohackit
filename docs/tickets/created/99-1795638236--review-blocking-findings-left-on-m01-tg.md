# [review] Blocking findings left on m01-tg5b1-ucumvert-validation

Labels: autodev

[
 {
  "file": "backend/pyproject.toml",
  "line": 1,
  "severity": "critical",
  "claim": "The branch has none of the task's work. ucumvert is not a dependency, and there is no validation code, tests or spec changes.",
  "fix": "Fetch the licences from PyPI, run `uv add ucumvert==<verified version>` in backend/, and commit pyproject.toml and uv.lock. Then do Steps 1-6.",
  "confirmed": true,
  "reason": "`git diff main --name-status` shows only a ticket-file rename (R100). `git log main..HEAD` shows only the ticket commit 19e4934. backend/terminology/ucum.py does not exist. grep for ucumvert in backend/pyproject.toml returns 0 matches."
 },
 {
  "file": "backend/pyproject.toml",
  "line": 9,
  "severity": "critical",
  "claim": "Step 0 was never done: ucumvert is not in pyproject.toml or uv.lock.",
  "fix": "Run `uv add ucumvert==<verified version>` in backend/ and commit pyproject.toml and uv.lock together. Then run test_lockfile_sync and the licence gate.",
  "confirmed": true,
  "reason": "Same evidence as the first finding. The only diff from main is the ticket rename, and ucumvert appears nowhere in pyproject.toml. This is a duplicate of the first finding, but the defect is real."
 },
 {
  "file": "backend/terminology/services.py",
  "line": 23,
  "severity": "critical",
  "claim": "UCUM validation is not wired in. terminology/ucum.py does not exist, and `_unit` only looks up the stored unit.",
  "fix": "Add terminology/ucum.py with is_valid_ucum on top of ucumvert. Call it from Unit.clean(), services._unit and seed_loader, and flag bad rows in inspect_seed_dir.",
  "confirmed": true,
  "reason": "ucum.py is missing (ls fails). The branch has no code changes relative to main, so the validation cannot be present. I did not open services.py itself; this rests on the diff showing no change to it."
 },
 {
  "file": "openspec/changes/m01-terminology-reference-data/tasks.md",
  "line": 27,
  "severity": "high",
  "claim": "The spec scenario, tests, docs and STATE updates are missing.",
  "fix": "Add the 'Invalid UCUM syntax' scenario and tests tagged with its scenario id. Record the licences with today's date, annotate tasks.md:27 as part B1 only, and update STATE.md.",
  "confirmed": true,
  "reason": "`git diff main` shows no changes to openspec, tests, docs/ecosystem or docs/STATE.md. Only the ticket rename differs."
 }
]
