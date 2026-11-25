# [review] Residual medium findings on m00c-tg2-spec-discovery-d1a-slides-v2

Labels: autodev

[
 {
  "file": "openspec/changes/s01-spec-discovery/specs/analytics-and-open-data/spec.md",
  "line": 17,
  "severity": "medium",
  "claim": "The spec cites slide page 9 as naming a Creative Commons licence, but the slide says \"Common Criteria\". The same sentence also says the source does not name the licences.",
  "fix": "Quote the slide exactly: \"AGPL-3.0 license free software and all the material are under Common Criteria\". Drop \"Creative Commons\" from the citation. Record the ambiguity in Q16 or a new question in docs/QUESTIONS.md.",
  "confirmed": true,
  "reason": "I read spec.md:17 and slides.md:46. The spec citation asserts Creative Commons, while the register's own Notes cell says the slide text reads \"Common Criteria\". My `pdftotext` check of page 9 was blocked, so I did not read the slide text myself. The Q16 text was not checked because that command was blocked. The self-contradiction inside the citation is visible in the line itself. The second reviewer's finding on this same line is a duplicate of this one."
 },
 {
  "file": "docs/spec-discovery/slides.md",
  "line": 46,
  "severity": "medium",
  "claim": "The Feature cell states \"material under a Creative Commons licence\" as the slide's claim, but per the register's own Notes the slide says \"Common Criteria\".",
  "fix": "Change the Feature cell to: material under \"Common Criteria\" (licence unclear). Point the Notes cell to the question about it in QUESTIONS.md.",
  "confirmed": true,
  "reason": "I read slides.md:46. The Feature cell says Creative Commons and the Notes cell in the same row admits the slide says Common Criteria. The register is meant to record the slide's own claims, so this is an unrecorded interpretation. I did not read the slide text myself."
 }
]
