# Give-back register

Contributions we propose to make to the projects we build on. **Nothing is posted to any external repo, forum or person without Fabio's approval.** Agents only add rows here; `status` moves `proposed` → `approved` (Fabio) → `done`.

Only concrete items found during a scan are listed.

| date | upstream project | proposed contribution | status | link |
|---|---|---|---|---|
| 2026-11-24 | OHDSI/CommonDataModel | Propose adding a `LICENSE` file to the repository root: GitHub detects no licence and only the R package `DESCRIPTION` states Apache License 2.0 | proposed | https://github.com/OHDSI/CommonDataModel |
| 2026-11-24 | OHDSI/Athena | Propose a short licence statement for the application repository (no licence detected, no LICENSE file in the root) | proposed | https://github.com/OHDSI/Athena |
| 2026-11-24 | ucum-org/ucum | Ask for machine-readable licence metadata for the custom UCUM licence, so downstream tools can classify it (GitHub reports `NOASSERTION`) | proposed | https://github.com/ucum-org/ucum |
| 2026-11-24 | dalito/ucumvert | Once adopted: share our list of analyte UCUM units as extra test cases and report any validation issue found | proposed | https://github.com/dalito/ucumvert |
| 2026-11-24 | nazrulworld/fhir.resources | Propose declaring an SPDX licence expression in package metadata: GitHub reports `NOASSERTION` and PyPI says only "BSD license" | proposed | https://github.com/nazrulworld/fhir.resources |
| 2026-11-24 | forever-healthy/evipedia-mcp | Ask for a stated licence for the evipedia.ai review content (the MCP server is MIT; the content licence was not found), so downstream apps know how reviews may be stored and quoted | proposed | https://github.com/forever-healthy/evipedia-mcp |
| 2026-11-26 | bio-learn/biolearn | Propose declaring an SPDX licence expression in package metadata: GitHub reports `NOASSERTION` and PyPI says only "new BSD" | proposed | https://github.com/bio-learn/biolearn |
| 2026-11-26 | 199-mcp/mcp-phenoage-clock | Report that the accepted units (g/dL, mg/dL, mg/dL, CRP mg/L) do not match the units of the Levine 2018 coefficients (g/L, umol/L, mmol/L, CRP mg/dL), with the supplement Table S1 page as reference (docs/research/phenoage-coefficients.md D5) | proposed | https://github.com/199-mcp/mcp-phenoage-clock |
| 2026-11-26 | elkimek/get-based | Share the Bortz comparison: the variant omits 4 of the 25 biomarkers of the authors' coefficient file, rounds coefficients, caps inputs without a cited source and names the journal Nature Communications instead of Communications Biology (docs/research/phenoage-coefficients.md E1-E4) | proposed | https://github.com/elkimek/get-based |
| 2026-11-26 | lucascamillomd/pyaging | Ask the maintainers to re-check the 0.090165 vs 0.09165 divisor and the "leading 1" statement against the original supplement and the 2019 correction (docs/research/phenoage-coefficients.md D3, D8) | proposed | https://github.com/lucascamillomd/pyaging |
