# [X01] get-based archive importer, part 1: format document and import spec

Labels: autodev, spec
Milestone: X01
Parent: #38

Goal: document the get-based export, backup and planned migration-archive format from its source with citations, and write the OpenSpec requirement "Import of a get-based archive" with get-based's per-value provenance (`importedWith`, `markerSources` with `reported`, `manuallyEdited`, `derivedFrom`) kept. Docs and spec only: no code, no dependency, no migration.

Spec refs: biomarkers-and-labs "Import of a get-based archive" (change x01-ecosystem-reuse); Q71, Q75, Q79, Q90, Q91-Q96.

Acceptance:
- `docs/ecosystem/getbased-archive-format.md` cites each field at a pinned commit or marks it unknown.
- The requirement has at least 12 scenarios; the trace matrix lists them as uncovered.
- GIVEBACK row added, marked as needing Fabio's OK and not posted.
- `bash tools/autodev2/gates.sh origin/main` passes.
