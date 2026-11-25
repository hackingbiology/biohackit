# Spec discovery register — part D2a: competitive landscape

Source compared with `openspec/specs/**`: `docs/analysis/competitive-landscape.html` (6 `<h2>` sections). One row per feature claim about biohack.it, including the gaps the document says it should fill. Descriptions of competitors are `out-of-scope`.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/analysis/competitive-landscape.html § What this maps | Make the link from intervention to biomarker computable and public | added | analytics-and-open-data/Research API answers intervention-by-biomarker queries | |
| docs/analysis/competitive-landscape.html § What this maps | Market reading: crowded edges, empty middle, 2025-26 tracker growth | out-of-scope | — | Market analysis of competitors; not software behaviour |
| docs/analysis/competitive-landscape.html § Category map | 88 named competitors across 19 segments (category counts and product lists) | out-of-scope | — | Description of competitors; the document does not ask biohack.it to offer these features |
| docs/analysis/competitive-landscape.html § Feature matrix | Open source | added | community-and-social/Stewardship and mission lock are published | The requirement states the AGPL-3.0 licence |
| docs/analysis/competitive-landscape.html § Feature matrix | Open data | covered | analytics-and-open-data/Full clonable public snapshot | |
| docs/analysis/competitive-landscape.html § Feature matrix | Standards-coded (FHIR, LOINC, UCUM, RxNorm, OMOP) | covered | data-standards-and-typing/Document each standard and its rationale | |
| docs/analysis/competitive-landscape.html § Feature matrix | Intervention→biomarker link | added | analytics-and-open-data/Research API answers intervention-by-biomarker queries | |
| docs/analysis/competitive-landscape.html § Feature matrix | N-of-1 | covered | studies-nof1/Study with pre-declared endpoints | |
| docs/analysis/competitive-landscape.html § Feature matrix | Causal inference | out-of-scope | — | Conflicts with scientific-method-and-evidence/Observed, never caused (no causal phrasing); see QUESTIONS.md Q35 |
| docs/analysis/competitive-landscape.html § Feature matrix | Biological clocks | covered | biomarkers-and-labs/Biological clocks are first-class biomarkers | |
| docs/analysis/competitive-landscape.html § Feature matrix | Self-hosting | covered | accounts-and-profiles/Self-hosting a full instance (distinct from local-first) | |
| docs/analysis/competitive-landscape.html § Feature matrix | Target: biohacker | out-of-scope | — | Audience positioning, not a feature |
| docs/analysis/competitive-landscape.html § Feature matrix | Rows and cells for the 88 competitors, and the yes/no/unknown legend | out-of-scope | — | Descriptions of competitors |
| docs/analysis/competitive-landscape.html § Where the cells are empty | Open data as a reusable-science column | covered | analytics-and-open-data/Full clonable public snapshot | |
| docs/analysis/competitive-landscape.html § Where the cells are empty | Standards coding (RxNorm/LOINC/UCUM) carried into a public intervention→outcome record | covered | data-standards-and-typing/Coding plus provenance make aggregation valid | |
| docs/analysis/competitive-landscape.html § Where the cells are empty | Computable and public intervention→biomarker link | added | analytics-and-open-data/Research API answers intervention-by-biomarker queries | |
| docs/analysis/competitive-landscape.html § Where the cells are empty | Layer for distributed, self-organised trials | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/analysis/competitive-landscape.html § Where the cells are empty | Which competitor covers which capability | out-of-scope | — | Description of competitors |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Non-profit foundation, AGPL-3.0, free | added | community-and-social/Stewardship and mission lock are published | |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Open data by default | covered | analytics-and-open-data/Defined OpenData scope | |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Internal HL7 FHIR with OMOP export | covered | analytics-and-open-data/Researcher access and OMOP export | |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | gVCF behind heightened consent | covered | genomics/Public by default with heightened consent (incl. gVCF) | |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Raw lab reports behind heightened consent | out-of-scope | — | Source's heightened-consent gate for raw lab reports conflicts with biomarkers-and-labs/Original report file retained and public raw (public by default, no consent step); see Q36 |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Distributed, self-organised n-of-1 trials as the goal | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Comparative SWOT against these tools (pending step) | out-of-scope | — | The document states it is a separate, pending analysis; no software behaviour |
| docs/analysis/competitive-landscape.html § Where biohack.it sits | Nearest to Open Humans; overlaps Biohacker-OS products | out-of-scope | — | Positioning against competitors |
| docs/analysis/competitive-landscape.html § Emerging “Biohacker OS” | Public research commons coupling open data, standards-coding and a computable intervention→biomarker record | covered | analytics-and-open-data/Full clonable public snapshot | |
| docs/analysis/competitive-landscape.html § Emerging “Biohacker OS” | Outliyr, Trialist, Protocol, Aurboda, Open Wearables feature descriptions | out-of-scope | — | Descriptions of competitors; the document says only to watch them |
