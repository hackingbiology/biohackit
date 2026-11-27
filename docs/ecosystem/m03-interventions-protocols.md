# Ecosystem scan — M03 Interventions catalog and protocols

Method, decision categories and licence table: [README.md](README.md). Capabilities: `interventions-and-catalog` and `protocols` (`openspec/specs/*/spec.md`; no OpenSpec change for M03 exists yet, this scan precedes it). Areas: (a) substance identifiers and codes, (b) multilingual name resolution, (c) standard models for interventions and protocols, (d) Evipedia MCP, (e) queued resumable jobs, (f) protocol versioning and diff, (g) get-based components. Facts were fetched on 2026-11-27. "Last activity" is the GitHub `pushed_at` date. Our own assessments (not fetched facts) are marked "assessment". No dependency is added by this scan.

**About the `Verified` field.** `backend/tests/test_ecosystem_docs.py` accepts a source host only from a fixed list (GitHub API, PyPI, npm, raw.githubusercontent.com, gnu.org, cdc.gov). An official page on another host (nlm.nih.gov, hl7.org, who.int, pubchem.ncbi.nlm.nih.gov, wikidata.org) therefore cannot be written in `Verified` for an entry that has no GitHub or PyPI source. For those entries `Verified` is the literal `unknown` and the page that was actually fetched, with its date and what it said, is in the `Licence note` (same practice as the LOINC entry in m01-terminology.md). Question Q107 asks whether the check should accept official pages.

## (a) Substance identifiers and codes

### RxNorm and the RxNav API (NLM)
- **URL:** https://www.nlm.nih.gov/research/umls/rxnorm/docs/termsofservice.html
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q105)
- **Last activity:** unknown
- **Decision:** reuse schema or dataset
- **Verified:** unknown
- **Licence note:** fetched 2026-11-27 from the terms-of-service page above: "A free UMLS license is required to download the full RxNorm monthly and weekly releases"; RxNorm names and codes are described as public domain; "Public domain information may be freely distributed and copied within and outside the U.S."; republishers must keep data current or say it may not reflect the latest NLM data; "The full RxNorm dataset includes proprietary data from various terminology providers", each with a Source Restriction Level. Fetched 2026-11-27 from https://lhncbc.nlm.nih.gov/RxNav/TermsofService.html: "With one exception, no license is needed to use these APIs", free of charge, "no more than 20 requests per second per IP address" (100 with a UTS API key), the RxNorm API gives "non-proprietary content from RxNorm", and the SNOMED CT limit applies to RxClass, not to the RxNorm API. An NLM attribution sentence is asked for and the NLM name and logo may not be used. Which exact bulk data may be committed to git is not settled by those pages (Q105).
- **Provisional:** yes, we store only the RxCUI code string with source and fetch date, obtained by API call at seed time; no RxNorm release file and no proprietary-source term is committed until Q105 is answered.

### WHO ATC classification and DDD (WHO Collaborating Centre, Oslo)
- **URL:** https://atcddd.fhi.no/copyright_disclaimer/
- **Licence:** unknown
- **AGPL-compatible:** no — the page says copying and distribution for commercial purposes and changing the material are not allowed; treated as not usable for redistribution until Q106 is answered
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** unknown
- **Licence note:** fetched 2026-11-27 from the URL above: "Use of all or parts of the material requires reference to the WHO Collaborating Centre for Drug Statistics Methodology"; "Copying and distribution for commercial purposes is not allowed"; "Changing or manipulating the material is not allowed". No fee or permission process was found on that page. The WHO page https://www.who.int/tools/atc-ddd-toolkit/atc-classification returned no licence text to the fetch (only the link labels "Permissions and licensing" and "Terms of use"), so the WHO terms are unknown. Assessment: the ATC tree and DDD tables are not copied; a single ATC code string may be stored next to a substance only where a cited seed source (for example Evipedia, an RxNorm class lookup) gives it, with the source recorded.
- **Provisional:** yes, ATC codes are not stored from a WHO file until Q106 is answered.

### PubChem and PUG REST (NCBI/NLM)
- **URL:** https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q105)
- **Last activity:** unknown
- **Decision:** reuse schema or dataset
- **Verified:** unknown
- **Licence note:** the PubChem documentation pages (pug-rest, programmatic-access) returned only their titles to the fetch on 2026-11-27, so usage limits and licence text of PubChem itself are unknown here. A live request to `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/sirolimus/cids/JSON` returned HTTP 200 with an `x-throttling-control` header (2026-11-27), so the endpoint form works and is throttled. Fetched 2026-11-27 from https://www.ncbi.nlm.nih.gov/home/about/policies/: "NCBI itself places no restrictions on the use or distribution of the data", but "some submitters of the original data... may claim patent, copyright, or other intellectual property rights"; PubChem is listed among resources with contributed or licensed material, and reusers "are expected to adhere to the terms and conditions asserted by the copyright holder".
- **Provisional:** yes, we store only the compound id (CID) with source and fetch date; no synonym list, description or depositor text from PubChem is committed until Q105 is answered.

### GSRS (NCATS Global Substance Registration System code)
- **URL:** https://github.com/ncats/gsrs-spring-starter
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q105)
- **Last activity:** 2026-11-12
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/ncats/gsrs-spring-starter (`license: null`) and raw.githubusercontent.com/ncats/gsrs-spring-starter/master/LICENSE (HTTP 404), 2026-11-27
- **Licence note:** GitHub detects no licence and no LICENSE file was found on the `master` branch. The FDA UNII pages tried on 2026-11-27 (https://www.fda.gov/industry/structured-product-labeling-resources/unique-ingredient-identifier-unii and `.../unique-ingredient-identifiers-unii`) returned HTTP 404, and https://gsrs.ncats.nih.gov/ returned only the text "gsrs"; the terms of the UNII data are therefore unknown. A UNII code is a required identifier in the spec; we use it only where a cited source gives it.

## (b) Multilingual substance-name resolution

### Wikidata (labels and aliases in several languages)
- **URL:** https://www.wikidata.org/wiki/Wikidata:Licensing
- **Licence:** CC0-1.0
- **AGPL-compatible:** yes (CC0)
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** unknown
- **Licence note:** fetched 2026-11-27 from the URL above: data in the main, Property, Lexeme and EntitySchema namespaces is "released into the public domain under Creative Commons Zero". The licence value is taken from that page; no GitHub or PyPI source applies. Assessment: Italian and Chinese names of a substance could be proposed from Wikidata aliases, but each alias would need review and a stored item id as provenance, and wrong-entity matches are possible (an alias shared by two items). Not adopted before the spec's `ambiguous` flow exists; kept as a candidate source for the review queue.

### RapidFuzz
- **URL:** https://github.com/rapidfuzz/RapidFuzz
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-26
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/rapidfuzz/RapidFuzz and pypi.org/pypi/rapidfuzz/json (license_expression `MIT`, version 3.14.6), 2026-11-27
- **Licence note:** assessment: the scenario "Italian input resolves" is an exact lookup in a synonym table, and the spec forbids matching to the wrong entity, so fuzzy scoring is at most a way to propose a candidate to the review queue, never to resolve. The PostgreSQL `pg_trgm` module does the same inside the database (its documentation was fetched 2026-11-27 at https://www.postgresql.org/docs/current/pgtrgm.html: trigram similarity with index support, shipped as a supplied module); its licence was not fetched (GitHub reports `NOASSERTION` for postgres/postgres), so it is not an entry here.

## (c) Standard models for interventions and protocols

### HL7 FHIR R4 (MedicationStatement, MedicationRequest, PlanDefinition, CarePlan)
- **URL:** https://github.com/HL7/fhir
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q55)
- **Last activity:** 2026-11-25
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/HL7/fhir (licence `NOASSERTION`) and the pages https://hl7.org/fhir/R4/medicationstatement.html, medicationrequest.html, plandefinition.html, careplan.html and license.html, 2026-11-27
- **Licence note:** same open question as the m02 scan (Q55), not re-decided. The FHIR licence page (https://hl7.org/fhir/R4/license.html, 2026-11-27) says "This document is licensed under Creative Commons 'No Rights Reserved'", "You can redistribute FHIR", and does not grant rights over third-party terminologies; that page covers the specification text, and the repository's own LICENSE says the source has several licences (m02 scan), so the verdict is left to Q55. Read facts: MedicationStatement is Maturity Level 3, "Trial Use", records what is actually taken (including non-prescription use), `medication[x]` and `status` are required, `effective[x]`, `dosage`, `reasonCode`, `basedOn` optional. MedicationRequest is Maturity Level 3 and is an order (`intent` required), its scope names diet and vitamin supplements. PlanDefinition is Maturity Level 2, "Trial Use", a "pre-defined group of actions", with `version`, `status` (draft, active, retired, unknown), `action`, `goal`, `relatedAction`, `timing[x]`. CarePlan is Maturity Level 2, with `status`, `intent`, `activity`, `period`, `instantiatesCanonical`. Assessment: MedicationStatement fits "what a user takes" and PlanDefinition fits a protocol template (with `version`), CarePlan a user's running instance; each is an export mapping target, not a storage schema. Each page was read only in part (the first 100,000 characters of the text; the rest was not read).

### OMOP CDM DRUG_EXPOSURE
- **URL:** https://github.com/OHDSI/CommonDataModel
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-10-28
- **Decision:** reuse schema or dataset
- **Verified:** api.github.com/repos/OHDSI/CommonDataModel (licence null, as in m01), raw.githubusercontent.com/OHDSI/CommonDataModel/main/DESCRIPTION (`License: Apache License 2.0`) and https://ohdsi.github.io/CommonDataModel/cdm54.html#drug_exposure, 2026-11-27
- **Licence note:** the licence is from the R package `DESCRIPTION`, as in m01 and m02. The CDM v5.4 page describes DRUG_EXPOSURE as "records about the exposure to a Drug ingested or otherwise introduced into the body", with fields including `drug_concept_id`, `drug_exposure_start_date`/`_datetime`, `drug_exposure_end_date`/`_datetime`, `drug_type_concept_id`, `stop_reason`, `quantity`, `days_supply`, `sig`, `route_concept_id`, `drug_source_value`, `drug_source_concept_id`, `route_source_value` and `dose_unit_source_value` (marked as an older column to be deprecated). Assessment: alignment target for the export of tracked interventions, following docs/omop/measurement-mapping.md; concept ids need the OHDSI vocabularies (Athena, see m01-terminology.md) and stay null until those are loaded.

## (d) Evipedia MCP

### evipedia-mcp
- **URL:** https://github.com/forever-healthy/evipedia-mcp
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-09-09
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/forever-healthy/evipedia-mcp, 2026-11-27 (tool list from raw.githubusercontent.com/forever-healthy/evipedia-mcp/main/README.md, 2026-11-24, see integrations.md)
- **Licence note:** licence and activity re-fetched today; the README was not re-read today. The server code is MIT, but the licence of the evipedia.ai content is unknown (Q15, and the give-back row of 2026-11-24). The spec requirement "Seed and enrich the catalog from Evipedia" states CC BY 4.0 for Evipedia content; that statement is from our spec and was not verified against evipedia.ai in this scan. Whether Evipedia exposes interventions and alternate names through the MCP tools (the spec says the synonym table is seeded from them) was not checked: the tools named in integrations.md are about reviews (`search_reviews`, `get_conclusion`, `get_metadata`), and no intervention or alias tool is listed there.
- **Provisional:** yes, until Q15 is answered and an alias source is confirmed; the M03 change must say how the synonym table is seeded if Evipedia offers no alias tool.

## (e) Queued, resumable extraction jobs

### Celery
- **URL:** https://github.com/celery/celery
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-26
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/celery/celery (licence `NOASSERTION`) and pypi.org/pypi/celery/json (license field `BSD-3-Clause`, version 5.7.0, summary "Distributed Task Queue."), 2026-11-27
- **Licence note:** the licence comes from PyPI because GitHub reported `NOASSERTION`. Assessment: it needs a separate broker, which the project does not run today.

### django-q2
- **URL:** https://github.com/django-q2/django-q2
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-16
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/django-q2/django-q2 and pypi.org/pypi/django-q2/json (license_expression `MIT`, version 1.11.1, summary "A multiprocessing distributed task queue for Django"), 2026-11-27
- **Licence note:** GitHub marks this repository as a fork of Koed00/django-q; the PyPI project URL points to GDay/django-q2, a different owner path than the repository fetched. The release and package ownership was not resolved here.

### Procrastinate
- **URL:** https://github.com/procrastinate-org/procrastinate
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-25
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/procrastinate-org/procrastinate and pypi.org/pypi/procrastinate/json (classifier "MIT License", version 3.12.0, summary "Postgres-based distributed task processing library", requires Python >=3.11), 2026-11-27
- **Licence note:** assessment: it uses the PostgreSQL we already run, so no extra broker. Its job-locking and retry behaviour, its Django integration, and whether it works with Django 5 under `Django>=5.0,<6.0` in `backend/pyproject.toml`, were not read; the M03 change must check them against "Job survives a timeout" and idempotent re-run before choosing. Nothing is adopted by this scan.

## (f) Protocol versioning and diff

### django-simple-history
- **URL:** https://github.com/django-commons/django-simple-history
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-01
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/django-commons/django-simple-history and pypi.org/pypi/django-simple-history/json (classifiers "BSD License", "Framework :: Django :: 5.2" and "6.0", version 3.13.0, summary "Store model history and view/revert changes from admin site."), 2026-11-27
- **Licence note:** assessment: it stores one history row per save of a model, which does not by itself give "a dose change is a tracked event" bound to a protocol version; the diff of two versions is a separate step. Learn the pattern; M03 decides whether a model of protocol versions is simpler than a library.

### django-reversion
- **URL:** https://github.com/etianen/django-reversion
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-12
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/etianen/django-reversion and pypi.org/pypi/django-reversion/json (classifiers "BSD License", "Framework :: Django :: 5.2", "6.0", "6.1", version 6.5.2, summary "An extension to the Django web framework that provides version control for model instances."), 2026-11-27
- **Licence note:** assessment: it versions a group of related objects as one revision, which resembles a protocol with its items. How it stores revisions and how it diffs them was not read.

### django-pghistory
- **URL:** https://github.com/AmbitionEng/django-pghistory
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-02-17
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/AmbitionEng/django-pghistory and pypi.org/pypi/django-pghistory/json (classifiers "BSD License", "Framework :: Django :: 5.2", version 3.9.2, summary "History tracking for Django and Postgres"), 2026-11-27
- **Licence note:** assessment: it records history in PostgreSQL, which matches our database; its interaction with TimescaleDB hypertables was not checked. Its last push is the oldest of the three.

## (g) get-based components for supplements and interventions

### get-based supplement model and mitochondrial evidence catalogue
- **URL:** https://github.com/elkimek/get-based
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-27
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/elkimek/get-based (licence `AGPL-3.0`, pushed 2026-11-27T07:49:39Z) and raw.githubusercontent.com/elkimek/get-based at commit 002c3e1e8d256854102eefe51833bca75adda1a6, 2026-11-27
- **Licence note:** read at the commit pinned in getbased-archive-format.md. `types/supplement-data.d.ts` (lines 1-68): a `SupplementRecord` with `name`, `type`, `dosage`, `startDate`, `endDate`, `periods[]` (each with `start`, `end`, `endReason`, `dose`, `ingredientDoses`, `schedule`), `schedule` (`mode`, `timesPerDay`, `daysOfWeek`, `intervalDays`), `lifecycle`, `ingredients[]`, `qualityTests[]`, `sourceUrl`, `importProvenance`. No RxNorm, ATC, PubChem or UNII field exists there, so get-based does not resolve substances to external codes in that type. `js/supplement-medication-domain.ts` has `SUPPLEMENT_RECORD_VERSION = 2` and a unit list (mg, mcg, g, mL, IU, CFU, %, mmol, mEq, units, capsule, tablet, drop, scoop, spray, patch) with aliases (line 34-60). `js/supplement-import-draft.ts` builds a "Validated, review-before-apply extraction draft" (line 1) with `fieldSources` and `source.reviewed`. `data/mito-compounds.json` is a list of 30 items: a `_meta` item (schemaVersion 2, verifiedOn 2026-08-09, an inclusion rule that every statement must be directly supported by its cited primary study) and compounds with `name`, `aliases`, `category`, `evidence[]` (each with `pmid`, `title`, `direction`, `studyType`, `model`, `exposure`, `limitations`); the first compound read is sertraline with aliases `sertraline`, `zoloft`, `lustral`. Assessment: the dosing periods and the review-before-apply draft are patterns to learn; the alias list is brand-to-generic only, with no Italian or Chinese names found in the item read, and it is not a code-resolved catalogue. No code or data is imported. The other 25 supplement files, and the full alias coverage of the 29 compounds, were not read.

## Decisions for the M03 OpenSpec change

No dependency is added in this task. The M03 change cites this scan and takes these decisions as input; each library is re-checked there against the scenarios.

- **(a) Codes:** reuse identifiers only (RxCUI through the RxNav API, PubChem CID through PUG REST), stored as code strings with source and fetch date, Provisional until Q105. ATC and UNII: learn-from only, no WHO or FDA file stored (Q105, Q106). No bulk release is committed.
- **(b) Multilingual resolution:** exact lookup in our own synonym table, with a source and reviewer per synonym; Wikidata and RapidFuzz are learn-from only candidate sources for the review queue, never for silent resolution.
- **(c) Models:** FHIR MedicationStatement / PlanDefinition / CarePlan and OMOP DRUG_EXPOSURE are export mapping targets. FHIR is learn-from only until Q55; OMOP DDL is reuse schema.
- **(d) Evipedia:** learn-from only; store review IDs and PMIDs, not review text, until Q15. The M03 change must say where synonyms come from if the MCP has no alias tool.
- **(e) Queue:** no library adopted; Procrastinate (PostgreSQL-based, MIT) is the first candidate to evaluate because it needs no new broker, Celery and django-q2 are learn-from only.
- **(f) Versioning and diff:** no library adopted; compare a plain protocol-version model with django-simple-history, django-reversion and django-pghistory in the M03 change. Diff of two versions can use the standard-library `difflib` (assessment; not fetched).
- **(g) get-based:** learn-from only (period and schedule model, review-before-apply draft, evidence record with a PMID); nothing imported.
