# [M00b] Frontend: low-friction sign-in page (providers, email code, passkey)
Labels: autodev, feature
Milestone: M00 Foundations
Parent: #3

Goal: a single sign-in/sign-up page backed by the allauth headless API (plain fetch, no new auth dependency): provider buttons from the `config` endpoint (only configured ones, rapamycin.news first), email-code login, passkey login via the browser WebAuthn API. Plain language, WCAG 2.2 AA basics (labels, roles, focus rings, contrast), EN/IT/ZH strings.

Spec: openspec/changes/m00b-low-friction-login/ (module ticket #22; backend ticket #23)

Acceptance (tested in frontend/src/__tests__/signin.test.tsx):
- only configured providers are shown, rapamycin.news first; zero providers still shows email code
- email-code flow request -> confirm signs the user in
- a wrong code shows an accessible alert
- UI strings exist for en/it/zh and locale is picked from the browser

Also: jest config moved to jest.config.js because ts-node is not installed (jest could not start).
