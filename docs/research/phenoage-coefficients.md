# PhenoAge and Bortz blood-age clocks: coefficients across sources

Research task from Fabio's Q56 answer (docs/QUESTIONS.md, "Answers (Fabio 2026-11-26)"). Scope: compare the coefficients, constants, units and transformations of the PhenoAge clock (Levine 2018) and the Bortz blood-age clock (Bortz 2023) across the papers and the maintained implementations, record every difference, and recommend whether to adopt a library as the computation engine (x01 rule, docs/ecosystem/README.md).

**Rules of this document.**
- Every number below was read from a page or file fetched on **2026-11-26** (the access date for every source). Each is cited by source id (S1, S2, ...) from the sources tables. Numbers marked "my computation" were calculated here from cited numbers, not fetched.
- A value that could not be fetched is written `unknown (not fetched)`. Nothing is filled in from memory.
- Where sources differ, "the paper prevails unless an erratum says otherwise" (Fabio, Q56). Where that rule does not settle the case (see D3), the choice is a question with a default (Q77), not a decision.
- Documentation only. The numbers of this document are in code only in backend/core/phenoage.py (TG-i part 1, S2 constants plus the Q77 defaults). The TG-i computation item stays unchecked until part 2.

---

## Part 1. PhenoAge (Levine 2018)

### 1.1 Sources

| id | Source | Identifier | Version / commit | Accessed | Fetched how |
|---|---|---|---|---|---|
| S1 | Levine ME, Lu AT, Quach A, et al. "An epigenetic biomarker of aging for lifespan and healthspan." Aging (Albany NY) 2018;10(4):573-591 (CC BY 3.0) | DOI 10.18632/aging.101414, PMC5940111, https://pmc.ncbi.nlm.nih.gov/articles/PMC5940111/ | published 2018-04-17 (journal version) | 2026-11-26 | WebFetch of the PMC page (Table 1). Only the first 100000 of 121284 characters were read |
| S2 | Supplement SD1 "Additional file for ..." of S1 (43 pages) | https://cdn.aging-us.com/article/101414/supplementary/SD1/0/aging-v10i4-101414-supplementary-material-SD1.pdf | file as served 2026-11-26 (no version id; 4.1 MB) | 2026-11-26 | PDF downloaded by WebFetch and **pages 1, 2 and 10 read as images** (formulas on pp. 1-2, Table S1 on p. 10). The other 40 pages were not read |
| S3 | Liu Z, Kuo P-L, Horvath S, Crimmins E, Ferrucci L, Levine M. "Correction: A new aging measure captures morbidity and mortality risk across diverse subpopulations from NHANES IV: A cohort study." PLoS Med 2019;16(2):e1002760 (CC BY 4.0). It corrects the equation printed in Liu et al. 2018 (PLoS Med 15(12):e1002718, PMC6312200), not S1 | DOI 10.1371/journal.pmed.1002760, PMC6388911, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6388911/fullTextXML | published 2019-02-25 | 2026-11-26 | Europe PMC JATS XML, equation text read. The journal page (https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002760) shows the equation only as images |
| S4 | Kuo C-L, Pilling LC, Liu Z, Atkins JL, Levine ME. "Genetic associations for two biological age measures point to distinct aging phenotypes." Aging Cell 2021;20(6):e13376, section 4.3 | DOI 10.1111/acel.13376, PMC8208797, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8208797/fullTextXML | published 2021 | 2026-11-26 | Europe PMC JATS XML (formula MathML read) and WebFetch of https://pmc.ncbi.nlm.nih.gov/articles/PMC8208797/. The publisher page (onlinelibrary.wiley.com) returned HTTP 403 |
| S5 | pyaging (clinical `phenoage`), `src/pyaging/models/_models.py`, `clocks/notebooks/phenoage.ipynb`, `src/pyaging/data/feature_ranges.json`, `docs/development/phenoage-gompertz-correction.md` | https://github.com/lucascamillomd/pyaging | commit `db77b4bc263c82bfd2d5330029f232c71f2b33ec` (2026-11-19); PyPI 0.6.3 | 2026-11-26 | raw.githubusercontent.com at that commit |
| S6 | get-based, `js/data-calculated-markers.ts` lines 336-378 | https://github.com/elkimek/get-based | commit `3fba237f89f004cad915fa5c7767aaf9efe1d9d6` (2026-11-26) | 2026-11-26 | raw.githubusercontent.com at that commit |
| S7 | biolearn, `biolearn/clinical/registry.py`, `biolearn/model.py` | https://github.com/bio-learn/biolearn | commit `0d714f5a0c0ad5743b6315f3edab1f86112d394f` (2026-07-11); PyPI 0.9.1 | 2026-11-26 | raw.githubusercontent.com at that commit |
| S8 | mcp-phenoage-clock, `src/phenoage.ts` | https://github.com/199-mcp/mcp-phenoage-clock | commit `67bbb0440839ffcd49c8a6d17bbf8f2136729ce0` (2025-05-31) | 2026-11-26 | raw.githubusercontent.com (branch `main` resolved to this commit) |
| S9 | BioAge (R), `R/phenoage_calc.R` | https://github.com/dayoonkwon/BioAge | commit `b1f9fc02f086cd4aa74185f2335ab1366082e7fe` (2026-04-02) | 2026-11-26 | raw.githubusercontent.com |

**Errata search.** Crossref's record for S1 (https://api.crossref.org/works/10.18632/aging.101414, fetched 2026-11-26) has no `update-to` or `updated-by` entry, and a Europe PMC title search found no correction notice for S1. So no registered erratum to S1 was found. This is absence of evidence from two indexes, not proof. The only correction found is S3, and it is a correction of another paper (Liu 2018) that reprints the same equation.

### 1.2 What each source says

**S2 (original supplement), formulas.**
- p. 1: mortality score `MortalityScore_j = CDF(120, xb_j) = 1 - exp(-exp(xb_j) * (exp(120*gamma) - 1) / gamma)`.
- p. 1: `PhenotypicAge_j = 141.50225 + ln(-0.00553 * ln(1 - MortalityScore_j)) / 0.090165`. The same equation is printed again on p. 2.
- p. 1: "a lambda of 0.0192" is the penalty of the Cox penalised regression used to select variables. p. 2: "gamma = 0.0076927" is the Gompertz parameter. These are different quantities.
- p. 2: the 120-month horizon: "t denotes time (here in units of months)".

**S2 Table S1 (p. 10)**, "Phenotypic Aging Measures and Gompertz Coefficients": the weights and units are in the table of 1.3. It also prints `Constant -19.9067` and `Gamma 0.0077`. The main-paper Table 1 (S1, as fetched) lists the same ten weights and units (ALP 0.0019) but no constant and no gamma.

**S3 (2019 correction)** replaces the Liu 2018 equation with: `Phenotypic Age = 141.50 + ln[-0.00553 * ln(1 - M)] / 0.09165`, `M = 1 - exp(-1.51714 * exp(xb) / 0.0076927)`, and `xb = -19.907 - 0.0336*Albumin + 0.0095*Creatinine + 0.1953*Glucose + 0.0954*ln(CRP) - 0.0120*LymphocytePercent + 0.0268*MeanCellVolume + 0.3306*RedCellDistributionWidth + 0.00188*AlkalinePhosphatase + 0.0554*WhiteBloodCellCount + 0.0804*ChronologicalAge`. The correction states what was wrong: the original equation "is missing a step which makes it impossible to resolve". It gives no units.

**S4 (Kuo 2021, section 4.3)** prints the same `xb` (intercept -19.907, ALP 0.00188, `ln(CRP)`), `gamma = 0.0076927`, `mortality risk = 1 - exp{-exp(xb)[exp(120 gamma) - 1]/gamma}`, and `PhenoAge = 141.50 + ln{-0.00553 * ln(1 - mortality risk)} / 0.09165`, with an expanded form containing `1.51714`. The fetched text states no units.

My computation: `exp(120 * 0.0076927) - 1 = 1.51714167...`, so `1.51714` in S3/S4 is that term rounded.

### 1.3 Per-term comparison

Weights are the coefficient of the analyte in `xb`. "unit" is the unit the coefficient expects. "n/s" = the fetched source does not state a unit.

| Term | S2 supplement Table S1 / pp.1-2 (original) | S3 2019 correction | S4 Kuo 2021 | S5 pyaging 0.6.3 (db77b4b) | S6 get-based (3fba237) | S8 mcp-phenoage-clock (67bbb04) |
|---|---|---|---|---|---|---|
| Intercept (constant) | -19.9067 | -19.907 | -19.907 | -19.907 | -19.907 | -19.907 |
| Albumin | -0.0336, g/L | -0.0336, n/s | -0.0336, n/s | -0.0336, g/L | -0.0336, g/L | -0.0336, code takes **g/dL** (validation 1-6 g/dL) |
| Creatinine | 0.0095, umol/L | 0.0095, n/s | 0.0095, n/s | 0.0095, umol/L | 0.0095, umol/L | 0.0095, code takes **mg/dL** (0.1-15) |
| Glucose | 0.1953, mmol/L | 0.1953, n/s | 0.1953, n/s | 0.1953, mmol/L | 0.1953, mmol/L | 0.1953, code takes **mg/dL** (30-500) |
| C-reactive protein | 0.0954 on "(log)", mg/dL | 0.0954 on ln(CRP), n/s | 0.0954 on ln(CRP), n/s | 0.0954 on ln(CRP), mg/dL; value floored at 0.01 mg/dL before ln | 0.0954 on ln(CRP), mg/dL after dividing the stored mg/L by 10; a value <= 0 gives no result | 0.0954 on ln(CRP), code takes **mg/L** |
| Lymphocyte percent | -0.0120, % | -0.0120, n/s | -0.0120, n/s | -0.0120, % | -0.0120, % (stored fraction x 100) | -0.0120, % |
| Mean cell volume | 0.0268, fL | 0.0268, n/s | 0.0268, n/s | 0.0268, fL | 0.0268, fL | 0.0268, fL |
| Red cell distribution width | 0.3306, % | 0.3306, n/s | 0.3306, n/s | 0.3306, % | 0.3306, % | 0.3306, % |
| Alkaline phosphatase | **0.0019**, U/L | **0.00188**, n/s | **0.00188**, n/s | **0.00188**, U/L | **0.00188**, U/L (stored ukat/L x 60, see 1.4) | **0.00188**, U/L |
| White blood cell count | 0.0554, 1000 cells/uL | 0.0554, n/s | 0.0554, n/s | 0.0554, 10^3 cells/uL | 0.0554, 10^9/L as stored | 0.0554, 1000 cells/uL |
| Age | 0.0804, years | 0.0804, n/s | 0.0804, n/s | 0.0804, years | 0.0804, years | 0.0804, years |
| Gompertz gamma | 0.0076927 (p. 2 text); 0.0077 (Table S1) | 0.0076927 | 0.0076927 | 0.0076927 | 0.0076927 | 0.0076927 |
| Horizon | 120 months | 120 (in `1.51714` = exp(120 gamma) - 1, my computation) | 120 | folded into 1.51714 | 120 | 120 |
| Mortality-to-age: additive constant | **141.50225** | **141.50** | **141.50** | **141.50** | **141.50225** | **141.50225** |
| Mortality-to-age: divisor | **0.090165** | **0.09165** | **0.09165** | **0.09165** | **0.090165** | **0.090165** |
| Mortality-to-age: 0.00553 | 0.00553 | 0.00553 | 0.00553 | 0.00553 | 0.00553 | 0.00553 |
| Form of the final step | `141.50225 + ln(-0.00553 ln(1-M)) / 0.090165` | same shape with the S3 constants | same shape, plus an expanded form | `141.50 + (xb + ln(0.00553*1.51714/0.0076927)) / 0.09165`, computed in log space, no M | computes M then the S2 formula; returns no result if M <= 0 or M >= 1 | computes M, clamps M to [0.000001, 0.999999], then the S2 formula |

S7 (biolearn): **no clinical PhenoAge model was found** at commit 0d714f5. `biolearn/model.py` defines `PhenoAge` (line 382) as a `LinearMethylationModel` over `PhenoAge.csv`, which is the DNA-methylation clock of S1 (source URL `https://www.aging-us.com/article/101414/text`), not the blood-chemistry formula. Its `biolearn/clinical/registry.py` only defines canonical units: albumin g/L, creatinine umol/L, glucose mmol/L, C-reactive protein mg/dL, white blood cell count 1000 cells/uL, lymphocyte percent %, red blood cell distribution width %, mean cell volume fL, alkaline phosphatase U/L, with conversion factors (albumin g/dL x 10, creatinine mg/dL x 88.42, glucose mg/dL x 0.05551, CRP mg/L / 10 and nmol/L / 95.24). These units match the S2 Table S1 units. The conversion factors were read, not independently checked here. I only grep-searched `model.py` and the repository file list for a clinical clock; I did not read every file, so "not found" means not found by those searches.

S9 (BioAge, R): `phenoage_calc` *re-fits* a Gompertz model on the supplied data (flexsurv) and derives its own gamma and mortality-to-age constants (`m_n`, `m_d`, `BA_n`, `BA_d`, `BA_i`); with `orig = TRUE` the original is mentioned in the signature, but the excerpt read (first 90 lines) does not show the original constants. Its biomarker names carry units: `albumin_gL`, `creat_umol`, `glucose_mmol`, `lncrp`. Original constants in S9: `unknown (not fetched)`.

pyaging history (S5, `docs/development/phenoage-gompertz-correction.md`, a secondary statement, not verified against the releases): 0.5.7 used the S2 constants `141.50225` and `0.090165`; 0.6.1 used the S3 correction with `log1p` and described a "leading 1 inside the logarithm" of the correction; 0.6.2 and later (current 0.6.3) use S4. The text of S3 as fetched (JATS XML) shows no leading 1 inside the logarithm; I could not see the equation images, so that pyaging claim is **not confirmed**. The file also states 0.5.7 corrected an earlier error where the Cox penalty 0.0192 was used as gamma, a mistake that matches the lambda/gamma distinction on S2 pp. 1-2.

### 1.4 Unit and transformation notes

- **CRP.** S2 Table S1: "C-reactive protein (log)", mg/dL. S3 and S4 say `ln(CRP)`. S5 uses the natural log with a floor of 0.01 mg/dL (a pyaging design choice, not in the papers). S6 converts the stored mg/L to mg/dL by dividing by 10. S8 takes mg/L and applies the coefficient to `ln(CRP in mg/L)`. My computation: feeding mg/L instead of mg/dL adds `0.0954 * ln(10) = 0.2197` to `xb`.
- **Lymphocyte percent.** % (0-100), not a fraction. S6 multiplies its stored fraction by 100.
- **ALP.** S6 multiplies its stored value by 60 to reach U/L. That factor is in S6's own code (comment `µkat/L→U/L`). I did not fetch an independent source for 1 ukat = 60 U, so it is `assessment` only.
- **Glucose, creatinine, albumin.** The coefficients are for mmol/L, umol/L and g/L (S2). Conventional-unit (mg/dL, g/dL) values must be converted first. S8 does not.
- **Gamma rounding.** S2 Table S1 prints 0.0077; the text of S2 p. 2 gives 0.0076927. S3, S4, S5, S6, S8 all use 0.0076927.

### 1.5 Differences found, and which source prevails

| # | Difference | Sources | Size of effect (my computation) | Prevails | Why |
|---|---|---|---|---|---|
| D1 | Intercept -19.9067 vs -19.907 | S2 vs S3/S4/S5/S6/S8 | 0.0003 in `xb`, about 0.003 years | -19.9067 | S2 prints more digits; -19.907 is the same number rounded. Not a conflict |
| D2 | ALP coefficient 0.0019 vs 0.00188 | S1 Table 1 and S2 Table S1 vs S3/S4/S5/S6/S8 | 0.00002 x ALP (80 U/L gives 0.0016 in `xb`, about 0.02 years) | 0.00188 | 0.0019 is 0.00188 rounded to two significant figures; the authors' own later publications (S3, S4) print the unrounded value. The paper's value is consistent with it, so this is a rounding, not a conflict. Default taken, see Q77 |
| D3 | Mortality-to-age constants: `141.50225` and `0.090165` (S2, p. 1 and p. 2) vs `141.50` and `0.09165` (S3, S4, S5 0.6.2+) | S2/S6/S8 vs S3/S4/S5 | At log hazard xb = -12, -9, -6: S2 gives 9.375, 42.647, 75.920 years and S3/S4 give 11.514, 44.247, 76.980 years, a difference of -2.14, -1.60, -1.06 years. These match the "R 4.5.3" figures in S5's own note (9.37497..., 42.6473..., 75.9196...) | **open** (Q77). Default: **S2** | `141.50225` rounds to `141.50`, but `0.090165` does not round to `0.09165` (they differ in the third digit, about 1.6 %): this is a different number, probably a transposed digit in S3 that S4 and pyaging 0.6.2 then repeated. I cannot prove which is the transcription error, because the fit itself was not fetched. Under Fabio's rule the original paper prevails unless an erratum says otherwise. S3 is an erratum, but of the Liu 2018 paper, and Crossref lists none for S1. So the default is S2, and the choice is flagged to Fabio |
| D4 | Gamma 0.0077 (Table S1) vs 0.0076927 (text p. 2) | S2 | negligible if the text value is used | 0.0076927 | Table S1 is a rounding of the text value; all implementations use the text value |
| D5 | Units: conventional units accepted by S8 for albumin (g/dL), creatinine (mg/dL), glucose (mg/dL), CRP (mg/L) but the coefficients are for g/L, umol/L, mmol/L, mg/dL | S8 vs S2 | large: e.g. albumin 4.5 g/dL fed as 4.5 instead of 45 g/L changes `xb` by `0.0336 x 40.5 = 1.36` (my computation) | S2 | Units are part of the coefficient. S8 appears to have no conversion between its validated units and `calculateXb` (lines 81-91). This is an upstream mismatch (see GIVEBACK.md) |
| D6 | Edge handling: S5 floors CRP at 0.01 mg/dL; S6 returns no result for CRP <= 0 or M outside (0, 1); S8 clamps M | S5/S6/S8 | not in the papers | none: not covered by the papers | Our implementation must define one rule and say so (Q77) |
| D7 | S7 biolearn's `PhenoAge` is the DNA-methylation clock; no clinical formula | S7 | n/a | n/a | Do not treat biolearn as a source for these numbers |
| D8 | S5's note that S3 prints a "leading 1" inside the log | S5 vs S3 text | n/a | S3 text as fetched | Not confirmed (see 1.3) |

### 1.6 Verdict for PhenoAge

The ten weights match across S2, S3, S4, S5, S6 and S8 except the ALP rounding (D2) and the constants (D1, D3). The only substantive disagreement is D3, a 1-2 year offset caused by `0.090165` vs `0.09165`. Implementations split on it: S6 and S8 use S2's pair; S5 (current) uses S4's pair. No fetched source settles it, so the choice is raised as Q77.

---

## Part 2. Bortz blood-age clock

### 2.1 Sources

| id | Source | Identifier | Version / commit | Accessed | Fetched how |
|---|---|---|---|---|---|
| B1 | Bortz J, Guariglia A, Klaric L, Tang D, Ward P, Geer M, Chadeau-Hyam M, Vuckovic D, Joshi PK. "Biological age estimation using circulating blood biomarkers." Communications Biology 2023;6:1089 (CC BY 4.0; Humanity Inc and Imperial College London) | DOI 10.1038/s42003-023-05456-z, PMC10603148, https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10603148/fullTextXML (preprint: DOI 10.1101/2023.02.23.23285864) | published 2023-10-26 | 2026-11-26 | Europe PMC JATS XML; the PMC page itself returned a browser-verification page |
| B2 | bortzjd/bloodmarker_BA_estimation: `Data/coefficients_and_means.csv`, `Data/sample_observation.csv`, `BAA_calculation_demo.r`, `README.md` (the repository named in the "Code availability" statement of B1, archived on Zenodo per B1) | https://github.com/bortzjd/bloodmarker_BA_estimation | commit `789db0ec99853a8278bcc5036b5f419de4b96c89` (2023-09-29) | 2026-11-26 | raw.githubusercontent.com at that commit |
| B3 | get-based `js/data-calculated-markers.ts` lines 380-437 | https://github.com/elkimek/get-based | commit `3fba237f89f004cad915fa5c7767aaf9efe1d9d6` | 2026-11-26 | raw.githubusercontent.com |

Not fetched: B1's supplementary tables (Supplementary Table 1 lists the 57 biomarkers; Table 3 the ten panels). The model's own units are not stated in B2 (see 2.3).

### 2.2 What the model is (B1, B2)

- **Model type (B1):** an Elastic-Net penalised Cox proportional-hazards model ("Full ENC") with 25 selected biomarkers, age and sex (age and sex not penalised), trained on UK Biobank (n = 306,116; 18,688 deaths) with England and Wales for training and Scotland for testing. C-index 0.778 (95 % CI 0.767-0.788) versus 0.750 (0.739-0.761) for PhenoAge, as reported in the abstract.
- **Transformations (B1):** "a log-transformation was applied to variables with strong positive skew (alanine aminotransferase, aspartate aminotransferase, gamma glutamyltransferase, C-reactive protein, sex hormone binding globulin (SHBG), testosterone, total bilirubin, triglyceride and vitamin-D)". Of these, the model uses ALT, GGT, CRP, SHBG, vitamin D (the `log_` features in B2). The log base is not stated in the text read or in B2. get-based uses the natural log (B3).
- **Output is an acceleration, not an absolute age (B2 README and R script):** `BAA = 10 x sum((value - featureMean) x BAA_coefficient)` over the features, with `BAA_coefficient = coefficient_ENET - coefficient_SexAge` (sex excluded). Only age has a non-zero null-model coefficient, so the age term is the age coefficient minus the null-model coefficient (values in B2 `Data/coefficients_and_means.csv` at the commit above; not reproduced here, see 2.6). Means are the UK Biobank Scottish test-set means. Biological age is chronological age plus BAA (the B2 script's final comment: "Biological Age of 69.5 vs Chronological age of 68" for the sample, BAA 1.5). My computation reproduces the sample: 1.5317 years from the 26 features of B2.
- **Inputs:** 25 biomarkers plus age. This resolves/narrows Q26 (see 2.5).
- **Code licence statement (B1):** "The code used and resultant models for this project are the intellectual property of Humanity Inc. Model coefficients and R code demonstrating the application of the model can be found in this GitHub repository". GitHub reports no licence for B2 (API `license: null`, 2026-11-26) and the repository tree has no LICENSE file. So the coefficients are published but not under an open software licence. The paper itself is CC BY 4.0.

### 2.3 Coefficients (B2) next to get-based (B3)

The coefficient and mean values are deliberately not reproduced in this document until Q78 (publication licence) is answered; read them in B2 at commit `789db0ec99853a8278bcc5036b5f419de4b96c89`, `Data/coefficients_and_means.csv`. Units are **not stated** in B2. The magnitudes of the means suggest UK Biobank-style SI units (g/L, umol/L, mmol/L, mmol/mol, mg/L for albumin, creatinine, glucose, HbA1c, cystatin C), but this is an inference, not a fetched statement; B1 says only that "Measurement units for biomarkers were the same across both models" (Fig. 3b legend, referring to PhenoAge). Real units: `unknown (not fetched)` until B1's supplementary tables are read.

| feature (B2 name) | in B3 get-based? | log-transformed |
|---|---|---|
| `age` | yes | no |
| `albumin` | yes | no |
| `alkaline_phosphatase` | yes | no |
| `urea` | yes | no |
| `cholesterol` | yes | no |
| `creatinine` | yes | no |
| `cystatin_c` | yes | no |
| `glycated_haemoglobin` | yes | no |
| `log_c_reactive_protein` | yes | yes |
| `log_gamma_glutamyltransf` | yes | yes |
| `red_blood_cell_erythrocyte_count` | yes | no |
| `mean_corpuscular_volume` | yes | no |
| `red_blood_cell_erythrocyte_distribution_width` | yes | no |
| `monocyte_count` | yes | no |
| `neutrophill_count` | yes | no |
| `lymphocyte_percentage` | yes | no |
| `mean_sphered_cell_volume` | no | no |
| `log_alanine_aminotransfe` | yes | yes |
| `log_shbg` | yes | yes |
| `log_vitamin_d` | yes | yes |
| `high_light_scatter_reticulocyte_percentage` | no | no |
| `glucose` | yes | no |
| `platelet_distribution_width` | no | no |
| `mean_corpuscular_haemoglobin` | yes | no |
| `platelet_crit` | no | no |
| `apolipoprotein_a` | yes | no |
| `sexM` | n/a (sex not used in BAA) | no |

### 2.4 Differences found (B2 vs B3 get-based)

| # | Difference | Size (my computation unless noted) | Prevails |
|---|---|---|---|
| E1 | get-based omits four of the 25 biomarkers: mean sphered cell volume, high light scatter reticulocyte percentage, platelet distribution width, plateletcrit. B2 says the example needs "all biomarkers ... required by the Full ENC model" | On the B2 sample observation the four omitted terms sum to -1.617 years of BAA. A get-based-style calculation (22 features, rounded coefficients, caps) of the B2 sample gives about 3.09 years against 1.53 years from B2 | B2 / the paper (25 biomarkers) |
| E2 | get-based rounds coefficients to 3-4 significant figures, visible by comparing B3 with B2 at the commit above (age, ALP, creatinine, monocytes among others) | the age-term rounding alone is of the order of 0.1 year at age 80 (my computation) | B2 (unrounded) |
| E3 | get-based clamps ("caps") 15 inputs to fixed values (e.g. albumin <= 54, cystatin C >= 0.38, vitamin D <= 112.6) | not in B1 or B2 as fetched; get-based attributes them to "longevityworldcup.com", which was not fetched | B2 has no caps; the caps are `unknown (not fetched)` as a source. A cap changes the result for any value outside the cap |
| E4 | get-based labels the paper "Nature Communications" | B1 is Communications Biology (DOI 10.1038/s42003-023-05456-z, Europe PMC `journalTitle`) | B1 |
| E5 | The B2 repository has no licence; B1 declares the code and models Humanity Inc's intellectual property | cannot be used as AGPL-3.0 code | see 2.6, Q78 |
| E6 | B2 means are for the UK Biobank Scottish test set; the formula centres on them. For a different population the B2 script says "the same should be done for the reference population in question" | Means are not universal constants | B2 states it; the product must show Bortz as acceleration relative to the UK Biobank (Scotland) reference unless a reference is chosen |

### 2.5 Q26 (Bortz inputs)

The s01 requirement "Deterministic Bortz clock computation" (openspec/changes/s01-spec-discovery/specs/biomarkers-and-labs/spec.md:27-37) left the inputs open (Q26). From B2 the inputs are the 25 biomarkers of the table above plus age, in the units of the UK Biobank, with five of them log-transformed (CRP, GGT, ALT, SHBG, vitamin D), and the output is BAA relative to the Scottish test-set means. The panel needed is much larger than the nine-marker PhenoAge panel. The units remain open until B1's supplementary tables are read.

### 2.6 Verdict for Bortz

The paper (B1) and the repository (B2) agree on the model description and the sample reproduces (1.53 vs the README's 1.5). get-based's version is a simplified and rounded variant, not a faithful implementation (E1-E3). The coefficients can be cited from B2, but B2 carries no licence, and the paper says the code and models are Humanity Inc's IP. Whether publishing the coefficients in an AGPL-3.0 product is permitted is a question for Fabio (Q78). Until answered: no Bortz numbers enter code.

---

## Part 3. Library assessment (x01)

Licence and activity are from GitHub API and PyPI responses fetched 2026-11-26. "AGPL-compatible" follows the README table in docs/ecosystem/README.md.

| Project | Licence (fetched) | Last activity (fetched) | Stars / state | Has the clinical PhenoAge formula? | Numbers match the papers? | Bortz? |
|---|---|---|---|---|---|---|
| pyaging (https://github.com/lucascamillomd/pyaging) | MIT (GitHub `spdx_id: MIT`; `pyproject.toml` `license = "MIT"`; LICENSE file "MIT License ... Lucas Paulo de Lima Camillo"). PyPI 0.6.3 shows no licence in `info.license` | `pushed_at` 2026-11-22; last commit 2026-11-19; PyPI 0.6.3 uploaded 2026-11-19 | 134 stars, not archived | Yes: `PhenoAge` class (`_models.py` line 1772) plus weights downloaded from Hugging Face | S3/S4 constants (D3), 0.00188 (D2). Differs from S2 by D3. Floors CRP (D6) | No Bortz model found by file-name search |
| biolearn (https://github.com/bio-learn/biolearn) | GitHub `NOASSERTION`; LICENSE file heading "New BSD License"; PyPI "new BSD" | `pushed_at` 2026-07-11; PyPI 0.9.1 uploaded 2026-03-29 | 96 stars, not archived | No clinical formula found; only a unit registry and the DNAm PhenoAge | n/a | No Bortz model found by file-name search |
| get-based (https://github.com/elkimek/get-based) | AGPL-3.0 | `pushed_at` 2026-11-26 | 168 stars, not archived | Yes: JavaScript/TypeScript | S2 constants plus -19.907/0.00188 (mixed, D1-D3); Bortz is simplified (E1-E4) | Yes, simplified |
| mcp-phenoage-clock (https://github.com/199-mcp/mcp-phenoage-clock) | MIT | `pushed_at` 2025-05-31 | 5 stars | Yes (Node/TypeScript) | S2 constants; unit mismatch (D5) | No |
| BioAge (https://github.com/dayoonkwon/BioAge) | GPL-3.0 | `pushed_at` 2026-04-02 | 198 stars | R package that refits PhenoAge on supplied data | original constants not read (see 1.3) | No |
| bortzjd/bloodmarker_BA_estimation | none (`license: null`) | `pushed_at` 2023-09-29 | 18 stars | no (Bortz only) | matches B1 (the sample reproduces) | Yes: the authors' reference coefficients |

Other PhenoAge repositories seen in a GitHub search for "phenoage" on 2026-11-26 (not assessed in depth): fangtiancheng/phenoage (MIT, pushed 2025-07-25), hillarylinmd/phenoage (licence `NOASSERTION`), DPUSystems/PhenoAge (CC0-1.0, pushed 2025-05-16). Their code was not read.

pyaging's dependency list (S5 `pyproject.toml`) includes torch >= 2.2.0, scikit-learn, pandas, numpy, scipy, statsmodels, anndata, huggingface-hub, httpx and rich; requires Python >= 3.11. Its clinical clock's weights are a downloaded artifact (S5 notes: "The corrected Hugging Face artifact ... require pyaging >=0.5.7"), so the result depends on the installed class and on a network download. biolearn's dependency list includes cvxpy, matplotlib, scikit-learn, scipy.

### Recommendation

**Hand-write the clinical PhenoAge computation against the original paper; do not adopt a library as the engine.**

1. **No maintained AGPL-compatible library has the clinical formula with our constants and a small footprint.** pyaging (MIT, active) is the only active candidate that carries the clinical formula, but it is a torch-based compendium of mostly methylation clocks, downloads its weights from a hosting service at runtime, and its current constants differ from the original paper on the one open point (D3). Adopting it would put a very large dependency in front of a ten-term closed formula, and the code would still need the paper check Fabio asked for.
2. **biolearn has no clinical formula; get-based is AGPL but written in TypeScript**, with mixed constants and, for Bortz, a simplified and capped variant. mcp-phenoage-clock has a unit defect. BioAge is R and refits the model.
3. **The formula is ten multiplications, one `exp` and one `ln`**: the maintenance cost of owning it is small, and owning it keeps every constant next to its citation as the FROZEN criteria require. The pyaging unit tests and its documented reference values (log hazard -12, -9, -6) can be reused as cross-checks (they are consistent with my computation for both constant pairs; see D3).
4. **Bortz: do not implement until Q78 is answered.** B2 has no licence and B1 claims the code as IP. If permitted, hand-write it from B2's CSV with the sample observation as the test.

This is a recommendation to the implementer of TG-i; the decision to depend or not is recorded in docs/ecosystem/m02-blood-layer.md and Q77.

### Give-back candidates (proposed only, nothing is posted)

- mcp-phenoage-clock: units accepted (g/dL, mg/dL, mg/dL) do not match the units of the coefficients (g/L, umol/L, mmol/L); D5.
- get-based: Bortz variant omits four of 25 biomarkers, rounds coefficients, caps inputs without a cited source, and names the wrong journal (E1-E4).
- pyaging: its note says the correction S3 prints a leading 1 inside the log; the XML text of S3 has none (D8), and its current constants (D3) differ from the original supplement; the discrepancy could be raised for a maintainer's check.

These are listed in docs/ecosystem/GIVEBACK.md as `proposed`.

---

## Part 4. What the implementer may do next (TG-i)

- Implement PhenoAge by hand, constants in one module, each with a comment naming the table/page of S2 (and S3/S4 where used for a rounding such as D2), units as in S2 Table S1, conversions through the existing `normalize_value`/`Unit` machinery, edge-case rule documented (D6).
- Cross-check with a fixed log-hazard test (xb = -12, -9, -6 against the values in D3) for the constants chosen.
- Bortz stays blocked on Q78.
- Constant choice D3 and rounding D2 follow Q77's default unless Fabio answers otherwise.
