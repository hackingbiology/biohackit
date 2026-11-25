# [M00c] Docs site part E: changelog
Labels: autodev, feature
Milestone: M00c
Parent: #34

Goal: publish docs/CHANGELOG.md at /docs/changelog, with a sync test and a test that every cited commit and OpenSpec change exists.

Spec: openspec/changes/m00c-autodev-v2/specs/dev-process/spec.md, "Changelog reflects merged work".

Acceptance: tools/docs/export_changelog.py --check exits 0; scenarios dev-process::changelog-entries-resolve and dev-process::changelog-page-in-sync covered; gates pass.
