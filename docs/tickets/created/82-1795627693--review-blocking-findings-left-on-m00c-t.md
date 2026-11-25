# [review] Blocking findings left on m00c-tg2-docs-d1-openapi-schema-backend

Labels: autodev

[
 {
  "file": "backend/pyproject.toml",
  "line": 1,
  "severity": "critical",
  "claim": "Nothing from the task was implemented; the branch differs from main only by a renamed ticket file.",
  "fix": "Do steps 0 to 5.",
  "confirmed": true,
  "reason": "`git diff main --stat` shows one file changed, a rename with 0 insertions and 0 deletions. docs/openapi.yaml and tools/docs/export_openapi.py do not exist."
 },
 {
  "file": "backend/pyproject.toml",
  "line": 1,
  "severity": "critical",
  "claim": "Step 0 was not done: drf-spectacular is not added to pyproject.toml or uv.lock.",
  "fix": "Fetch the PyPI and GitHub metadata, run `uv add --project backend 'drf-spectacular>=<ver>'`, run test_lockfile_sync.py, and commit.",
  "confirmed": true,
  "reason": "grep for 'spectacular' in backend/pyproject.toml and backend/biohackit/settings.py returned no matches. The diff against main shows neither file changed."
 },
 {
  "file": "backend/biohackit/settings.py",
  "line": 1,
  "severity": "critical",
  "claim": "Step 2 is missing: settings.py has no drf_spectacular app, DEFAULT_SCHEMA_CLASS or SPECTACULAR_SETTINGS.",
  "fix": "Add 'drf_spectacular' to INSTALLED_APPS and set DEFAULT_SCHEMA_CLASS and SPECTACULAR_SETTINGS.",
  "confirmed": true,
  "reason": "grep for 'spectacular' in settings.py returned no matches, and settings.py is not in the diff against main."
 },
 {
  "file": "tools/docs/export_openapi.py",
  "line": 1,
  "severity": "critical",
  "claim": "Step 3 is missing: the export script and docs/openapi.yaml do not exist.",
  "fix": "Create the deterministic exporter with --check, then generate and commit docs/openapi.yaml.",
  "confirmed": true,
  "reason": "`ls tools/docs` lists only export_ai_surfaces.py, export_architecture.py and export_user_guide.py. `ls docs/openapi.yaml` reports no such file."
 },
 {
  "file": "backend/tests/test_openapi_doc.py",
  "line": 1,
  "severity": "critical",
  "claim": "Step 4 is missing: no tests exist for the two new scenarios.",
  "fix": "Add the three tests with the scenario tags.",
  "confirmed": true,
  "reason": "The branch diff against main contains no backend/tests files, and the implementation they would test does not exist."
 },
 {
  "file": "openspec/changes/m00c-autodev-v2/specs/dev-process/spec.md",
  "line": 162,
  "severity": "high",
  "claim": "Step 1 is missing: there is no 'OpenAPI reference schema' requirement or scenarios in the spec delta.",
  "fix": "Add the requirement and both scenarios, then run matrix.py and validate_gate.py.",
  "confirmed": true,
  "reason": "The spec file is not in the diff against main, so the branch has no change to it."
 }
]
