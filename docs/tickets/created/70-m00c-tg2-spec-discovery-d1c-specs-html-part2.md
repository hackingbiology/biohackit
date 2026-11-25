# [M00c] Spec discovery part D1c: gap register for sections 14–26 of docs/specs/biohackit-specification.html

Labels: autodev, spec
Milestone: M00c
Parent: #34

Goal: extend docs/spec-discovery/specs-html.md with rows for sections 14–26 (Daily Log & Adherence … Agent Access), same format as part D1b.

Spec refs: openspec/changes/m00c-autodev-v2/tasks.md part D; openspec/changes/s01-spec-discovery.

Acceptance:
- every one of the 13 remaining h2 titles appears in at least one row's Source
- `backend/tests/test_spec_discovery_register.py` passes and requires the 13 titles
- each `added` requirement exists once under s01-spec-discovery with a scenario and an Implement line
- gates pass
