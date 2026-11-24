# Ecosystem scan: integration anchors

Scan of the software the slides and the x01 proposal name as integration anchors (`openspec/changes/x01-ecosystem-reuse/proposal.md`). Later modules (M02+: FHIR/OMOP export, AI4L reviews, Evipedia lookups, Discourse login) depend on these decisions. Method and entry format: [README.md](README.md). Every fact below was fetched on 2026-11-24; nothing is from memory. Nothing here has been wired into code yet: "Decision" states the intended use, and each module scan re-checks it before the dependency is added (including the dependency licences, which the licence gate also checks).

## get-based

### get-based
- **URL:** https://github.com/elkimek/get-based
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-22
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/elkimek/get-based, 2026-11-24
- **Licence note:** Same facts as the get-based entry in [m00-foundations.md](m00-foundations.md); not repeated here. Component-level reuse (biomarker schema, import pipeline) is analysed in `docs/getbased-reuse-analysis.md`. The licence is the same as ours, so later modules may port code with attribution; that is decided per module.

## Forever Healthy: AI4L and Evipedia

### AI4L
- **URL:** https://github.com/forever-healthy/AI4L
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-08
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/forever-healthy/AI4L and raw.githubusercontent.com/forever-healthy/AI4L/main/README.md, 2026-11-24
- **Licence note:** README describes it as "Enabling anyone to use AI to generate high-quality, evidence-based reviews of health & longevity interventions" (v2.0.5 badge). Its method is read for the AI4L surface design; no code is imported. Any AI text we produce stays labelled and listed in the AI surfaces map.

### evipedia-mcp
- **URL:** https://github.com/forever-healthy/evipedia-mcp
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-09-09
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/forever-healthy/evipedia-mcp and raw.githubusercontent.com/forever-healthy/evipedia-mcp/main/README.md, 2026-11-24
- **Licence note:** A Model Context Protocol server for evipedia.ai, published to npm as `evipedia-mcp` (per its README) and run over stdio. We would talk to it as a separate process. The README lists the tools `search_reviews`, `list_reviews`, `list_updates`, `get_conclusion`, `get_review`, `get_metadata` (includes PubMed PMIDs of citations), `suggest_review` and `get_version`. `suggest_review` submits to a public form, so it is outward-facing and must not be called by agents without Fabio's approval. The licence of the evipedia.ai review content itself was not fetched: unknown, see Q15 in docs/QUESTIONS.md (stored values need provenance).
- **Provisional:** yes, the MCP server code is MIT but the evipedia.ai content licence is unknown (Q15); until answered we store only the review URL/ID and PMIDs, never review text.

## FHIR Python libraries

### fhir.resources
- **URL:** https://github.com/nazrulworld/fhir.resources
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-09-14
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/nazrulworld/fhir.resources (licence `NOASSERTION`), raw.githubusercontent.com/nazrulworld/fhir.resources/main/LICENSE and pypi.org/pypi/fhir.resources/json (version 8.3.0 uploaded 2026-07-03, classifier "BSD License"), 2026-11-24
- **Licence note:** same verdict as docs/ecosystem/m01-terminology.md: the file is a BSD licence, but the number of clauses was not determined, so no SPDX id is claimed. Pydantic FHIR models. Re-check its dependency licences if it is ever adopted.
- **Provisional:** yes, fhir.resources is not used until Fabio answers Q9; the default is that it is not a dependency.

### fhirpy
- **URL:** https://github.com/beda-software/fhir-py
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-21
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/beda-software/fhir-py and pypi.org/pypi/fhirpy/json, 2026-11-24
- **Licence note:** PyPI release 2.3.3 (uploaded 2026-11-21) carries no licence metadata; the licence comes from GitHub. A client for talking to FHIR servers; biohack.it does not call a FHIR server yet, so it is not adopted now.

## OMOP CDM

### OMOP CDM DDL
- **URL:** https://github.com/OHDSI/CommonDataModel
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-10-28
- **Decision:** reuse schema or dataset
- **Verified:** api.github.com/repos/OHDSI/CommonDataModel, api.github.com/repos/OHDSI/CommonDataModel/contents/inst/ddl and raw.githubusercontent.com/OHDSI/CommonDataModel/main/DESCRIPTION (`License: Apache License 2.0`), 2026-11-24
- **Licence note:** Same licence evidence as the OMOP CDM entry in [m01-terminology.md](m01-terminology.md): GitHub detects no licence and the root has no LICENSE file; only `DESCRIPTION` states Apache License 2.0 (give-back item in GIVEBACK.md). `inst/ddl` has versions 5.3, 5.4 and 5.5, and the 5.4 directory has a `postgresql` subfolder. Which version to target is a later module decision.

## Discourse

### Discourse API
- **URL:** https://docs.discourse.org/
- **Licence:** GPL-2.0
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q14)
- **Last activity:** 2026-11-24
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/discourse/discourse, raw.githubusercontent.com/discourse/discourse/main/LICENSE.txt (GNU GPL, Version 2, June 1991) and docs.discourse.org (HTTP 200, title "Discourse API Docs"), 2026-11-24
- **Licence note:** The Licence and Last activity fields describe the server repository https://github.com/discourse/discourse; the URL field is the API documentation. GPL-2.0 is not in the README licence table (the GNU list was only checked for GPLv3 compatibility), so the verdict is unknown. We would only talk to a Discourse forum (rapamycin.news) over HTTP, never link or bundle its code. DiscourseConnect login is already tracked in docs/QUESTIONS.md.
- **Provisional:** yes, only the public HTTP API documentation is used and no Discourse code is imported; the decision waits on Q14.
