# [M00c] Gates hardening part A: changed-file backend coverage ≥ 90%
Labels: autodev, feature
Milestone: M00c
Parent: #34

Goal: gates fail when a changed backend source file (excluding tests, migrations, manage.py) has < 90% line coverage. Also fixes the GIVEBACK fhir.resources licence wording.

Spec: openspec/changes/m00c-autodev-v2/specs/dev-process/spec.md (Changed backend code is tested).

Real run on the branch: `backend/.venv/bin/python tools/coverage/changed_coverage.py origin/main` printed `changed-file coverage: no changed backend source files to check` (exit 0).

Acceptance: gates.sh ends ALL GATES PASSED with the changed-file coverage step; backend/tests/test_changed_coverage.py passes; 3 new scenarios covered.

Refs #34
