# [X01] Ecosystem scan for M03 (interventions catalog + protocols)

Labels: autodev, spec
Milestone: X01
Parent: unknown

Goal: write docs/ecosystem/m03-interventions-protocols.md before the M03 OpenSpec change, with every licence, activity date and API fact fetched on the day.

Spec refs: openspec/changes/x01-ecosystem-reuse (scenarios `scan-entries-are-verified`, `proposed-upstream-contribution`); capabilities `interventions-and-catalog`, `protocols`.

Acceptance:
- The scan covers identifier codes, multilingual resolution, FHIR/OMOP models, Evipedia MCP, task queues, versioning libraries and get-based components.
- `backend/tests/test_ecosystem_docs.py` and `test_ecosystem_page_data.py` pass; `export_page_data.py --check` exits 0.
- Q105-Q107 recorded with defaults. No code, dependency or migration.
