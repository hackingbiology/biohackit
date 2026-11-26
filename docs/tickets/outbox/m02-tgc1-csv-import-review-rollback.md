# [M02] TG-c part 1: CSV lab import with review and rollback

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: two-step CSV import (preview stores nothing, confirm stores one import LabReport with its LabResults in one transaction) and rollback of an import.
Spec refs: biomarkers-and-labs "Human review before persistence", m02-blood-layer "Lab report import can be rolled back".
Acceptance: backend/tests/test_lab_csv_import.py; Q71; docs/api-labs.md. The retained-file part stays with TG-g.
