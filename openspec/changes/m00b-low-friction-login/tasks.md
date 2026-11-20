# Tasks — m00b low-friction login
Depends on M00 TG2 (accounts app). Ticket: m00b-low-friction-login.

## TG1 Backend
- [x] Upgrade django-allauth to ≥65 (`[mfa,socialaccount]`); enable `allauth.socialaccount`, `allauth.headless`, `allauth.mfa`; fix deprecated `ACCOUNT_EMAIL_REQUIRED/USERNAME_REQUIRED` → `ACCOUNT_SIGNUP_FIELDS`, `ACCOUNT_LOGIN_METHODS={"email"}`
- [x] Providers google, microsoft, apple, facebook, weixin (+ github, twitter_oauth2, openid_connect, telegram available) configured from env (`SOCIALACCOUNT_PROVIDERS` built only for those with credentials); `.env.example` documents each variable
- [x] Custom provider `accounts/providers/discourse_connect/` (generic DiscourseConnect, instance `rapamycin_news`: base URL + secret from env): build signed request, verify `sig` with `hmac.compare_digest`, single-use nonce with expiry, map `external_id`/`email`/`username`/`name`; fill `SocialHandle(rapamycin_news)`
- [x] `ACCOUNT_LOGIN_BY_CODE_ENABLED=True`; passkeys (`MFA_PASSKEY_LOGIN_ENABLED`, `MFA_PASSKEY_SIGNUP_ENABLED`)
- [x] Linking rule: `SOCIALACCOUNT_EMAIL_AUTHENTICATION=True` only with verified provider emails; `SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT=True`
- [x] Headless API: frontend uses allauth headless endpoints (`/_allauth/browser/v1/...`); keep `/api/auth/me/` working

## TG2 Frontend
- [ ] Sign-in/sign-up page: provider buttons fetched from headless `config` endpoint (only configured ones), rapamycin.news first; email-code and passkey options; plain language, WCAG 2.2 AA, EN/IT/ZH strings
- [ ] No new frontend auth dependency (plain fetch to headless API; WebAuthn via browser API)

## TG3 Tests (one per SHALL scenario)
- [x] DiscourseConnect: valid payload → login + handle; bad sig → rejected; replayed nonce → rejected
- [x] Config endpoint lists only configured providers; zero providers OK
- [x] Login by code flow; passkey options endpoint reachable
- [x] Unverified social email does not auto-connect to existing account
- [x] Requested scopes are identity-only (assert settings)

## Fabio's action list (not for the agent)
- [ ] Ask the rapamycin.news admin to enable *DiscourseConnect provider* with a shared secret and return URL https://biohack.it/…/discourse_connect/callback
- [ ] Create OAuth apps: Google Cloud, Microsoft Entra (personal+org), Apple Developer (Sign in with Apple, paid), Meta for Developers, WeChat Open Platform (requires Chinese entity/verification)
