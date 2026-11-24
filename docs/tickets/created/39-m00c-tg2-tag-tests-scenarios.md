# [M00c] Tag every existing test with its scenario ids; matrix shows true coverage

Labels: autodev, test
Milestone: M00 Foundations
Parent: #34

Goal: tests declare `scenario: <capability>::<slug>`; delta specs use the standard layout so the matrix counts them.
Spec refs: openspec/changes/m00c-autodev-v2 (TG2).
Acceptance: `matrix.py --strict` exits 0, covered > 0, test diffs comment-only.
