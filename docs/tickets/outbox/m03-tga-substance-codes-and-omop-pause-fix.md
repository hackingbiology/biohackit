# [M03] TG-a: Substance model with cited code strings

Labels: autodev, feature
Milestone: M03 Interventions catalog and protocols
Parent: unknown

Goal: a `Substance` model whose RxCUI, PubChem CID, UNII and ATC identifiers are stored only as code strings, each with source and fetch date (Q105, Q106 defaults). No row seeded, no bulk file. Also fixes the review finding at backend/protocols/omop.py:51 (a pause ends the run used for the DRUG_EXPOSURE start date).

Spec refs: M03 "Substance codes are stored as cited code strings"; main-IC "Substance catalog metadata"; protocols "an exported intervention has no invented concept id".

Acceptance: a code with no source is refused; staff-only writes at /api/substances/; no migration inserts rows; no bulk file under backend/; docs/api-substances.md; gates pass.
