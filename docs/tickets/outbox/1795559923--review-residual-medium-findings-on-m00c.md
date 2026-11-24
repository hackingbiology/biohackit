# [review] Residual medium findings on m00c-tg2-spec-discovery-a-whitepaper

Labels: autodev

[
 {
  "file": "openspec/changes/m00c-autodev-v2/specs/dev-process/spec.md",
  "line": 88,
  "severity": "medium",
  "claim": "The 'Register rows resolve' scenario allows a covered row to resolve in an open change. The test rejects that case, so the spec and its tagged tests contradict each other.",
  "fix": "Reword the THEN line: the source file exists, a covered row's requirement exists in openspec/specs/**, and an added row's requirement exists in an open change's specs.",
  "confirmed": true,
  "reason": "Spec lines 86-88 say the requirement may be in `openspec/specs/**` or in an open change. The test's covered branch (line 73) errors when the requirement is not in the specs set. test_covered_row_resolving_only_to_open_change_fails (line 132) asserts that failure and is tagged with this scenario."
 },
 {
  "file": "docs/spec-discovery/whitepaper.md",
  "line": 72,
  "severity": "medium",
  "claim": "The whitepaper promises open and linked data in \u00a711. No register row and no requirement captures it.",
  "fix": "Add a register row with status added for the linked-data promise, plus an ADDED requirement in s01-spec-discovery/specs/analytics-and-open-data. Name no serialisation format. Add a QUESTIONS.md entry with a reversible default for the format.",
  "confirmed": true,
  "reason": "whitepaper.src.html:314, 318 and 337 state the linked-data promise. `grep -i linked` finds nothing in docs/spec-discovery/whitepaper.md. `grep -rni 'linked data'` over openspec/specs and openspec/changes also finds nothing."
 }
]
