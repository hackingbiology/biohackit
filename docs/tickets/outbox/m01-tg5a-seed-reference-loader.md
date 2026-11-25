# [M01] TG5 part A: seed_reference loader

Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

Goal: idempotent `manage.py seed_reference` for sourced JSON seed files; unsourced row aborts its file. No data rows (UCUM in part B).

Spec refs: terminology-reference-data::unsourced-seed-row, terminology-reference-data::seed-contents.

Acceptance: backend/tests/test_seed_reference.py passes; trace matrix covers both scenarios; no new dependency.
