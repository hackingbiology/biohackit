# Autodev log

One entry per iteration: date · module · what was done · commit.

2026-11-09 · M00 Foundations · wrote OpenSpec change m00-foundations: proposal.md, tasks.md (TG1–TG5), foundations-architecture spec, QUESTIONS.md Q1–Q4, STATE updated · d92b3f2
2026-11-18 · M00 Foundations · TG1 repo layout: Django+Next.js skeleton, Docker Compose, Makefile, CI, env example; ruff/eslint/tsc clean (Django check and docker compose up not run on runner) · see git log
2026-11-19 · M00 Foundations · TG2 backend auth: accounts app (email User, Profile, SocialHandle), JWT register/token/refresh/me, public profile, 10 tests green · see git log
2026-11-19 · M00 Foundations · TG3 core domain stubs (Intervention/Biomarker/Measurement), hypertable migration with composite PK, 5 domain tests, 15 total green · see git log
2026-11-20 · M00b low-friction login · TG1 backend (allauth socialaccount+headless+mfa, DiscourseConnect provider, env-driven providers, code login, passkeys, verified-email linking) + TG3 tests, 26 green · see git log
2026-11-21 · M00b low-friction login · TG2 frontend sign-in (SignInForm: providers/email code/passkey, EN/IT/ZH, plain fetch), jest.config.js fix, 5 jest tests green · see git log
2026-11-21 · M00b low-friction login · archived change into openspec/specs/accounts-and-profiles (Fabio's action list still open) · see git log
2026-11-22 · M00 Foundations · TG4 frontend skeleton done: sign-up uses SignInForm, logout via allauth headless, middleware session check, Button/Input/logout tests, 9 jest green · see git log
2026-11-22 · M00 Foundations · TG5 backend tests confirmed (26 green), frontend auth.test.ts added (unrun: pnpm blocked), CI verification pending · see git log
2026-11-23 · M00 Foundations · frontend checks run via node (jest 11 green, tsc ok), fixed eslint error in jest.config.js; CI-on-GitHub confirmation requested from Fabio · see git log
2026-11-23 · M01 Terminology · OpenSpec change written (proposal, tasks TG1-5, spec delta), Q5-Q7 raised; M00 CI confirmation still pending · see git log
2026-11-24 · M01 Terminology · TG2 done: terminology app (Source/Unit/UnitConversion, normalize_value), 4 tests, 30 pytest green · see git log
2026-11-24 · M00c · TG2 tag-tests: delta specs moved to specs/<capability>/spec.md; 7/206 scenarios covered by tagged tests · see git log
2026-11-24 · M00c · TG2 staging part A: gunicorn added to pyproject and uv.lock from PyPI JSON; lockfile-sync test covers dev-process::lockfile-in-sync · see git log
2026-11-24 · M00c · TG2 staging part B: docker-compose.staging.yml, noindex middleware + Next headers/rewrites, seed_demo, docs/STAGING.md; PyPI requires_dist for gunicorn 27.0.1 lists packaging only under extras gevent/testing, so uv.lock left unchanged · see git log
2026-11-24 · M00c · TG2 staging part B review fixes: skipTrailingSlashRedirect + slash-terminated rewrites (no 308/APPEND_SLASH loop); seed_demo creates a verified primary EmailAddress; staging uses console EMAIL_BACKEND; tests added · see git log
2026-11-24 · M00c · TG2 staging B round 2: NoIndexMiddleware moved first in MIDDLEWARE (covers redirects, 400s, WhiteNoise; tests added); STAGING.md documents e-mail-code sign-in via backend logs · see git log
2026-11-24 · X01 · TG1 docs/ecosystem README+GIVEBACK+m00 scan (fetched from GitHub/PyPI/npm), proposal link, test_ecosystem_docs.py; Q8 added for unknown licence verdicts · see git log
2026-11-24 · X01 · TG2 m01 terminology scan (docs/ecosystem/m01-terminology.md), m01 proposal link + task annotations, licence-table check in test_ecosystem_docs.py, psycopg-binary entry; Q9–Q11 · see git log
2026-11-24 · X01 · TG3 licence gate: tools/licence/check_licences.py + overrides.toml, `licences` step appended to gates.sh, README table gains ISC/0BSD/PSF-2.0/MIT-0, tests; Q12 · see git log
2026-11-24 · X01 · TG4 integration anchor scan (docs/ecosystem/integrations.md), scans test covers it, give-back register test, m01 TG column fix; Q14 · see git log
2026-11-24 · M00c · TG2 gates A: changed-file backend coverage ≥ 90% gate (tools/coverage/changed_coverage.py, step appended to gates.sh), dev-process spec + tests, GIVEBACK fhir.resources wording fix · see git log
2026-11-24 · M00c · TG2 spec discovery A: whitepaper + foundation register (docs/spec-discovery/whitepaper.md), change s01-spec-discovery with 8 ADDED requirements, register-consistency test, dev-process requirement; Q16–Q17 · see git log
2026-11-24 · M00c · TG2 spec discovery B: project-spec register (docs/spec-discovery/project-spec.md), 14 ADDED requirements plus the linked-data requirement in s01-spec-discovery, register test covers both registers; Q18–Q24; next part C (getbased analysis, presentation) · see git log
2026-11-24 · M00c · TG2 spec discovery C: getbased-reuse and presentation registers, 14 ADDED requirements in s01-spec-discovery (new genomics delta), linked-data scenario public-only fix; Q25–Q30; next part D · see git log
2026-11-25 · M00c · TG2 gates B1: next + eslint-config-next 15.1.0 -> 15.5.29, advisory register, offline test; Q33 · see git log
2026-11-25 · M00c · fix main (no .npmrc): verified shared node_modules gates, STATE root-cause section, Q34 orchestrator proposal · see git log
2026-11-25 · M00c · TG2 gates C: pip-audit gate via uvx (pinned 2.10.1), offline tests, dev-process scenarios · see git log
2026-11-25 · X01 · public /ecosystem page, exporter and sync test; requirement added to x01 delta · see git log
2026-11-25 · M00c · TG2 spec discovery D1a: slides register (14 pages), 2 ADDED requirements, test covers slides.md · see git log
2026-11-25 · M00c · TG2 spec discovery D1b: specs-html register (sections 1–13, 112 rows), parser accepts escaped pipes, test added · see git log
2026-11-25 · M00c · TG2 spec discovery D1c: specs-html register extended to all 27 sections, test checks titles against the HTML · see git log
2026-11-25 · M00c · TG2 spec discovery D2a: competitive-landscape register (6 sections, 28 rows), test added, Q35 · see git log
2026-11-25 · M00c · TG2 spec discovery D2b1: proposal-critique register (7 sections, 65 rows), 1 added requirement, test added, Q37 · see git log
2026-11-25 · M00c · TG2 spec discovery D2b2: hb-protocol-structure register (6 worksheets), 3 added requirements (per-weight posology gated on provenance, route and formulation, multi-ingredient products), test extended, Q38 · see git log
2026-11-25 · M00c · TG2 spec discovery D2b3: foundation-html register (8 sections, 23 rows, all reuse part A foundation.md rows, no new requirement), test added, Q39; part D closed · see git log
2026-11-25 · M00c · TG2 gates D: openspec validate gate (pinned @fission-ai/openspec 2.2.0 via pnpm dlx), 3 scenarios, m00-foundations delta header fixed · see git log
2026-11-25 · M00c · TG2 gates E: semgrep gate (pinned semgrep 1.187.0 via uvx, p/django on backend, p/typescript on frontend/src), 0 findings, 11 offline tests, Q40 · see git log
2026-11-25 · M00c · TG2 gates F: mypy strict gate (pinned mypy 2.4.1 + django-stubs 6.1.2 via uv run --isolated) on backend/terminology, type-only fixes, 3 scenarios, Q41 · see git log
2026-11-25 · M00c · TG2 gates G: mutmut gate (pinned mutmut 3.8.1 via uv run --isolated in a scratch copy) on terminology/services.py, 43-44/44 killed + 1 accepted equivalent, 3 new tests, 16 offline gate tests, Q42 · see git log
2026-11-25 · M00c · TG2 docs A: AI surfaces map docs/ai-surfaces.md -> /docs/ai-surfaces (3 AI surfaces, 7 deterministic, exporter + sync test + jest test), Q43 · see git log
2026-11-25 · M00c · TG2 docs B: architecture page docs/architecture.md -> /docs/architecture (exporter, path/requirement-exists test, sync test, jest test), ai-surfaces safety-threshold row split · see git log
2026-11-25 · M00c · TG2 docs C: user guide docs/user-guide.md -> /docs/user-guide (exporter, route/requirement-exists test, sign-in fact test, sync test, jest test), Q45 · see git log
2026-11-25 · M00c · TG2 docs E: changelog docs/CHANGELOG.md -> /docs/changelog (exporter, commit/change-exists test, sync test, jest test, CI fetch-depth 0), Q46 · see git log
2026-11-25 · M01 · TG3 coded analyte registry: Biomarker requires unique LOINC + Unit FK + Source FK, Measurement unit checked against analyte unit, migrations core/0003-0005 fail loudly on uncoded rows, Q47-Q48 · see git log
2026-11-25 · M01 · TG4 part A: Reference/Optimal/SafetyThreshold models, displayable_optimal_range, range_status, TG3 residual fixes (blank + duplicate LOINC), Q49 · see git log
2026-11-25 · M01 · TG4 part B: GET /api/terminology/biomarkers/<loinc>/ranges/ (three ranges separate, provenance, per-range status), 20 API tests · see git log
2026-11-25 · M01 · TG5 part A: seed_reference loader + seed format + inspector, no data rows (UCUM in part B) · see git log
2026-11-25 · M00c · TG2 gates B2: pnpm override postcss >=8.5.23 <9 + tools/audit/pnpm_audit_gate.py (3 scenarios, tests, gates.sh step) · see git log
2026-11-25 · M00c · TG2 gates B2 review fixes: gate rejects pnpm.auditConfig waiver (new scenario + tests); build verification stays open (Q34) · see git log
2026-11-25 · M01 · TG-STRATA: nullable age band/sex/ancestry strata on ReferenceRange and OptimalRange (+ ReferenceRange.evidence_grade), most-specific-complete-row selectors, None on a tie (5 scenarios, tests) · see git log
2026-11-25 · M01 · TG-LOINC part A: LoincTerm model + idempotent import_loinc for Loinc.csv (synthetic fixture, Source per release, 4 scenarios, tests) · see git log
2026-11-25 · M01 · TG-LOINC part B: authenticated paginated GET /api/terminology/loinc/?q= (full-text + pg_trgm + exact code, migration 0005, 7 scenarios, tests) · see git log
2026-11-25 · M01 · TG-LOINC part B2: LOINC search q capped at 200 chars (400), scoped throttle loinc_search, pg_trgm threshold merged into DATABASE_URL options (2 scenarios, tests, Q51) · see git log
2026-11-25 · M01 · TG-LOINC part C1: import_loinc also imports optional ConsumerName and it-IT/zh-CN LinguisticVariants (2 models, migration 0006, 4 scenarios, tests, Q52) · see git log
2026-11-25 · M01 · TG-LOINC part C2: LOINC search also matches consumer names and it-IT/zh-CN variant names, each term once (migration 0007, 3 scenarios, tests) · see git log
2026-11-25 · M01 · TG-LOINC part D1: import_loinc also imports optional Part and LoincPartLink_Primary into LoincPart/LoincPartLink (migration 0008, 3 scenarios + 2 extended, tests, Q53) · see git log
2026-11-25 · M01 · TG-LOINC part D2: import_loinc also imports optional AnswerList and LoincAnswerListLink into LoincAnswerList/LoincAnswer/LoincAnswerListLink (migration 0009, 3 scenarios + 1 extended, tests); PanelsAndForms left out until its header is verified (Q54) · see git log
2026-11-26 · M01 · TG-LOINC part D3: key length checked on every keyed LOINC file (parse_csv key_field), 1 scenario, tests · see git log
2026-11-26 · X01 · M02 ecosystem scan docs/ecosystem/m02-blood-layer.md (15 entries, Q55), /ecosystem page data regenerated · see git log
2026-11-26 · M02 · TG1: OpenSpec change m02-blood-layer (proposal, tasks TG-a..k, spec delta, Q56–Q60), ecosystem test covers it · see git log
2026-11-26 · M02 · TG1b: spec review fixes (LabResult source/validation/eligibility, UCUM = stored Unit.ucum_code, rollback, s01 relation), Q63–Q64 · see git log
2026-11-26 · M02 · TG1c: stored-and-flagged rule blood-only, DEXA/microbiome follow s01 Result without provenance, Q66 · see git log
2026-11-26 · M02 · TG-a part 1: LabReport/LabResult models + migration 0006, normalisation via normalize_value, aggregation eligibility, Q67 · see git log
2026-11-26 · M02 · TG-a part 1b: LabResult.reported_value never rounded, out-of-range precision rejected · see git log
2026-11-26 · M02 · TG-a part 2: Biomarker.category + category_source (Q66, migration 0008), DEXA/microbiome LabResult refused without laboratory/method, Q68 · see git log
2026-11-26 · M02 · TG-a part 3: LabResult -> OMOP MEASUREMENT mapping doc (DDL v5.4.0) + pure mapper core/omop.py, Q69 · see git log
2026-11-26 · M02 · TG-b: POST/GET /api/labs/reports/ manual lab entry (same save path as imports) + deterministic plausibility from stored cited ReferenceRange rows, Q70 · see git log
2026-11-26 · M02 · TG-b part 2: reported_value ≤40 chars, ≤200 results per report, O(n) trailing-zero strip (review 1795662883) · see git log
2026-11-26 · M02 · TG-c part 1: CSV lab import preview/confirm + DELETE rollback of an import (stdlib csv, Q71) · see git log
2026-11-26 · M02 · TG-d part 1: opt-in deterministic exact-term PII redaction for the CSV import, diff in preview, Q72 · see git log
2026-11-26 · M02 · TG-d part 1b: redaction overflow names redact_terms, linear-time matching, bounds and redaction see the stripped cell · see git log
2026-11-26 · M02 · TG-j part 1: hand-written FHIR R4 DiagnosticReport/Observation Bundle of a lab report + owner-only GET /api/labs/reports/<id>/fhir/, Q73 · see git log
2026-11-26 · M02 · Q63 applied: lab result states entered|user_confirmed|source_verified|disputed|retracted, eligibility needs a confirmed state, owner-only PATCH /api/labs/results/<id>/validation/, migration 0009, Q75 · see git log
2026-11-26 · M02 · TG-g part 1: confirmed CSV kept as private file with SHA-256 on the LabReport, deleted on rollback, not kept with redaction, migration 0010, Q76 · see git log
2026-11-26 · M02 · Q56 applied: docs/research/phenoage-coefficients.md (PhenoAge + Bortz, sources compared, engine decision = hand-write), ecosystem entries, give-back rows, Q77, Q78; documentation only · see git log
2026-11-26 · M02 · TG-i part 1: pure PhenoAge engine backend/core/phenoage.py (S2 + Q77 defaults, no imputation), D3 vectors tested, get-based ecosystem entry corrected; no dependency, no migration · see git log
2026-11-26 · M02 · TG-i part 2: owner-only GET /api/labs/reports/<id>/phenoage/ and core/phenoage_binding.py (LOINC binding, stored unit conversions only); loinc.org returned 403 so the code map is empty and every request refuses analyte_not_mapped (Q79); no dependency, no migration · see git log
2026-11-26 · M02 · TG-i part 2b: age_years too large for a float is a 400 naming age_years (review 1795694970) · see git log
2026-11-26 · M02 · TG-j part 2: owner-only GET /api/labs/reports/<id>/omop/ exports non-retracted results as OMOP MEASUREMENT rows through the existing mapper; concept ids null (Q69, Q80); no dependency, no migration · see git log
2026-11-26 · M02 · TG-l part 1: owner-only GET /api/labs/results/<id>/convert/?unit= shows a result in a requested UCUM unit via stored UnitConversion only (normalize_value), reported value always kept, nothing written; SI/US flag asked in Q81; no dependency, no migration · see git log
2026-11-26 · M02 · TG-m part 1: owner-only GET /api/labs/results/<id>/ranges/ shows a result against reference range, optimal range (displayable gate) and safety threshold, separate, with provenance and computed status; Subject unknown, nothing converted on the fly (Q82); no dependency, no migration · see git log
2026-11-26 · M02 · TG-n part 1: owner-only GET /api/labs/reports/<id>/calculated/ computes stored CalculatedRatioDefinition quotients (Decimal, labelled calculated, inputs and dates listed, missing input gives value null); no ratio seeded, no formula in code (Q83); migration 0011 table only, no dependency · see git log
2026-11-26 · M02 · TG-h part 1: owner-only GET /api/labs/completeness/ gives, per stored OrganSystemPanel, n of m expected markers present and the newest collection date (own results, disputed/retracted excluded); no panel seeded (Q84); migration 0012 table only, no dependency · see git log
2026-11-26 · S01 · Personal data erasure part 1: owner-only GET/POST /api/auth/me/erase/ deletes account, data and retained originals (delete_everything); keep_for_research refused 409 until M12 (Q85); no migration, no dependency · see git log
2026-11-26 · M02 · TG-o part 1: /labs/import page (upload, per-row recognised/not recognised with reason, save only when all recognised, undo) and session authentication with CSRF for the API; no migration, no dependency (Q86) · see git log
2026-11-26 · M02 · TG-o part 1b: /labs/import shows a 'Range check' column (within / outside / not checked, flag only), 'Check file' is locked while a saved report is not undone, changelog row cites 77f6eb3; frontend only, no migration, no dependency · see git log
2026-11-26 · M02 · TG-o part 2: /labs/new (manual entry) and /labs/reports/<id> (report view with validation state, aggregation and range check in words, undo); frontend only, no migration, no dependency (Q87) · see git log
2026-11-26 · M02 · TG-o part 2b: /labs/new intro no longer promises undo for typed reports; Remove moves focus and announces the removal (WCAG 2.4.3); frontend only, no migration, no dependency · see git log
2026-11-26 · M02 · TG-m part 2: report page shows each result against its three ranges (reference, optimal, safety) from GET /api/labs/results/<id>/ranges/, optimal provenance in one click; frontend only, no migration, no dependency (Q88) · see git log
