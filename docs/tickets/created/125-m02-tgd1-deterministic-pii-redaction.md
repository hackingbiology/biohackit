# [M02] TG-d part 1: deterministic, opt-in PII redaction for the CSV lab import
Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: when the user opts in with exact terms, the CSV preview shows a diff of what was removed and where; default off (Q58).

Spec refs: m02-blood-layer TG-d; biomarkers-and-labs::user-opts-to-obfuscate; Q58, Q72.

Acceptance: backend/tests/test_lab_redaction.py passes; no new dependency or migration; docs/api-labs.md section added.
