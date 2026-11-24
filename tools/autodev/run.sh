#!/usr/bin/env bash
# One autonomous build iteration (authorized by Fabio 2026-11-09). State lives in git + docs/STATE.md.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 0
D=tools/autodev; source $D/budget.conf; source ~/.claude-oauth-env 2>/dev/null
export DATABASE_URL=postgres://biohackit:biohackit@localhost:5433/biohackit  # local TimescaleDB container biohackit-db (managed by admin)
export DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY:-autodev-local-not-secret} SECRET_KEY=${SECRET_KEY:-autodev-local-not-secret} DEBUG=${DEBUG:-1}
exec 9>/tmp/biohackit-autodev.lock; flock -n 9 || exit 0
[ -f $D/STOP ] && exit 0
git pull -q --rebase --autostash origin main || { git rebase --abort 2>/dev/null; echo "$(date -Is) pull failed" >> $D/runner.log; exit 0; }
SPENT=$(python3 -c "
import json,time
t=time.time()-7*86400;s=0
try:
 for l in open('$D/ledger.jsonl'):
  r=json.loads(l); s+=r.get('usd',0) if r['ts']>t else 0
except FileNotFoundError: pass
print(round(s,2))")
if python3 -c "import sys;sys.exit(0 if $SPENT>=$WEEKLY_USD else 1)"; then
  echo "$(date -Is) budget reached $SPENT/$WEEKLY_USD" >> $D/runner.log; exit 0; fi
TOOLS='Read Edit Write Glob Grep Bash(git:*) Bash(python3:*) Bash(pip:*) Bash(pytest:*) Bash(node:*) Bash(npm:*) Bash(npx:*) Bash(ls:*) Bash(mkdir:*) Bash(cat:*) Bash(sed:*) Bash(grep:*) Bash(find:*) Bash(mv:*) Bash(cp:*) Bash(rm:*) Bash(psql:*) Bash(createdb:*) Bash(cd:*) Bash(echo:*) Bash(touch:*) Bash(head:*) Bash(tail:*) Bash(wc:*) Bash(pnpm:*) Bash(curl -s https://api.github.com/repos/hackingbiology/biohackit/actions:*) Bash(pg_isready:*) Bash(.venv/bin/python:*) Bash(.venv/bin/pytest:*) Bash(.venv/bin/ruff:*) Bash(.venv/bin/pip:*) Bash(.venv/bin/django-admin:*) Bash(backend/.venv/bin/python:*) Bash(backend/.venv/bin/pytest:*) Bash(backend/.venv/bin/ruff:*) Bash(backend/.venv/bin/pip:*) Bash(backend/.venv/bin/django-admin:*) Bash(/home/gl-auditor/biohackit/backend/.venv/bin/python:*) Bash(/home/gl-auditor/biohackit/backend/.venv/bin/pytest:*) Bash(/home/gl-auditor/biohackit/backend/.venv/bin/ruff:*) Bash(/home/gl-auditor/biohackit/backend/.venv/bin/pip:*) Bash(/home/gl-auditor/biohackit/backend/.venv/bin/django-admin:*)'
CI=$(curl -s -m 15 "https://api.github.com/repos/hackingbiology/biohackit/actions/workflows/ci.yml/runs?branch=main&per_page=5" | python3 -c "
import json,sys
try:
 rs=[r for r in json.load(sys.stdin)['workflow_runs'] if r['conclusion']]
 r=rs[0]; print(f\"{r['conclusion']} on {r['head_sha'][:7]} ({r['display_title'][:60]}) {r['html_url']}\")
except Exception: print('unknown')")
OUT=$(timeout 3h claude -p "$(cat $D/PROMPT.md)

Last GitHub CI result on main: $CI" --allowedTools $TOOLS \
      --model ${MODEL:-sonnet} --max-turns $MAX_TURNS --output-format json 2>>$D/runner.log)
echo "$OUT" > $D/last-result.json
python3 -c "
import json,sys,time
try: r=json.loads(sys.argv[1])
except Exception: r={}
u=r.get('usage',{})
print(json.dumps({'ts':time.time(),'usd':r.get('total_cost_usd',0),'in':u.get('input_tokens',0),'out':u.get('output_tokens',0),'turns':r.get('num_turns'),'err':r.get('is_error')}))" "$OUT" >> $D/ledger.jsonl
echo "$(date -Is) iteration done (spent before $SPENT)" >> $D/runner.log
git add $D/ledger.jsonl; git commit -qm "autodev: ledger" 2>/dev/null; git push -q origin main 2>/dev/null
exit 0
