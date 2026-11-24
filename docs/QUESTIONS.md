# Questions for Fabio

Format: date · module · question · default taken (work continues with the default).

---

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
