#!/usr/bin/env python3
"""biohack.it autodev v2 — continuous multi-agent graph (OpenSpec change m00c-autodev-v2).

Graph per task: planner -> implementer -> gates (deterministic) -> parallel adversarial
reviewers -> verifier -> fix loop -> rebase + gates -> push to main.
Stdlib only. Runs as systemd service under gl-auditor. State persists in state/.
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "tools/autodev2"
STATE = D / "state"
WT_BASE = ROOT.parent / "biohackit-wt"
TZ = ZoneInfo("Europe/Rome")
USAGE_FILE = Path("/var/lib/biohackit-usage/usage.json")

CFG = {
    "weekly_share_pct": 40.0,  # Fabio 2026-11-24
    "account_stop_pct": 90.0,
    "pace_headroom_pct": 6.0,
    "usd_per_pct_default": 4.0,
    "models": {"planner": "opus", "implementer": "sonnet", "reviewer": "opus", "verifier": "sonnet"},
    "max_gate_rounds": 3,
    "max_review_rounds": 2,
    "digest_hour": (8, 15),
}

WRITE_TOOLS = (
    "Read,Edit,Write,Glob,Grep,Bash(git add:*),Bash(git commit:*),Bash(git status:*),Bash(git diff:*),Bash(git log:*),Bash(git show:*),Bash(git mv:*),Bash(git rm:*),Bash(python3:*),Bash(node:*),Bash(pnpm:*),Bash(npx:*),"
    "Bash(ls:*),Bash(mkdir:*),Bash(cat:*),Bash(sed:*),Bash(grep:*),Bash(find:*),Bash(mv:*),Bash(cp:*),"
    "Bash(rm:*),Bash(touch:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(diff:*),Bash(pg_isready:*),"
    "Bash(bash tools/autodev2/gates.sh:*),Bash(backend/.venv/bin/python:*),Bash(backend/.venv/bin/pytest:*),"
    "Bash(backend/.venv/bin/ruff:*),Bash(backend/.venv/bin/pip:*),Bash(curl -s:*),WebFetch,WebSearch"
)
READ_TOOLS = "Read,Glob,Grep,Bash(git diff:*),Bash(git log:*),Bash(git show:*),Bash(ls:*),Bash(cat:*),Bash(grep:*)"
VERIFY_TOOLS = READ_TOOLS + ",WebFetch"


# ----------------------------------------------------------------------------- utils
def now() -> dt.datetime:
    return dt.datetime.now(TZ)


def log(msg: str) -> None:
    line = f"{now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with open(STATE / "orchestrator.log", "a") as f:
        f.write(line + "\n")


def sh(cmd: str, cwd: Path = ROOT, timeout: int = 1800, env: dict | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, **(env or {})})
    return p.returncode, (p.stdout + p.stderr)


def jload(p: Path, default):
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def jsave(p: Path, obj) -> None:
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False))
    tmp.replace(p)


def extract_json(text: str):
    """Last fenced ```json block, else last {...} object."""
    blocks = re.findall(r"```json\s*(.*?)```", text, re.S)
    for cand in reversed(blocks):
        try:
            return json.loads(cand)
        except Exception:
            pass
    for m in reversed(list(re.finditer(r"\{.*\}", text, re.S))):
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None


# ----------------------------------------------------------------------------- budget
def usage_pct() -> tuple[float | None, str | None]:
    u = jload(USAGE_FILE, {})
    if not u or time.time() - u.get("sampled_at", 0) > 3 * 3600:
        return None, None
    sd = u.get("seven_day") or {}
    return sd.get("utilization"), sd.get("resets_at")


def ledger() -> list[dict]:
    p = STATE / "ledger.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def budget_status() -> dict:
    util, resets = usage_pct()
    week_start = time.time() - 7 * 86400
    if resets:
        week_start = dt.datetime.fromisoformat(resets).timestamp() - 7 * 86400
    rows = [r for r in ledger() if r["ts"] >= week_start]
    usd = sum(r.get("usd", 0) for r in rows)
    dpct = sum(r.get("dpct", 0) for r in rows if r.get("dpct") is not None)
    cal = [r for r in ledger() if r.get("dpct")]
    usd_per_pct = (sum(r["usd"] for r in cal) / sum(r["dpct"] for r in cal)) if sum(r["dpct"] for r in cal) >= 2 else CFG["usd_per_pct_default"]
    share = max(dpct, usd / usd_per_pct)  # conservative: the larger of the two estimates
    elapsed = min(1.0, max(0.0, (time.time() - week_start) / (7 * 86400)))
    allowed = min(CFG["weekly_share_pct"], CFG["weekly_share_pct"] * elapsed + CFG["pace_headroom_pct"])
    ok = share < allowed and (util is None or util < CFG["account_stop_pct"])
    return {"ok": ok, "share": round(share, 2), "allowed": round(allowed, 2), "account": util,
            "usd_week": round(usd, 2), "usd_per_pct": round(usd_per_pct, 2), "stale_usage": util is None}


# ----------------------------------------------------------------------------- agents
def agent(role: str, prompt: str, cwd: Path, tools: str, max_turns: int, task: str) -> str:
    model = CFG["models"][role]
    u0, _ = usage_pct()
    t0 = time.time()
    cmd = ["claude", "-p", prompt, "--model", model, "--max-turns", str(max_turns),
           "--output-format", "json", "--allowedTools", *[t.strip() for t in tools.split(",") if t.strip()]]
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=3 * 3600)
        out = p.stdout
        if not out.strip():
            log(f"  agent {role} produced no output, rc={p.returncode}: {p.stderr[:500]}")
            raise RuntimeError("agent call failed")
    except subprocess.TimeoutExpired:
        out = ""
    r = jload_str(out)
    u1, _ = usage_pct()
    dpct = (u1 - u0) if (u0 is not None and u1 is not None and u1 >= u0) else None
    rec = {"ts": time.time(), "role": role, "model": model, "task": task, "usd": r.get("total_cost_usd", 0) or 0,
           "turns": r.get("num_turns"), "err": r.get("is_error"), "secs": round(time.time() - t0), "dpct": dpct}
    with open(STATE / "ledger.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    log(f"  agent {role}/{model} turns={rec['turns']} usd={rec['usd']:.2f} dpct={dpct} err={rec['err']}")
    return r.get("result", "") or ""


def jload_str(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        return {}


def prompt(name: str, **kw) -> str:
    text = (D / "prompts" / f"{name}.md").read_text()
    common = (D / "prompts" / "_rules.md").read_text()
    for k, v in kw.items():
        text = text.replace("{{" + k + "}}", v if isinstance(v, str) else json.dumps(v, indent=1, ensure_ascii=False))
    return common + "\n\n" + text


# ----------------------------------------------------------------------------- git / gates
def covered_on_main() -> int:
    rc, out = sh("python3 tools/trace/matrix.py --json")
    try:
        return json.loads(out)["covered"]
    except Exception:
        return 0


def gates(wt: Path) -> tuple[bool, str]:
    rc, out = sh("bash tools/autodev2/gates.sh origin/main", cwd=wt, timeout=3600,
                 env={"BASE_COVERED": str(covered_on_main())})
    tail = "\n".join(out.splitlines()[-120:])
    return rc == 0, tail


def make_worktree(slug: str) -> Path:
    wt = WT_BASE / slug
    sh("git fetch -q origin")
    if wt.exists():
        sh(f"git worktree remove --force {wt}")
    sh(f"git branch -D autodev/{slug}")
    rc, out = sh(f"git worktree add -q -b autodev/{slug} {wt} origin/main")
    if rc:
        raise RuntimeError(out)
    for rel in ("backend/.venv", "frontend/node_modules"):
        if (ROOT / rel).exists() and not (wt / rel).exists():
            (wt / rel).symlink_to(ROOT / rel)
    return wt


def drop_worktree(slug: str) -> None:
    sh(f"git worktree remove --force {WT_BASE / slug}")
    sh(f"git branch -D autodev/{slug}")


def diff_of(wt: Path) -> str:
    _, d = sh("git diff --stat origin/main...HEAD && git diff origin/main...HEAD", cwd=wt)
    return d[:120_000]


def merge(wt: Path, task: dict) -> tuple[bool, str]:
    for attempt in range(3):
        sh("git fetch -q origin", cwd=wt)
        rc, out = sh("git rebase -q origin/main", cwd=wt)
        if rc:
            sh("git rebase --abort", cwd=wt)
            return False, "rebase conflict: " + out[-2000:]
        ok, g = gates(wt)
        if not ok:
            return False, "gates failed after rebase:\n" + g
        rc, out = sh("git push -q origin HEAD:main", cwd=wt)
        if rc == 0:
            sh("git pull -q --ff-only origin main")
            return True, "merged"
        time.sleep(20)
    return False, "push failed: " + out[-1000:]


# ----------------------------------------------------------------------------- graph
def plan(history: list[dict]) -> dict | None:
    sh("git pull -q --ff-only origin main")
    _, matrix = sh("python3 tools/trace/matrix.py")
    ok_main, gate_tail = gates_on_main()
    ctx = {
        "matrix": matrix.strip(),
        "main_gates": "PASS" if ok_main else "FAIL\n" + gate_tail[-4000:],
        "open_changes": sorted(p.name for p in (ROOT / "openspec/changes").iterdir() if p.is_dir() and p.name != "archive"),
        "recent_tasks": [{k: (str(v)[:400]) for k, v in h.items()} for h in history[-12:]],
    }
    out = agent("planner", prompt("planner", context=ctx), ROOT, READ_TOOLS, 30, "plan")
    t = extract_json(out)
    if not t or "slug" not in t:
        log("planner returned no task JSON")
        return None
    t["slug"] = re.sub(r"[^a-z0-9-]+", "-", t["slug"].lower())[:50].strip("-") or "task"
    return t


_main_gate_cache: dict = {}


def gates_on_main() -> tuple[bool, str]:
    rc, head = sh("git rev-parse HEAD")
    head = head.strip()
    if _main_gate_cache.get("head") != head:
        wt = make_worktree("main-check")
        ok, tail = gates(wt)
        drop_worktree("main-check")
        _main_gate_cache.update(head=head, ok=ok, tail=tail)
    return _main_gate_cache["ok"], _main_gate_cache["tail"]


def review(wt: Path, task: dict) -> list[dict]:
    diff = diff_of(wt)
    lenses = ["correctness-spec", "science-security"]
    if task.get("frontend"):
        lenses.append("a11y-frontend")
    with cf.ThreadPoolExecutor(len(lenses)) as ex:
        futs = {ex.submit(agent, "reviewer", prompt("reviewer", lens=lens, task=task, diff=diff), wt, READ_TOOLS, 25,
                          task["slug"]): lens for lens in lenses}
        findings = []
        for f in cf.as_completed(futs):
            j = extract_json(f.result()) or {}
            for x in j.get("findings", []):
                x["lens"] = futs[f]
                findings.append(x)
    findings = [f for f in findings if f.get("severity") in ("critical", "high", "medium")]
    if not findings:
        return []
    out = agent("verifier", prompt("verifier", task=task, findings=findings), wt, VERIFY_TOOLS, 30, task["slug"])
    j = extract_json(out) or {}
    return [f for f in j.get("verdicts", []) if f.get("confirmed")]


def run_task(task: dict) -> dict:
    slug = task["slug"]
    log(f"TASK {slug}: {task.get('title')}")
    wt = make_worktree(slug)
    _, base = sh("git rev-parse HEAD", cwd=wt)
    base = base.strip()
    result = {"slug": slug, "title": task.get("title"), "change": task.get("change"), "start": now().isoformat()}
    feedback, confirmed, ok, tail = "", [], False, ""
    try:
        for rnd in range(CFG["max_review_rounds"] + 1):
            for g in range(CFG["max_gate_rounds"]):
                agent("implementer", prompt("implementer", task=task, feedback=feedback or "none"), wt, WRITE_TOOLS, 80, slug)
                sh("git add -A && git commit -qm 'autodev: wip' || true", cwd=wt)  # never lose work
                ok, tail = gates(wt)
                if ok:
                    break
                feedback = "Deterministic gates FAILED. Fix all of these, then rerun bash tools/autodev2/gates.sh origin/main:\n" + tail
                log(f"  gates failed (round {g + 1})")
            if not ok:
                result.update(status="failed-gates", detail=tail[-3000:])
                return result
            confirmed = review(wt, task)
            log(f"  review round {rnd + 1}: {len(confirmed)} confirmed findings")
            if not confirmed:
                break
            feedback = "Adversarial review CONFIRMED these defects. Fix each one, adding a test where applicable:\n" + json.dumps(confirmed, indent=1)
        blocking = [c for c in confirmed if c.get("severity") in ("critical", "high")]
        if blocking:
            result.update(status="failed-review", detail=json.dumps(blocking)[:3000])
            file_ticket(f"[review] Blocking findings left on {slug}", json.dumps(blocking, indent=1))
            return result
        sh(f"git reset -q --soft {base}", cwd=wt)  # squash wip commits into one, on the original base
        msg = (f"{task.get('title', slug)}\n\n{task.get('summary', '')}\n\nChange: {task.get('change', '-')}"
               f"\n{task.get('refs', '')}\n\nautodev2 graph: planner -> implementer -> gates -> adversarial review -> verify\n\n"
               "Co-Authored-By: Claude <noreply@anthropic.com>")
        (STATE / "msg.txt").write_text(msg)
        sh(f"git commit -q -F {STATE / 'msg.txt'}", cwd=wt)
        ok, why = merge(wt, task)
        result.update(status="merged" if ok else "failed-merge", detail=why[-3000:])
        if ok and confirmed:
            file_ticket(f"[review] Residual medium findings on {slug}", json.dumps(confirmed, indent=1))
        return result
    finally:
        drop_worktree(slug)
        result["end"] = now().isoformat()


def file_ticket(title: str, body: str, labels: str = "autodev") -> None:
    p = ROOT / "docs/tickets/outbox" / f"{int(time.time())}-{re.sub(r'[^a-z0-9]+', '-', title.lower())[:40]}.md"
    p.write_text(f"# {title}\n\nLabels: {labels}\n\n{body}\n")
    sh(f"git add {p} && git commit -qm 'ticket: {title[:60]}' && git push -q origin HEAD:main")


# ----------------------------------------------------------------------------- digest
def digest_due() -> bool:
    n = now()
    h, m = CFG["digest_hour"]
    return (n.hour, n.minute) >= (h, m) and not (ROOT / f"docs/digest/{n:%Y-%m-%d}.md").exists()


def write_digest(history: list[dict]) -> None:
    sh("git pull -q --ff-only origin main")
    n = now()
    since = (n - dt.timedelta(days=1)).timestamp()
    _, mx = sh("python3 tools/trace/matrix.py --write")
    _, commits = sh(f"git log --since=@{int(since)} --no-merges --format='- %h %s' origin/main | grep -v -E 'ledger|tickets:|digest' | head -60")
    day = [h for h in history if h.get("end", "") >= (n - dt.timedelta(days=1)).isoformat()]
    failed = [h for h in day if h.get("status") != "merged"]
    b = budget_status()
    qpath = ROOT / "docs/QUESTIONS.md"
    q_new = ""
    if qpath.exists():
        _, q_new = sh(f"git log --since=@{int(since)} -p --format= -- docs/QUESTIONS.md | grep -E '^\\+[^+]' | sed 's/^+//' | head -40")
    body = [f"# Daily digest {n:%Y-%m-%d}", "",
            f"**Traceability:** {mx.strip()}  ",
            f"**Tasks (24h):** {len(day)} run, {len(day) - len(failed)} merged, {len(failed)} failed  ",
            f"**Budget:** autodev share {b['share']}% of weekly limit (allowed now {b['allowed']}%, cap {CFG['weekly_share_pct']}%), account {b['account']}%, {b['usd_week']} USD-equiv this week  ",
            f"**Staging:** http://51.158.36.151:18800", "", "## Merged", commits.strip() or "- none", "",
            "## Failed / abandoned"] + [f"- `{h['slug']}` {h.get('status')}: {(h.get('detail') or '')[:300].replace(chr(10), ' ')}" for h in failed] + \
           ["" if failed else "- none", "", "## New questions and defaults taken (docs/QUESTIONS.md)", q_new.strip() or "- none", ""]
    text = "\n".join(body) + "\n"
    (ROOT / "docs/digest").mkdir(exist_ok=True)
    (ROOT / f"docs/digest/{n:%Y-%m-%d}.md").write_text(text)
    (ROOT / f"docs/tickets/outbox/digest-{n:%Y-%m-%d}.md").write_text(f"# Daily digest {n:%Y-%m-%d}\n\nLabels: digest\n\n" + "\n".join(body[2:]) + "\n")
    sh(f"git add docs/digest docs/TRACEABILITY.md docs/tickets/outbox && git commit -qm 'digest {n:%Y-%m-%d}' && git push -q origin HEAD:main")
    log("digest written")


# ----------------------------------------------------------------------------- main loop
def main() -> None:
    STATE.mkdir(exist_ok=True)
    WT_BASE.mkdir(exist_ok=True)
    hist_p = STATE / "history.json"
    history = jload(hist_p, [])
    log("orchestrator start")
    fails_in_row = 0
    while True:
        if (D / "STOP").exists():
            log("STOP file present; sleeping")
            time.sleep(600)
            continue
        try:
            if digest_due():
                write_digest(history)
            b = budget_status()
            jsave(STATE / "budget.json", b)
            if not b["ok"]:
                log(f"budget pause: {b}")
                time.sleep(1800)
                continue
            task = plan(history)
            if not task:
                fails_in_row += 1
                time.sleep(min(3600, 300 * fails_in_row))
                continue
            res = run_task(task)
            history.append(res)
            jsave(hist_p, history[-500:])
            log(f"RESULT {res['slug']}: {res['status']}")
            fails_in_row = 0 if res["status"] == "merged" else fails_in_row + 1
            if fails_in_row >= 3:
                log("3 failures in a row; cooling down 1h")
                time.sleep(3600)
        except Exception as e:  # keep the loop alive, never die silently
            log(f"ERROR {type(e).__name__}: {e}")
            time.sleep(600)


if __name__ == "__main__":
    if "--budget" in sys.argv:
        STATE.mkdir(exist_ok=True)
        print(json.dumps(budget_status(), indent=1))
    elif "--digest" in sys.argv:
        STATE.mkdir(exist_ok=True)
        write_digest(jload(STATE / "history.json", []))
    else:
        main()
