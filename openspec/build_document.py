#!/usr/bin/env python3
"""Faithful, human-readable EXPORT of the OpenSpec tree — the reference document.

One source of truth (specs/*/spec.md) -> two readable artefacts:
  docs/specs/index.html                     (the web review page, via build_review.py)
  docs/specs/biohackit-specification.html   (this: linear, section-numbered document)
  docs/specs/biohackit-specification.pdf     (this: print-quality, footer-stamped)

This document is the faithful reference: Purpose prose + every requirement (verbatim
SHALL) + every scenario, numbered §N.M for citable review. The narrative companion is
the white paper; where the two differ, the specification is authoritative.

Regenerate:  python openspec/build_document.py
"""
import re, json, html, subprocess, pathlib, sys

ROOT  = pathlib.Path(__file__).resolve().parent.parent
SPECS = ROOT / "openspec" / "specs"
OUT   = ROOT / "docs" / "specs"
OUT.mkdir(parents=True, exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

meta = json.loads((ROOT / "openspec" / "document-meta.json").read_text(encoding="utf-8"))
VERSION, DATE = meta["version"], meta["date"]

# capability order + chapter codes (mirror build_review.py)
MODULES = [
    ("domain-model","DOMAIN"), ("ai-uses-and-attribution","AI USES"),
    ("data-standards-and-typing","STANDARDS"),
    ("scientific-method-and-evidence","METHOD"), ("statistical-methodology","STATS"),
    ("related-initiatives","LANDSCAPE"),
    ("accounts-and-profiles","ACCOUNTS"), ("management-and-delegation","DELEGATION"),
    ("protocols","PROTOCOLS"), ("interventions-and-catalog","INTERVENTIONS"),
    ("biomarkers-and-labs","BLOOD LAYER"), ("measurement-planning","PLANNING"),
    ("safety-guardrails","SAFETY"), ("daily-log-and-adherence","ADHERENCE"),
    ("dashboards-and-doctor-view","DASHBOARDS"), ("community-and-social","COMMUNITY"),
    ("studies-nof1","STUDIES"), ("procurement-and-inventory","PROCUREMENT"),
    ("pills-management","PILLS"), ("therapeutics-management","THERAPEUTICS"),
    ("exercise-reporting","EXERCISE"), ("nutrition-management","NUTRITION"),
    ("evidence-layer","EVIDENCE"), ("analytics-and-open-data","OPEN DATA"),
    ("genomics","GENOMICS"), ("agent-access","AGENT ACCESS"),
]

def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s

def parse_spec(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title, purpose, reqs = "", [], []
    i, n = 0, len(lines)
    while i < n and not lines[i].startswith("# "): i += 1
    if i < n: title = lines[i][2:].strip(); i += 1
    while i < n and lines[i].strip() != "## Purpose": i += 1
    i += 1
    while i < n and not lines[i].startswith("## "): purpose.append(lines[i]); i += 1
    while i < n and lines[i].strip() != "## Requirements": i += 1
    i += 1
    cur = None
    while i < n:
        line = lines[i]
        if line.startswith("### Requirement:"):
            if cur: reqs.append(cur)
            cur = {"title": line.split(":",1)[1].strip(), "body": [], "callouts": [], "scenarios": []}
        elif line.startswith("#### Scenario:") and cur is not None:
            cur["scenarios"].append({"title": line.split(":",1)[1].strip(), "lines": []})
        elif cur is not None and line.startswith("> "):
            cur["callouts"].append(line[2:])
        elif cur is not None and cur["scenarios"]:
            cur["scenarios"][-1]["lines"].append(line)
        elif cur is not None:
            cur["body"].append(line)
        i += 1
    if cur: reqs.append(cur)
    return title, purpose, reqs

def prose(lines):
    """Render a block of markdown-ish lines to paragraphs + bullet lists."""
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip() == "": i += 1; continue
        if lines[i].lstrip().startswith("- "):
            items = []
            while i < n and lines[i].lstrip().startswith("- "):
                items.append("<li>" + inline(lines[i].lstrip()[2:]) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        para = []
        while i < n and lines[i].strip() != "" and not lines[i].lstrip().startswith("- "):
            para.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)

def callout(text):
    t = re.sub(r"^\*\*(.+?)\*\*:?", r"\1", text).strip()
    kind = "note"
    for k in ("RESOLVED","DECISION","OPEN"):
        if t.upper().startswith(k): kind = k.lower(); break
    label = {"resolved":"RESOLVED","decision":"DECISION","open":"OPEN","note":"NOTE"}[kind]
    return f'<div class="callout {kind}"><span class="cl">{label}</span>{inline(text)}</div>'

def scenario(sc, num):
    bullets = [l.lstrip()[2:] for l in sc["lines"] if l.lstrip().startswith("- ")]
    steps = "".join("<li>" + inline(b) + "</li>" for b in bullets)
    return (f'<div class="scn"><div class="scn-h">Scenario {num} · {inline(sc["title"])}</div>'
            f'<ul class="steps">{steps}</ul></div>')

# ---- product posture (Principles chapter) from project.md ----
def posture():
    m = (ROOT/"openspec"/"project.md").read_text(encoding="utf-8")
    seg = m.split("## Product posture",1)
    if len(seg) < 2: return ""
    body = seg[1].split("\n## ",1)[0]
    items = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("- **") or (s.startswith("- ") and not s.startswith("  ")):
            items.append("<li>" + inline(s[2:]) + "</li>")
    return "<ul>" + "".join(items) + "</ul>" if items else ""

# ---- build chapters ----
chapters, toc, tot_req, tot_scn = [], [], 0, 0
ch = 0
# Chapter 0 · Principles
principles = posture()
if principles:
    toc.append(('0','Principles &amp; product posture'))
    chapters.append(f'<section class="ch"><div class="chnum">§0</div>'
                    f'<h2 class="ct">Principles &amp; product posture</h2>'
                    f'<p class="intro">Settled directions that shape every capability. Where one supersedes an earlier spec decision it says so; these are the frame within which the requirements below are read.</p>'
                    f'{principles}</section>')

for d, code in MODULES:
    p = SPECS / d / "spec.md"
    if not p.exists(): continue
    ch += 1
    title, pur, reqs = parse_spec(p)
    tot_req += len(reqs); tot_scn += sum(len(r["scenarios"]) for r in reqs)
    toc.append((str(ch), html.escape(title)))
    body = [f'<section class="ch"><div class="chnum">§{ch} · {code}</div>'
            f'<h2 class="ct">{html.escape(title)}</h2>'
            f'<div class="intro">{prose(pur)}</div>']
    for j, r in enumerate(reqs, 1):
        body.append(f'<div class="req"><div class="rid">§{ch}.{j}</div>'
                    f'<h3>{inline(r["title"])}</h3>')
        if any(x.strip() for x in r["body"]):
            body.append(f'<div class="rtext">{prose(r["body"])}</div>')
        for c in r["callouts"]:
            body.append(callout(c))
        for k, sc in enumerate(r["scenarios"], 1):
            body.append(scenario(sc, k))
        body.append("</div>")
    body.append("</section>")
    chapters.append("\n".join(body))

toc_html = "".join(f'<div class="tr"><span class="tn">§{n}</span><span class="tt">{t}</span></div>'
                   for n,t in toc)

# ---- fonts from the live site ----
site = (ROOT/"docs"/"index.html").read_text(encoding="utf-8")
faces = "\n".join(re.findall(r'@font-face\{[^}]*\}', site))

DOC = f"""<meta charset="utf-8"><title>BIOHACK.IT — Functional Specification</title>
<style>
{faces}
:root{{--ink:#25292c;--muted:#4c565c;--faint:#8b9398;--line:rgba(37,41,44,.14);
--line-strong:rgba(37,41,44,.26);--accent:#0c877a;--accent-ink:#0a6f64;--fill:rgba(12,135,122,.07);
--surface:#f6f8f8;--surface-2:#eef2f1;--amber:#9a6a12;--amber-fill:rgba(179,130,42,.09);
--disp:"Jost",system-ui,sans-serif;--body:Georgia,"Times New Roman",serif;}}
@page{{size:A4;margin:20mm 18mm 20mm;}}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0}}
body{{font-family:var(--body);color:var(--ink);font-size:10pt;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
h1,h2,h3,h4{{font-family:var(--disp);font-weight:400;line-height:1.14;color:var(--ink)}}
p{{margin:0 0 7pt}} strong{{font-weight:600}} em{{font-style:italic}}
code{{font-family:"Jost",ui-monospace,Consolas,monospace;background:var(--surface-2);padding:0 3px;border-radius:3px;font-size:9pt}}
ul{{margin:0 0 7pt;padding-left:15pt}} li{{margin:0 0 3pt}}

.cover{{height:257mm;display:flex;flex-direction:column;page-break-after:always}}
.cover .kicker{{font-family:var(--disp);font-weight:500;font-size:11pt;letter-spacing:.30em;text-transform:uppercase;color:var(--accent-ink);margin-top:auto}}
.cover h1{{font-size:46pt;letter-spacing:-.02em;margin:6pt 0 0}}
.cover .rule{{width:56pt;height:3pt;background:var(--accent);margin:11pt 0 13pt;border-radius:2pt}}
.cover .sub{{font-family:var(--disp);font-weight:300;font-size:19pt;color:var(--muted);margin:0}}
.cover .doctype{{font-family:var(--disp);font-weight:500;font-size:10pt;letter-spacing:.22em;text-transform:uppercase;color:var(--faint);margin-top:5pt}}
.cover .counts{{display:flex;gap:26pt;margin-top:16pt}}
.cover .counts .c b{{font-family:var(--disp);font-weight:400;font-size:26pt;color:var(--ink);display:block}}
.cover .counts .c span{{font-family:var(--disp);font-size:8.5pt;letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}}
.cover .foot{{margin-top:auto;border-top:1px solid var(--line);padding-top:9pt;display:flex;justify-content:space-between;align-items:flex-end}}
.cover .gen{{font-family:var(--disp);font-size:8.5pt;color:var(--muted);max-width:96mm;line-height:1.5}}
.cover .meta{{font-family:var(--disp);font-size:8.5pt;letter-spacing:.12em;text-transform:uppercase;color:var(--faint);text-align:right;line-height:1.7}}

.toc{{page-break-after:always}}
.toc h2{{font-family:var(--disp);font-weight:500;font-size:12pt;letter-spacing:.16em;text-transform:uppercase;color:var(--accent-ink);margin:0 0 12pt}}
.tr{{display:flex;gap:12pt;padding:4pt 0;border-bottom:1px solid var(--line)}}
.tn{{font-family:var(--disp);font-weight:500;color:var(--accent-ink);width:46pt;flex:none}}
.tt{{font-family:var(--disp);font-size:11pt}}

section.ch{{page-break-before:always}}
.chnum{{font-family:var(--disp);font-weight:500;font-size:9.5pt;letter-spacing:.18em;color:var(--accent-ink)}}
h2.ct{{font-size:22pt;letter-spacing:-.01em;margin:2pt 0 9pt}}
.intro{{font-family:var(--body);color:var(--muted);font-size:10.5pt;border-left:2px solid var(--line-strong);padding-left:12pt;margin:0 0 12pt}}
.intro p{{margin:0 0 6pt}} .intro p:last-child{{margin:0}}
.req{{margin:0 0 11pt;page-break-inside:avoid}}
.rid{{font-family:var(--disp);font-weight:500;font-size:9pt;letter-spacing:.10em;color:var(--accent-ink)}}
.req h3{{font-family:var(--disp);font-weight:500;font-size:13pt;margin:1pt 0 4pt}}
.rtext{{margin:0 0 6pt}}
.scn{{background:var(--surface);border:1px solid var(--line);border-radius:6pt;padding:8pt 11pt;margin:6pt 0}}
.scn-h{{font-family:var(--disp);font-weight:500;font-size:9pt;letter-spacing:.04em;color:var(--ink);margin-bottom:4pt}}
.steps{{margin:0;padding-left:14pt;font-size:9.5pt}}
.steps li{{margin:0 0 2pt}}
.callout{{border-radius:0 6pt 6pt 0;padding:7pt 12pt;margin:7pt 0;font-size:9.5pt;background:var(--fill);border-left:3px solid var(--accent)}}
.callout .cl{{display:block;font-family:var(--disp);font-weight:500;font-size:8pt;letter-spacing:.16em;color:var(--accent-ink);margin-bottom:2pt}}
.callout.decision{{background:var(--amber-fill);border-left-color:var(--amber)}}
.callout.decision .cl{{color:var(--amber)}}
.callout.open{{background:var(--surface-2);border-left-color:var(--faint)}}
.callout.open .cl{{color:var(--muted)}}
</style>

<div class="cover">
  <svg width="48" height="60" viewBox="0 0 52 66" style="margin-top:6mm"><circle cx="26" cy="24" r="19" fill="none" stroke="#25292c" stroke-width="6"/><rect x="9" y="52" width="34" height="7" rx="3.5" fill="#0c877a"/></svg>
  <div class="kicker">Hacking Biology</div>
  <h1>BIOHACK.IT</h1>
  <div class="rule"></div>
  <div class="sub">Functional Specification</div>
  <div class="doctype">Reference document · generated from OpenSpec</div>
  <div class="counts">
    <div class="c"><b>{ch}</b><span>Capabilities</span></div>
    <div class="c"><b>{tot_req}</b><span>Requirements</span></div>
    <div class="c"><b>{tot_scn}</b><span>Scenarios</span></div>
  </div>
  <div class="foot">
    <div class="gen">Generated from the OpenSpec tree. <strong>Do not edit this document</strong> — edit the specs and regenerate. The narrative companion is the white paper; where the two differ, this specification is authoritative.</div>
    <div class="meta">Version {VERSION} · {DATE}<br>Open source · AGPL-3.0 · Non-profit<br>biohack.it/specs</div>
  </div>
</div>

<div class="toc"><h2>Contents</h2>{toc_html}</div>

{"".join(chapters)}
"""

html_out = OUT / "biohackit-specification.html"
html_out.write_text(DOC, encoding="utf-8")
build_html = ROOT/"openspec"/"_specbuild.html"; build_html.write_text(DOC, encoding="utf-8")

pdf_raw = ROOT/"openspec"/"_specraw.pdf"
cmd=[CHROME,"--headless=new","--disable-gpu","--no-sandbox","--no-pdf-header-footer",
     "--run-all-compositor-stages-before-draw","--virtual-time-budget=5000",
     f"--print-to-pdf={pdf_raw}", build_html.resolve().as_uri()]
r=subprocess.run(cmd,capture_output=True,text=True)
if not pdf_raw.exists(): sys.exit("Chrome failed:\n"+r.stderr[-2000:])

import pymupdf
doc=pymupdf.open(pdf_raw)
LEFT=f"BIOHACK.IT · Functional Specification · v{VERSION} · {DATE}"
for i,page in enumerate(doc):
    if i==0: continue
    w,h=page.rect.width,page.rect.height; y=h-26
    page.draw_line((54,y-8),(w-54,y-8),color=(0.85,0.87,0.86),width=0.6)
    page.insert_text((54,y),LEFT,fontname="helv",fontsize=7,color=(0.55,0.58,0.60))
    num=f"{i+1}"; tw=pymupdf.get_text_length(num,fontname="helv",fontsize=8)
    page.insert_text((w-54-tw,y),num,fontname="helv",fontsize=8,color=(0.16,0.16,0.17))
pdf_out=OUT/"biohackit-specification.pdf"
pages=doc.page_count
doc.save(pdf_out,deflate=True,garbage=4); doc.close()
pdf_raw.unlink(missing_ok=True); build_html.unlink(missing_ok=True)

print(f"specification v{VERSION} ({DATE}) · {ch} capabilities · {tot_req} requirements · {tot_scn} scenarios · {pages}pp")
print(f"  {html_out}")
print(f"  {pdf_out}  ({pdf_out.stat().st_size//1024} KB)")
