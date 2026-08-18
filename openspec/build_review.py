#!/usr/bin/env python3
"""Build a single self-contained HTML review page from the OpenSpec tree.

Output: openspec/review.html  (publish as an Artifact for comfortable review).
Faithful to specs/*/spec.md; regenerate after edits by re-running this script.
"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SPECS = ROOT / "specs"

# (dir, module code, phase, short-code for requirement chips)
MODULES = [
    ("domain-model",             "cross-cutting", "0",   "DOMAIN"),
    ("ai-uses-and-attribution",  "cross-cutting", "0",   "AIUSES"),
    ("accounts-and-profiles",    "onboarding",    "1",   "ACCOUNTS"),
    ("protocols",                "M1",            "1",   "PROTOCOLS"),
    ("interventions-and-catalog","M1/M4",         "1",   "INTERVENTIONS"),
    ("biomarkers-and-labs",      "M2",            "1",   "BLOODLAYER"),
    ("measurement-planning",     "M3",            "2",   "PLANNER"),
    ("safety-guardrails",        "M7",            "1-2", "SAFETY"),
    ("daily-log-and-adherence",  "M13",           "1",   "DAILYLOG"),
    ("dashboards-and-doctor-view","M5",           "1",   "DASHBOARD"),
    ("community-and-social",     "M6",            "2",   "COMMUNITY"),
    ("studies-nof1",             "Study",         "2",   "STUDIES"),
    ("procurement-and-inventory","M4",            "3",   "PROCUREMENT"),
    ("evidence-layer",           "M11",           "0/3", "EVIDENCE"),
    ("claims-validator",         "M12",           "2",   "CLAIMS"),
    ("analytics-and-open-data",  "M8",            "4",   "ANALYTICS"),
    ("genomics",                 "M9",            "2",   "GENOMICS"),
    ("agent-access",             "MCP",           "3",   "AGENT"),
]

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

def render_blocks(lines):
    """Generic markdown-ish block renderer (headings, fences, lists, quotes, paras)."""
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("```"):
            i += 1; buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append('<pre class="ascii">' + html.escape("\n".join(buf)) + "</pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lvl = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>"); i += 1; continue
        if line.startswith("> "):
            out.append(callout(line[2:])); i += 1; continue
        if line.lstrip().startswith("- "):
            items = []
            while i < n and lines[i].lstrip().startswith("- "):
                items.append("<li>" + inline(lines[i].lstrip()[2:]) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if line.strip() == "":
            i += 1; continue
        para = []
        while i < n and lines[i].strip() != "" and not lines[i].lstrip().startswith("- ") \
              and not lines[i].startswith("> ") and not lines[i].strip().startswith("```") \
              and not re.match(r"^#{1,6}\s", lines[i]):
            para.append(lines[i]); i += 1
        out.append("<p>" + inline(" ".join(l.strip() for l in para)) + "</p>")
    return "\n".join(out)

def callout(text):
    t = re.sub(r"^\*\*(.+?)\*\*:?", r"\1", text).strip()
    kind = "note"
    for k in ("RESOLVED", "DECISION", "OPEN"):
        if t.upper().startswith(k):
            kind = k.lower(); break
    return f'<div class="callout {kind}">{inline(text)}</div>'

def parse_spec(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title, purpose, reqs = "", [], []
    i, n = 0, len(lines)
    while i < n and not lines[i].startswith("# "): i += 1
    if i < n: title = lines[i][2:].strip(); i += 1
    # purpose
    while i < n and lines[i].strip() != "## Purpose": i += 1
    i += 1
    while i < n and not lines[i].startswith("## "):
        purpose.append(lines[i]); i += 1
    # requirements
    while i < n and lines[i].strip() != "## Requirements": i += 1
    i += 1
    cur = None
    while i < n:
        line = lines[i]
        if line.startswith("### Requirement:"):
            if cur: reqs.append(cur)
            cur = {"title": line.split(":", 1)[1].strip(), "body": [], "callouts": [], "scenarios": []}
        elif line.startswith("#### Scenario:") and cur is not None:
            cur["scenarios"].append({"title": line.split(":", 1)[1].strip(), "lines": []})
        elif cur is not None and line.startswith("> "):
            cur["callouts"].append(line[2:])
        elif cur is not None and cur["scenarios"]:
            cur["scenarios"][-1]["lines"].append(line)
        elif cur is not None:
            cur["body"].append(line)
        i += 1
    if cur: reqs.append(cur)
    return title, purpose, reqs

def render_scenario(sc):
    bullets = [l.lstrip()[2:] for l in sc["lines"] if l.lstrip().startswith("- ")]
    lis = "".join("<li>" + inline(b) + "</li>" for b in bullets)
    return f'<div class="scn"><div class="scn-t">Scenario · {inline(sc["title"])}</div><ul class="steps">{lis}</ul></div>'

# ---- build ----
sections, nav, tot_req, tot_scn = [], [], 0, 0
for d, code, phase, short in MODULES:
    p = SPECS / d / "spec.md"
    if not p.exists(): continue
    title, purpose, reqs = parse_spec(p)
    tot_req += len(reqs); tot_scn += sum(len(r["scenarios"]) for r in reqs)
    nav.append(f'<a href="#{d}"><span class="nc">{code}</span>{html.escape(title)}<span class="nn">{len(reqs)}</span></a>')
    req_html = []
    for idx, r in enumerate(reqs, 1):
        rid = f"{short} · R{idx}"
        tags = "".join(
            f'<span class="tag {("resolved" if c.upper().lstrip("*").startswith("RESOLVED") else "decision" if "DECISION" in c.upper() else "open" if c.upper().lstrip("*").startswith("OPEN") else "note")}">'
            + ("RESOLVED" if c.upper().lstrip("*").startswith("RESOLVED") else "DECISION" if "DECISION" in c.upper() else "OPEN" if c.upper().lstrip("*").startswith("OPEN") else "NOTE")
            + "</span>" for c in r["callouts"])
        body = render_blocks(r["body"]) if any(x.strip() for x in r["body"]) else ""
        cos = "".join(callout(c) for c in r["callouts"])
        scns = "".join(render_scenario(s) for s in r["scenarios"])
        req_html.append(
            f'<details class="req" id="{d}-r{idx}"><summary>'
            f'<span class="rid">{rid}</span><span class="rtitle">{inline(r["title"])}</span>'
            f'<span class="rtags">{tags}<span class="scount">{len(r["scenarios"])} scn</span></span>'
            f'</summary><div class="rbody">{body}{cos}{scns}</div></details>')
    sections.append(
        f'<section class="mod" id="{d}"><div class="modhead">'
        f'<span class="chip">{code}</span><h2>{html.escape(title)}</h2>'
        f'<span class="phase">Phase {phase}</span><span class="rcount">{len(reqs)} requirements</span></div>'
        f'<div class="purpose">{render_blocks(purpose)}</div>'
        f'<div class="reqs">{"".join(req_html)}</div></section>')

# wireframes + navigation embeds
def embed(pathname, anchor, heading):
    f = ROOT / "wireframes" / pathname
    body = render_blocks(f.read_text(encoding="utf-8").splitlines())
    nav.append(f'<a href="#{anchor}" class="extra"><span class="nc">◇</span>{heading}</a>')
    return f'<section class="mod extra" id="{anchor}"><div class="modhead"><h2>{heading}</h2></div><div class="purpose">{body}</div></section>'

sections.append(embed("navigation.md", "navigation", "Navigation &amp; journeys"))
sections.append(embed("wireframes.md", "wireframes", "Wireframes"))

DECISIONS = """
<div class="dl">
<div class="dlrow"><b>D1</b> No local-first — server-hosted only. <em>ACCOUNTS</em></div>
<div class="dlrow"><b>D2</b> Public by default — incl. genomics (gVCF public) behind heightened consent. <em>ACCOUNTS · GENOMICS</em></div>
<div class="dlrow"><b>D10</b> Fully clonable + self-hostable; OpenData incl. public profiles, protocols, treatments, measurements, original lab files, public genomics. <em>ANALYTICS · ACCOUNTS</em></div>
<div class="dlrow"><b>O1</b> Copy gate = baseline <b>and</b> risk acknowledgment (never a bypass). <em>SAFETY</em></div>
<div class="dlrow"><b>O2</b> Rapamycin News via Discourse Connect SSO where feasible, else link; partnership expected. <em>COMMUNITY</em></div>
<div class="dlrow"><b>O3</b> Study pre-registration = mandatory community proposal (forum) for consensus; endpoints frozen. <em>STUDIES</em></div>
<div class="dlrow"><b>O4</b> Imported baseline: coarse lineage note + flag <code>history: synthesized</code>. <em>PROTOCOLS</em></div>
<div class="dlrow"><b>O5</b> Dashboard: headline biological-age Δ first, then organ-system grid. <em>DASHBOARD</em></div>
<div class="dlrow"><b>O6</b> Cohort comparison inline (A) <b>and</b> dedicated view (B); + sex/age percentile vs published distributions. <em>DASHBOARD · ANALYTICS</em></div>
</div>"""

CSS = """
:root{--bg:#eef1ef;--surface:#fff;--surface2:#f4f7f5;--ink:#131f1b;--muted:#586b64;--faint:#7d8d87;
--line:rgba(19,31,27,.12);--line2:rgba(19,31,27,.22);--teal:#0a8477;--teal-ink:#075f55;--amber:#b06f18;--amber-ink:#8f5a12;
--green:#127a4a;--blue:#2563a8;--ff:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--ffd:Georgia,"Times New Roman",serif;
--ffm:ui-monospace,"Cascadia Code",Consolas,monospace;}
@media (prefers-color-scheme:dark){:root{--bg:#0a120f;--surface:#111d18;--surface2:#0e1814;--ink:#e9f1ee;--muted:#94a59e;--faint:#6f817a;
--line:rgba(233,241,238,.12);--line2:rgba(233,241,238,.22);--teal:#37c9b8;--teal-ink:#5fd6c7;--amber:#e0a94e;--amber-ink:#ecbd6f;--green:#4bd08a;--blue:#7db1e8;}}
:root[data-theme=light]{--bg:#eef1ef;--surface:#fff;--surface2:#f4f7f5;--ink:#131f1b;--muted:#586b64;--faint:#7d8d87;--line:rgba(19,31,27,.12);--line2:rgba(19,31,27,.22);--teal:#0a8477;--teal-ink:#075f55;--amber:#b06f18;--amber-ink:#8f5a12;--green:#127a4a;--blue:#2563a8;}
:root[data-theme=dark]{--bg:#0a120f;--surface:#111d18;--surface2:#0e1814;--ink:#e9f1ee;--muted:#94a59e;--faint:#6f817a;--line:rgba(233,241,238,.12);--line2:rgba(233,241,238,.22);--teal:#37c9b8;--teal-ink:#5fd6c7;--amber:#e0a94e;--amber-ink:#ecbd6f;--green:#4bd08a;--blue:#7db1e8;}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--ff);line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{display:grid;grid-template-columns:270px minmax(0,1fr);gap:0;max-width:1280px;margin:0 auto}
aside{position:sticky;top:0;align-self:start;height:100vh;overflow:auto;padding:22px 14px 40px;border-right:1px solid var(--line)}
aside .brand{font-family:var(--ffd);font-size:22px;letter-spacing:-.01em;padding:0 8px 4px}
aside .brand b{color:var(--teal)}
aside .sub{font-family:var(--ffm);font-size:11px;color:var(--faint);padding:0 8px 14px;letter-spacing:.04em}
aside a{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:8px;color:var(--ink);text-decoration:none;font-size:13.5px}
aside a:hover{background:var(--surface2)}
aside a.extra{color:var(--muted);margin-top:2px}
.nc{font-family:var(--ffm);font-size:10px;color:var(--teal-ink);min-width:34px}
.nn{margin-left:auto;font-family:var(--ffm);font-size:11px;color:var(--faint)}
main{padding:34px clamp(18px,4vw,54px) 120px;min-width:0}
h1{font-family:var(--ffd);font-weight:400;font-size:clamp(28px,4vw,44px);letter-spacing:-.015em;margin:0 0 6px}
.tagline{color:var(--muted);max-width:64ch;margin:0 0 22px}
.metrics{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 26px}
.metric{background:var(--surface2);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.metric b{font-family:var(--ffd);font-size:22px} .metric span{display:block;font-size:12px;color:var(--muted)}
.howto{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--teal);border-radius:12px;padding:16px 18px;margin:0 0 22px}
.howto h3{margin:0 0 8px;font-size:15px} .howto ol{margin:0;padding-left:20px} .howto li{margin:4px 0;font-size:14px;color:var(--muted)}
.howto b{color:var(--ink)}
.dl{display:grid;gap:6px;margin-top:10px}
.dlrow{font-size:13.5px;background:var(--surface2);border:1px solid var(--line);border-radius:8px;padding:8px 12px}
.dlrow b{font-family:var(--ffm);color:var(--teal-ink);margin-right:6px} .dlrow em{font-family:var(--ffm);font-style:normal;font-size:11px;color:var(--faint);float:right}
.bar{display:flex;gap:10px;align-items:center;margin:26px 0 8px}
.bar button{font-family:var(--ffm);font-size:12px;background:var(--surface);border:1px solid var(--line2);border-radius:8px;padding:6px 12px;color:var(--ink);cursor:pointer}
.mod{border-top:1px solid var(--line);padding:30px 0 8px;scroll-margin-top:12px}
.modhead{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:8px}
.chip{font-family:var(--ffm);font-size:11px;letter-spacing:.06em;color:#fff;background:var(--teal);border-radius:6px;padding:3px 8px}
.modhead h2{font-family:var(--ffd);font-weight:400;font-size:clamp(22px,2.6vw,30px);margin:0;letter-spacing:-.01em}
.phase{font-family:var(--ffm);font-size:11px;color:var(--amber-ink)}
.rcount,.scount{font-family:var(--ffm);font-size:11px;color:var(--faint)}
.purpose{color:var(--muted);max-width:74ch} .purpose p{margin:8px 0} .purpose h4,.purpose h5{color:var(--ink);margin:16px 0 4px;font-size:15px}
.purpose code,.rbody code,.dlrow code{font-family:var(--ffm);font-size:.88em;background:var(--surface2);border:1px solid var(--line);border-radius:4px;padding:1px 5px}
.reqs{margin-top:14px;display:grid;gap:8px}
details.req{background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
details.req[open]{border-color:var(--line2)}
summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:12px;padding:12px 14px}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸";color:var(--teal);font-size:12px;transition:transform .15s}
details[open] summary::before{transform:rotate(90deg)}
.rid{font-family:var(--ffm);font-size:11px;color:var(--teal-ink);min-width:104px;letter-spacing:.02em}
.rtitle{font-weight:600;font-size:14.5px;flex:1;min-width:0}
.rtags{display:flex;align-items:center;gap:6px;flex-shrink:0}
.tag{font-family:var(--ffm);font-size:9.5px;letter-spacing:.08em;padding:2px 6px;border-radius:5px;border:1px solid}
.tag.resolved{color:var(--green);border-color:var(--green)} .tag.decision{color:var(--amber-ink);border-color:var(--amber)}
.tag.open{color:var(--blue);border-color:var(--blue)} .tag.note{color:var(--faint);border-color:var(--line2)}
.rbody{padding:2px 16px 16px 40px;border-top:1px solid var(--line)}
.rbody p{margin:10px 0;font-size:14.5px}
.scn{background:var(--surface2);border:1px solid var(--line);border-radius:9px;padding:10px 14px;margin:8px 0}
.scn-t{font-family:var(--ffm);font-size:11px;color:var(--amber-ink);letter-spacing:.04em;margin-bottom:4px}
.steps{margin:0;padding-left:18px} .steps li{font-size:13.5px;margin:2px 0;color:var(--ink)}
.callout{border-radius:9px;padding:9px 13px;margin:10px 0;font-size:13px;border:1px solid}
.callout.resolved{background:color-mix(in srgb,var(--green) 8%,transparent);border-color:var(--green)}
.callout.decision{background:color-mix(in srgb,var(--amber) 10%,transparent);border-color:var(--amber)}
.callout.open{background:color-mix(in srgb,var(--blue) 8%,transparent);border-color:var(--blue)}
.callout.note{background:var(--surface2);border-color:var(--line2)}
pre.ascii{font-family:var(--ffm);font-size:11.5px;line-height:1.35;background:var(--surface2);border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;color:var(--ink)}
.extra .purpose{max-width:none}
.tgl{position:fixed;top:14px;right:16px;z-index:9;width:34px;height:34px;border-radius:50%;background:var(--surface);border:1px solid var(--line);color:var(--ink);cursor:pointer}
@media(max-width:900px){.wrap{grid-template-columns:1fr}aside{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}}
"""

JS = """
document.getElementById('exp').onclick=function(){document.querySelectorAll('details.req').forEach(d=>d.open=true)};
document.getElementById('col').onclick=function(){document.querySelectorAll('details.req').forEach(d=>d.open=false)};
document.getElementById('tgl').onclick=function(){var r=document.documentElement,c=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');r.setAttribute('data-theme',c==='dark'?'light':'dark')};
"""

page = f"""<title>biohack.it — Functional Spec Review</title>
<style>{CSS}</style>
<button class="tgl" id="tgl" aria-label="Toggle theme">◐</button>
<div class="wrap">
<aside>
  <div class="brand">biohack<b>.</b>it</div>
  <div class="sub">FUNCTIONAL SPEC · REVIEW</div>
  {''.join(nav)}
</aside>
<main>
  <h1>Functional Specification — Review</h1>
  <p class="tagline">Everything produced for biohack.it, in one place, structured for a module-by-module review. Give feedback by requirement code — e.g. <b>“SAFETY R1: …”</b>.</p>
  <div class="metrics">
    <div class="metric"><b>{len(MODULES)}</b><span>capabilities</span></div>
    <div class="metric"><b>{tot_req}</b><span>requirements</span></div>
    <div class="metric"><b>{tot_scn}</b><span>scenarios</span></div>
    <div class="metric"><b>0</b><span>open decisions</span></div>
  </div>
  <div class="howto">
    <h3>How to review — three levels</h3>
    <ol>
      <li><b>Shape (10 min):</b> read the posture + decisions below, and each module's <b>Purpose</b>. Is the direction right?</li>
      <li><b>Coverage (20 min):</b> skim the <b>requirement titles</b> (collapsed rows) per module. Anything missing or wrong?</li>
      <li><b>Detail (as needed):</b> expand a requirement to read its scenarios. Reference it by its code when you comment.</li>
    </ol>
  </div>
  <h3 style="font-size:15px;margin:22px 0 0">Decisions resolved</h3>
  {DECISIONS}
  <div class="bar"><button id="exp">Expand all</button><button id="col">Collapse all</button></div>
  {''.join(sections)}
</main>
</div>
<script>{JS}</script>
"""

out = ROOT / "review.html"
out.write_text(page, encoding="utf-8")
print(f"wrote {out}  ({len(page):,} bytes)  modules={len(MODULES)} req={tot_req} scn={tot_scn}")
