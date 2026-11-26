# [M02] TG-o part 1: CSV import review page (/labs/import) and browser session authentication

Labels: autodev, feature
Milestone: M02 Blood Layer
Parent: unknown (Q60)

Goal: the first lab page. A signed-in user uploads a lab CSV, sees each row as recognised or not recognised with the reason, saves only when every row is recognised, and can undo the import. The API also accepts the browser session cookie (CSRF enforced) next to JWT.

Spec refs: main biomarkers-and-labs "Human review before persistence"; s01 "Import can be rolled back"; m02-blood-layer TG-o; Q86.

Acceptance: backend/tests/test_session_api_auth.py and frontend/src/__tests__/lab-import.test.tsx pass; trace matrix covers both scenarios; no migration, no dependency; gates pass.
