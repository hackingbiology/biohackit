# Change: m00b — Low-friction login (social + forum SSO + passwordless)

## Why
Fabio (2026-11-19): sign-up friction must be minimal. Users must be able to sign in with the accounts they already have, above all their **rapamycin.news** forum account (the community biohack.it is born from), with the smallest possible software footprint. This supersedes M00 decision D2 ("OAuth stubbed until M13"): social login is now in scope for M00.

## What changes
- One library does all of it: **django-allauth** (already a dependency), upgraded to ≥65 for `allauth.socialaccount`, `allauth.headless` (API for the Next.js frontend, no frontend auth library) and `allauth.mfa` passkeys. No other auth package is added.
- Providers enabled in this order:
  - **rapamycin.news**: Discourse, via the **DiscourseConnect provider** protocol. allauth has no built-in provider for it, so it gets a small custom provider: HMAC-SHA256 signed payload plus nonce, about 100 lines, with no new dependency. It requires the forum admin to enable `enable discourse connect provider` and share a secret.
  - Google, Microsoft (personal + work/school), Apple, Facebook/Meta, WeChat (`weixin`).
  - Also available through configuration only (they are built into allauth): GitHub, X, LinkedIn (OIDC), Telegram, plus any generic OpenID Connect provider.
- Passwordless: **email login code** (`ACCOUNT_LOGIN_BY_CODE_ENABLED`) and **passkeys** (WebAuthn via `allauth.mfa`). Email + password remains.
- A provider appears in the UI **only if its credentials are configured** (env/admin), so a self-hosted instance works with none of them.
- Account linking: same verified email ⇒ the social account is offered for connection to the existing account, never silently merged unless the provider's email is verified. Any number of providers per account.
- The rapamycin.news login also pre-fills the `SocialHandle(platform=rapamycin_news)` of the profile (username + profile URL), creating the link between forum identity and protocol page.

## Decisions
| # | Question | Decision | Why |
|---|----------|----------|-----|
| L1 | Libraries | allauth only (+ existing simplejwt if still needed by headless token strategy) | Minimum footprint, 1 maintained library covers 100+ providers, passkeys and headless API |
| L2 | Discord | Not included | Fabio 2026-11-19 |
| L3 | rapamycin.news mechanism | DiscourseConnect provider (custom allauth provider) | Discourse has no native OAuth/OIDC provider; DiscourseConnect is its official SSO-provider protocol |
| L4 | Data minimisation | Request only identity scopes (openid, email, profile); no contacts/friends | Health platform, privacy by design |

## Out of scope
Creating provider apps/secrets (Fabio's action list in tasks.md), and the provider-side approval reviews (Apple, Meta, WeChat require developer accounts).
