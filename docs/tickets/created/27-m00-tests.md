# [M00] Tests and CI green: auth.test.ts and CI verification
Labels: autodev, test
Milestone: M00 Foundations
Parent: #3

Goal: close TG5. Backend account tests exist (10 in test_accounts.py, 26 backend tests green, ruff clean). Add frontend `auth.test.ts` covering register() and login() against the JWT endpoints. CI workflow already has backend (ruff+pytest) and frontend (eslint+tsc+jest) jobs.

Spec: openspec/changes/m00-foundations/ TG5.

Acceptance:
- register() posts email/password to /api/auth/register/ and returns tokens on 201
- login() calls /api/auth/token/ and returns access+refresh on 200
- CI is green on a test branch (pending)
- Frontend test run pending: runner cannot execute pnpm/jest (see QUESTIONS.md)
