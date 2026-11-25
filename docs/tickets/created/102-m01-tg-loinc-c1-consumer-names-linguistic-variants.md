# [M01] TG-LOINC part C1: ConsumerName and it-IT/zh-CN LinguisticVariants import
Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

## Goal
`import_loinc` also imports the optional ConsumerName file and the it-IT and zh-CN LinguisticVariants files into `LoincConsumerName` and `LoincLinguisticVariant`, linked to the release `Source`. Search is unchanged (part C2).

## Spec refs
openspec/changes/m01-terminology-reference-data: requirement "LOINC consumer names and linguistic variants are imported" (4 scenarios). Column names and paths: docs/ecosystem/m01-terminology.md (part C1), question Q52.

## Acceptance
- Column names and paths cited from fetched sources; no new dependency; no LOINC content in git.
- Idempotent import; absent optional files named in the output (exit 0); unknown LOINC code rolls back the whole import naming file and line.
- Tests tagged with the 4 scenario ids; gates pass.
