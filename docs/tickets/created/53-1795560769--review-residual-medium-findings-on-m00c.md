# [review] Residual medium findings on m00c-tg2-spec-discovery-b-project-spec

Labels: autodev

[
 {
  "file": "openspec/changes/s01-spec-discovery/specs/analytics-and-open-data/spec.md",
  "line": 39,
  "severity": "medium",
  "claim": "The linked-data scenario requires a link to every referenced entity, including withheld ones, which contradicts per-item withholding",
  "fix": "Reword the THEN line to 'a link to every public entity it references, and no identifier or link for a withheld entity'. Add an AND line saying the dataset contains no reference to withheld items.",
  "confirmed": true,
  "reason": "Line 39 reads 'a link to every entity it references' and has no public-only qualifier. A public entity can reference a withheld one. Read literally, that forces a link or identifier for the withheld item. That contradicts openspec/specs/analytics-and-open-data/spec.md, which says only withheld per-item data is excluded, and the community-and-social 'absent from anything an indexer can read' scenario. The wording is a real, easily fixed ambiguity."
 }
]
