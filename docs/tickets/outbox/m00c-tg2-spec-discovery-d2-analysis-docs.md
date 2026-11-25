# [M00c] Spec discovery part D2: gap registers for docs/analysis/ and the remaining docs/*.md

Labels: autodev, spec
Milestone: M00c
Parent: #34

Goal: add registers under docs/spec-discovery/ for docs/analysis/competitive-landscape.html and the docs/*.md files not yet registered (foundation.md, ROADMAP.md, STAGING.md, TRACEABILITY.md, QUESTIONS.md), same table format as part D1c. Create each register file first, then fill it section by section.

Spec refs: openspec/changes/m00c-autodev-v2/tasks.md part D (D2); openspec/changes/s01-spec-discovery.

Acceptance:
- every feature claim has one status (covered / added / out-of-scope with a reason)
- `backend/tests/test_spec_discovery_register.py` passes and requires the new registers
- each `added` requirement exists once under s01-spec-discovery with a scenario and an Implement line
- gates pass
