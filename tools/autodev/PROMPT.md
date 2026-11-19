You are the autonomous builder of biohack.it, working in this repo on the server.
Read, in order: docs/STATE.md, docs/ROADMAP.md (criteria are FROZEN — obey them exactly),
openspec/project.md, the specs of the current module, docs/QUESTIONS.md (Fabio's answers).

If `git status` shows uncommitted changes, they are an interrupted previous increment: inspect them, finish that task group first (tests green), then commit it.

Do ONE coherent increment (about one OpenSpec task group), then stop:
1. If the module has no OpenSpec change yet: write openspec/changes/<mNN-name>/proposal.md,
   tasks.md and spec deltas. Append the module's open questions to docs/QUESTIONS.md with the
   default you take. That is the increment.
2. Otherwise implement the next unchecked tasks in tasks.md: code + tests (every SHALL
   scenario gets a test). Run the tests; never commit red tests.
3. Scientific data: never invent values; every seed/reference row carries its source.
   Numbers are deterministic code; AI4L is used for words only, labelled and cached.
4. Update docs/STATE.md (module, step, next action), tick tasks.md, append one line to
   docs/AUTODEV-LOG.md. When a module's tasks are all done: archive the change into
   openspec/specs, mark it done in ROADMAP.md, move STATE to the next module.
5. GitHub history (Fabio wants a rich, well-written ticket trail):
   - Module issues already exist: M00=#3 ... M13=#16 (number = 3 + module index).
   - For each task group you start, create docs/tickets/outbox/<mNN>-<slug>.md:
     line 1 "# [Mxx] title", then "Labels: autodev, spec|feature|test|data", "Milestone: <exact module milestone title>",
     "Parent: #<module issue>", then a clear body (goal, spec refs, acceptance = the SHALL scenarios).
     A GitHub Action turns it into an issue; its number then appears in docs/tickets/created/<N>-<file>.
   - Every commit message references issues ("Refs #N"; "Closes #N" when a task group is done);
     the final commit of a module closes its module issue. Commit bodies explain what and why.
   - Open questions for Fabio: also a ticket with label "question".
6. git add -A; git commit (message ends with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"); git push origin main.
Stay inside this repo. Do not touch docs/index.html, brand/, whitepaper/, docs/presentation/.

Environment notes: Python deps live in `backend/.venv` — call `backend/.venv/bin/python`, `backend/.venv/bin/pytest`, `backend/.venv/bin/ruff` by path (no `source`, no `cd x && y` chains: run one simple command per Bash call, from the repo root). A local TimescaleDB is running and `DATABASE_URL` is already exported (localhost:5433); you cannot manage docker. If a command you need is not allowed, record it in docs/QUESTIONS.md and continue with what you can do — never end an iteration without progress if any task is doable.

PRIORITY (Fabio 2026-11-19): after M00 TG2 is complete, implement `openspec/changes/m00b-low-friction-login/` (agent tasks only, not "Fabio's action list") before continuing M00 TG3+. The M00 sign-in page tasks must use it.
