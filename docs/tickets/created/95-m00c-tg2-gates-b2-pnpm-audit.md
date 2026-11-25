# [M00c] Gates hardening part B2: pnpm audit --prod gate
Labels: autodev, feature
Milestone: M00c
Parent: #34

Goal: pin `postcss` with a pnpm override to a patched version, then add `tools/audit/pnpm_audit_gate.py` (no waiver list) as a gates.sh step.

Spec refs: openspec/changes/m00c-autodev-v2 dev-process "Frontend dependencies have no fixable known vulnerability" (3 scenarios).

Acceptance: `pnpm --dir frontend audit --prod` reports nothing fixable; gate exits 0 on the branch, 1 on a fixable high/critical advisory, 2 when it cannot run; gates.sh diff is append-only.
