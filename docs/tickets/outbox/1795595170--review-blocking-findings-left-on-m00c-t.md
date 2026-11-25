# [review] Blocking findings left on m00c-tg2-spec-discovery-d1a-slides

Labels: autodev

[
 {
  "file": "docs/spec-discovery/slides.md",
  "line": 1,
  "severity": "critical",
  "claim": "The required gap register docs/spec-discovery/slides.md was never created.",
  "fix": "Run pdftotext -layout on the slides PDF into a temp directory, then write slides.md in the presentation.md format with one row per page or claim.",
  "confirmed": true,
  "reason": "`ls docs/spec-discovery/` lists only getbased-reuse.md, presentation.md, project-spec.md and whitepaper.md. `git diff main --stat` shows one change, a ticket-file rename with 0 insertions."
 },
 {
  "file": "backend/tests/test_spec_discovery_register.py",
  "line": 1,
  "severity": "high",
  "claim": "test_part_d1a_slides_register_exists_and_resolves is missing.",
  "fix": "Add the test, modelled on test_part_c_registers_exist_and_resolve, with the Source-prefix check and check_rows(...) == []. Tag it `# scenario: dev-process::register-rows-resolve`.",
  "confirmed": true,
  "reason": "grep for 'D1a' in backend/tests/test_spec_discovery_register.py returns nothing, and the file is not in the diff."
 },
 {
  "file": "openspec/changes/s01-spec-discovery/tasks.md",
  "line": 1,
  "severity": "high",
  "claim": "None of the spec and bookkeeping updates were made: no ADDED requirements, no D1a line, no D1a/D1b split, no STATE.md line, no questions from Q33.",
  "fix": "Do every task item: ADDED requirements with scenarios, the tasks.md line, the D1a/D1b split, the STATE.md line, and questions from Q33 each with a default.",
  "confirmed": true,
  "reason": "The diff against main touches no files except the ticket rename. grep for 'D1a' in openspec/changes/*/tasks.md returns nothing."
 }
]
