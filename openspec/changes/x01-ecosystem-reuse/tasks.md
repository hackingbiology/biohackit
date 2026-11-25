# Tasks — x01 ecosystem reuse
- [x] `docs/ecosystem/README.md` (method, decision categories, licence table) + `GIVEBACK.md`
- [x] Retroactive scan `docs/ecosystem/m00-foundations.md` (auth/allauth, Django stack, Next PWA, get-based components, OpenSpec)
- [x] Retroactive scan `docs/ecosystem/m01-terminology.md` (LOINC tooling, UCUM libraries, OHDSI Athena/OMOP vocabularies, FHIR terminology tooling, open reference-range datasets); feed decisions back into m01 tasks
- [x] Integration scans (`docs/ecosystem/integrations.md`) for the anchors named in the slides: get-based, AI4L, evipedia-mcp, FHIR (Python libs), OMOP CDM DDL, Discourse API
- [x] Licence gate in gates.sh (append): backend deps via pip metadata, frontend via pnpm licenses; fail on AGPL-incompatible licences
- [ ] Planner rule: scan precedes each module change M02–M13
- [x] Scan docs/ecosystem/m02-blood-layer.md (lab report ingestion CSV/PDF/photo, FHIR DiagnosticReport/Observation, OMOP MEASUREMENT, PhenoAge/biological clocks, PII obfuscation)
- [x] Docs page "Ecosystem": what we build on, what we give back
