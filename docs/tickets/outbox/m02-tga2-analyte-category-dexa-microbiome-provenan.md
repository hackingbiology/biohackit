# [M02] TG-a part 2: analyte category and DEXA/microbiome provenance rule

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: `core.Biomarker.category` (blood | body_composition | microbiome) with a cited `category_source` (Q66, NULL = blood), and `LabResult.save` refuses a DEXA or microbiome result without laboratory or method.

Spec refs: biomarkers-and-labs "A DEXA or microbiome result without provenance is not stored", "Result without provenance", "DEXA result recorded".

Acceptance: migration 0008; no category assigned to any real analyte; tests in backend/tests/test_lab_result_category.py; part 3 (OMOP mapping) stays open.
