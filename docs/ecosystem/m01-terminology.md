# Ecosystem scan — M01 terminology & reference data (retroactive)

Method, decision categories and licence table: [README.md](README.md). Change: `openspec/changes/m01-terminology-reference-data`. Areas: UCUM, LOINC, OHDSI Athena / OMOP vocabularies, FHIR terminology tooling, open reference-range datasets. Facts were fetched on 2026-11-24 from GitHub API, PyPI, npm and raw licence files; "last activity" is the GitHub `pushed_at` date. Anything that could not be fetched is `unknown`. Where GitHub reported `NOASSERTION` or no licence, the licence file or package registry was used and the entry says so.

Our own assessments (not fetched facts) are marked "assessment". Feed-back into `m01` tasks is listed at the end.

## UCUM

### UCUM specification and essence file
- **URL:** https://github.com/ucum-org/ucum
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-11-09
- **Decision:** reuse schema or dataset
- **Verified:** api.github.com/repos/ucum-org/ucum (pushed_at; licence `NOASSERTION`) and raw.githubusercontent.com/ucum-org/ucum/main/LICENSE.md, 2026-11-24
- **Licence note:** custom "UCUM Copyright Notice and License, Version 1.1, June 2024" (Regenstrief Institute); not an SPDX licence. The repository contains `ucum-essence.xml` (the machine-readable unit table).
- **Provisional:** yes, we take UCUM codes (no code) for the `Unit` table, as M01 TG2 already does; open question Q9 on the UCUM licence terms.

### ucumvert
- **URL:** https://github.com/dalito/ucumvert
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-10
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/dalito/ucumvert and pypi.org/pypi/ucumvert/json (license_expression `MIT`, version 0.3.3 uploaded 2026-11-06, summary "Python parser & interface for UCUM", requires `lark` and `pint>=0.25.0`), 2026-11-24
- **Licence note:** replaces a hand-written UCUM validator (assessment: parsing the UCUM grammar ourselves is the larger risk). Adds `lark` and `pint` as transitive dependencies; their licences must be re-checked when the dependency is added.

### pint
- **URL:** https://github.com/hgrecco/pint
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-15
- **Decision:** learn-from only
- **Verified:** pypi.org/pypi/pint/json (license_expression `BSD-3-Clause`; api.github.com reports `NOASSERTION`) and api.github.com/repos/hgrecco/pint (pushed_at), 2026-11-24
- **Licence note:** general units library, not UCUM. It arrives transitively through ucumvert; we do not call it directly. Assessment: per-analyte mass↔molar conversions need an analyte factor with a source, which a units library does not supply, so `UnitConversion` stays our table.

### ucum-lhc (JavaScript)
- **URL:** https://github.com/LHNCBC/ucum-lhc
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-10-29
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/LHNCBC/ucum-lhc (licence `NOASSERTION`), raw.githubusercontent.com/LHNCBC/ucum-lhc/master/LICENSE.md and registry.npmjs.org/@lhncbc/ucum-lhc (latest 8.0.1 published 2026-10-19, license field "SEE LICENSE IN LICENSE.md"), 2026-11-24
- **Licence note:** BSD-based custom terms with a notice requirement, a citation request and the UCUM licence. Not used until Q9 is answered; M01 has no frontend UCUM validation task today.

## LOINC

### LOINC (release tables and terms of use)
- **URL:** https://loinc.org/license/
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q10)
- **Last activity:** unknown
- **Decision:** reuse schema or dataset
- **Verified:** unknown
- **Licence note:** the licence page returned HTTP 403 to the runner on 2026-11-24, so the terms are not verified here. The M01 proposal (D-LOINC) records Fabio's statement that redistribution is free with notice and unmodified content; that statement is Fabio's, not fetched. The `ucum-lhc` licence file quotes LOINC as "available at no cost under the license at http://loinc.org/terms-of-use".
- **Provisional:** yes, the release zip stays in git-ignored `data/vendor/loinc/` and is user-supplied; nothing from LOINC is committed until Q10 is answered.

### OHDSI Vocabulary-v5.0 (LOINC loader scripts)
- **URL:** https://github.com/OHDSI/Vocabulary-v5.0
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-11-23
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/OHDSI/Vocabulary-v5.0 (licence reported as `Unlicense`; the repository root contains a `LICENSE` file and a `LOINC` directory), 2026-11-24
- **Licence note:** GitHub reports Unlicense, which is not yet in the README licence table, hence `unknown`. Read as a reference for how LOINC releases are staged into OMOP concept tables; no code is copied. The vocabularies it builds carry their own licences.

**Loinc.csv column names (TG-LOINC part A).** Verified on 2026-11-25 from https://raw.githubusercontent.com/OHDSI/Vocabulary-v5.0/master/LOINC/create_source_tables.sql (table `SOURCES.LOINC`; read as a reference only, no code copied) and https://raw.githubusercontent.com/OHDSI/Vocabulary-v5.0/master/LOINC/readme.md, which says that table is loaded from `LoincTable\Loinc.csv`. Columns the importer requires: LOINC_NUM, COMPONENT, PROPERTY, TIME_ASPCT, SYSTEM, SCALE_TYP, METHOD_TYP, CLASS, LONG_COMMON_NAME, SHORTNAME, STATUS. Caveat: this is the OHDSI staging DDL, not a real Loinc.csv header (no release was available to read); an actual release is the final check. Licence note: that file's header says Apache-2.0 while the GitHub API reported Unlicense for the repository.

**Part C1 column names (ConsumerName, LinguisticVariants).** Verified on 2026-11-25 by fetching (read as reference only, no code copied): (1) https://raw.githubusercontent.com/OHDSI/Vocabulary-v5.0/master/LOINC/create_source_tables.sql, table `SOURCES.LOINC_CONSUMER_NAME` with columns LOINCNUMBER, CONSUMERNAME, and https://raw.githubusercontent.com/OHDSI/Vocabulary-v5.0/master/LOINC/load_stage.sql, which loads those into OMOP concept synonyms (English); (2) https://raw.githubusercontent.com/hapifhir/hapi-fhir/master/hapi-fhir-jpaserver-base/src/main/resources/ca/uhn/fhir/jpa/term/loinc/loincupload.properties, which gives the release-relative paths `AccessoryFiles/ConsumerName/ConsumerName.csv` and `AccessoryFiles/LinguisticVariants/LinguisticVariants.csv`; (3) https://raw.githubusercontent.com/hapifhir/hapi-fhir/master/hapi-fhir-jpaserver-base/src/main/java/ca/uhn/fhir/jpa/batch2/jobs/term/loinc/ImportLoincStep20LinguisticVariant.java, whose filename pattern is `<xx><XX><id>LinguisticVariant.csv` in the LinguisticVariants folder; (4) HAPI test fixtures under `hapi-fhir-jpaserver-test-utilities/src/main/resources/loinc-ver/v267/AccessoryFiles/` for the headers: ConsumerName.csv `"LoincNumber","ConsumerName"`; per-language file (zhCN5LinguisticVariant.csv) `LOINC_NUM, COMPONENT, PROPERTY, TIME_ASPCT, SYSTEM, SCALE_TYP, METHOD_TYP, CLASS, SHORTNAME, LONG_COMMON_NAME, RELATEDNAMES2, LinguisticVariantDisplayName`; index file `ID, ISO_LANGUAGE, ISO_COUNTRY, LANGUAGE_NAME, PRODUCER` (not read by the importer: the language comes from the per-language file name). Caveat as in part A: these are a staging DDL and a third-party test fixture, not a real release; the OHDSI readme does not list these two files, so their paths rest on HAPI alone (Q52). Models: `LoincConsumerName` and `LoincLinguisticVariant` keep OMOP CONCEPT_SYNONYM-alignable fields (concept = term, synonym name = consumer_name / display_name, language = the language tag; consumer names carry no language column and are English).

**Part D1 column names (Part, LoincPartLink_Primary).** Verified on 2026-11-25 by fetching (read as reference only, no code copied): (1) https://raw.githubusercontent.com/hapifhir/hapi-fhir/master/hapi-fhir-jpaserver-base/src/main/resources/ca/uhn/fhir/jpa/term/loinc/loincupload.properties, lines `loinc.part.file=AccessoryFiles/PartFile/Part.csv` and `loinc.part.link.primary.file=AccessoryFiles/PartFile/LoincPartLink_Primary.csv` (the supplementary link file and PartRelatedCodeMapping.csv exist too and are not imported); (2) https://raw.githubusercontent.com/hapifhir/hapi-fhir/master/hapi-fhir-jpaserver-test-utilities/src/main/resources/loinc-ver/v267/AccessoryFiles/PartFile/Part.csv, header `"PartNumber","PartTypeName","PartName","PartDisplayName","Status"`; (3) the v268 fixture `.../loinc-ver/v268/AccessoryFiles/PartFile/LoincPartLink_Primary.csv`, header `"LoincNumber","LongCommonName","PartNumber","PartName","PartCodeSystem","PartTypeName","LinkTypeName","Property"` (the v267 fixture has only the first five columns; LinkTypeName and Property first appear in v268; Property values there look like `http://loinc.org/property/COMPONENT`); (4) https://raw.githubusercontent.com/OHDSI/Vocabulary-v5.0/master/LOINC/create_source_tables.sql, tables `SOURCES.LOINC_PART` (PARTNUMBER, PARTTYPENAME, PARTNAME, PARTDISPLAYNAME, STATUS) and `SOURCES.LOINC_PARTLINK_PRIMARY` (LOINCNUMBER, LONGCOMMONNAME, PARTNUMBER, PARTNAME, PARTCODESYSTEM, PARTTYPENAME, LINKTYPENAME, PROPERTY); (5) https://raw.githubusercontent.com/OHDSI/Vocabulary-v5.0/master/LOINC/load_stage.sql: parts become concepts (concept_code = partnumber, concept_name = partdisplayname, vocabulary LOINC, class from parttypename, validity from status) and primary links (linktypename = 'Primary') become CONCEPT_RELATIONSHIP rows loincnumber -> partnumber whose relationship_id comes from the part's type (SYSTEM -> Has system, METHOD -> Has method, PROPERTY -> Has property, TIME -> Has time aspect, COMPONENT -> Has component, SCALE -> Has scale type). Columns the importer reads: Part.csv PartNumber, PartTypeName, PartName, PartDisplayName, Status; LoincPartLink_Primary.csv LoincNumber, PartNumber, LinkTypeName, Property (LongCommonName, PartName, PartCodeSystem, PartTypeName are ignored: they repeat Loinc.csv/Part.csv). Models: `LoincPart` is CONCEPT-alignable (part_number = concept_code, part_display_name = concept_name, part_type_name -> concept_class_id, status -> invalid_reason); `LoincPartLink` is CONCEPT_RELATIONSHIP-alignable (term = concept_1, part = concept_2; the OMOP relationship_id is derived from part.part_type_name, link_type_name and property are kept as given). Parts are upserted by part_number and never deleted; links of the release's terms missing from a present link file are deleted. Caveat as before: fixtures, not a real release (Q53).

No Python loader package for LOINC releases was verified: a PyPI lookup for the package name `loinc` returned HTTP 404 on 2026-11-24 and no other candidate was found. This is a "no verified candidate found" result for loaders; `import_loinc` (TG-LOINC) is our own importer, kept thin and aligned to the OMOP concept layout.

## OHDSI Athena / OMOP vocabularies

### OMOP CDM (DDL and documentation)
- **URL:** https://github.com/OHDSI/CommonDataModel
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-10-28
- **Decision:** reuse schema or dataset
- **Verified:** api.github.com/repos/OHDSI/CommonDataModel (pushed_at; no licence detected) and raw.githubusercontent.com/OHDSI/CommonDataModel/main/DESCRIPTION (`License: Apache License 2.0`), 2026-11-24
- **Licence note:** GitHub detects no licence and the repository root has no LICENSE file; the R package `DESCRIPTION` states Apache License 2.0. Weaker evidence than a licence file; a LICENSE-file check is a give-back item.

### OHDSI Athena (vocabulary download service)
- **URL:** https://athena.ohdsi.org/
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-09-02
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/OHDSI/Athena (pushed_at for the application repo; no licence detected, no LICENSE file in the root), 2026-11-24
- **Licence note:** the vocabulary files themselves carry per-vocabulary licences; the Athena page fetched gave no licence information. Vocabularies would be bring-your-own downloads, like LOINC.

## FHIR terminology tooling

### HAPI FHIR
- **URL:** https://github.com/hapifhir/hapi-fhir
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-11-24
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/hapifhir/hapi-fhir, 2026-11-24
- **Licence note:** a Java server. Assessment: running a JVM terminology server for a lookup table of tens of thousands of rows is more overhead than M01 needs; revisit when FHIR export (module on interoperability) needs `$lookup`/`$translate`. Read for the CodeSystem / ValueSet / ConceptMap shapes only.

### Snowstorm
- **URL:** https://github.com/IHTSDO/snowstorm
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-11-24
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/IHTSDO/snowstorm (pushed_at; licence `NOASSERTION`) and raw.githubusercontent.com/IHTSDO/snowstorm/master/LICENSE.md (Apache License, Version 2.0 text), 2026-11-24
- **Licence note:** a SNOMED CT terminology server; the server code is Apache-2.0, SNOMED content is separately licensed (see TG-SNOMED). Relevant to the bring-your-own-SNOMED importer as a reference for RF2 handling only.

### fhir.resources
- **URL:** https://github.com/nazrulworld/fhir.resources
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q9)
- **Last activity:** 2026-09-14
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/nazrulworld/fhir.resources (licence `NOASSERTION`), raw.githubusercontent.com/nazrulworld/fhir.resources/main/LICENSE and pypi.org/pypi/fhir.resources/json (version 8.3.0 uploaded 2026-07-03, classifier "BSD License"), 2026-11-24
- **Licence note:** the file is a BSD licence with the 2018 "AS IS" disclaimer; the number of clauses (2 or 3) was not determined, so no SPDX id is claimed. Pydantic FHIR models; the choice of FHIR library belongs to the integration scan (`x01-ecosystem-reuse` tasks), not M01.

## Open reference-range datasets

### NHANES (CDC / NCHS)
- **URL:** https://www.cdc.gov/nchs/nhanes/about/index.html
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q11)
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** cdc.gov/nchs/nhanes/about (page fetched; it says the data files are "publicly available to download and analyze" and states no licence), 2026-11-24
- **Licence note:** US population laboratory survey data. Not a published reference-interval set. Any range derived from it would be our own analysis under research programme R1, with the method recorded; no range is imported in M01.

No other open reference-range dataset with a stated licence was found and verified in this scan. This is a "no verified candidate found" result, recorded as Q11 in docs/QUESTIONS.md; M01 therefore keeps D2/D-OPTIMAL (structure and provenance gate, no seeded ranges).

## Decisions fed back into M01 tasks

| Decision | M01 task changed |
|---|---|
| Adopt ucumvert for UCUM validation instead of a custom parser | TG5 (UCUM validation of seed rows and `services.resolve_unit`) |
| Align `Unit`/`Source` columns and the LOINC tables with OMOP `CONCEPT`/`VOCABULARY` vocabulary where it fits | TG5, TG-LOINC |
| LOINC and Athena content stay user-supplied until Q9/Q10 are answered | TG5, TG-LOINC |
| No open reference-range dataset: ranges stay structure-only | TG4 |
| Snowstorm/HAPI read as references only | TG-SNOMED |
