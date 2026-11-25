# [M00c] Spec discovery part D1b: docs/specs/, docs/analysis/ and remaining docs/*.md registers

Labels: autodev, spec
Milestone: M00c
Parent: #34

Goal: continue spec discovery after D1a (docs/slides/): create one register per source under docs/spec-discovery/, file first, then fill it.

Spec refs: openspec/changes/m00c-autodev-v2 (part D), dev-process::register-rows-resolve, dev-process::unspecified-feature-captured.

Acceptance:
- each register exists and has a row for every feature claim
- backend/tests/test_spec_discovery_register.py checks it
- `python3 tools/trace/matrix.py --json` reports 0 unknown ids
