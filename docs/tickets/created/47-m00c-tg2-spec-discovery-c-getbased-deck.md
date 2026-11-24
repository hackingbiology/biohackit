# [M00c] Spec discovery part C: getbased reuse analysis and conference deck

Labels: autodev, spec
Milestone: M00c
Parent: unknown

## Goal
Compare `docs/getbased-reuse-analysis.md` and `docs/presentation/biohackit-deck.pdf` with `openspec/specs`, write the gap registers, add every unspecified feature to `openspec/changes/s01-spec-discovery`, and fix the part B linked-data scenario (public entities only).

## Spec refs
dev-process::register-rows-resolve, dev-process::unspecified-feature-captured

## Acceptance
- `docs/spec-discovery/getbased-reuse.md` and `docs/spec-discovery/presentation.md` pass `backend/tests/test_spec_discovery_register.py`.
- Each added row resolves to a requirement with a scenario and a source citation; new questions Q25–Q30 have defaults.
- Part D (remaining docs) stays tracked in `openspec/changes/m00c-autodev-v2/tasks.md`.
