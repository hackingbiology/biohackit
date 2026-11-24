# [M00c] Spec discovery part A: whitepaper and foundation register
Labels: autodev, spec
Milestone: M00c
Parent: #34

Goal: every feature promised by whitepaper/whitepaper.src.html and docs/foundation.md is mapped to a requirement (register docs/spec-discovery/whitepaper.md); the eight unspecified ones become ADDED requirements in the open change s01-spec-discovery. A test keeps the register and the specs consistent.

Spec: openspec/changes/m00c-autodev-v2/specs/dev-process/spec.md (Specification discovery is traceable); openspec/changes/s01-spec-discovery/.

Acceptance: backend/tests/test_spec_discovery_register.py passes; matrix --strict exits 0 and shows dev-process::register-rows-resolve and dev-process::unspecified-feature-captured covered; part B (hackingbiology project spec, getbased reuse analysis, presentation) remains.

Refs #34
