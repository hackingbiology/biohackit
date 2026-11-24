#!/usr/bin/env bash
# Deterministic quality gates. APPEND-ONLY: removing or weakening a line is rejected by the orchestrator.
# Usage: tools/autodev2/gates.sh [base-ref]   (env BASE_COVERED = covered scenarios on base)
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 2
BASE=${1:-origin/main}; FAIL=0
step() { echo "=== GATE: $1"; }
bad() { echo "!!! GATE FAILED: $1"; FAIL=1; }

step "protected paths"
CHANGED=$(git diff --name-only "$BASE"...HEAD)
echo "$CHANGED" | grep -E '^tools/autodev2/' | grep -vE '^tools/autodev2/gates\.sh$' && bad "orchestrator files modified"
git diff "$BASE"...HEAD -- tools/autodev2/gates.sh | grep -E '^-[^-]' && bad "gates.sh lines removed/changed (append-only)"

step "secrets"
git diff "$BASE"...HEAD | grep -E '^\+' | grep -nE 'sk-ant-|BEGIN [A-Z ]*PRIVATE KEY|ghp_[A-Za-z0-9]{20}|AKIA[0-9A-Z]{16}' && bad "secret-like string added"

step "backend ruff format"; backend/.venv/bin/ruff format --check backend || bad "ruff format"
step "backend ruff check";  backend/.venv/bin/ruff check backend || bad "ruff check"
step "backend migrations";  backend/.venv/bin/python backend/manage.py makemigrations --check --dry-run >/dev/null || bad "missing migrations"
step "backend pytest";      backend/.venv/bin/pytest -q -p no:cacheprovider backend 2>&1 | tail -25; [ "${PIPESTATUS[0]}" = 0 ] || bad "pytest"

if [ -f frontend/package.json ]; then
  step "frontend lint";       pnpm --dir frontend lint >/tmp/gate-fe-$$.log 2>&1 || { tail -30 /tmp/gate-fe-$$.log; bad "eslint"; }
  step "frontend type-check"; pnpm --dir frontend type-check >/tmp/gate-fe-$$.log 2>&1 || { tail -30 /tmp/gate-fe-$$.log; bad "tsc"; }
  step "frontend jest";       pnpm --dir frontend test:ci >/tmp/gate-fe-$$.log 2>&1 || { tail -40 /tmp/gate-fe-$$.log; bad "jest"; }
  rm -f /tmp/gate-fe-$$.log
fi

step "traceability"
python3 tools/trace/matrix.py --strict || bad "test declares unknown scenario id"
COV=$(python3 tools/trace/matrix.py --json | python3 -c "import json,sys;print(json.load(sys.stdin)['covered'])")
echo "covered=$COV base=${BASE_COVERED:-?}"
[ -n "${BASE_COVERED:-}" ] && [ "$COV" -lt "$BASE_COVERED" ] && bad "scenario coverage regressed"

[ $FAIL = 0 ] && echo "ALL GATES PASSED" || echo "GATES FAILED"
exit $FAIL
