# Change: m00c — Autodev v2: continuous multi-agent graph with adversarial review

## Why
Fabio (2026-11-24) wants a fully automatic development process that delivers **100% of the features described**, including the preliminary ones, plus new proposed ones. It must run with very strict code-quality requirements and continuous adversarial review, must not hallucinate, and must document everything. Fabio gives feedback once a day, and the process never stops while there is budget. Autodev v1 (one `claude -p` per cron, twice a day, self-review only) cannot guarantee this.

## What changes
- **Definition of done = the traceability matrix** (`tools/trace/matrix.py` → `docs/TRACEABILITY.md`):
  - every `#### Scenario` in `openspec/specs/**` and in open changes is a row;
  - a row is *covered* when at least one test declares `scenario: <capability>::<scenario-slug>`;
  - 100% = every row covered, and CI is green.
- **Orchestrator** `tools/autodev2/orchestrator.py`:
  - Python stdlib only, running as a systemd service under `gl-auditor`;
  - the graph state is persisted, so it resumes after a crash or reboot;
  - each node is a `claude -p` call with a role-specific model and tool allowlist.
- **Graph per task:**
  1. **planner** (Opus): picks the next highest-value task from the matrix, open changes, ROADMAP and failures;
  2. **implementer** (Sonnet): works on an isolated git worktree branch;
  3. **gates** (deterministic `tools/autodev2/gates.sh`, no LLM): on failure, back to the implementer (max 3 rounds);
  4. **adversarial reviewers** (Opus, in parallel, read-only): correctness+spec-conformance, science+security, a11y+frontend when relevant;
  5. **verifier** (Sonnet): confirms each finding against the code and rejects unsupported ones;
  6. **fix**: confirmed findings go back to the implementer, then gates and review again (max 2 review rounds);
  7. **merge**: rebase on main, gates again, push.
  
  Unresolved findings become tickets, never silent merges.
- **Anti-hallucination rules:**
  - every claim must have executable evidence: a test, a command output or an import;
  - every finding must cite file:line and be verified;
  - every data value carries a source, and source URLs must be fetched and checked by a gate test;
  - "the LLM writes words, never numbers" (ROADMAP criterion 4).
- **Self-protection:**
  - the implementer may not modify `tools/autodev2/**`, except the gates file;
  - a diff that removes or weakens any gate line is rejected deterministically.
- **Budget:**
  - autodev's attributed share is ≤ **40%** of the weekly plan limit, measured from the account's real 7-day utilization (sampled to `/var/lib/biohackit-usage/usage.json`);
  - it is paced linearly over the week (allowed share = 40 × elapsed fraction + 6), and stops if account-wide utilization ≥ 90%;
  - it falls back to a USD ledger calibrated in %/USD when the sample is stale.
- **Daily feedback:**
  - at 08:15 Europe/Rome the deterministic digest goes to `docs/digest/YYYY-MM-DD.md` and to a GitHub issue (label `digest`); it reports matrix %, merged work, failures, decisions taken by default, open questions and budget;
  - at 08:30 the report reaches Fabio in chat;
  - questions are batched there; the process never waits and takes reversible defaults.
- **Staging:**
  - `docker-compose.staging.yml`, publicly at `http://51.158.36.151:18800`, without a password;
  - only synthetic or demo data, `noindex`, DEBUG off;
  - redeployed by a root timer from a separate read-only clone after each green merge.
- **Documentation:** user guide, API reference (OpenAPI), architecture and AI surfaces map, generated and kept current as part of each task's definition of done.
- **New features:** after spec discovery, a proposer may add `proposed-*` OpenSpec changes, which are implemented only after Fabio approves them in the digest.

## Decisions (Fabio 2026-11-24)
| # | Topic | Decision |
|---|-------|----------|
| A1 | Budget | ≤40% of weekly limit |
| A2 | Feedback | GitHub issue + chat report at 08:30, once a day |
| A3 | Staging | Public IP, high port, no password |
| A4 | Models | Opus plans and reviews, Sonnet implements and verifies, Haiku handles mechanical chores; a non-Claude second opinion is optional later (needs a key) |
