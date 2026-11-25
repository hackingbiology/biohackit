# Spec discovery register — part D2b2: HB protocol structure workbook

Source compared with `openspec/specs/**`: `docs/reference/hb-protocol-structure.xlsx` (6 worksheets, one section each). Cell values were read without modification, with the Python standard library (`zipfile` + XML), because `openpyxl` is not installed in `backend/.venv`; the worksheets carry no dimension tag, so the extents below are computed from the non-empty cells.

| Worksheet | Last non-empty row | Last non-empty column | Non-empty cells |
|---|---|---|---|
| Pharmacy | 317 | Q (17) | 1035 |
| Sheet10 | 8 | C (3) | 18 |
| Blood Sampling | 41 | K (11) | 31 |
| Targets | 1 | A (1) | 1 |
| Rapamycin | 3 | B (2) | 2 |
| Gene Therapy | 4 | B (2) | 3 |

The workbook is one person's working list, not a specification. One row per feature it implies. Every number quoted from it is an observation with `sheet!cell` provenance; no value from the workbook is seed data, a default or a recommendation. Doses and per-weight values are never copied into `openspec/`. Any dose-related requirement is gated on posology provenance (`interventions-and-catalog/Posology provenance (human vs animal)`) and on `safety-guardrails/Heightened acknowledgment for research-level or animal-derived dosing`.

- **covered**: an existing requirement already promises the feature.
- **added**: no requirement existed; one is added in the open change `openspec/changes/s01-spec-discovery`.
- **out-of-scope**: not software behaviour, or a decision not taken; the Notes cell gives the reason.

The Requirement column reads `<capability>/<Requirement title>`. `backend/tests/test_spec_discovery_register.py` checks every row and that there is one section per worksheet.

## Pharmacy

The sheet holds four stacked blocks. Block 1 (rows 1-177): header row 1 reads A "Supplement", B "SUPPLEMENTS", D "Daily Pills", E "Dose Serving", F "Under protocol", G "Note", H "Presc", J "Sourcing", K "How many", P "Website" (Pharmacy!A1:P1). Block 2 (rows 179-230): header row 179 reads A "PHARMA", B "PRODUCT NAME", D "Daily Pills", E "Dose Serving", F "Under protocol", I "Posologia", J "Sourcing", K "Scorta" (Pharmacy!A179:K179). Block 3 (rows 231-307): header Pharmacy!A231 "SUPPLEMENTS", F231 "When", D232 "Mg", E232 "Effective Mg", G232 "Long Description", then effect-label columns I232 "NAD+", K232 "Autophagy", L232 "Telomere", M232 "Glicemic", N232 "HDL/LDL", O232 "Homocysteine"; one product per row in column A and its ingredients in column B. Block 4 (rows 312-317): header Pharmacy!A312 "PHARMA", D313 "Mg", E313 "Effective Mg", with four drug products below. The "Posologia" cells (column I) state no human or animal provenance anywhere in the sheet; every figure quoted below is a quoted observation, not a recommendation.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | A list of substances, one per row in column A, with free-text rationale in column B | covered | interventions-and-catalog/Substance catalog metadata | Names resolve to codes per `Substance resolution on codes, not English strings` |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Substances are resolved on codes; spelling variants and typos exist in the list (Pharmacy!A61 ";AGNESIUM COMPLEX") | covered | interventions-and-catalog/Substance resolution on codes, not English strings | Observation only; the typo is not corrected here |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Source links next to items (columns B, C, G, P, Q), for example Pharmacy!P79 a PubMed address | covered | evidence-layer/Structured evidence claims | Links are a pointer to evidence; each would need verification before use |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Daily intake count per item (column D "Daily Pills") and per serving (column E "Dose Serving"), for example Pharmacy!D10 and Pharmacy!E10 | covered | pills-management/Daily intake schedule across slots | Counts are the author's own, not copied |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Column F flags an item as in the running protocol ("Ok") or not ("No") | covered | protocols/Import an already-running protocol (experienced baseline) | Observation Pharmacy!F10 "Ok", Pharmacy!F69 "No" |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Timing and absorption remarks, for example "Don't go with magnesium, they compete" (Pharmacy!B57) and "night" (Pharmacy!G76) | covered | pills-management/Spacing and distance rules | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Intake with or without meals, for example Pharmacy!B105 on berberine before fatty meals | covered | pills-management/Meal timing and absorption requirements | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Interaction remarks between items, for example Pharmacy!C72 "Don't go with statin" | covered | safety-guardrails/Interaction and critical-value alerts | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Liver-toxicity caution recorded next to an item (Pharmacy!B18) | covered | safety-guardrails/Safety markers inherited automatically | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Per-weight values in a "mg/kg" form, quoted at Pharmacy!C35, Pharmacy!C43, Pharmacy!C47 (with a source link in the same row, G35, G43, G47) and Pharmacy!B165 | added | interventions-and-catalog/Weight-relative posology is gated on posology provenance | Observation only, values not carried into `openspec/`. Provenance (human or animal) is not stated in the sheet, so under the new requirement they are shown as recorded and never converted to an absolute dose; see Q38 |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | A dose written in the free-text rationale (Pharmacy!B38) and unit-bearing remarks (Pharmacy!C49, Pharmacy!G127) | covered | safety-guardrails/Dose sanity check | Observation only; numbers are checked against limits, never recommended |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Skin and scalp preparations in rows 2 to 8 (Pharmacy!A2:A8), mixed in with oral items | added | interventions-and-catalog/Route and formulation are recorded per intake item | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Formulation matters: liposomal, re-esterified triglyceride (Pharmacy!B22), named branded forms (Pharmacy!I92) | added | interventions-and-catalog/Route and formulation are recorded per intake item | Bioavailability claims in the sheet are the author's remarks, not data |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Column H "Presc": which items need a prescription | out-of-scope | — | Column H holds only its header (Pharmacy!H1) and no value in any row; semantics unclear, see Q38 |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Column J "Sourcing" (a place or a person, Pharmacy!J186, a person's name, redacted) and column K "How many" / "Scorta" (stock to hold, Pharmacy!K186 "3 mesi") | covered | procurement-and-inventory/Projected need from protocol | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Product name, pack size and number of packs per drug (Pharmacy!B194, Pharmacy!C194, Pharmacy!L194) | covered | procurement-and-inventory/Inventory with lots and expiry | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Product website per item (column P), for example Pharmacy!P10 | covered | procurement-and-inventory/No monetised procurement initially | Links are informational; no purchase is brokered |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Cost and restock of a long regimen | covered | pills-management/Restock link to procurement | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | A very long list (the used range reaches row 317) | covered | pills-management/Scale to high-volume regimens | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Items marked "to be evaluated" (Pharmacy!B91 "TBevaluated") and alternatives to consider (Pharmacy!G13) | out-of-scope | — | Personal to-do notes; a protocol in `draft` state already holds unreviewed items |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Mixed-language notes (Italian and English, for example Pharmacy!B105) | out-of-scope | — | Observation about the author's notes; user-entered text is stored as typed |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | A "Posologia" column for each drug (Pharmacy!I179 header; values such as Pharmacy!I192, Pharmacy!I197, Pharmacy!I200) with no stated human or animal provenance | covered | interventions-and-catalog/Posology provenance (human vs animal) | Observation only; values are not copied to `openspec/`. A posology without provenance is not presented as established |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Regimen includes research-level and prescription-only drugs (for example Pharmacy!A192, Pharmacy!A197, Pharmacy!A221) | covered | safety-guardrails/Heightened acknowledgment for research-level or animal-derived dosing | Activation needs the explicit acknowledgment on top of the mandatory baseline |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Same baseline needed before following any protocol containing those drugs | covered | safety-guardrails/Mandatory baseline AND risk acknowledgment before following a protocol | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Drugs and hormones listed for off-label use (for example Pharmacy!A175, Pharmacy!A182, Pharmacy!A197) | added | safety-guardrails/Platform describes and never prescribes | The platform shows the list as the user's own plan and never advises taking any item |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Splitting or compounding a product to a smaller amount (Pharmacy!G200) | out-of-scope | — | A practical instruction between a user and their clinician; the platform never prescribes, and any resulting amount passes `safety-guardrails/Dose sanity check` |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Unusual or unavailable substances (Pharmacy!A220 "not yet on market", Pharmacy!C147 "Can't find it") | covered | interventions-and-catalog/Substance resolution on codes, not English strings | Unresolved names are held for review, not guessed |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Same substance listed twice by route (oral Pharmacy!A210 and topical Pharmacy!A202 for one drug; Pharmacy!A192 and Pharmacy!A209 for another) | added | interventions-and-catalog/Route and formulation are recorded per intake item | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Product breakdown into ingredients with amounts per unit (Pharmacy!A233 product, Pharmacy!B233:B243 ingredients, column D) | added | interventions-and-catalog/Multi-ingredient products list their declared ingredients | Amounts are label content with the label as source; none is copied here |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | "Mg" versus "Effective Mg" per ingredient (Pharmacy!D232, Pharmacy!E232): the second reflects the number of daily units, for example Pharmacy!D259 against Pharmacy!E259 | added | interventions-and-catalog/Multi-ingredient products list their declared ingredients | The daily total is computed by code from label amounts, not typed by hand |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Same ingredient in several products, for example magnesium in Pharmacy!B272 and Pharmacy!B274 | added | interventions-and-catalog/Multi-ingredient products list their declared ingredients | Summed daily intake is passed through the dose sanity check |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | "When" column for products ("morning/evening", Pharmacy!F233; "With lipo / food", Pharmacy!F264) | covered | pills-management/Daily intake schedule across slots | |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Effect labels per product marked with "X" (Pharmacy!I232 "NAD+", Pharmacy!N232 "HDL/LDL", Pharmacy!O232 "Homocysteine"; marks at Pharmacy!I233, Pharmacy!O242) | covered | evidence-layer/Outcome↔Biomarker link | Only labels that map to a biomarker; pathway labels such as "Autophagy" (Pharmacy!K232) have no biomarker and stay free text |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Outcome claims copied from social posts and news (Pharmacy!B121, Pharmacy!B229, Pharmacy!B167) | added | evidence-layer/Claims Validator | A claim without a verified source is shown as unverified |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Weak sources: social-media and forum links for support (Pharmacy!B34, Pharmacy!C25, Pharmacy!B19) | covered | scientific-method-and-evidence/Evidence hierarchy | Anecdote ranks below trials |
| docs/reference/hb-protocol-structure.xlsx § Pharmacy | Block 4 repeats four drug products with "Mg" and "Effective Mg" (Pharmacy!A314:E317) | covered | pills-management/Daily intake schedule across slots | Observation only; no value copied |

## Sheet10

Cells Sheet10!B1 "Chi", then substance names in column A, a person's name in column B and a short remark in column C (Sheet10!A2:C8).

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/reference/hb-protocol-structure.xlsx § Sheet10 | A short list of substance names (for example Sheet10!A2, Sheet10!A5) | covered | interventions-and-catalog/Substance catalog metadata | |
| docs/reference/hb-protocol-structure.xlsx § Sheet10 | Column B "Chi" assigns each substance to a person, with a short rationale in column C (Sheet10!B6, a person's name, redacted; Sheet10!C5) | out-of-scope | — | Meaning unclear (who takes it, who buys it, who prescribes). Each user keeps their own protocol; a manager acts for a managed user under `management-and-delegation/Management scope — administer, measure, monitor`; see Q38 |

## Blood Sampling

Content in Blood Sampling!B2, Blood Sampling!K6:K23 (a metabolic panel analyte list), Blood Sampling!A32:A41 and D38:E39 (cancer markers with tumour-type remarks).

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/reference/hb-protocol-structure.xlsx § Blood Sampling | A comprehensive metabolic panel analyte list (Blood Sampling!K6 to K23, from "Glucose" to "Estimated Glomerular Filtration Rate (eGFR)") | covered | biomarkers-and-labs/Coded analyte registry | Codes come from LOINC at seed time, never from this sheet |
| docs/reference/hb-protocol-structure.xlsx § Blood Sampling | Calculated analytes inside the list (Blood Sampling!K20 "Globulin, Calculated", K21, K22) | covered | biomarkers-and-labs/Deterministic pipeline with a hard boundary | |
| docs/reference/hb-protocol-structure.xlsx § Blood Sampling | A cancer-marker group (Blood Sampling!A32 "Cancer Biomarkers", rows 33 to 41) | covered | biomarkers-and-labs/Coded analyte registry | Tumour-type remarks (Blood Sampling!D38, E39) are the author's notes |
| docs/reference/hb-protocol-structure.xlsx § Blood Sampling | Choose which analytes to draw together in one blood draw | covered | measurement-planning/Analyte pooling into one draw | |
| docs/reference/hb-protocol-structure.xlsx § Blood Sampling | A commercial biological-age test product link (Blood Sampling!B2) | covered | biomarkers-and-labs/Inventory of biological clocks with accessibility assessment | The link is a reference to verify, not a recommendation |

## Targets

A single cell, Targets!A1, naming molecular targets (sirtuins, Klotho, FOXO1, TERT, TP53, GDF11).

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/reference/hb-protocol-structure.xlsx § Targets | A list of molecular targets of interest for ageing | out-of-scope | — | A reading list of biology terms, no stated behaviour and no dose; evidence about a target belongs to `evidence-layer/Outcome↔Biomarker link`; see Q38 |

## Rapamycin

Cells Rapamycin!A3 "Turkey travel" and Rapamycin!B3 (a forum thread address).

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/reference/hb-protocol-structure.xlsx § Rapamycin | A note on carrying rapamycin through customs when travelling | out-of-scope | — | Legal and travel advice is not a platform behaviour; see Q38 |

## Gene Therapy

Cells Gene Therapy!A3 "Follistatin" with a clinic link in B3, and Gene Therapy!A4 naming TERT and follistatin with a literature link.

| Source | Feature | Status | Requirement | Notes |
|---|---|---|---|---|
| docs/reference/hb-protocol-structure.xlsx § Gene Therapy | Gene therapy as a tracked periodic therapy | covered | therapeutics-management/Extensible therapy catalog | No dose or schedule is given in the sheet and none is invented |
| docs/reference/hb-protocol-structure.xlsx § Gene Therapy | A clinic address and a paper link for the therapy | covered | evidence-layer/Structured evidence claims | Links are to be verified before use |
