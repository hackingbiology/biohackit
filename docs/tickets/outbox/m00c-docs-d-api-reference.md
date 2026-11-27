# [M00c] Docs site part D: API reference page at /docs/api

Labels: autodev, feature
Milestone: M00c
Parent:

Goal: publish an API reference generated from `docs/api-*.md` and checked against the real Django `/api/` routes, so no route is undocumented and no documented endpoint is invented. No new dependency; a machine-readable OpenAPI file waits on Q104.

Spec refs: openspec/changes/m00c-autodev-v2 (docs part D), dev-process::api-routes-documented, dev-process::api-reference-page-in-sync.

Acceptance:
- `docs/api-accounts.md` and `docs/api-terminology.md` document the missing endpoints
- `python3 tools/docs/export_api_reference.py --check` exits 0; `backend/tests/test_api_reference_doc.py` fails on an undocumented route, an unresolved documented path or a stale JSON
- `/docs/api` renders and is linked from `/docs`
