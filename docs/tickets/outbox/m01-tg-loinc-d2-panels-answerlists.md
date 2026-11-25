# [M01] TG-LOINC part D2: import Panels & Forms and AnswerList files

Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

Note: PanelsAndForms.csv is not imported until its header is verified (Q54).

Goal: `import_loinc` also imports the optional AnswerList and LoincAnswerListLink files into LoincAnswerList, LoincAnswer and LoincAnswerListLink, linked to the release Source and alignable with OMOP CONCEPT / CONCEPT_RELATIONSHIP.

Spec refs: openspec/changes/m01-terminology-reference-data, requirement "LOINC panels and answer lists are imported".

Acceptance: 3 new scenarios plus the extended "Optional LOINC accessory files absent" covered by backend/tests/test_import_loinc_panels_answers.py; idempotent re-run; unknown code or list rolls back naming file and line; no new dependency; search and API unchanged.
