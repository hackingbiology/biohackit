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

def lockup(x, base, wm_size, sub="HACKING BIOLOGY", color=INK):
    """Two-line lockup: wordmark + bar + one sub-line (payoff or 'HACKING BIOLOGY')."""
    wm,wmw = wordmark("BIOHACK.IT", F300, wm_size, x, base, color)
    subg,_ = wordmark(sub, F500, wm_size*0.205, x+wm_size*0.02, base+wm_size*0.55, color, tracking=0.28)
    b=bar(x, base+wm_size*0.30, wm_size*1.15, wm_size*0.05, color)
    return wm+b+subg, wmw

def mark_on(cx, base, wm_size, d, ring=INK, barc=TEAL):
    """Mark with its ring centred on the wordmark cap-centre (proper optical alignment)."""
    top = base - 0.365*wm_size - d/2
    return mark(cx, top, d, ring, barc)

# ---------------- SOCIAL BANNERS (light) ----------------
social=ROOT/"social"; social.mkdir(exist_ok=True)
def banner(w,h,wm_size,pad,centered=False):
    _,wmw=wordmark("BIOHACK.IT",F300,wm_size,0,0,INK)
    d=wm_size*1.35; gap=wm_size*0.6; bw=d*1.18
    lx=(w-(wmw+gap+bw))/2 if centered else pad
    base=h*0.5+wm_size*0.365            # wordmark cap-centre at h/2
    body,_=lockup(lx, base, wm_size, "AN OPEN LABORATORY FOR LONGEVITY", INK)
    mcx=(lx+wmw+gap+d/2) if centered else (w-pad-bw/2)
    body+=mark_on(mcx, base, wm_size, d)
    return svg(w,h,body)
banners={
 "x-header":(1500,500,140,120,False),
 "linkedin-profile":(1584,396,90,120,False),
 "linkedin-company":(1128,191,50,90,True),
 "youtube-channel":(2560,1440,150,0,True),
 "banner-wide":(1600,600,150,130,False),
 "facebook-cover":(820,312,56,60,True),
 "weibo-cover":(920,300,56,60,True),
 "wechat-cover":(900,383,66,80,True),
 "square-1080":(1080,1080,120,0,True),
 "xiaohongshu-cover":(1080,1440,110,0,True),
 "telegram-preview":(1200,630,110,0,True),
}
for n,(w,h,wm,pad,cen) in banners.items():
    (social/f"{n}.svg").write_text(banner(w,h,wm,pad,cen),encoding="utf-8")

# ---------------- BUSINESS CARD (90x50mm @ ~300dpi = 1063x591; +bleed) ----------------
prnt=ROOT/"print"; prnt.mkdir(exist_ok=True)
CW,CH=1063,591
# front
fwm=112
_,fwmw=wordmark("BIOHACK.IT",F300,fwm,0,0,INK)
fbase=CH*0.5+fwm*0.365
fbody,_=lockup(80, fbase, fwm, "AN OPEN LABORATORY FOR LONGEVITY", INK)
fbody+=mark_on(80+fwmw+95, fbase, fwm, 88)
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
lbase=150
lb=wordmark("BIOHACK.IT", F300, 74, 200, lbase, INK)[0]
lb+=mark_on(120, lbase, 74, 58)
lb+=bar(96, 210, 1048, 3, HAIR)
lb+=bar(96, AH-140, 1048, 2, HAIR)
lb+=wordmark("Hacking Biology Foundation  ·  non-profit  ·  AGPL-3.0  ·  biohack.it", F500, 22, 96, AH-96, FAINT, tracking=0.12)[0]
(prnt/"letterhead.svg").write_text(svg(AW,AH,lb),encoding="utf-8")

# ---------------- DOWNLOADABLE LOGOS (transparent, PNG-ready) ----------------
logos=ROOT/"logos"; logos.mkdir(exist_ok=True)
def svg_t(w,h,body,bg=None):
    r=f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg {NS} viewBox="0 0 {w} {h}" width="{w}" height="{h}">{r}{body}</svg>'
def full_lockup(color, teal, wm=160, pad=48):
    _,wmw=wordmark("BIOHACK.IT",F300,wm,0,0,color)
    d=wm*1.35; gap=wm*0.6; bw=d*1.18
    top=max(0.73*wm, 0.5*d+0.365*wm); bot=max(0.80*wm, 0.82*d-0.365*wm)
    base=pad+top; Wc=pad*2+wmw+gap+bw; Hc=pad*2+top+bot
    body,_=lockup(pad, base, wm, "AN OPEN LABORATORY FOR LONGEVITY", color)
    body+=mark_on(pad+wmw+gap+d/2, base, wm, d, color, teal)
    return Wc,Hc,body
def wm_only(color, teal, wm=160, pad=48):
    _,wmw=wordmark("BIOHACK.IT",F300,wm,0,0,color)
    d=wm*1.15; gap=wm*0.55; bw=d*1.18
    top=max(0.73*wm, 0.5*d+0.365*wm); bot=max(0.18*wm, 0.82*d-0.365*wm)
    base=pad+top; Wc=pad*2+wmw+gap+bw; Hc=pad*2+top+bot
    body,_=wordmark("BIOHACK.IT",F300,wm,pad,base,color)
    body+=mark_on(pad+wmw+gap+d/2, base, wm, d, color, teal)
    return Wc,Hc,body
for tag,col in [("dark",INK),("white","#ffffff")]:
    Wc,Hc,b=full_lockup(col,TEAL); (logos/f"logo-full-{tag}.svg").write_text(svg_t(Wc,Hc,b),encoding="utf-8")
    Wc,Hc,b=wm_only(col,TEAL);     (logos/f"logo-wordmark-{tag}.svg").write_text(svg_t(Wc,Hc,b),encoding="utf-8")
Wc,Hc,b=full_lockup(INK,TEAL); (logos/"logo-full-onwhite.svg").write_text(svg_t(Wc,Hc,b,PAPER),encoding="utf-8")
(logos/"mark-dark.svg").write_text(svg_t(130,168, mark(65,12,104,INK,TEAL)),encoding="utf-8")
(logos/"mark-white.svg").write_text(svg_t(130,168, mark(65,12,104,"#ffffff",TEAL)),encoding="utf-8")
print("SVGs written to brand/social, brand/print, brand/logos")
