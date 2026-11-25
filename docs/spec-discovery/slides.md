# Spec discovery register — part D1a: slides

Source compared with `openspec/specs/**`: `docs/slides/hacking-biology-project-presentation.pdf` (14 pages; the page count and content were read page by page as images because `pdftotext` was not permitted in the authoring sandbox). One row per feature claim; pages that carry only motivation, background science, costs or notes are `out-of-scope`.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/slides/hacking-biology-project-presentation.pdf § page 1 | Title slide: "Hacking Biology", DIY protocol to measure and address the hallmarks of aging | out-of-scope | — | Title and project URL; not a product feature |
| docs/slides/hacking-biology-project-presentation.pdf § page 2 | Background: hallmarks of aging and anti-aging strategies (two linked figures) | out-of-scope | — | Scientific background with external references; not software behaviour |
| docs/slides/hacking-biology-project-presentation.pdf § page 3 | Let people compose a custom protocol from a database of interventions | covered | protocols/Create a protocol from scratch | |
| docs/slides/hacking-biology-project-presentation.pdf § page 3 | Report specific health KPIs back to measure the impact of anything new | covered | studies-nof1/Pre/post read-out | |
| docs/slides/hacking-biology-project-presentation.pdf § page 3 | Example thread from the rapamycin.news forum | covered | community-and-social/Integrate with Rapamycin News (Discourse Connect where feasible) | |
| docs/slides/hacking-biology-project-presentation.pdf § page 4 | Motivation: author's age, market of clinics and subscription pills | out-of-scope | — | Personal motivation and problem statement |
| docs/slides/hacking-biology-project-presentation.pdf § page 4 | Measure the effect of multiple approaches in a structured, comparable way | covered | analytics-and-open-data/Cohort aggregation | |
| docs/slides/hacking-biology-project-presentation.pdf § page 4 | DIY applied-research protocol with data sharing; "open laboratory" producing a distributed trial | covered | scientific-method-and-evidence/Qualification bar for a distributed trial | |
| docs/slides/hacking-biology-project-presentation.pdf § page 4 | Community chooses a protocol, gets the requested KPIs to measure, reported for trend analytics | covered | analytics-and-open-data/Cohort aggregation | |
| docs/slides/hacking-biology-project-presentation.pdf § page 4 | Machine learning once thousands of subjects share their data | out-of-scope | — | Aspiration with no stated feature; research use is covered by analytics-and-open-data/Researcher access and OMOP export |
| docs/slides/hacking-biology-project-presentation.pdf § page 5 | Methodology step 1: record biological age and the chronological-age delta | covered | dashboards-and-doctor-view/Headline metric first, then organ-system grid | |
| docs/slides/hacking-biology-project-presentation.pdf § page 5 | Methodology step 2: act with supplements, therapeutics, nutrition, pharma | covered | domain-model/Intervention subtypes | |
| docs/slides/hacking-biology-project-presentation.pdf § page 5 | Methodology step 3: measure effectiveness on a public dashboard | covered | dashboards-and-doctor-view/Public dashboard grouped by biomarker family | |
| docs/slides/hacking-biology-project-presentation.pdf § page 5 | Collaborative analysis of the results of own protocol parameters (OpenData) | covered | analytics-and-open-data/Defined OpenData scope | |
| docs/slides/hacking-biology-project-presentation.pdf § page 5 | Continuously experiment with new research findings | out-of-scope | — | Process statement, no testable software behaviour |
| docs/slides/hacking-biology-project-presentation.pdf § page 6 | Blood panel input (very wide) and DNA (methylation, telomere length) | covered | biomarkers-and-labs/Coded analyte registry | The slide says "+130 biomarkers"; the number is not a requirement |
| docs/slides/hacking-biology-project-presentation.pdf § page 6 | DNA analytics, microbiome and DEXA measured frequently | added | biomarkers-and-labs/Body composition and microbiome results are accepted as measurements | |
| docs/slides/hacking-biology-project-presentation.pdf § page 6 | Blood panel monthly | covered | measurement-planning/Phase-dependent cadence | |
| docs/slides/hacking-biology-project-presentation.pdf § page 6 | Load data by uploading examinations or typing manually | covered | biomarkers-and-labs/Import from PDF, photo, and CSV with learned templates | Manual entry: biomarkers-and-labs/Manual entry of equal standing |
| docs/slides/hacking-biology-project-presentation.pdf § page 6 | Display biological age and chronological age delta | covered | dashboards-and-doctor-view/Headline metric first, then organ-system grid | |
| docs/slides/hacking-biology-project-presentation.pdf § page 6 | Measure the impact of new actions, whether to maintain them or not | covered | studies-nof1/Pre/post read-out | |
| docs/slides/hacking-biology-project-presentation.pdf § page 7 | Supplements, pharmaceuticals, peptide injections and IV infusion as actions | covered | domain-model/Intervention subtypes | |
| docs/slides/hacking-biology-project-presentation.pdf § page 7 | Plasmapheresis, HBOT with hypoxia-hyperoxia fluctuations | covered | therapeutics-management/Model periodic therapy sessions | |
| docs/slides/hacking-biology-project-presentation.pdf § page 7 | Lipid control, glycaemic control and hormone regulation as protocol goals | covered | protocols/Create a protocol from scratch | |
| docs/slides/hacking-biology-project-presentation.pdf § page 7 | Nutrition habits: fasting 16/8 and/or calorie restriction with a target body fat | covered | nutrition-management/Declare the typical eating schedule/pattern | |
| docs/slides/hacking-biology-project-presentation.pdf § page 7 | Gym and exercise practice | covered | exercise-reporting/Define the exercise activity profile | |
| docs/slides/hacking-biology-project-presentation.pdf § page 7 | What matters is which biomarker an action intervenes on, for different goals | covered | domain-model/Biomarker with role and three ranges | |
| docs/slides/hacking-biology-project-presentation.pdf § page 8 | Scheduling for taking supplements and pharmaceuticals | covered | pills-management/Daily intake schedule across slots | |
| docs/slides/hacking-biology-project-presentation.pdf § page 8 | Scheduling measurements (booking, appointments, recording data) | added | measurement-planning/Measurement appointments are recorded | Scheduling views: measurement-planning/Planner views |
| docs/slides/hacking-biology-project-presentation.pdf § page 8 | Record fasting adherence and nutrition exceptions | covered | nutrition-management/Log adherence to the nutrition plan | |
| docs/slides/hacking-biology-project-presentation.pdf § page 8 | Supply organization: when to buy what and from where | covered | procurement-and-inventory/Projected need from protocol | |
| docs/slides/hacking-biology-project-presentation.pdf § page 9 | Software platform to orchestrate the personal protocol, self-managed | covered | protocols/Create a protocol from scratch | |
| docs/slides/hacking-biology-project-presentation.pdf § page 9 | Shared among online aging communities and usable by market players providing products | out-of-scope | — | Audience statement; monetised procurement is not planned (procurement-and-inventory/No monetised procurement initially) |
| docs/slides/hacking-biology-project-presentation.pdf § page 9 | Provided as AGPL-3.0 free software, material under a Creative Commons licence | added | analytics-and-open-data/Open licences declared on published data and content | Slide text says "Common Criteria"; AGPL-3.0 is stated in community-and-social/Stewardship and mission lock are published |
| docs/slides/hacking-biology-project-presentation.pdf § page 10 | Estimated operational and startup costs | out-of-scope | — | Cost estimate for the author's own protocol; not software behaviour; no figure is adopted |
| docs/slides/hacking-biology-project-presentation.pdf § page 11 | Divider: "From here just notes / slides notes" | out-of-scope | — | No feature content |
| docs/slides/hacking-biology-project-presentation.pdf § page 12 | NRF2 loss increases ROS and links to the hallmarks of aging | out-of-scope | — | Scientific background; evidence would arrive through evidence-layer/Evipedia as the primary evidence source |
| docs/slides/hacking-biology-project-presentation.pdf § page 13 | Lifespan chart of genetic manipulations by pathway | out-of-scope | — | Scientific background figure with an external source link |
| docs/slides/hacking-biology-project-presentation.pdf § page 14 | Dietary approach: 20% calorie restriction; methionine and cysteine restriction as enhancement | covered | nutrition-management/Declare the typical eating schedule/pattern | Specific percentages are the author's choice and are not adopted as defaults |
