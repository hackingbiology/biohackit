# [M00c] Docs site part A: canonical AI surfaces map at /docs/ai-surfaces

Labels: autodev, feature
Milestone: M00c
Parent: 

Goal: publish "what is AI, what is NOT AI" from docs/ai-surfaces.md as the Next route /docs/ai-surfaces, generated into frontend/src/content/ai-surfaces.json by tools/docs/export_ai_surfaces.py (pattern of /ecosystem).

Spec refs: openspec/specs/ai-uses-and-attribution (Published AI surfaces map; scenario "The numbers are not AI"); openspec/changes/m00c-autodev-v2 tasks (docs site A).

Acceptance: exactly 3 AI surfaces; every row cites an existing spec requirement or file; sync test, backend and jest tests pass; frontend/package.json and pnpm-lock.yaml unchanged.
