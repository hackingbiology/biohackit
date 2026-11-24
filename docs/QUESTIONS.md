# Questions for Fabio

Format: date · module · question · default taken (work continues with the default).

---

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
