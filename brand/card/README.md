# BIOHACK.IT — business card (layout P1)

Chosen design. Front **English**, back **中文** (one language per side).
Regenerate everything with:

```bash
python brand/card/build_card.py
```

## Print specification (as required by the print shop)
- **Trim size:** 85 × 54 mm
- **Bleed:** 2 mm each side → **file page 89 × 58 mm**
- **Corners:** rounded, radius ≈ 3.2 mm (die-cut by the printer)
- **File:** 2-page PDF (page 1 = front / EN, page 2 = back / 中文), ~450 dpi, no crop marks
- Card background is white, so the 2 mm bleed is white (seamless at the cut)
- Convert to CMYK at the printer; keep teal `#0C877A` and charcoal `#25292C`

## Fonts
- Latin: **Jost** (300/400/500) — embedded as vector outlines from `docs/index.html`
- CJK: **Microsoft YaHei** (regular + bold) — system font; edit `cjk_font()` for another machine

## Files
- `fabio/` — Fabio Pietrosanti's card (real data + real WeChat QR from `brand/wechat-qr.png`)
  - `card-front.svg`, `card-back.svg` (with a hairline keyline, screen preview)
  - `biohackit-card-fabio.pdf` (**print-ready**, no keyline)
- `template/` — same layout with placeholder fields and a **WeChat-QR placeholder box**, for future team cards
  - fill `TEMPLATE` in `build_card.py` (or copy the block) with the new person's data + drop in their WeChat QR

## Content model (per person)
name (EN + 中文 + latin sub), title (EN + 中文), org (Hacking Biology Foundation / 基金会),
descriptor "Open-source biohacking software / 开源生物黑客软件", email, phone, biohack.it,
LinkedIn (front), WeChat id + QR (back), Signal/WhatsApp icons (front).
