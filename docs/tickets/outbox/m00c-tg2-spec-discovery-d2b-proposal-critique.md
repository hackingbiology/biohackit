# [M00c] Spec discovery part D2b: gap registers for docs/proposal-critique.html, docs/reference/hb-protocol-structure.xlsx and docs/foundation.html

Labels: autodev, spec
Milestone: M00c
Parent: #34

Goal: add registers under docs/spec-discovery/ for the three remaining sources, same table format as docs/spec-discovery/competitive-landscape.md. Create each register file first, then fill it section by section. Every feature claim gets one status (covered / added / out-of-scope with a reason).

Spec refs: openspec/changes/m00c-autodev-v2/tasks.md part D (D2b); openspec/changes/s01-spec-discovery.

Acceptance:
- each register has at least one row per section of its source
- `backend/tests/test_spec_discovery_register.py` is widened and passes
- every added row resolves to an ADDED requirement in s01-spec-discovery
- full gates.sh passes
