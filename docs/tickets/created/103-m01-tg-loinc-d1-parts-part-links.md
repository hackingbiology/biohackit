# [M01] TG-LOINC part D1: import LOINC Part and LoincPartLink_Primary
Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

Goal: `import_loinc` imports the optional Part.csv and LoincPartLink_Primary.csv into `LoincPart` / `LoincPartLink` (OMOP CONCEPT / CONCEPT_RELATIONSHIP-alignable), same transaction and release Source.

Spec: openspec/changes/m01-terminology-reference-data, requirement "LOINC parts and part links are imported".

Acceptance: 3 new scenarios tested; a link to an unknown part or LOINC code aborts with file and row; no new dependency; search and API unchanged.
