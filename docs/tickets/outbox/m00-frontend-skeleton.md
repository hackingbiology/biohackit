# [M00] Frontend skeleton: sign-up via SignInForm, logout, session middleware, UI primitives
Labels: autodev, feature
Milestone: M00 Foundations
Parent: #3

Goal: finish the frontend skeleton (TG4). Sign-up and sign-in are one low-friction flow (m00b SignInForm), logout ends the allauth session through the headless API, the middleware protects `/dashboard/*` by session cookie, and Button/Input primitives are tested.

Spec: openspec/changes/m00-foundations/ TG4; accounts-and-profiles (low-friction login); tickets #22, #24.

Acceptance:
- Account needed to contribute: unauthenticated `/dashboard` redirects to `/sign-in` (middleware checks `sessionid` or `access_token` cookie).
- Onboarding invites sharing: sign-up completes into `/onboarding`.
- Tests: logout issues DELETE on the headless session endpoint; Button aria-label + onClick; Input label, error text, aria-describedby.
