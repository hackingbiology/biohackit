# Tasks — s01 spec discovery

Registers: `docs/spec-discovery/whitepaper.md` (part A), `docs/spec-discovery/project-spec.md` (part B)

Registers part C: `docs/spec-discovery/getbased-reuse.md`, `docs/spec-discovery/presentation.md`

Registers part D1b: docs/spec-discovery/specs-html.md (sections 1–14)
Registers part D1c: docs/spec-discovery/specs-html.md (sections 15–27)

## safety-guardrails
- [ ] Implement "Platform describes and never prescribes" (copy review, AI narration check)
- [ ] Implement "LLM-assisted curation requires human review"

## accounts-and-profiles
- [ ] Implement "Full personal data export"
- [ ] Implement "Personal data erasure"
  - Part 1 done: owner-only `GET/POST /api/auth/me/erase/` implements "delete everything" (user, reports, results, measurements, retained originals). The research-retention path (needs M12 de-identification; refused with 409) and the UI remain.
- [ ] Implement "Consent to public-by-default is explicit and revocable"
- [ ] Implement "Lifestyle context cards"

## community-and-social
- [ ] Implement "Three layers of quality assurance"
- [ ] Implement "Knowledge is not for sale" (incl. commercial-content labelling)
- [ ] Implement "Stewardship and mission lock are published" (About section)
- [ ] Implement "Specification is publicly browsable"
- [ ] Implement "Public profile and protocol pages are indexable"
- [ ] Implement "Moderation policy for community-contributed protocols"
- [ ] Implement "Medical objections are collected as a public backlog"

## analytics-and-open-data
- [ ] Implement "Research API answers intervention-by-biomarker queries"
- [ ] Implement "Open licences declared on published data and content"
- [ ] Implement "Analytics pipeline works on pseudonymised data"
- [ ] Implement "Public data is published as linked data"
- [ ] Implement "Public-by-default reasoning and opt-out are stated publicly"

## daily-log-and-adherence
- [ ] Implement "Reminders for intake, due tests and restock"

## biomarkers-and-labs
- [ ] Implement "Body composition and microbiome results are accepted as measurements"
- [ ] Implement "Import from wearable export files"
- [ ] Implement "Deterministic calculated markers"
- [ ] Implement "Deterministic Bortz clock computation"
- [x] Implement "Unit conversion between unit systems"
- [ ] Implement "Cycle-phase-dependent ranges"
- [ ] Implement "Import can be rolled back"
- [ ] Implement "Extraction benchmark on a synthetic report"

## procurement-and-inventory
- [ ] Implement "Protocol cost is tracked and shown"

## evidence-layer
- [ ] Implement "Claims Validator" (fetch safeguards: public addresses only, limits, rate limit, untrusted page text)

## ai-uses-and-attribution
- [ ] Implement "LLM usage is capped by a monthly credit allowance"
- [ ] Implement "AI proposals are offered as a block"
- [ ] Implement "AI verdict shape with insufficient-data state"
- [ ] Implement "Choice of AI provider including a local model"

## measurement-planning
- [ ] Implement "Lab request generated from a pooled draw"
- [ ] Implement "Measurement appointments are recorded"

## interventions-and-catalog
- [ ] Implement "Early partial result during long waits"
- [ ] Implement "Weight-relative posology is gated on posology provenance"
- [ ] Implement "Route and formulation are recorded per intake item"
- [ ] Implement "Multi-ingredient products list their declared ingredients"

## dashboards-and-doctor-view
- [ ] Implement "Quick actions on the dashboard"
- [ ] Implement "Trend alerts"
- [ ] Implement "Intervention timeline overlaid on biomarker chart"
- [ ] Implement "Time-limited password-protected sharing link"

## genomics
- [ ] Implement "Import of consumer DNA test files"
