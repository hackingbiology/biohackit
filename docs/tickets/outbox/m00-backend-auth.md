# [M00] Backend auth and user model

Labels: autodev, feature
Milestone: M00 Foundations
Parent: #3

## Goal

Email-primary custom User, public-by-default Profile (biological traits), social/forum
handles, and JWT auth endpoints (register, token, refresh, me) plus a public profile read.

## Spec refs

- `openspec/specs/accounts-and-profiles` (server-hosted account, public-by-default, biological profile, social handles)
- `openspec/changes/m00-foundations/specs/foundations-architecture.md` §JWT authentication

## Acceptance

- Account needed to contribute: write/me endpoints need auth; public profile reads do not
- Stable traits captured: date_of_birth, sex, ethnicity, height_cm stored and returned
- Social and forum handles linked: telegram, wechat, xiaohongshu, rapamycin_news
- JWT token issued and refreshed (access 15 min, refresh 7 days)
