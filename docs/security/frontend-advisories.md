# Frontend advisories fixed by upgrading `next`

Plain language: the web app framework (`next`) was pinned at 15.1.0, which has known
serious security problems. We moved it to the newest 15.x release, 15.5.29, which has the
fixes. `eslint-config-next` moved with it so the two stay in step.

- Before: `next` 15.1.0, `eslint-config-next` 15.1.0
- After: `next` 15.5.29, `eslint-config-next` 15.5.29 (newest stable 15.x from `pnpm view next versions --json`, run 2026-11-25)
- Command: `pnpm --dir frontend audit --prod --json` (run 2026-11-25, before the upgrade). All values below are copied from its output (`github_advisory_id`, `severity`, `patched_versions`).
- After the upgrade the same command lists no advisory for `next`.

The recorded command output (trimmed to GHSA id, module, severity, vulnerable and patched
ranges, URL, title) is committed in `docs/security/recorded/`: `audit-before.json`,
`audit-after.json` and `next-versions.json` (stable 15.x only). The test
`backend/tests/test_frontend_advisories.py` checks that this table equals the high and
critical `next` advisories in `audit-before.json`, that `audit-after.json` has none for
`next`, and that the pin is the newest recorded release.

Each row's URL is `https://github.com/advisories/<GHSA>`.

| GHSA | Severity | Module | Patched range |
|------|----------|--------|---------------|
| GHSA-67rr-84xm-4c7r | high | next | >=15.1.8 |
| GHSA-9qr9-h5gf-34mp | critical | next | >=15.1.9 |
| GHSA-f82v-jwr5-mffw | critical | next | >=15.2.3 |
| GHSA-q4gf-8mx6-v5v3 | high | next | >=15.5.15 |
| GHSA-8h8q-6873-q5fj | high | next | >=15.5.16 |
| GHSA-mg66-mrh9-m8jx | high | next | >=15.5.16 |
| GHSA-c4j6-fc7j-m34r | high | next | >=15.5.16 |
| GHSA-36qx-fr4f-26g5 | high | next | >=15.5.16 |
| GHSA-m99w-x7hq-7vfj | high | next | >=15.5.21 |
| GHSA-89xv-2m56-2m9x | high | next | >=15.5.21 |
| GHSA-p9j2-gv94-2wf4 | high | next | >=15.5.21 |
| GHSA-p293-qw3h-jr36 | critical | next | >=15.5.24 |
| GHSA-2xp9-vwfh-vxw4 | critical | next | >=15.5.24 |
| GHSA-2464-fhr4-w9xw | critical | next | >=15.5.28 |
| GHSA-p3m5-59mp-jv5r | high | next | >=15.5.28 |

## Still open (not `next` itself)

After the upgrade `pnpm audit --prod` still reports `postcss` 8.4.31 (the copy bundled
inside `next`): GHSA-6g55-p6wh-862q and GHSA-r28c-9q8g-f849 (high), GHSA-qx2v-qp2m-jg93
and GHSA-fxqj-rqcc-2cmp (moderate). They are handled in B2; see QUESTIONS Q33.
