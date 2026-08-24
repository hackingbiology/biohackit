#!/usr/bin/env python3
"""Build the BIOHACK.IT white paper: self-contained HTML + print-quality PDF.

Source of design/fonts: docs/index.html (@font-face Jost data-URIs, palette).
Content source: whitepaper/whitepaper.src.html (authored narrative).
Version/date: whitepaper/meta.json.

Outputs (served by GitHub Pages -> biohack.it/whitepaper/):
  docs/whitepaper/index.html                  (online HTML, shareable)
  docs/whitepaper/biohackit-whitepaper.pdf    (print-quality PDF, footer stamped)

Regenerate after any edit to the source or the specs:  python whitepaper/build.py
"""
import re, json, subprocess, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WP   = ROOT / "whitepaper"
OUT  = ROOT / "docs" / "whitepaper"
OUT.mkdir(parents=True, exist_ok=True)

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

meta = json.loads((WP / "meta.json").read_text(encoding="utf-8"))
VERSION, DATE = meta["version"], meta["date"]

# --- pull the three @font-face (Jost) blocks from the live site so the doc matches the brand ---
site = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
faces = re.findall(r'@font-face\{[^}]*\}', site)
if len(faces) < 3:
    sys.exit(f"expected 3 @font-face blocks in docs/index.html, found {len(faces)}")
fonts_css = "\n".join(faces)

src = (WP / "whitepaper.src.html").read_text(encoding="utf-8")
src = src.replace("/*FONTS*/", fonts_css)
# stamp version/date into the cover (source carries placeholders-as-defaults; keep in sync with meta)
src = re.sub(r'Version [0-9.]+ · [A-Za-z]+ [0-9]{4}',
             f'Version {VERSION} · {DATE}', src)

# self-contained HTML for online viewing
html_out = OUT / "index.html"
html_out.write_text(src, encoding="utf-8")

# intermediate file Chrome renders from
build_html = WP / "_build.html"
build_html.write_text(src, encoding="utf-8")

pdf_raw = WP / "_raw.pdf"
uri = build_html.resolve().as_uri()
cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
       "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
       "--virtual-time-budget=4000",
       f"--print-to-pdf={pdf_raw}", uri]
r = subprocess.run(cmd, capture_output=True, text=True)
if not pdf_raw.exists():
    sys.exit("Chrome failed to produce PDF:\n" + r.stderr[-2000:])

# --- stamp a branded footer on every page except the cover ---
import pymupdf
doc = pymupdf.open(pdf_raw)
LEFT  = f"BIOHACK.IT · White Paper · v{VERSION} · {DATE}"
INK   = (0.16, 0.16, 0.17)
FAINT = (0.55, 0.58, 0.60)
for i, page in enumerate(doc):
    if i == 0:
        continue
    w, h = page.rect.width, page.rect.height
    y = h - 26
    page.draw_line((54, y - 8), (w - 54, y - 8), color=(0.85, 0.87, 0.86), width=0.6)
    page.insert_text((54, y), LEFT, fontname="helv", fontsize=7, color=FAINT)
    num = f"{i + 1}"
    tw = pymupdf.get_text_length(num, fontname="helv", fontsize=8)
    page.insert_text((w - 54 - tw, y), num, fontname="helv", fontsize=8, color=INK)

pdf_out = OUT / "biohackit-whitepaper.pdf"
doc.save(pdf_out, deflate=True, garbage=4)
doc.close()
pdf_raw.unlink(missing_ok=True)
build_html.unlink(missing_ok=True)

kb = pdf_out.stat().st_size // 1024
print(f"white paper v{VERSION} ({DATE}) · {len(faces)} fonts · {doc.page_count if False else ''}")
print(f"  {html_out}")
print(f"  {pdf_out}  ({kb} KB)")
