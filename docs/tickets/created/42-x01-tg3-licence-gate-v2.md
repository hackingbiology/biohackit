# [X01] Licence gate: fail on AGPL-incompatible or unknown dependency licences
Labels: autodev, feature
Milestone: X01
Parent: #38

Goal: deterministic gate (tools/licence/check_licences.py, step `licences` in gates.sh) over backend pip metadata and `pnpm licenses --prod`.
Spec: openspec/changes/x01-ecosystem-reuse, requirement "Licence-compatible reuse", scenario ecosystem-reuse::incompatible-dependency-rejected.
Acceptance: gate exits 0 on main deps, non-zero and names the package for an incompatible/unknown licence; overrides need a fetched source_url.
