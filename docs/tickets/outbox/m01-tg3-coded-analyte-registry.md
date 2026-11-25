# [M01] TG3 coded analyte registry

Labels: autodev, feature
Milestone: M01 — Terminology & Reference Data
Parent: #4

Goal: Biomarker requires a unique LOINC code, a UCUM Unit FK and a Source FK. Measurement unit is checked against the analyte unit with stored conversions only.

Spec refs: terminology-reference-data::missing-code, biomarkers-and-labs::coding-is-mandatory-for-a-measurement, domain-model::method-and-lab-are-mandatory-metadata.

Acceptance: a test per scenario; migration core/0003 fails loudly on uncoded legacy rows; gates pass.
