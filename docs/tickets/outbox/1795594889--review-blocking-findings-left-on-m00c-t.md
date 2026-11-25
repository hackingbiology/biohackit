# [review] Blocking findings left on m00c-tg2-spec-discovery-d1-specs-slides-v2

Labels: autodev

[
 {
  "file": "docs/spec-discovery/slides.md",
  "line": 1,
  "severity": "critical",
  "claim": "Nothing for the task was implemented: slides.md and specs.md do not exist, and there are no spec requirements, tests, questions or STATE update.",
  "fix": "Run pdftotext -layout on both PDFs and an html.parser extraction on both HTML files. Write slides.md and specs.md with intros that name the commands and the pdfinfo page counts. Add the ADDED requirements, the tasks.md lines, the QUESTIONS.md entries, the tests and the STATE.md update.",
  "confirmed": true,
  "reason": "`ls docs/spec-discovery/` lists only getbased-reuse.md, presentation.md, project-spec.md and whitepaper.md. `git diff main --name-status` shows only a renamed ticket file."
 },
 {
  "file": "docs/spec-discovery/slides.md",
  "line": 1,
  "severity": "critical",
  "claim": "The branch has no implementation: slides.md and specs.md are missing.",
  "fix": "Same as the first finding. This is a duplicate of it.",
  "confirmed": true,
  "reason": "The directory listing and the diff against main confirm that neither register exists. This duplicates the first finding but is accurate."
 },
 {
  "file": "backend/tests/test_spec_discovery_register.py",
  "line": 1,
  "severity": "high",
  "claim": "No test parses or resolves the new registers, and no test checks that the intro names the extraction tool.",
  "fix": "Add tests that cover slides.md and specs.md and carry the dev-process scenario comments. They should check that the intro contains pdftotext and does not claim the slides were read visually.",
  "confirmed": true,
  "reason": "The diff against main touches no test file, so no D1 tests exist."
 },
 {
  "file": "openspec/changes/s01-spec-discovery/tasks.md",
  "line": 1,
  "severity": "high",
  "claim": "The branch adds no ADDED requirements or tasks.md lines for unspecified features in docs/specs/ or docs/slides/.",
  "fix": "Add an ADDED requirement with a SHALL scenario for each `added` row, plus a matching tasks.md line.",
  "confirmed": true,
  "reason": "The diff against main touches no file under openspec/."
 }
]
