#!/usr/bin/env python3
"""BIOHACK.IT business card — layout P1 (chosen design), parameterised.
Front EN / back 中文, 85x54mm, rounded corners, WeChat QR on the Chinese side.
Emits per-card front/back SVGs and a print-ready PDF (3mm bleed + crop marks).

Two builds:
  - fabio/    : Fabio Pietrosanti's card (real data + real WeChat QR)
  - template/ : same layout with placeholder fields (+ WeChat-QR placeholder) for future team cards

Regenerate:  python brand/card/build_card.py
Deps: fontTools (Jost from docs/index.html + a CJK font), pymupdf, Pillow.
"""
import re, base64, io, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = pathlib.Path(__file__).resolve().parent          # brand/card
REPO = HERE.parent.parent                                # repo root
INK="#25292c"; PAPER="#ffffff"; TEAL="#0c877a"; TEALD="#0a6f64"; MUTED="#59636a"; FAINT="#8b9398"; HAIR="#dde3e1"
NS='xmlns="http://www.w3.org/2000/svg"'

site=(REPO/"docs"/"index.html").read_text(encoding="utf-8")
def jost(w):
    m=re.search(r"@font-face\{[^}]*?font-weight:%d;[^}]*?base64,([A-Za-z0-9+/=]+)\)"%w, site)
    return TTFont(io.BytesIO(base64.b64decode(m.group(1))))
F300=jost(300); F500=jost(500)
# CJK font: Microsoft YaHei on Windows; fall back to any provided CJK TTF/TTC.
def cjk_font(bold=False):
    for p,n in ([(r"C:/Windows/Fonts/msyhbd.ttc",0)] if bold else [(r"C:/Windows/Fonts/msyh.ttc",0)]):
        try: return TTFont(p, fontNumber=n)
        except Exception: pass
    # generic fallbacks
    for p in ([r"C:/Windows/Fonts/simhei.ttf"] if bold else [r"C:/Windows/Fonts/Deng.ttf"]):
        try: return TTFont(p)
        except Exception: pass
    raise SystemExit("No CJK font found — install Microsoft YaHei or edit cjk_font().")
Y400=cjk_font(False); Y700=cjk_font(True)

def T(text, font, size, x, baseline, color, tracking=0.0):
    upm=font["head"].unitsPerEm; cmap=font.getBestCmap(); gs=font.getGlyphSet(); hmtx=font["hmtx"]
    s=size/upm; cur=0.0; parts=[]; trk=tracking*upm
    for ch in text:
        g=cmap.get(ord(ch))
        if g is None: cur+=upm*0.4+trk; continue
        pen=SVGPathPen(gs); gs[g].draw(pen); d=pen.getCommands()
        if d: parts.append(f'<path d="{d}" transform="translate({cur:.1f},0)"/>')
        cur+=hmtx[g][0]+trk
    return (f'<g fill="{color}" transform="translate({x:.1f},{baseline:.1f}) scale({s:.5f},{-s:.5f})">'+"".join(parts)+"</g>"), cur*s
def Wd(text,font,size,tracking=0.0):
    upm=font["head"].unitsPerEm; cmap=font.getBestCmap(); hmtx=font["hmtx"]; cur=0.0; trk=tracking*upm
    for ch in text:
        g=cmap.get(ord(ch)); cur+=(upm*0.4 if g is None else hmtx[g][0])+trk
    return cur*size/upm
def mark(cx, top, d, ring=INK, barc=TEAL, sr=0.16):
    st=d*sr; bw=d*1.18; bh=d*0.16
    return (f'<circle cx="{cx:.1f}" cy="{top+d/2:.1f}" r="{d/2:.1f}" fill="none" stroke="{ring}" stroke-width="{st:.1f}"/>'
            f'<rect x="{cx-bw/2:.1f}" y="{top+d+d*0.16:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{bh/2:.1f}" fill="{barc}"/>')
def bar(x,y,w,h,c): return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h/2:.1f}" fill="{c}"/>'
CW,CH=1004,638; RX=38
def svg(body,border=True,bg=PAPER):
    b=f'<rect x="0.5" y="0.5" width="{CW-1}" height="{CH-1}" rx="{RX}" fill="none" stroke="{HAIR}" stroke-width="1"/>' if border else ""
    return (f'<svg {NS} xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {CW} {CH}" width="{CW}" height="{CH}">'
            f'<clipPath id="rc"><rect width="{CW}" height="{CH}" rx="{RX}"/></clipPath>'
            f'<g clip-path="url(#rc)"><rect width="{CW}" height="{CH}" fill="{bg}"/>{body}</g>{b}</svg>')

ICONS={
 "email":'<g fill="none" stroke="{c}" stroke-width="1.8"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M3.5 7 L12 13 L20.5 7"/></g>',
 "phone":'<path fill="{c}" d="M6.6 3.5c.5 0 .9.3 1.1.8l1.2 3c.2.5.1 1-.3 1.4L8.2 13c1 2 2.8 3.8 4.8 4.8l1.3-1.4c.4-.4.9-.5 1.4-.3l3 1.2c.5.2.8.6.8 1.1V21c0 .8-.7 1.5-1.5 1.4C9.7 21.6 2.4 14.3 2.6 5 2.5 4.2 3.2 3.5 4 3.5z"/>',
 "web":'<g fill="none" stroke="{c}" stroke-width="1.7"><circle cx="12" cy="12" r="9.2"/><ellipse cx="12" cy="12" rx="4" ry="9.2"/><path d="M3 12h18M4.5 7h15M4.5 17h15"/></g>',
 "linkedin":'<g><rect x="2" y="2" width="20" height="20" rx="3.2" fill="{c}"/><rect x="5" y="9.5" width="2.7" height="9" fill="#fff"/><circle cx="6.35" cy="6.3" r="1.6" fill="#fff"/><path fill="#fff" d="M10 9.5h2.6v1.3c.5-.9 1.6-1.6 3-1.6 2.6 0 3.4 1.6 3.4 4v4.8h-2.7v-4.3c0-1.1-.4-1.9-1.5-1.9-1 0-1.5.7-1.5 1.9v4.3H10z"/></g>',
 "signal":'<g fill="none" stroke="{c}" stroke-width="1.8"><path d="M12 3.2c5 0 8.8 3.6 8.8 8 0 4.5-3.9 8-8.8 8-1.2 0-2.4-.2-3.4-.6L4 20l1.2-3.9C4 14.8 3.2 13 3.2 11.2c0-4.4 3.8-8 8.8-8z"/></g>',
 "whatsapp":'<g><path fill="{c}" d="M12 3.3c-4.8 0-8.7 3.9-8.7 8.7 0 1.6.4 3.1 1.2 4.4L3.2 21l4.8-1.3c1.2.7 2.6 1 4 1 4.8 0 8.7-3.9 8.7-8.7S16.8 3.3 12 3.3z"/><path fill="#fff" d="M9.2 7.7c-.2-.5-.4-.5-.6-.5h-.5c-.2 0-.5.1-.7.4-.3.3-1 1-1 2.3s1 2.7 1.1 2.9c.1.2 2 3.1 4.9 4.2 2.4.9 2.9.8 3.4.7.5-.1 1.6-.7 1.9-1.3.2-.6.2-1.2.2-1.3-.1-.1-.3-.2-.6-.3l-1.8-.9c-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1-.7-.3-1.5-.6-2.4-1.5-.7-.6-1.1-1.4-1.3-1.6-.1-.2 0-.4.1-.5l.5-.6c.1-.2.2-.3.3-.5.1-.2 0-.4 0-.5z"/></g>',
 "wechat":'<g fill="{c}"><path d="M8.6 4.3C4.9 4.3 2 6.9 2 10.1c0 1.8.9 3.4 2.4 4.5L3.8 16.4l2.1-1.1c.7.2 1.5.4 2.3.4h.5c-.2-.6-.3-1.2-.3-1.8 0-3.2 3-5.7 6.7-5.7h.5C15 6 12.1 4.3 8.6 4.3z"/><path d="M22 13.7c0-2.7-2.6-4.9-5.8-4.9s-5.8 2.2-5.8 4.9 2.6 4.9 5.8 4.9c.7 0 1.3-.1 1.9-.3l1.8.9-.5-1.5c1.6-.9 2.6-2.3 2.6-4z"/></g>',
}
def icon(name,x,y,size,c=INK):
    return f'<g transform="translate({x:.1f},{y:.1f}) scale({size/24.0:.4f})">'+ICONS[name].replace("{c}",c)+'</g>'
def crow(ic,val,x,y,sz=23,c=INK,ic_c=TEAL,zh=False):
    return icon(ic,x,y-sz*0.86,sz*1.05,ic_c)+T(val,Y400 if zh else F300,sz,x+sz*1.5,y,c)[0]
def lockup(x,base,size,sub):
    g,wmw=T("BIOHACK.IT",F300,size,x,base,INK)
    g+=bar(x,base+size*0.30,size*1.15,size*0.05,INK)
    g+=T(sub,F500,size*0.205,x+size*0.02,base+size*0.55,MUTED,tracking=0.24)[0]
    d=size*1.35; top=base-0.365*size-d/2
    g+=mark(x+wmw+size*0.6+d/2,top,d)
    return g
def qr_real(x,y,size):
    b64=base64.b64encode((REPO/"brand"/"wechat-qr.png").read_bytes()).decode()
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/png;base64,{b64}"/>'
            f'<rect x="{x-3}" y="{y-3}" width="{size+6}" height="{size+6}" rx="6" fill="none" stroke="{HAIR}" stroke-width="1"/>'
            +T("微信 · WeChat",Y400,17,x,y-9,MUTED)[0])
def qr_placeholder(x,y,size):
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="6" fill="#f6f8f8" stroke="{HAIR}" stroke-width="1"/>'
            +T("WeChat QR",F300,18,x+(size-Wd("WeChat QR",F300,18))/2,y+size/2+6,FAINT)[0]
            +T("微信 · WeChat",Y400,17,x,y-9,MUTED)[0])

# ---------- P1 layout, parameterised ----------
def card(D, real_qr=True):
    # FRONT (EN)
    f=lockup(80,140,112,"AN OPEN LABORATORY FOR LONGEVITY")
    f+=bar(80,252,CW-160,2,HAIR)
    f+=T(D["name_en"],F500,48,80,300,INK)[0]+T(D["title_en"]+"  ·  "+D["org_en"],F300,25,80,338,MUTED)[0]
    f+=T(D["desc_en"],F500,21,80,372,TEALD,0.02)[0]
    f+=crow("email",D["email"],80,450,23,INK)+crow("phone",D["phone"],80,490,23,INK)+crow("web",D["site"],80,530,23,TEALD,TEAL)
    f+=icon("signal",640,432,28,MUTED)+icon("whatsapp",686,432,28,MUTED)+icon("linkedin",732,432,28,MUTED)+T(D["link"],F300,19,640,490,MUTED)[0]
    # BACK (中文)
    b=lockup(80,140,112,D["payoff_zh"])
    b+=bar(80,252,CW-160,2,HAIR)
    b+=T(D["name_zh"],Y700,48,80,300,INK)[0]+T(D["name_zh2"],F300,22,80+Wd(D["name_zh"],Y700,48)+18,298,MUTED)[0]
    b+=T(D["title_zh"]+"  ·  "+D["org_zh"],Y400,24,80,338,MUTED)[0]+T(D["desc_zh"],Y700,22,80,374,TEALD)[0]
    b+=crow("email",D["email"],80,452,23,INK)+crow("phone",D["phone"],80,492,23,INK)+crow("wechat","微信 "+D["wechat"],80,532,23,INK,TEAL,True)
    b+=(qr_real(770,400,150) if real_qr else qr_placeholder(770,400,150))
    return f,b

FABIO=dict(name_en="Fabio Pietrosanti", name_zh="石风翔", name_zh2="Fabio Pietrosanti",
    title_en="Co-Founder", title_zh="联合创始人", org_en="Hacking Biology Foundation", org_zh="Hacking Biology 基金会",
    desc_en="Open-source biohacking software", desc_zh="开源生物黑客软件",
    email="research@hackingbiology.com", phone="+39 340 180 1049", site="biohack.it",
    link="linkedin.com/in/secret", wechat="fpietrosanti", payoff_zh="一个开放的长寿实验室")
TEMPLATE=dict(name_en="Full Name", name_zh="姓名", name_zh2="Full Name",
    title_en="Role", title_zh="职位", org_en="Hacking Biology Foundation", org_zh="Hacking Biology 基金会",
    desc_en="Open-source biohacking software", desc_zh="开源生物黑客软件",
    email="name@hackingbiology.com", phone="+00 000 000 0000", site="biohack.it",
    link="linkedin.com/in/username", wechat="wechat-id", payoff_zh="一个开放的长寿实验室")

# ---------- print-ready PDF (3mm bleed + crop marks) ----------
import pymupdf, subprocess, tempfile, shutil, os
MM=72/25.4
BLEED_MM=2; TRIM_MM=(85,54)
PPMM=CW/TRIM_MM[0]                       # SVG px per mm (1004px = 85mm)
BLP=BLEED_MM*PPMM                        # bleed in SVG px
BW,BH=CW+2*BLP, CH+2*BLP                 # bleed canvas in SVG px
SOFFICE=r"C:/Program Files/LibreOffice/program/soffice.exe"

def svg_print(body):
    """Bleed-size VECTOR svg: 89x58mm (trim 85x54 + 2mm bleed), white ground, no clip/border.
    Physical size set via width/height in mm so the exported PDF is exactly 89x58mm.
    All text/CJK is already outlined (paths) → no font dependency at the printer."""
    return (f'<svg {NS} xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {BW:.2f} {BH:.2f}" width="{TRIM_MM[0]+2*BLEED_MM}mm" height="{TRIM_MM[1]+2*BLEED_MM}mm">'
            f'<rect x="0" y="0" width="{BW:.2f}" height="{BH:.2f}" fill="{PAPER}"/>'
            f'<g transform="translate({BLP:.2f},{BLP:.2f})">'
            f'<rect width="{CW}" height="{CH}" fill="{PAPER}"/>{body}</g></svg>')

def _svg2pdf(svg_str, workdir, name):
    svgp=pathlib.Path(workdir)/f"{name}.svg"; svgp.write_text(svg_str, encoding="utf-8")
    prof=pathlib.Path(workdir)/f"lo_{name}"
    subprocess.run([SOFFICE,"--headless","--norestore","--convert-to","pdf","--outdir",str(workdir),
                    str(svgp),f"-env:UserInstallation=file:///{str(prof).replace(chr(92),'/')}"],
                   capture_output=True, text=True)
    return pathlib.Path(workdir)/f"{name}.pdf"

def print_pdf(front_body, back_body, out):
    """Vector 2-page PDF (front, back) via LibreOffice SVG->PDF, merged with PyMuPDF."""
    wd=tempfile.mkdtemp(prefix="card_")
    try:
        fp=_svg2pdf(svg_print(front_body), wd, "front")
        bp=_svg2pdf(svg_print(back_body),  wd, "back")
        if not fp.exists() or not bp.exists():
            raise SystemExit("LibreOffice SVG->PDF failed")
        doc=pymupdf.open()
        for pth in (fp,bp):
            src=pymupdf.open(str(pth)); doc.insert_pdf(src); src.close()
        # force the page box to exactly (trim + 2*bleed) mm, centred (trims only white bleed)
        tw=(TRIM_MM[0]+2*BLEED_MM)*MM; th=(TRIM_MM[1]+2*BLEED_MM)*MM
        for pg in doc:
            r=pg.rect; dx=(r.width-tw)/2; dy=(r.height-th)/2
            pg.set_mediabox(pymupdf.Rect(dx, dy, dx+tw, dy+th))
        doc.save(out, deflate=True, garbage=4); doc.close()
    finally:
        shutil.rmtree(wd, ignore_errors=True)
    return out

def build(D, name, real_qr):
    d=HERE/name; d.mkdir(parents=True, exist_ok=True)
    f,b=card(D, real_qr=real_qr)
    (d/"card-front.svg").write_text(svg(f,border=True),encoding="utf-8")
    (d/"card-back.svg").write_text(svg(b,border=True),encoding="utf-8")
    pdf=print_pdf(f, b, str(d/f"biohackit-card-{name}.pdf"))
    print(f"  {name}: SVGs + {pdf}")

if __name__=="__main__":
    print("Building business cards (layout P1)…")
    build(FABIO,"fabio",True)
    build(TEMPLATE,"template",False)
    print("Done. Print spec: 85x54mm trim, 2mm bleed (page 89x58mm), rounded corners r≈3.2mm (die-cut). Convert to CMYK at printer.")
