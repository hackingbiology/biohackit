#!/usr/bin/env bash
# One autonomous build iteration (authorized by Fabio 2026-11-09). State lives in git + docs/STATE.md.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 0
D=tools/autodev; source $D/budget.conf; source ~/.claude-oauth-env 2>/dev/null
exec 9>/tmp/biohackit-autodev.lock; flock -n 9 || exit 0
[ -f $D/STOP ] && exit 0
git pull -q --rebase origin main || { git rebase --abort; exit 0; }
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
TOOLS='Read Edit Write Glob Grep Bash(git:*) Bash(python3:*) Bash(pip:*) Bash(pytest:*) Bash(node:*) Bash(npm:*) Bash(npx:*) Bash(ls:*) Bash(mkdir:*) Bash(cat:*) Bash(sed:*) Bash(grep:*) Bash(find:*) Bash(mv:*) Bash(cp:*) Bash(rm:*) Bash(psql:*) Bash(createdb:*) Bash(cd:*) Bash(echo:*) Bash(touch:*) Bash(head:*) Bash(tail:*) Bash(wc:*)'
OUT=$(timeout 3h claude -p "$(cat $D/PROMPT.md)" --allowedTools $TOOLS \
      --max-turns $MAX_TURNS --output-format json 2>>$D/runner.log)
python3 -c "
import json,sys,time
try: r=json.loads(sys.argv[1])
except Exception: r={}
u=r.get('usage',{})
print(json.dumps({'ts':time.time(),'usd':r.get('total_cost_usd',0),'in':u.get('input_tokens',0),'out':u.get('output_tokens',0),'turns':r.get('num_turns'),'err':r.get('is_error')}))" "$OUT" >> $D/ledger.jsonl
echo "$(date -Is) iteration done (spent before $SPENT)" >> $D/runner.log
git add $D/ledger.jsonl; git commit -qm "autodev: ledger" 2>/dev/null; git push -q origin main 2>/dev/null
exit 0
