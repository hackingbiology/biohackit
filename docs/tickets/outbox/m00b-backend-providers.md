# [M00b] Backend: social providers, DiscourseConnect, passkeys, email code
Labels: autodev, feature
Milestone: M00 Foundations
Parent: #3

Goal: allauth socialaccount + headless + mfa; env-driven providers (google, microsoft, apple, facebook, weixin); custom DiscourseConnect provider for rapamycin.news filling SocialHandle; login by code; passkeys; verified-email-only auto-linking.

Spec: openspec/changes/m00b-low-friction-login/ (module ticket #22)

Acceptance (SHALL scenarios, all tested in backend/tests/test_login_providers.py):
- valid DiscourseConnect payload logs in and sets handle; bad signature and replayed nonce rejected
- config endpoint lists only configured providers (zero is OK)
- login-by-code flow; passkey options endpoint reachable
- unverified social email does not connect to an existing account
- requested scopes are identity-only
