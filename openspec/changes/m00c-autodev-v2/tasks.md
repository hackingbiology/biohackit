# Tasks — m00c autodev v2
## TG1 Bootstrap (done by the admin session)
- [x] `tools/trace/matrix.py` + `docs/TRACEABILITY.md`
- [x] `tools/autodev2/` orchestrator, prompts, `gates.sh`, systemd unit; v1 cron retired
- [x] usage sampler → `/var/lib/biohackit-usage/usage.json`
- [x] staging deploy timer (root) on port 18800
## TG2 First graph tasks (done by the graph)
- [x] Tag every existing test with its `scenario:` ids; matrix shows true coverage
- [x] `docker-compose.staging.yml` (gunicorn + `next start`, Next rewrites `/api` and `/_allauth` to backend, DEBUG off, demo-data seed, `X-Robots-Tag: noindex`), port 18800 only
- [ ] Gates hardening (append-only to gates.sh): mypy (strict on new apps), coverage ≥ 90% on changed backend files, `pip-audit`, `pnpm audit --prod`, semgrep (p/django, p/typescript), openspec validate (CLI `@fission-ai/openspec`), Playwright e2e + axe WCAG 2.2 AA on key pages, mutmut on statistics/unit-conversion modules
  - [ ] mypy (strict on new apps)
  - [x] changed-file coverage ≥ 90% (tools/coverage/changed_coverage.py)
  - [ ] pip-audit
  - [x] B1 upgrade next to a patched release (no waiver for fixable high/critical advisories)
  - [ ] B2 pnpm audit --prod gate
  - [ ] semgrep (p/django, p/typescript)
  - [ ] openspec validate
  - [ ] Playwright e2e + axe WCAG 2.2 AA
  - [ ] mutmut
- [ ] Spec discovery: compare whitepaper/, docs/presentation/, docs/*.md against openspec/specs; every feature not yet specified becomes a requirement in an OpenSpec change
  - [x] part A: whitepaper/ + docs/foundation.md (docs/spec-discovery/whitepaper.md)
  - [x] part B: docs/hackingbiology-project-spec.md (docs/spec-discovery/project-spec.md)
  - [x] part C: docs/getbased-reuse-analysis.md, docs/presentation/
  - [ ] part D: docs/slides/, docs/specs/, docs/analysis/, remaining docs/*.md
- [ ] Docs site generated from repo (MkDocs Material or Next route `/docs`): user guide, OpenAPI reference, architecture, AI surfaces map, changelog
