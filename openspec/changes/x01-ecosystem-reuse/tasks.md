# Tasks — x01 ecosystem reuse
- [x] `docs/ecosystem/README.md` (method, decision categories, licence table) + `GIVEBACK.md`
- [x] Retroactive scan `docs/ecosystem/m00-foundations.md` (auth/allauth, Django stack, Next PWA, get-based components, OpenSpec)
- [x] Retroactive scan `docs/ecosystem/m01-terminology.md` (LOINC tooling, UCUM libraries, OHDSI Athena/OMOP vocabularies, FHIR terminology tooling, open reference-range datasets); feed decisions back into m01 tasks
- [ ] Integration scans for the anchors named in the slides: get-based, AI4L, evipedia-mcp, FHIR (Python libs), OMOP CDM DDL, Discourse API
- [ ] Licence gate in gates.sh (append): backend deps via pip metadata, frontend via pnpm licenses; fail on AGPL-incompatible licences
- [ ] Planner rule: scan precedes each module change M02–M13
- [ ] Docs page "Ecosystem": what we build on, what we give back
