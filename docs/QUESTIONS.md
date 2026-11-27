# Questions for Fabio

Format: date · module · question · default taken (work continues with the default).

---

## 2026-11-25 · m00c B1 next upgrade

**Q33** · After upgrading `next` to 15.5.29, `pnpm audit --prod` still reports `postcss` 8.4.31 (bundled inside `next`; GHSA-6g55-p6wh-862q and GHSA-r28c-9q8g-f849, high, patched >=8.5.12 and >=8.5.18). Default taken: **B1 only fixes `next`; B2 adds a pnpm override for `postcss` to a patched version, with no waiver.** Please confirm the override approach. **Applied in B2: override `postcss` `>=8.5.23 <9` (covers the two moderate advisories too).**

## 2026-11-24 · s01 spec discovery C

**Q25** · getbased trend alerts use thresholds on slope and R² plus jump detection (getbased analysis § A4) but the document gives no values. Default taken: **the requirement fixes no threshold or minimum point count**; they are declared in code with their rationale at implementation. Please set them if you have a view.

**Q26** · The calculated markers and the Bortz clock (getbased analysis § A3) are named without formulas or inputs. Default taken: **the requirements name the markers only**; formulas and inputs are taken from the published method, cited with provenance at implementation, never recalled. Please confirm the list of markers wanted.

**Q27** · The password-protected sharing link (getbased analysis § B8) has no stated lifetime. Default taken: **the requirement only says the link expires and is revocable**; no default duration is chosen. Please say how long a link should live.

**Q28** · getbased offers six AI providers, local models and in-browser DNA parsing (analysis § 1, § A6, § B9) and asks whether biohack.it has a local-first mode (their Q28). Default taken: **provider-agnostic requirement with a local option; no provider is named; no local-first storage mode is specified**. Please decide on the local-first mode.

**Q29** · The deck (slide 13) lists "produce dosing algorithms proposal" as an AI use, which conflicts with the requirement that the platform describes and never prescribes. Default taken: **not specified; the never-prescribes rule stands**. Please say whether any dosing proposal is wanted and how it would be framed. The same slide also says AI evaluates safety profiles and biomarkers and optimises scheduling: default taken: **safety and biomarker values and scheduling stay deterministic (rules and a constraint solver); AI only writes words about them**. Please confirm.

**Q30** · Cycle-phase ranges (getbased analysis § A1) are named for four hormones but no values or phase definitions are given. Default taken: **the requirement fixes no values; each range comes with its source via the range governance**. Please confirm phase-dependent ranges are wanted.

**Q31** · How many wrong passwords on a sharing link (Q27) before it is delayed or locked? The source gives none. Default taken: **the requirement says attempts are throttled without a number**. Please set the limit.

**Q32** · User-supplied AI endpoints (getbased analysis § B9): may the server ever call them? Default taken: **calls are made from the user's browser only; a server-side call needs a later requirement (private, loopback, link-local refused, HTTPS required)**. Please confirm.

## 2026-11-24 · s01 spec discovery B

**Q18** · The project spec wants protocol cost shown (§ 6 M4bis) but does not say where prices come from or in what currency. Default taken: **the requirement only says each price shows who entered it**; no price source, catalogue or currency is chosen. Please say where prices should come from.

**Q19** · The project spec wants a monthly LLM credit allowance (§ 8.5bis) with "a generous balance" but gives no amounts; the 3 and 10 credits it quotes are MyAgingTests' values. Default taken: **the requirement fixes no amount**. Please set the allowance and the regeneration day.

**Q20** · The project spec has the system "generate the request for the laboratory" (§ 4.1 C) without a format. Default taken: **the requirement fixes no format** (printable page); no laboratory is named. Please say which format labs accept.

**Q21** · Erasure (§ 7) conflicts with a clonable public snapshot (whitepaper § 11): copies already cloned cannot be recalled. Default taken: **delete from the instance and later snapshots, and tell the user plainly that clones are out of reach**. Please confirm this is acceptable under your reading of GDPR art. 9.

**Q22** · Reminders (§ 4.2) name no channel. Default taken: **channel-agnostic requirement**; in-app first when built. Please say whether e-mail or push is wanted.

**Q23** · The project spec says a policy on "what is not publishable" is needed (§ 7) but not its content. Default taken: **the requirement only says the policy is published and enforced**; no categories chosen. Please say what must be excluded.

**Q24** · The whitepaper promises "open and linked data" (§ 11) without a serialisation. Default taken: **the requirement names no format**; implementation will pick a standard RDF or JSON-LD form during the data-export task and record it as an ADR, reversible. Please name a preferred format if you have one.

## 2026-11-24 · s01 spec discovery A

**Q16** · The Foundation text says content and the public dataset are under "open licenses" without naming them. Default taken: **the requirement only says a licence is declared per artefact**; no licence is chosen. Please name the licences (code is AGPL-3.0).

**Q17** · The whitepaper names three quality layers (deterministic validation, community review, expert oversight) but not who the experts are or how they flag. Default taken: **the requirement only says the mechanism exists**, no roles defined. Please say who counts as an expert.

## 2026-11-09 · M00 Foundations

**Q1** · Should OAuth social login (GitHub, Google) be live from day one, or stubbed and enabled later?  
Default taken: **stubbed** — OAuth provider secrets would need to be in CI and dev env from day one; enabling live OAuth in M13 Hardening is cleaner. Reverse if you want OAuth active earlier.

**Q2** · Email-only accounts (no visible username), or email + chosen display name used as the public handle?  
Default taken: **email-primary auth, display name as public handle** — `User.email` is the auth credential, `Profile.display_name` is the public-facing slug. Reverse if you want a separate username field.

**Q3** · Docker Compose for local development, or should the README document bare-metal PostgreSQL + local Python instead?  
Default taken: **Docker Compose** — reproducible for contributors; devs who prefer bare-metal can ignore it. Reverse if you want Docker optional-only.

**Q4** · `Measurement` hypertable: set up the TimescaleDB hypertable in M00 migrations now (empty), or defer until M02 Blood Layer when data first arrives?  
Default taken: **set up in M00** — avoids a painful later migration that may need to convert an existing table; the hypertable is empty until M02. Reverse if you prefer to defer.
- 2026-11-19 · login: DiscourseConnect provider on rapamycin.news needs the forum admin to enable it and share a secret; OAuth apps (Google, Microsoft, Apple, Meta, WeChat) must be created by Fabio — see openspec/changes/m00b-low-friction-login/tasks.md
- 2026-11-22 · runner: `pnpm`, `jest` and `node_modules/.bin/*` need approval in this session, so frontend tests/lint/tsc could not be run; `frontend/src/__tests__/auth.test.ts` is written but unverified. Please allow `pnpm --dir frontend test:ci|lint|type-check` or run them once.
- 2026-11-23 · runner: `pnpm` is still blocked, but frontend checks run via `node -e "process.chdir('frontend');process.argv=[...];require('/abs/path/node_modules/<tool>')"` (jest needs `-i`): jest 11 green, tsc clean, eslint clean. `gh run list` is not allowed, so CI on GitHub cannot be verified by the runner — Fabio: please confirm CI on main is green; then M00 can be archived.

## 2026-11-24 · X01 M01 terminology scan

**Q9** · Licence terms not in the README AGPL table and not grounded in a fetched source: the UCUM licence v1.1 (ucum-org/ucum, and the BSD-based terms of ucum-lhc), the Unlicense (OHDSI Vocabulary-v5.0), OHDSI Athena vocabulary licences, and the `fhir.resources` BSD variant. Default taken: **marked `unknown`**; UCUM codes stay as already seeded in M01 TG2 (provisional), Athena/OHDSI vocabularies are bring-your-own and not committed, ucum-lhc and fhir.resources are not used. Please confirm, or point to the terms.
**Q10** · LOINC redistribution terms: https://loinc.org/license/ returned HTTP 403 to the runner, so the terms in M01 D-LOINC (free redistribution with notice, unmodified) are Fabio's statement, not verified. Default taken: **the release stays user-supplied in git-ignored `data/vendor/loinc/`, nothing from LOINC is committed**, and the licence notice is stored with the `Source`. Please confirm that the full LOINC table may be redistributed in exports and where to copy the notice text from.
**Q11** · No open reference-range dataset with a stated licence was found. Default taken: **no ranges imported**; ranges come only with a citation under research programme R1. If you know of one (licence stated), please name it.

## 2026-11-24 · X01 ecosystem scan

**Q8** · AGPL-3.0 compatibility could not be grounded in the fetched GNU list for: GPL-3.0, CC-BY-SA, the PostgreSQL licence, and the Timescale License (`tsl/` directory of TimescaleDB). Default taken: **marked `unknown`** in docs/ecosystem/; PostgreSQL and TimescaleDB run as separate server processes. Please confirm or point to a source.

**Q12** · The licence gate admits MIT-0, by per-version override only (used by `cffi`, a backend dependency) although the GNU licence list does not name it; the basis is that the fetched cffi LICENSE is the MIT grant without the attribution condition. `caniuse-lite` (CC-BY-4.0, browser-support data used by the frontend build chain) is accepted only through a documented override, since CC-BY is "data/docs only" in the README table. Default taken: **both accepted**; GPL-3.0 and CC-BY-SA stay `unknown` and fail the gate (see Q8). Please confirm or tell me to drop them.

## 2026-11-24 · X01 integration anchor scan

**Q14** · Discourse is GPL-2.0 (fetched LICENSE.txt: GNU GPL Version 2, June 1991), which is not in the README AGPL table. Default taken: **verdict unknown, learn-from only**; we talk to a forum only over its HTTP API and import no Discourse code. Please confirm that API use alone raises no licence concern, or tell us otherwise.

**Q15** · The licence of the evipedia.ai review content (as returned by evipedia-mcp) was not fetched; only the MCP server code is MIT. Default taken: **store only the review URL/ID and PubMed PMIDs, never review text**, until the content licence is confirmed. Please confirm the content terms or tell us what may be stored.

## 2026-11-23 · M01 Terminology & reference data

**Q5** · Bundle a small curated LOINC subset (standard panel) under the LOINC licence notice, full table user-supplied? Default taken: **yes, subset only**.
**Q6** · Optimal ranges: no citation can be verified by the runner, so none are seeded. Default taken: **structure + provenance gate only**; please supply or approve sourced optimal ranges.
**Q7** · SNOMED: Default taken: **not bundled** (licence); field reserved.

**Answers (Fabio 2026-11-24):**
- **Q5:** yes, and the full, most detailed LOINC is wanted (see m01 D-LOINC). Fabio will provide the release zip.
- **Q6:** optimal ranges become research programme R1 (ROADMAP). Only structure and gate in M01.
- **Q7:** explained to Fabio. Bundle GPS where the licence allows, support bring-your-own SNOMED, cross-refs only.
- **Login:** OAuth and DiscourseConnect credentials are deferred by Fabio; nothing more to ask for now.
- **uv.lock stale for django-allauth extras:** uv.lock metadata has `[mfa]` and `>=0.61`; pyproject has `[mfa,socialaccount]>=65.0`. Fabio/admin to run `uv lock` in backend/ when convenient (default: leave as is until the admin session regenerates).
- **Staging demo data:** default = demo account only (`DEMO_USERNAME` as sign-in e-mail, `DEMO_PASSWORD`), no health values until M01 seed_reference and sourced data exist; please confirm or provide demo content.
- **Q13 (licence gate, fido2 2.2.1):** package classifiers list BSD, Apache-2.0 and MPL-2.0, but upstream COPYING (fetched) is only the 2-clause BSD text and names no Apache/MPL files. Default: override records BSD-2-Clause only. Please confirm whether any bundled part is Apache/MPL (all are AGPL-compatible).

## 2026-11-25 · M00c spec discovery D2a

**Q35** · docs/analysis/competitive-landscape.html (Feature matrix) ticks "Causal inference" for biohack.it, but `scientific-method-and-evidence/Observed, never caused` forbids causal phrasing on every surface. Default taken: **the cell is treated as out-of-scope and no causal-inference requirement is added**. Please confirm whether the column means future causal-analysis methods or should read "no" for biohack.it.

**Q36** · docs/analysis/competitive-landscape.html (Where biohack.it sits) says raw lab reports sit behind heightened consent, but `biomarkers-and-labs/Original report file retained and public raw` makes them public by default with no consent step. Default taken: **row is out-of-scope and no requirement is added; the existing spec stands**. Please confirm whether raw lab reports need a heightened-consent gate (then an ADDED requirement follows).

## 2026-11-25 · M00c spec discovery D2b1

**Q38** · docs/reference/hb-protocol-structure.xlsx has unclear semantics in five places: Pharmacy column H "Presc" (header only, no values), Sheet10 column B "Chi" (a person per substance), the Targets sheet (one cell of molecular targets), the Rapamycin sheet (a customs note), and the Pharmacy "mg/kg" cells (C35, C43, C47, B165) with no human or animal provenance. Default taken: **those rows are out-of-scope or gated, nothing is invented**: no per-person assignment, no prescription flag, no target or travel feature is specified, and any per-weight value is accepted only with a posology provenance tag (`interventions-and-catalog/Weight-relative posology is gated on posology provenance`), so no absolute dose is ever computed from an untagged or animal-derived value. Please say what "Presc" and "Chi" mean if you want them specified.

**Q37** · docs/proposal-critique.html (What I need from you) asks six things; none is a requirement, so a default is taken for each. (1) Distributed trials: default = keep the word and publish the bar, as `scientific-method-and-evidence/Qualification bar for a distributed trial` already states. (2) Hero copy: default = not applied; site copy untouched until approved. (3) GitHub table: default = not applied on site or slide. (4) Genomics public by default: default = decision kept; the added requirement `analytics-and-open-data/Public-by-default reasoning and opt-out are stated publicly` only publishes the reasoning. (5) Advisory board (one board, scientific and clinical-safety seats, names): default = no requirement; it is a Foundation governance decision and names are unknown. (6) MVP ring-fence of four and the three flagship protocol topics: default = roadmap order unchanged and no flagship topic seeded until confirmed. Please answer or amend.

## 2026-11-25 · M00c spec discovery D2b3

**Q39** · docs/foundation.html (Resolved & still open) lists three open items that no requirement covers: the data-hosting jurisdiction for EU/GDPR users, the first board members, and the grant programmes to target. None is software behaviour. Default taken: **no requirement, no code change**; the register rows are `out-of-scope`, and the About page states only what the source states (Foundation steward, mission lock). Please tell me if the hosting jurisdiction should become a deployment requirement once chosen.

## 2026-11-25 · M00c shared frontend/node_modules

**Q34** · Task worktrees symlink `frontend/node_modules` to the shared install, so deleting a worktree or running pnpm inside one breaks the shared links (MODULE_NOT_FOUND). `make_worktree` in `tools/autodev2/orchestrator.py` is out of reach for agents. Options: **A (default)** run `pnpm --dir frontend install --frozen-lockfile --offline --node-linker=hoisted` in each worktree instead of symlinking; **B** keep the symlink and run `pnpm install --node-linker=hoisted` at the root after every merge that changes `frontend/package.json` or `pnpm-lock.yaml`; **C** upgrade the `packageManager` pin to pnpm 10 and set `nodeLinker` in `pnpm-workspace.yaml`, as a separate task with its own staging check. Caveat: `pnpm help install` on pnpm 9.15.9 does not list `--node-linker` (0 matches), so whether the CLI flag works there is **unverified**; test A or B in a scratch directory before adopting. Please pick one.

## 2026-11-25 · M00c semgrep rules licence

**Q40** · The Semgrep Registry rules behind `p/django` and `p/typescript` are under the Semgrep Rules License v1.0 (internal business purposes only; no distribution, no service use). Our gate only runs them in CI and never ships them, but whether that counts as "internal business purposes" for an open-source project is **unverified**. Default taken: **keep the gate**. Alternative if you object: drop the registry rules and use the LGPL semgrep engine with our own rules. Please decide.

## 2026-11-25 · M00c mypy strict scope

**Q41** · The mypy gate is strict only for `backend/terminology` (the newest app, M01). `core` and `accounts` have untyped functions and model-override errors and are not checked. Default taken: **strict on new apps only**; add a path to `tools/mypy/strict_apps.txt` to widen. Should `core` and `accounts` become strict later, and when?

## 2026-11-25 · M00c mutation-testing scope

**Q42** · The mutmut gate mutates only the unit-conversion code, `backend/terminology/services.py` (no statistics module exists yet). Default taken: **any survivor not listed with a written reason in `tools/mutmut/accepted_survivors.txt` fails the gate**; one equivalent mutant is accepted today. Statistics modules should be added to `tools/mutmut/targets.txt` (with their test files) in the same task that creates them. Do you want the same strictness for them, or a minimum kill ratio?

## 2026-11-25 · M00c AI surfaces map

**Q43** · The map has no row for the attribution register (spec scenario "Public trust artifact"), and every row except unit conversion is `specified` (no code yet). Default taken: **the register stays out of this page**; the map covers only the AI vs deterministic scenario. Should the attribution register be shown on the same page? Also, "Index" and "Calculated markers" cite biomarkers-and-labs requirements because no dedicated "index" requirement exists; tell me if a better one should be cited.

## 2026-11-25 · M00c AI surfaces map: extraction conflict

**Q44** · `biomarkers-and-labs/spec.md` ("Deterministic pipeline with a hard boundary") says extraction is deterministic and the LLM only writes narration, while `ai-uses-and-attribution/spec.md` lists lab-report extraction as an AI surface and "Import from PDF, photo, and CSV with learned templates" says known labs bypass the LLM. Default taken: **the map lists extraction as AI, used only when no learned template matches, with the user confirming values**. Should the hard-boundary requirement be amended to match?

## 2026-11-25 · M00c changelog

**Q46** · The changelog is written by hand and the export never reads `git log`, so later commits cannot break the sync test; a test checks that every cited commit and OpenSpec change exists. It is English only; IT and ZH fall back to EN. Default taken: **hand-written, cited commits verified by test, EN only**. Should it be generated from git instead, and should it be translated?

## 2026-11-25 · M01 TG3 coded analyte registry

**Q47** · LOINC codes are only checked for being non-empty and unique; there is no check-digit validator because no verified algorithm or source for it is cited in the repo. Default taken: **no check-digit validation**. Should one be added, and from which authoritative source (LOINC publishes a mod-10 rule, which we have not fetched or verified)?

**Q48** · Legacy `core.Biomarker` rows without a LOINC code cannot be coded without inventing data. Default taken: **migrations `core/0003-0005` (fields, data, constraints; split so Postgres has no pending trigger events) fail loudly naming the row ids and never fill codes; the Source is never inferred: on a non-empty table the operator must set `BIOHACK_LEGACY_BIOMARKER_SOURCE` to the exact name of one stored `terminology.Source`**. Fresh and staging databases have no such rows. If production ever has them, should the operator fix the data by hand, or should we ship a reviewed mapping file?

## 2026-11-25 · M01 TG4 part A ranges

**Q49** · The evidence-grade vocabulary for `OptimalRange` is not defined, and several complete optimal rows may exist for one analyte (different populations or endpoints). Default taken: **`evidence_grade` is free text naming the grading system used by the cited source (no scale invented); `displayable_optimal_range()` returns the most specific complete row that applies to the subject (TG-STRATA) and None when two or more tie at the highest specificity; it never picks one**. Which grading scale(s) should be allowed, and how should one be chosen among several complete rows (stratification is TG-STRATA)?

## 2026-11-25 · M01 TG-STRATA

**Q50** · Ancestry has no controlled vocabulary (`Profile.ethnicity` is free text, backend/accounts/models.py:60), so a range row's `ancestry` is matched against the subject exactly after strip() and casefold(). Default taken: **free text, exact match**. Which vocabulary should be used for ancestry (none is proposed or invented here)?

## 2026-11-25 · M00c user guide

**Q45** · The user guide is English only; IT and ZH fall back to EN as on /docs/architecture. The `/dashboard` page that sign-in redirects to does not exist yet, so the guide lists it under "Coming later". Default taken: **EN only, no translation yet**. Should the guide be translated to IT/ZH now, and should the sign-in redirect point somewhere that exists until the dashboard is built?

## 2026-11-25 · M01 LOINC search hardening

**Q51** · The LOINC search is rate-limited per user with a DRF scoped throttle (`loinc_search`) and queries are capped at 200 characters. Neither value comes from a cited source; both are operational limits that can be configured (LOINC_SEARCH_THROTTLE_RATE). Default taken: **60/min, 200 characters**. Are these limits right for staging and production, and should the throttle use a shared cache (Redis) instead of the per-process local-memory cache?

## 2026-11-25 · M01 LOINC consumer names and linguistic variants (part C1)

**Q52** · The ConsumerName and LinguisticVariants file paths and headers were verified only from the HAPI FHIR loader config and its test fixtures, and the OHDSI staging DDL for ConsumerName; no real LOINC release was read, and the it-IT file's numeric id in its file name is unknown (the importer matches any id). Also, ConsumerName may hold several names per LOINC code, so rows are unique per (term, consumer_name) rather than per term. Default taken: **import what was verified (ConsumerName; it-IT and zh-CN variants), other languages skipped, everything else not imported**. Please check the headers against a real release when one is available, and say whether a term may have several consumer names.

**Q53** · The Part and LoincPartLink_Primary paths and headers were verified only from HAPI FHIR (loader config, v267/v268 test fixtures) and the OHDSI staging DDL; no real LOINC release was read. The v267 fixture lacks LinkTypeName/Property, which the v268 fixture and OHDSI DDL have, so the importer requires them (an older release file without them aborts with "missing column"). Default taken: **import Part.csv and LoincPartLink_Primary.csv with the verified columns; Panels&Forms, AnswerList and the supplementary links are not imported**. Please check the headers against a real release when one is available.

**Q54** · The header of PanelsAndForms.csv was not seen in any fetched source (HAPI has no panel key; its fixture under PanelsAndForms/ is a copy of Loinc.csv). Only the OHDSI staging DDL names (PARENTLOINC, LOINC, LSEQUENCE) are verified, and they are used case-insensitively. Default taken: **PanelsAndForms.csv is NOT imported (no model, no fixture) until a real header is verified**. Please check the header against a real release and tell us the actual names if they differ.

**Q55** · Two M02 scan candidates have a licence that cannot be fixed to an SPDX id: the HL7 FHIR specification repository (GitHub `NOASSERTION`; its LICENSE file says the source is under multiple licences and the specification itself under a different one) and biolearn ("new BSD" on PyPI, clause count unknown). Default taken: **both stay learn-from only, nothing is imported from either**; DiagnosticReport/Observation are written by hand against the spec. Please say whether the FHIR specification's licence allows us to ship profiles or value sets derived from it.

## 2026-11-26 · M02 Blood Layer change

**Q56** · PhenoAge coefficients are not stored anywhere in the repo. Default taken: **coefficients are taken from the original paper only and entered with a citation; pyaging, biolearn and get-based are not a source of numbers**. May that be the rule, and which paper edition is authoritative?

**Q57** · How long is the original uploaded report file retained? Default taken: **kept until the user deletes it or erases the account**. Should there be a fixed limit?

**Q58** · Is PII redaction on by default at import? The main spec ("Optional PII obfuscation on import") says the original is retained raw unless the user opts in. Default taken: **off by default (as the spec says); the user may opt in and sees a diff of what was removed**. What is retained after opt-in (raw or redacted) is left undecided. Should redaction be on or mandatory instead? That would need a MODIFIED requirement.

**Q59** · Where does the import code live? Default taken: **results stay in `backend/core` next to `Measurement`; import and redaction code go in a new Django app named in TG-a**. Is a separate app preferred?

**Q60** · The M02 module issue number could not be verified (`gh` was not permitted to the implementer). Default taken: **"Module issue: unknown" in the proposal**. What is the right issue number?

**Q61** · `core.Measurement.save` rejects a unit with no conversion, but lab imports must keep such results as reported. Default taken: **`LabResult` is a separate model that accepts unconvertible units and leaves the normalised value empty**. Or should `Measurement` be relaxed instead?

**Q62** · The main spec makes the raw original report public by default, while PII redaction is off by default, so names and IDs could be published. Default taken: **the original stays private until the user explicitly publishes it; TG-g stores privately only**. Should the main spec be changed with a MODIFIED requirement?

**Q63** · domain-model "Measurement provenance" names a validation state but neither it nor the code defines its values. Default taken (a default, not a decision): **`unreviewed` | `reviewed`**. Which states do you want?

**Q64** · s01 puts body composition and microbiome results in the same time series model as blood analytes, but Q61 makes `LabResult` separate from `core.Measurement`. Default taken: **DEXA and microbiome lab results are stored as `LabResult` (the lab time series); `core.Measurement` stays for self-tracked values; a later MODIFIED requirement unifies them if you prefer**. Outcome: s01 "Result without provenance" (ask before storing) applies to DEXA and microbiome `LabResult`s; the stored-and-flagged rule applies to blood analytes only.

**Q65** · Should rolling back an import also delete the retained original report file? Default taken: **yes, rollback removes the file stored with that `LabReport`, so no uploaded document (possibly with PII) is left behind**. Should the file instead be kept with a notice to the user?

**Q66** · How is an analyte classed as blood, body composition (DEXA) or microbiome? Not defined anywhere yet. Default taken: **TG-a adds an explicit category on the analyte (or the `LabResult`), set only from a cited source or by the user, never guessed; an uncategorised analyte is treated as blood, so its result is stored and flagged and nothing is silently dropped**.

Q66 implementation note: `Biomarker.category` (blood | body_composition | microbiome) plus `Biomarker.category_source` (FK `terminology.Source`) are set together or both empty; NULL = uncategorised = blood; no analyte is categorised by a migration.

**Q68** · The s01 requirement text says DEXA/microbiome provenance is "laboratory or device, method, date". May a device stand in for the laboratory? Default taken: **no, laboratory and method are both required, as in the M02 delta; `device` alone does not satisfy the rule**.

**Q67** · Does a `LabResult` inherit `LabReport.laboratory`? Default taken: **yes, only when the result has none and the report states one; never invented. `reported_unit_ref` is set only on an exact `Unit.ucum_code` match, and a unit not stored, or with no stored factor, leaves the normalised pair empty**. Should the result require its own laboratory instead?

**Q69** · OMOP MEASUREMENT `*_concept_id` columns need OMOP vocabulary content (Athena) that is not in the repo. Default taken: **left empty until OMOP vocabularies are imported with provenance; LOINC and the reported unit go to the `*_source_value` columns. `person_id` and `measurement_type_concept_id` are likewise left empty by the mapper (TG-j fills them from a cited source)**.

**Q70** · What does "out-of-range" mean for a manually typed value (main "Manual entry of equal standing")? Default taken: **the value is compared only with stored, cited `terminology.ReferenceRange` rows of that analyte in the same unit (reported unit, or the normalised unit when a stored conversion exists); `within` or `outside` is returned with the range Source, and `not_checked` when no comparable range is stored. Only unstratified rows are used (age, sex and ancestry are not supplied, so none is guessed); a row with a population, or with a lab or method that differs from the result's (case-insensitive), counts as stratified and is ignored; more than one candidate also gives `not_checked`. It flags and never rejects; no range is invented or seeded**. Input bounds (abuse protection, open for Fabio to change): `reported_value` at most **40 characters**, at most **200 results** per report.

**Q71** · How does the CSV lab import work (M02 TG-c part 1)? Defaults taken: **UTF-8, comma-separated, header columns `loinc_code,value,unit,collected_at,reported_at,laboratory,method` (the first three required, the last four optional, any order; unknown or duplicate columns reject the file with a 400 naming the header). A row is `recognised` only if `loinc_code` exactly matches a stored `Biomarker.loinc_code` and the shared `LabResult.save` rules accept it (value exact, unit non-empty, ISO 8601 times with UTC offset); otherwise `not_recognised` with a reason naming the column. Nothing is guessed (no name matching, no unit inference); `inferred` is never emitted by this parser. Confirm re-parses the same file, refuses with 400 listing the rows while any is `not_recognised`, otherwise stores one `LabReport(origin=import, import_name=file name)` with results as `validation_state=reviewed` (the user confirmed the preview, Q63). Only `origin=import` reports can be rolled back (`DELETE /api/labs/reports/<id>/`); a manual report gives 409 because typed data is not an import. Bounds (open for Fabio to change, like Q70): file at most 1 MiB, at most 200 data rows, each field at most its model length (value 40 characters), non-UTF-8 rejected with a 400**. Should a manual report be deletable as well?

**Q72** · Which text does opt-in PII redaction remove (M02 TG-d part 1)? Default taken: **only exact, case-insensitive matches of terms the user supplies (at most 20, 1..200 characters); no built-in PII patterns (codice fiscale, phone, email, ...) and no NER until a verified rule source is recorded; Presidio stays learn-from only. Redaction runs per cell on data rows, the file name and the report `laboratory`; the header is untouched; a hit in `loinc_code`, `value`, `unit`, `collected_at` or `reported_at` makes the row `not_recognised` instead of changing it**. What is retained of the original file after opt-in is still Q58/TG-g.

**Q73** · How is a stored lab report represented in FHIR (M02 TG-j part 1)? Defaults taken: **a `collection` Bundle with one DiagnosticReport, one Observation per result and one Organization (name only) per distinct laboratory, referenced from `Observation.performer`; the method is `Observation.method.text`. FHIR requires `status` (and `code` on the DiagnosticReport) but nothing stored says either, so `status` is `unknown` (a code in both R4 value sets) and the DiagnosticReport `code` is only the text "Laboratory report", no coding; no patient `subject` is emitted. Nothing else is invented**. Should the laboratory instead be a coded identifier, and should `status` be derived from `validation_state`?

**Q74** · Can pdfplumber be added for M02 TG-e part 1? Blocked 2026-11-26: the implementer sandbox refused `uv add --project backend pdfplumber` (approval requested, none given), so the package and its transitive licences could not be fetched or locked; the rule is to stop rather than add an unverified dependency. Default taken: **nothing added; no PDF code, route or test written; TG-e stays unchecked**. Please run `uv add pdfplumber` in backend/ (or allow it for the implementer), then re-run TG-e part 1.

**Answers (Fabio 2026-11-26):**
- **Q56, biological-age clocks: a research task, not a single rule.**
  - **Compare sources:** compare the PhenoAge coefficients and constants across every source: the original Levine 2018 paper with its supplement, later errata, biolearn, pyaging, get-based and other maintained implementations.
  - **Document differences:** record every difference in values, units or transformations in `docs/research/phenoage-coefficients.md`, with a citation for each source.
  - **Bortz:** add the Bortz blood age clock (Bortz et al.) with the same analysis.
  - **Library preference:** if a well-maintained, AGPL-compatible library implements these clocks, adopt it as the computation engine, following the x01 ecosystem rule. Its numbers must still be checked against the papers; a mismatch is documented and the paper prevails, unless an erratum says otherwise.
  - **Numbers in code:** no numbers enter the code without that comparison.
- **Q57, retention of the original report:** it is kept while the user wants the data available for research purposes. When closing the account, the user may choose to **leave their data public for research**. Account erasure must therefore offer a choice: delete everything, or keep the de-identified data and reports public for research. This links to the consent model in M12 / analytics-and-open-data.
- **Q58:** OK. Redaction is off by default, opt-in, and the user sees a diff before confirming.
- **Q63, measurement validation states:** Fabio asked what the states mean. Proposed richer set, to be used as the default unless he says otherwise:
  - `entered`: typed or imported, not yet checked;
  - `user_confirmed`: the user checked it against their own report;
  - `source_verified`: the original document is attached and the value matches it, checked by deterministic extraction or by a second person;
  - `disputed`: flagged as possibly wrong;
  - `retracted`: withdrawn by the user and excluded from statistics, but kept for audit.
  
  Aggregations and public statistics use only `user_confirmed` and above.
- **Q65:** OK. Rollback also deletes the retained original file.

**Q75** · Q63 states applied (M02, 2026-11-26). Three points Fabio's answer left open, with the defaults taken (defaults, not decisions): (1) a **confirmed CSV/PDF import is stored as `user_confirmed`**, because the user checks every row in the preview against their own report before confirming; a typed entry is stored as `entered`. (2) The owner endpoint `PATCH /api/labs/results/<id>/validation/` lets the owner set `user_confirmed`, `disputed` or `retracted`; **`source_verified` cannot be self-declared** (it needs an attached original and a deterministic or second-person check, which do not exist yet), and `entered` cannot be set back. (3) **A retracted result stays retracted** (audit default); a disputed one can be confirmed again. Is that right, or should a user be able to un-retract?

**Q76** · Is the original CSV kept when the user opted into redaction (M02 TG-g part 1)? Default taken: **no. With `redact_terms` the three `original_*` fields stay empty and the confirm response says `original_retained: false` with a reason, because keeping the raw bytes would defeat the redaction the user asked for (Q58, Q72 left this open). Without redaction the original is kept with no automatic expiry (Q57), in a private store that no route serves, under a generated name (the report id), and is deleted when the import is rolled back (Q65)**. Should redaction instead produce a redacted copy of the original to retain?

**Q77** · Q56 applied (M02, 2026-11-26): the research is in `docs/research/phenoage-coefficients.md` (PhenoAge and Bortz, every value cited to a page fetched that day). Result: **no library is adopted as the engine** (pyaging has the formula but needs torch and a runtime weight download and uses different constants; biolearn has only the DNA-methylation clock; get-based is TypeScript; one other implementation has a unit defect); recommendation is to hand-write PhenoAge against the paper in TG-i, as the original Q56 default said. Two choices the answer's rule ("paper prevails unless an erratum says otherwise") does not settle, with the defaults taken (defaults, not decisions): (1) **mortality-to-age constants**: the original supplement prints `141.50225` and `0.090165`; a 2019 correction (of a different paper, Liu 2018) and Kuo 2021 print `141.50` and `0.09165`; they differ by about 1 to 2 years of PhenoAge. Default: **the original supplement's pair**, because no erratum of the Levine 2018 paper was found (Crossref and Europe PMC, 2026-11-26). Is that right, or does the 2019 correction count as the erratum? (2) **rounded values**: the paper prints ALP `0.0019` and intercept `-19.9067`; the authors' later papers print `0.00188` and `-19.907`. Default: **use `0.00188` and `-19.9067`** (more digits of the same numbers), and state it. Also: should TG-i add a PhenoAge result only when all nine markers are present (no imputation, CRP at or below 0 gives no result)? Default: yes.

**Q79** · PhenoAge from stored results (M02 TG-i part 2, 2026-11-26). Defaults taken (defaults, not decisions): (1) **age is a request parameter** (`age_years`) because no birth date is stored; (2) **only one report is used**, not the latest value per analyte across reports; (3) **disputed and retracted results are excluded; entered results are allowed** for a personal view (aggregation is a different rule); (4) **the result is not stored**. **Blocker:** every fetch of `https://loinc.org/<code>/` (WebFetch and curl on the analyte pages) returned HTTP 403 on 2026-11-26, so no LOINC code could be verified and none was written: `LOINC_BY_FIELD` in `backend/core/phenoage_binding.py` is empty and the API refuses every request with `analyte_not_mapped`. Can you name a fetchable LOINC source, or give the verified code for each of the nine analytes? Tests use synthetic test-only codes.

**Q78** · Bortz blood-age clock (M02, Q56): the authors' coefficients are in `github.com/bortzjd/bloodmarker_BA_estimation`, which has no licence, and the paper (Commun Biol 2023, CC BY 4.0) says the code and models are the intellectual property of Humanity Inc. Its output is an acceleration relative to the UK Biobank (Scotland) means, from 25 biomarkers plus age, with the units still unread (the paper's supplementary tables were not fetched). Default taken: **no Bortz number enters code; the s01 "Deterministic Bortz clock computation" requirement stays unimplemented**. May we use the published coefficients with a citation, may we ask the authors for permission, or should the Bortz clock be dropped? (This narrows Q26: the inputs are known now, see the research document, part 2.)

**Q80** · Which results does the OMOP export include? (M02 TG-j part 2, 2026-11-26.) Default taken (a default, not a decision): all results of the report except retracted ones; disputed and entered are included, because the export is the owner's own data, not an aggregation. Should only aggregation-eligible results be exported instead? Also: JSON only, no CSV file yet.

**Q81** · Unit conversion view (M02 TG-l part 1, 2026-11-26). Defaults taken (defaults, not decisions): (1) **"view in SI" is implemented as "view in a UCUM unit the user names"** (`GET /api/labs/results/<id>/convert/?unit=`), because no stored, cited classification marks a unit as SI or US conventional, and none is invented; (2) **only direct stored conversions are used**, never an inverse (1/factor) or a chain; (3) **retracted results remain viewable by their owner** (personal view, not an aggregation). Should we add a sourced SI/conventional flag on `terminology.Unit` (and from which source) so a `?unit_system=si` option can follow?

**Q82** · Result against its three ranges (M02 TG-m part 1, 2026-11-26). Defaults taken (defaults, not decisions): (1) the **subject is unknown** (`Subject()`), so only unstratified rows apply, until a profile stores age/sex/ancestry (Q79); (2) a **reference range is matched by laboratory and method** (each empty or equal, trimmed and casefolded), with generic rows as a fallback and a tie giving no range; (3) **bounds are inclusive** (a value equal to low or high is `inside`); (4) **several safety thresholds give no range** (`ambiguous_several_thresholds`), none is picked. May a reference range from a different laboratory ever be applied to a result?

**Q83** · Calculated ratio markers (M02 TG-n part 1, 2026-11-26). Defaults taken (defaults, not decisions): (1) **ratio definitions are stored rows with a cited Source and none is seeded**, because Q26 requires each formula and unit convention from a cited published method and loinc.org is unreachable (Q79). Can you give the source of each ratio you want (TG/HDL, LDL/HDL, ApoB/ApoA-I, NLR, PLR, De Ritis, hs-CRP/HDL, BUN/creatinine) and the unit convention it uses (e.g. TG/HDL in mg/dL or mmol/L)? (2) **inputs come from one report only**; (3) **disputed and retracted inputs are excluded**; (4) **the result is not stored**; (5) **HOMA-IR and free water deficit wait for a later part** (constants or extra terms).

**Q84** · Completeness and freshness per organ system (M02 TG-h part 1, 2026-11-26). Defaults taken (defaults, not decisions): (1) **organ-system panels are stored rows with a cited Source and none is seeded.** Which source should define the organ systems and their expected markers (e.g. the docs/specs dashboard grouping, or a lab panel standard)? (2) **results count across all of the user's reports**; (3) **disputed and retracted results are excluded** (as Q79/Q83); (4) **freshness uses `collected_at`, else `reported_at`**; a result with neither counts as present but gives no date; (5) **sparse means any expected marker is missing**, no threshold; (6) the sentence "Metabolic: 6/13, last updated 4 months ago" and the sparse-index annotation on dashboards are a later frontend part; the API gives numbers only.

**Q85** · Account erasure (S01 Personal data erasure, part 1; Q57 applied 2026-11-26). Defaults taken (defaults, not decisions): (1) **the keep-for-research option is offered but refused** (409, "de-identification not implemented yet") until M12 de-identification exists; nothing is deleted when it is chosen; (2) **public snapshots do not exist yet**, so "removed from later public snapshots" holds because the rows are gone; (3) **erasure is immediate, with no grace period** and needs `confirm: true`; (4) **no shared or delegated data exists yet**; when it does, it must be listed in the notice. Is a grace period wanted?

**Q86** · Lab import page (M02 TG-o part 1, 2026-11-26). Defaults taken (defaults, not decisions): (1) **the API accepts the browser session cookie in addition to JWT** (`SessionAuthentication` after JWT, CSRF enforced, nothing exempted); anonymous requests still get 401 because JWT is listed first; (2) **the page sends no `redact_terms` in part 1** (the library function supports it); (3) **IT and ZH fall back to EN**: are translations wanted now? (4) the page uses a plain browser `confirm` dialog before undo.

**Q87** · Manual entry and report pages (M02 TG-o part 2, 2026-11-26). Defaults taken (defaults, not decisions): (1) **date inputs are read as the browser's local time** and sent with the browser's UTC offset at that date; (2) **a result row needs LOINC code, value and unit**, checked in the browser before sending, the backend still decides everything else; (3) **the report page shows 'Not given' for empty fields and for a missing normalised value**; (4) the report page shows no analyte name because the API payload has none; (5) the changelog row cites the previous commit 98bb613 because the part 2 commit does not exist yet when the row is written.

**Q88** · Three ranges on the report page (M02 TG-m part 2, 2026-11-26). Defaults taken (defaults, not decisions): (1) **one `/ranges/` request per result**, no batch endpoint, because a backend change is out of scope; (2) **ranges of retracted results are not hidden** on the report page (the owner can view them, as in Q81); (3) **EN only**, IT and ZH fall back to EN (Q86). Is a batch endpoint or a per-analyte history page wanted next?

**Q75** · LingSante (change ai02) — Fabio 2026-11-26: "put it in the requirements to evaluate its use, study it well, it can be a political choice" → governance + behavioural audit + positioning analysis added; the decision stays with Fabio. Runtime: A hosted API (fast, data leaves our servers, consent and de-identification required), B GPU rented on demand for evaluation, C self-hosted hardware. Default taken: **none yet**; build the provider-agnostic interface and evaluation harness first.

**Q89** · Validation controls on the report page (M02 TG-o part 3, 2026-11-26). Defaults taken (defaults, not decisions): (1) the withdraw warning reads "Withdraw this result? It is kept for audit, no longer counts in statistics and cannot be restored." (2) controls are shown on every result, including those without a laboratory or method (confirming one still leaves it not counted in aggregations, as the API decides). (3) "Confirm" is offered on a disputed result (Q75 point 3). (4) after an update focus moves to that result's state line, because the pressed button may disappear. (5) the browser's own confirm dialog is used, as for Undo (Q86). (6) the changelog row cites 5636c1f, the latest m02-blood-layer commit on main: 8cb249f carries the trailer x01-ecosystem-reuse, and the changelog test requires the cited change to match a commit trailer; a commit of this branch is not yet an ancestor of main.

**Q90** · Withdrawn results on imported reports (M02 TG-o part 3 review, 2026-11-27). Default taken (a default, not a decision): backend `DELETE` of an imported report removes its withdrawn results too (backend/core/views.py:283-294), so on imported reports the warning and label say retention lasts only while the report exists; manual reports keep "kept for audit". Should rolling back an import with withdrawn results return 409 (backend follow-up)? Also: a pressed button now uses `aria-disabled` plus an early return while a request is pending, and errors are announced with `role="alert"`.

**Q91** · Marker mapping for the get-based archive importer (X01 part 1, 2026-11-27). get-based marker keys are its own dot keys (`lipids.cholesterol`), with no LOINC or other code in the files read (docs/ecosystem/getbased-archive-format.md). Default taken (a default, not a decision): **the importer matches only through a stored mapping table with a cited source per row, and none is seeded**; with an empty table every marker is "not recognised" and confirm is refused. loinc.org returns 403 (Q79), so no code can be verified here. Where should the mapping come from: a table written by hand and cited, a mapping agreed with the get-based maintainer (see GIVEBACK), or another fetchable LOINC source?

**Q92** · AI-read rows (X01 part 1, revised after review). `importedWith` is on the entry (a sample date), not on the marker, and each later import overwrites it (docs/ecosystem/getbased-archive-format.md). Defaults taken (a default, not a decision), **fail closed**: **every row is stored `entered`, never `user_confirmed`, until the user confirms that result, and is flagged, unless `importedWith` positively shows a non-AI path**. So a row with an import origin (`snapshotId` or `file`) is flagged "read by an AI model" when `importedWith` is present and "may have been read by an AI model" when it is absent; a row with no `markerSources` is flagged "origin unknown". The model and provider are stored and shown as entry-level provenance, qualified "last import into this date; the model for this value is unknown". **No bulk confirm** of flagged rows: each is confirmed one by one. May flagged rows be bulk-confirmed after one acknowledgement? Unknown: whether non-AI imports (spreadsheets) leave `importedWith` absent or with nulls, so no row can today be proven non-AI and in practice every row is flagged; what shape `importedWith` takes on a non-AI path is open.

**Q93** · Units from get-based (X01 part 1). Entries hold a number per marker and no unit; the unit is the get-based catalogue's canonical unit for the marker, and the file carries no catalogue version (docs/ecosystem/getbased-archive-format.md). Default taken: **the unit is a column of the stored, cited mapping row (Q91), not read from the archive**, so a catalogue change in get-based cannot silently change a unit. Default taken (a default, not a decision): **for measured rows (those with a Biomarker; deny-list rows carry no unit and are exempt) the unit column cites the get-based catalogue file at a pinned commit (`js/marker-schema/<group>.ts@<sha>`); a measured row with no cited unit is shown "not recognised: unit not verified" and blocks confirm** (scenario "Mapping row cites the get-based catalogue unit"). Still open: how should a mapping row be versioned against get-based releases?

**Q94** · Calculated and reported values (X01 part 1, revised after review). Defaults taken: **a marker with `derivedFrom` is never stored** and is shown as "not imported: calculated, not measured"; it is **excluded from the confirm refusal** (otherwise an archive holding HOMA-IR could never be imported), and the preview counts such rows. No per-row "leave out" action is added for other not recognised rows (confirm stays refused for them, as in Q71). `reported: true` (seen only for `diabetes.homaIR`) does not override `derivedFrom` if both are present; a marker with `reported` and no `derivedFrom` is imported as measured. Should a value printed on the report but also calculable (HOMA-IR) be imported? Should a per-row "leave out" be offered for unmatched rows? Whether other markers carry `derivedFrom` or `reported` is unknown.

**Q95** · Which get-based containers to read first (X01 part 1). Defaults taken: **the single-client export (`version: 2`) and the all-clients bundle (`type: 'database'`) first; the planned migration archive (PR #1719, unmerged, may change) after it is merged and released**; the full browser backup `labcharts-backup` is out of scope (raw stored values, possibly in-app encrypted). For the migration archive the decrypted `local` store holds the lab data under `labcharts-<profileId>-imported`, possibly encrypted a second time with the app passphrase; whether to ask for that passphrase is open (default: ask for nothing beyond the migration password; **an archive whose decrypted lab store is in the `v1:` form is refused with a plain message that it is still locked with the get-based passphrase, and nothing is stored**, a SHALL scenario of the spec).

**Q96** · Format version handling and undo (X01 part 1). get-based checks `version` only in some paths (the single-client export is not version-checked in the lines read; the migration envelope accepts only `version: 1` and `iterations: 600000`). Default taken: **accept exactly the versions listed in the format document (export/bundle `version: 2`; migration envelope and content `version: 1`) and reject anything else, a missing `version` included, with a plain message naming the version found and those supported**. Undo (default): deleting the import's report removes its results, as for the CSV import (Q71); withdrawn results go with it (Q90).

**Q97** · Deleted markers (X01 part 1 review, 2026-11-27). `entries[].deletedMarkers` is a tombstone map (docs/ecosystem/getbased-archive-format.md). Default taken (a default, not a decision): **a marker listed there is shown "not imported: deleted in get-based", never stored, and does not block confirm**. Unknown, to be checked in the source: whether `markers` keeps the value after deletion.

**Q98** · Profile selection and excluded data (X01 part 1 review). Defaults taken (defaults, not decisions): **exactly one profile is imported, chosen by the user in the preview** (none by default, so nothing is imported until chosen); **profile identity fields, chat, nutrition, wallet, credentials and the Sync recovery record are never read into storage or logs**. Should the chosen profile be checked against the user (for example by a confirmation sentence)? Unknown: whether a single-client export always holds exactly one profile.

**Q99** · Calculated ratios without `derivedFrom` (X01 part 1 review). It is unknown whether `calculatedRatios.*` values carry `derivedFrom` (format document). Default taken: **markers in the `calculatedRatios` group, and any key the mapping table marks as calculated, are "not imported: calculated" whether or not `derivedFrom` is present, and the mapping table may hold a deny-list row for such a key (no Biomarker, a cited reason, kind `calculated`) and refuses only a measured mapping row (one with a Biomarker) for it**. This is a default, not a decision. Which other get-based keys are calculated is unknown.

**Q100** · get-based preview (X01 part 2a, 2026-11-27). Defaults taken (defaults, not decisions): (1) **upload at most 5 MiB** (the CSV import allows 1 MiB, Q71); (2) **the sample date must be exactly `YYYY-MM-DD` and a real calendar date, else the row is "not recognised: date not in YYYY-MM-DD form"; it is not yet mapped to `collected_at`** (part 2b decides the time zone); (3) **`version` must be exactly the integer 2** for the single-client export and the all-clients bundle (a missing, other, boolean or decimal version is refused, Q96); (4) **`labcharts-backup` and the `getbased-migration` archive are refused as "not supported yet"** (Q95); (5) **the profile chooser lists profile ids only**, no names, and a single-client export refuses a `profile_id`; a bundle with one profile needs no choice; (6) a marker value that is not a number (boolean, text, null) is "not recognised" and its value is not echoed; (7) any `derivedFrom` that is present and not null (even an empty list) leaves the row out as calculated; (8) the preview flags every row that is not provably non-AI, so in practice every row is flagged (Q92); (9) **at most 1000 entries and 5000 marker values per profile**, else refused with 400 (the CSV import caps at 200 rows, Q71). Which marker keys, LOINC codes and units belong in the mapping table is still open (Q91).

**Q101** · get-based confirm (X01 part 2b, 2026-11-27). Defaults taken (defaults, not decisions): (1) **`LabResult.collected_at` stays empty**: get-based gives a calendar date with no time zone and none is guessed; the date is kept in the provenance (`entry_date`) and returned in the API; (2) **every get-based result is stored `entered`, never `user_confirmed`, and there is no bulk confirm**: the owner confirms each result one by one (Q92, fail closed; this differs from the CSV import, Q75); (3) **the unit is always the mapping row's cited unit**, never read from the archive, and the number is the archive's exact decimal; a value the shared result rules refuse (more than 6 decimals, too many digits, a marker that needs laboratory and method) makes the confirm answer 400 naming the marker, with nothing stored; (4) **the original file is never retained** (it holds identity and other non-lab data), so `original_retained` is false and undo has no file to remove; (5) the report records the fixed name `getbased-export.json` as `import_name`, not the upload name, because get-based names its download after the client; `markerSources.at` (a millisecond number) is kept verbatim as its digits; (6) a profile with no matched row cannot be confirmed (400).

**Q102** · get-based flag names (X01 part 2b). The task text named the stored flags `read_by_ai` and `may_be_ai`, and also asked that they match the part 2a preview flags exactly. The preview already returns `ai_read` and `may_be_ai_read`. Default taken: **the stored flag values are the preview's codes** (`ai_read`, `may_be_ai_read`, `origin_not_shown`, `origin_unknown`), so the preview and the stored result never disagree; renaming would change a tested 2a response.

**Q103** · get-based `labcharts-backup` (X01 part 2d, 2026-11-27). Defaults taken (defaults, not decisions): (1) **an encrypted backup is detected** by `encrypted: true`, a `profileList` starting `v1:`, or any profile's `keys.imported` starting `v1:` (the source's own `isEncryptedValue`, M js/backup-restore-plan.ts:7); it is refused, nothing is read further; (2) **`keys.imported` is parsed as JSON text** (M js/data-core.ts:303); a profile without it has no entries, one that is not valid JSON is refused; (3) the report's file name stays the fixed `getbased-export.json`; (4) no migration: `import_format` is a free `CharField(32)`. Unknown: the full key list of the decoded `imported` object, and whether a real backup matches this (no real archive was read).

**Q104** · machine-readable OpenAPI (M00c docs part D, 2026-11-27). Default taken (a default, not a decision): **no OpenAPI file yet**. `/docs/api` is generated from `docs/api-*.md` and checked against the Django URL resolver. A generated OpenAPI file would need `drf-spectacular`, a new dependency; adding packages was refused in the sandbox before (Q74), and its licence must be fetched from the source before any `uv add`. Should it be added?
