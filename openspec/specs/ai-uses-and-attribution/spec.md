# AI Uses, Provenance & Previous Work (cross-cutting)

## Purpose

Consolidates three things the scientific and biohacker audience asks first: **where AI is used and — crucially — where it is not**, **which frameworks and external knowledgebases the platform builds on**, and **the attribution and licensing of prior work**. It adopts the published "AI surfaces map" pattern and names the shoulders biohack.it stands on — above all **Forever Healthy's Evipedia and AI4L**, plus `get-based` and the open vocabularies. This capability governs the others; it owns the trust artifact, not a product screen.

## Requirements

### Requirement: Published AI surfaces map — "what is AI, what is NOT AI"
The system SHALL maintain and publish a canonical map of every surface where AI is used and every surface where it is deliberately not, so a reader can trust the numbers.

#### Scenario: The numbers are not AI
- **WHEN** a user views a computed value (safety threshold, index, sex/age percentile, trend, schedule)
- **THEN** the AI surfaces map documents these as deterministic and reproducible, not AI-generated
- **AND** only extraction, narration, and evidence-review generation are marked as AI surfaces

### Requirement: AI4L as the framework for AI-generated reviews and evidence queries
The system SHALL use Forever Healthy's **AI4L** audit-based-prompting framework for any AI-generated evidence review or evidence data query, rather than ad-hoc prompting.

#### Scenario: Audited generation, not single-shot
- **WHEN** the platform generates or refreshes an evidence review, or answers an evidence query with AI
- **THEN** it runs the AI4L create → audit → correct cycle against the QA checklist, restricted to trusted scientific sources
- **AND** outputs are cached and reproducible, and the LLM never writes numbers into constrained fields (see `interventions-and-catalog`, `biomarkers-and-labs`)

### Requirement: AI4L output conforms to the project's strict normalization
The system SHALL ensure AI4L-generated reviews and evidence queries conform to biohack.it's strict data normalization — analytes coded to LOINC/UCUM, substances resolved to RxNorm/ATC/PubChem/UNII, outcomes mapped to biomarkers — rather than free-text entities.

> OPEN: technical feasibility to decide — either (a) **extend AI4L to use these databases natively** (LOINC/UCUM/RxNorm/ATC/PubChem/UNII), or (b) **extend AI4L's prompting to use biohack.it's databases**. Evaluate both.

#### Scenario: Generated review is normalized
- **WHEN** AI4L produces or refreshes a review, or answers an evidence query
- **THEN** its interventions, analytes and outcomes are resolved to the project's coded vocabularies (see `interventions-and-catalog`, `biomarkers-and-labs`)
- **AND** non-resolvable entities are marked ambiguous for review, never left as silent free text

### Requirement: Integrate the Evipedia knowledgebase, attributed
The system SHALL integrate Forever Healthy's **Evipedia** as an external evidence knowledgebase via its MCP server (`mcp.evipedia.ai`) and public endpoints (`/reviews.json`, `/search.json`, `/{slug}.md`, `/{slug}.meta.json`), and SHALL attribute Forever Healthy per Evipedia's **CC BY 4.0** license wherever its content is surfaced.

#### Scenario: Review retrieved and attributed
- **WHEN** an intervention has an Evipedia review
- **THEN** the platform can retrieve its conclusion, metadata (alternate names, PMIDs), and full review via the Evipedia MCP or JSON/MD endpoints
- **AND** any surfaced Evipedia content carries visible attribution to Forever Healthy (CC BY 4.0)

### Requirement: Content structure aligned to the Evipedia / AI4L review model
The system SHALL align its intervention-evidence structure — conclusion, graded evidence, risk-benefit, ordered citations with PMIDs, review dates — with the Evipedia/AI4L model, so content interoperates and can be reused both ways.

#### Scenario: Interoperable structure with our differential on top
- **WHEN** the platform stores an intervention's evidence
- **THEN** its structure maps to the Evipedia review model (conclusion, grading, risk-benefit, citations, dates)
- **AND** biohack.it's differential — the Outcome↔Biomarker link and the observed-cohort column — is layered on top (see `evidence-layer`, `dashboards-and-doctor-view`)

### Requirement: Previous-work and license register
The system SHALL maintain a register of reused prior work with its license and attribution, and SHALL keep every integration compatible with the project's AGPL-3.0 license.

#### Scenario: License recorded before reuse
- **WHEN** a component or dataset is reused — Evipedia (CC BY 4.0), AI4L (MIT), `get-based` (AGPL), LOINC / UCUM / RxNorm / ATC / PubChem / UNII
- **THEN** its license and required attribution are recorded and shown
- **AND** any license incompatibility is flagged before integration proceeds

#### Scenario: Public trust artifact
- **WHEN** a physician or researcher asks "can I trust these numbers?"
- **THEN** the published AI surfaces map + attribution register answers where AI runs, where it does not, and whose vetted knowledge is reused
