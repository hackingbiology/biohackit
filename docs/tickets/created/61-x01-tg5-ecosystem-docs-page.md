# [X01] Public Ecosystem page (/ecosystem)
Labels: autodev, feature
Milestone: X01
Parent: #38

Goal: publish what biohack.it builds on and what it gives back, generated from docs/ecosystem/.

Spec: openspec/changes/x01-ecosystem-reuse, requirement "Ecosystem page is published".

Acceptance:
- `python3 tools/ecosystem/export_page_data.py --check` exits 0.
- Page /ecosystem is public, accessible, lists every scan entry and give-back row.
- Tests tag the three page scenarios; gates pass.
