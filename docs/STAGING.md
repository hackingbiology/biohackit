# Staging

Public test instance of biohack.it at <http://51.158.36.151:18800>.

**Policy:** demo data only, `X-Robots-Tag: noindex` on every response, no
password wall. Never put real health data here.

## Run

```bash
export SECRET_KEY='<long random string>'        # required, no default
export DEMO_USERNAME='demo@example.com'         # optional; the demo account's e-mail
export DEMO_PASSWORD='<password>'               # optional; set on the account, not used by the UI
docker compose -f docker-compose.staging.yml up -d --build
```

If `DEMO_USERNAME` or `DEMO_PASSWORD` is unset, `seed_demo` skips and creates
nothing. The seed creates only that one account; no measurements, ranges or
doses (see `docs/QUESTIONS.md`).

## Signing in

The sign-in form is passwordless: it asks for an e-mail and sends a code. On
staging the e-mail backend is the console, so the code is printed in the
backend logs. Read it with:

```bash
docker compose -f docker-compose.staging.yml logs backend
```

and enter it for the demo e-mail. `DEMO_PASSWORD` is stored on the account but
no page in the UI accepts it.

## What runs

- `backend`: migrate, collectstatic, `seed_demo`, then gunicorn; `DEBUG=false`,
  `NOINDEX=true`. Not published on the host.
- `frontend`: the Next standalone production server (`node server.js`, the
  `next start` equivalent for `output: standalone`). Rewrites `/api` and
  `/_allauth` to `http://backend:8000`; these and `NOINDEX` are fixed at build
  time via build args.
- `db`: TimescaleDB, not published.
- Only `18800:3000` is published on the host.

## Troubleshooting: `ERR_PNPM_IGNORED_BUILDS`

pnpm 10 and later fail `pnpm install` when a dependency has a build script
that is neither allowed nor ignored. The frontend therefore pins pnpm with
`packageManager` in `frontend/package.json` (read by `corepack enable` in
`frontend/Dockerfile`) and declares the policy next to it:

- `pnpm.onlyBuiltDependencies`: `sharp` (native image optimisation for
  `next build`).
- `pnpm.ignoredBuiltDependencies`: `unrs-resolver` (only used by lint tooling).

To approve a new dependency's build script, add its name to
`onlyBuiltDependencies`; to refuse it, add it to `ignoredBuiltDependencies`.
Keep `BUILD_SCRIPT_PACKAGES` in `frontend/src/__tests__/pnpm-build-policy.test.ts`
in step. If you bump the pinned pnpm, move the policy to the place that
version reads (`pnpm-workspace.yaml` in newer pnpm) and copy that file in the
Dockerfile `deps` stage.
