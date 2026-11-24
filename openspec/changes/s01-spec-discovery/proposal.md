# Change: s01 — Spec discovery

## Why
The whitepaper and the Foundation evaluation promise features that no requirement in `openspec/specs/**` states. The traceability matrix only measures what is specified, so unspecified promises are invisible to the definition of done.

## What changes
Part A compares `whitepaper/whitepaper.src.html` and `docs/foundation.md` with the existing specs. The result is the register `docs/spec-discovery/whitepaper.md`: every feature is `covered` by an existing requirement, `added` here, or `out-of-scope` with a reason. Eight requirements are added in four capabilities. Each is written at the level of detail the source gives; open details are in `docs/QUESTIONS.md` (Q16, Q17).

Later parts (B: `docs/hackingbiology-project-spec.md`, `docs/getbased-reuse-analysis.md`, `docs/presentation/`) append to this change.

## Impact
- New requirements in `safety-guardrails`, `accounts-and-profiles`, `community-and-social`, `analytics-and-open-data`.
- No code changes; implementation tasks are listed in `tasks.md`.
