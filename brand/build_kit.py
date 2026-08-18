#!/usr/bin/env python3
"""Generate the BIOHACK.IT social + print kit from the locked identity.
Vector wordmark via fontTools (Jost outlines) + ring/bar mark. Light-only."""
import re, base64, io, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = pathlib.Path(__file__).resolve().parent          # brand/
REPO = ROOT.parent
INK="#25292c"; PAPER="#ffffff"; TEAL="#0c877a"; MUTED="#59636a"; FAINT="#8b9398"; SURF="#f1f4f3"; HAIR="#dde3e1"
NS='xmlns="http://www.w3.org/2000/svg"'

# --- load Jost weights from the inlined data-URIs in the site ---
site = (REPO/"docs"/"index.html").read_text(encoding="utf-8")
def jost(weight):
    m = re.search(r"@font-face\{[^}]*?font-weight:%d;[^}]*?base64,([A-Za-z0-9+/=]+)\)" % weight, site)
    if not m: raise SystemExit("weight %d not found" % weight)
    return TTFont(io.BytesIO(base64.b64decode(m.group(1))))
F300=jost(300); F500=jost(500)

def wordmark(text, font, size, x, baseline, color, tracking=0.0):
    """Return (svg_group, width_px). tracking in em."""
    upm=font["head"].unitsPerEm; cmap=font.getBestCmap(); gs=font.getGlyphSet(); hmtx=font["hmtx"]
    s=size/upm; cur=0.0; parts=[]
    trk=tracking*upm
    for ch in text:
        g=cmap.get(ord(ch))
        if g is None: cur+=upm*0.4+trk; continue
        pen=SVGPathPen(gs); gs[g].draw(pen); d=pen.getCommands()
        if d: parts.append(f'<path d="{d}" transform="translate({cur:.1f},0)"/>')
        cur+=hmtx[g][0]+trk
    grp=(f'<g fill="{color}" transform="translate({x:.1f},{baseline:.1f}) scale({s:.5f},{-s:.5f})">'
         + "".join(parts) + "</g>")
    return grp, cur*s

def mark(cx, top, d, ring, bar, stroke_ratio=0.16):
    st=d*stroke_ratio
    bw=d*1.18; bh=d*0.16
    return (f'<circle cx="{cx:.1f}" cy="{top+d/2:.1f}" r="{d/2:.1f}" fill="none" stroke="{ring}" stroke-width="{st:.1f}"/>'
            f'<rect x="{cx-bw/2:.1f}" y="{top+d+d*0.16:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{bh/2:.1f}" fill="{bar}"/>')

def bar(x,y,w,h,color): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="{color}"/>'

def svg(w,h,body,bg=PAPER):
    return f'<svg {NS} viewBox="0 0 {w} {h}" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'

def lockup(cx_left, y, wm_size, color=INK, teal=TEAL, center_w=None):
    """Wordmark + bar + tagline + mark, returns svg body; anchored at left x=cx_left, wordmark baseline at y."""
    wm,wmw = wordmark("BIOHACK.IT", F300, wm_size, cx_left, y, color)
    tag,tagw = wordmark("HACKING BIOLOGY", F500, wm_size*0.22, cx_left+wm_size*0.02, y+wm_size*0.55, color, tracking=0.34)
    barw=wm_size*1.15
    b=bar(cx_left, y+wm_size*0.30, barw, wm_size*0.05, color)
    return wm+b+tag, wmw

# ---------------- SOCIAL BANNERS (light) ----------------
social=ROOT/"social"; social.mkdir(exist_ok=True)
def banner(w,h,wm_size,pad,centered=False):
    _,wmw=wordmark("BIOHACK.IT",F300,wm_size,0,0,INK)
    markd=wm_size*1.5; gap=wm_size*0.55; bw=markd*1.18
    lx=(w-(wmw+gap+bw))/2 if centered else pad
    base=h*0.46
    body,_=lockup(lx, base, wm_size, INK, TEAL)
    body+=wordmark("An open laboratory for longevity.", F300, wm_size*0.30, lx+2, base+wm_size*0.95, MUTED)[0]
    mcx = (lx+wmw+gap+markd/2) if centered else (w-pad-markd/2)
    body+=mark(mcx, h*0.5-markd/2, markd, INK, TEAL)
    return svg(w,h,body)
banners={
 "x-header":(1500,500,140,120,False),
 "linkedin-cover":(1584,396,90,120,False),
 "youtube-channel":(2560,1440,150,0,True),
 "banner-wide":(1600,600,150,130,False),
}
for n,(w,h,wm,pad,cen) in banners.items():
    (social/f"{n}.svg").write_text(banner(w,h,wm,pad,cen),encoding="utf-8")

# ---------------- BUSINESS CARD (90x50mm @ ~300dpi = 1063x591; +bleed) ----------------
prnt=ROOT/"print"; prnt.mkdir(exist_ok=True)
CW,CH=1063,591
# front
fwm=118
_,fwmw=wordmark("BIOHACK.IT",F300,fwm,0,0,INK)
fbody,_=lockup(80, CH*0.46, fwm, INK, TEAL)
fbody+=mark(80+fwmw+90, CH*0.5-45, 90, INK, TEAL)
(prnt/"card-front.svg").write_text(svg(CW,CH,fbody),encoding="utf-8")
# back
bb=mark(90, 70, 70, INK, TEAL)
bb+=wordmark("Fabio Pietrosanti", F500, 60, 90, 330, INK)[0]
bb+=wordmark("Founder", F300, 34, 90, 380, MUTED)[0]
bb+=wordmark("biohack.it   ·   hackingbiology.com", F300, 30, 90, 470, TEAL)[0]
bb+=bar(90, 500, 120, 4, INK)
bb+=wordmark("HACKING BIOLOGY  ·  non-profit  ·  AGPL-3.0", F500, 20, 90, 540, FAINT, tracking=0.16)[0]
(prnt/"card-back.svg").write_text(svg(CW,CH,bb),encoding="utf-8")

# ---------------- LETTERHEAD (A4 @150dpi = 1240x1754) ----------------
AW,AH=1240,1754
lb=mark(96, 84, 60, INK, TEAL)
lb+=wordmark("BIOHACK.IT", F300, 74, 190, 150, INK)[0]
lb+=bar(96, 210, 1048, 3, HAIR)
lb+=bar(96, AH-140, 1048, 2, HAIR)
lb+=wordmark("Hacking Biology Foundation  ·  non-profit  ·  AGPL-3.0  ·  biohack.it", F500, 22, 96, AH-96, FAINT, tracking=0.12)[0]
(prnt/"letterhead.svg").write_text(svg(AW,AH,lb),encoding="utf-8")

print("SVGs written to brand/social and brand/print")
PY = None
