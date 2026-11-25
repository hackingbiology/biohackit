# Questions for Fabio

Format: date · module · question · default taken (work continues with the default).

---

## 2026-11-25 · m00c B1 next upgrade

**Q33** · After upgrading `next` to 15.5.29, `pnpm audit --prod` still reports `postcss` 8.4.31 (bundled inside `next`; GHSA-6g55-p6wh-862q and GHSA-r28c-9q8g-f849, high, patched >=8.5.12 and >=8.5.18). Default taken: **B1 only fixes `next`; B2 adds a pnpm override for `postcss` to a patched version, with no waiver.** Please confirm the override approach.

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

## 2026-11-25 · M00c user guide

**Q45** · The user guide is English only; IT and ZH fall back to EN as on /docs/architecture. The `/dashboard` page that sign-in redirects to does not exist yet, so the guide lists it under "Coming later". Default taken: **EN only, no translation yet**. Should the guide be translated to IT/ZH now, and should the sign-in redirect point somewhere that exists until the dashboard is built?
