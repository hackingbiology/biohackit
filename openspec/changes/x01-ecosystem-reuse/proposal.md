# Change: x01 — Ecosystem reuse and give-back (cross-cutting)

## Why
Fabio (2026-11-24): biohack.it must become **part of an ecosystem**, not a silo. Before building anything, we do in-depth technical analysis of existing projects (GitHub and elsewhere) to reuse:
- libraries;
- database structures and data models;
- vocabularies;
- UI components;
- protocols.

The slides already name software to integrate or learn from: get-based (AGPL, reuse analysis in `docs/getbased-reuse-analysis.md`), Forever Healthy's AI4L and evipedia-mcp, HL7 FHIR, OMOP, LOINC/UCUM, and Discourse/rapamycin.news. Their verified scan is `docs/ecosystem/integrations.md`. Some overhead in the software is accepted: anchoring to third-party knowledge and giving our knowledge back is worth more than a lean custom design.

## What changes
- **Ecosystem scan before every module**, recorded as `docs/ecosystem/<module>.md`, which a module's OpenSpec change must cite. The scan covers:
  - candidate projects, each with URL, licence, AGPL-3.0 compatibility, activity (last commit, releases, maintainers), test and CI quality, and data model/schema relevance;
  - a decision per candidate: **adopt** (dependency), **vendor/fork**, **integrate** (API/MCP/export format), **port ideas**, or **reject** (with reason);
  - the give-back opportunities.
- **Standards-first data structures:** use upstream schemas where they exist, even at some cost. Examples:
  - FHIR resources and profiles;
  - the OMOP CDM and OHDSI vocabularies;
  - the Open mHealth / IEEE 1752 schemas for wearable data, if the scan confirms they fit;
  - existing open datasets.
- **Retroactive scans** for M00 (auth, stack) and M01 (terminology), then one scan per module M02–M13 before its spec is written.
- **Give-back register** `docs/ecosystem/GIVEBACK.md`: upstream issues and PRs, data contributions, attribution, and connector notifications (ties into `related-initiatives` and `ai-uses-and-attribution`). Outward actions (opening issues or PRs on third-party repos, contacting maintainers) are proposed in the daily digest and done only after Fabio approves them.
- **Ecosystem map page** in the docs site: what we build on, what we contribute.

## Decisions
| # | Topic | Decision |
|---|-------|----------|
| E1 | Licence gate | Only AGPL-3.0-compatible code is merged (MIT, BSD, Apache-2.0, LGPL, GPL-3.0, AGPL-3.0); data licences recorded per source (CC BY, CC0, LOINC, …) |
| E2 | Facts | Every claim about an external project (licence, activity, API) is checked from its repo/docs by fetch; unverifiable ⇒ marked unknown |
| E3 | Overhead | Accepted when it buys standard compliance or an active upstream; rejected when the upstream is abandoned (>18 months without commits) unless it is a stable standard |
