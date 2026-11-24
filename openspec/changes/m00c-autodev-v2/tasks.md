# Tasks — m00c autodev v2
## TG1 Bootstrap (done by the admin session)
- [x] `tools/trace/matrix.py` + `docs/TRACEABILITY.md`
- [x] `tools/autodev2/` orchestrator, prompts, `gates.sh`, systemd unit; v1 cron retired
- [x] usage sampler → `/var/lib/biohackit-usage/usage.json`
- [x] staging deploy timer (root) on port 18800
## TG2 First graph tasks (done by the graph)
- [x] Tag every existing test with its `scenario:` ids; matrix shows true coverage
- [ ] `docker-compose.staging.yml` (gunicorn + `next start`, Next rewrites `/api` and `/_allauth` to backend, DEBUG off, demo-data seed, `X-Robots-Tag: noindex`), port 18800 only
- [ ] Gates hardening (append-only to gates.sh): mypy (strict on new apps), coverage ≥ 90% on changed backend files, `pip-audit`, `pnpm audit --prod`, semgrep (p/django, p/typescript), openspec validate (CLI `@fission-ai/openspec`), Playwright e2e + axe WCAG 2.2 AA on key pages, mutmut on statistics/unit-conversion modules
- [ ] Spec discovery: compare whitepaper/, docs/presentation/, docs/*.md against openspec/specs; every feature not yet specified becomes a requirement in an OpenSpec change
- [ ] Docs site generated from repo (MkDocs Material or Next route `/docs`): user guide, OpenAPI reference, architecture, AI surfaces map, changelog
