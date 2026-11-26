# [M02] TG-g part 1: retain the original CSV privately and delete it on rollback
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: keep the uploaded CSV of a confirmed import as a private file with its SHA-256; delete it on rollback; never serve it.
Spec refs: m02-blood-layer TG-g; scenario biomarkers-and-labs::rollback-removes-the-retained-original; Q57, Q65, Q76.
Acceptance: tests in backend/tests/test_lab_original_retention.py; one migration; no new dependency.
