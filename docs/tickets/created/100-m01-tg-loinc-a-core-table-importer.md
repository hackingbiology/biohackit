# [M01] TG-LOINC part A: LoincTerm model and import_loinc for the core table

Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

Goal: `terminology.LoincTerm` and the idempotent `manage.py import_loinc <dir> --release-version <v>` for Loinc.csv only, recording the release as a `Source`; clean exit with instructions when `data/vendor/loinc/` is absent. Parts B-D (ConsumerName, variants, Panels, AnswerList, Parts, search) are deferred.
Spec: openspec/changes/m01-terminology-reference-data (Full LOINC release is imported from user-supplied files).
Acceptance: a test per scenario, synthetic fixture only, no LOINC content in git, gates.sh passes.
