# Wireframes — low-fidelity hypotheses

> Low-fi, ASCII, deliberately ugly. The point is layout, information priority, and flow — **not** visual design. Mark anything you want to move, cut, or add; we revise together.

Legend: `[button]` `( )` radio `[x]` checkbox `▸` expandable `◔` data-quality dot `⚠` safety.

---

## W1 · Public Protocol page (the acquisition + copy surface)

```
┌────────────────────────────────────────────────────────────────────┐
│ biohack.it   Explore  People  Compounds            [Sign in]        │
├────────────────────────────────────────────────────────────────────┤
│  Rapamycin + Metformin longevity base           origin: COMMUNITY   │
│  by @fabio  ·  verified reports ✓  ·  forked 12×  ·  cohort: 340    │
│                                                     [ Copy / Follow ]│
│                                                                      │
│  EVIDENCE BADGE  (calculated — not a claim)                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Rapamycin 6mg/week · 94 days · adherence 91%                  │  │
│  │ ApoB 78→91 (+17%) · ALT stable · lymphocytes −18%            │  │
│  │ 3 measurements · single lab · reports verified               │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  INTERVENTIONS                         GOALS → hallmarks             │
│   • Rapamycin  6mg  weekly (Mon) pulsed   • Senescence  ▸           │
│   • Metformin  500mg  2×/day continuous   • Inflammation ▸          │
│                                                                      │
│  OUTCOMES (literature ┈ vs cohort ━)      SAFETY MARKERS (inherited) │
│   [ ApoB curve: prediction vs observed ]   ⚠ ALT/AST  ⚠ creatinine  │
│                                             lymphocytes, fasting glc │
│                                                                      │
│  Discuss on Rapamycin News  ▸ (thread linked)                       │
└────────────────────────────────────────────────────────────────────┘
```
Priority order: what it is → is it trustworthy (badge) → what it involves → does it work (double column) → is it safe → discuss. `Copy/Follow` is always visible.

---

## W2 · Copy → Safety gate (harm reduction, blocks activation)

```
┌────────────────────────────────────────────────────────────────────┐
│  You're copying:  Rapamycin + Metformin base   (forked from @fabio) │
├────────────────────────────────────────────────────────────────────┤
│  ⚠ Before you can activate this protocol:                           │
│                                                                      │
│  BASELINE REQUIRED            SAFETY MARKERS (auto-added)            │
│   [x] Lipid panel (ApoB)       • ALT, AST      (rapamycin, metf.)   │
│   [ ] Kidney (creatinine)      • creatinine, eGFR                    │
│   [ ] Liver (ALT/AST)          • fasting glucose, HbA1c              │
│   [ ] Fasting glucose                                                │
│                                                                      │
│   ○ I have these reports  → [ Upload ]                               │
│   ○ I'll enter them manually                                         │
│   ○ I understand the risk and acknowledge  (logged)                 │
│                                                                      │
│                    [ Can't activate yet ]   ← disabled until met    │
└────────────────────────────────────────────────────────────────────┘
```

---

## W3 · My Dashboard (organ-system view; efficacy AND safety in one tile)

```
┌────────────────────────────────────────────────────────────────────┐
│  My Dashboard        Biological age Δ  −1.4y  (±2.1, PhenoAge, LabX)│
├───────────────┬───────────────┬───────────────┬────────────────────┤
│ LIPIDS   ◔◔◔◕ │ KIDNEY   ◔◔◑  │ LIVER   ◔◔◔◔  │ INFLAMMATION ◔◑    │
│ ApoB ↑ +17%   │ ⚠ creatinine  │ ALT stable    │ hsCRP ↓            │
│ optimal: out  │   not measured │               │                    │
│ reason: rapa  │   8 months —   │ reason: rapa  │ reason: goal       │
│               │   nephrotoxic  │               │                    │
│               │   compound ⚠   │               │                    │
├───────────────┴───────────────┴───────────────┴────────────────────┤
│ ◔ = data completeness/freshness   "Metabolic: 6/13, 4 months ago"   │
│ Index shown only where coverage suffices, else "not determinable".  │
└────────────────────────────────────────────────────────────────────┘
```
The kidney tile shows the whole thesis: the same tile that would show efficacy shows the safety gap.

---

## W4 · Import lab report → human review (fail loudly)

```
┌────────────────────────────────────────────────────────────────────┐
│  Import report   [ drop PDF/photo/CSV ]     PII removed ✓ (view diff)│
├────────────────────────────────────────────────────────────────────┤
│  We read 68 results. Review before saving:                          │
│   ✓ recognised (61)   ? not recognised (4)   ~ inferred (3)         │
│                                                                      │
│   ✓ ApoB        91 mg/dL   LOINC ok   method: immunoturb.  LabX      │
│   ✓ ALT         22 U/L     LOINC ok                                  │
│   ? "Lp-PLA2"   —          not mapped → [ map ] or leave ambiguous  │
│   ~ eGFR        88         inferred from creatinine  [confirm]       │
│                                                                      │
│  8 submitted · 5 recognised · 3 not understood  ← always shown       │
│                    [ Confirm & save ]   [ Cancel ]                   │
└────────────────────────────────────────────────────────────────────┘
```

---

## W5 · Protocol builder + version history

```
┌────────────────────────────────────────────────────────────────────┐
│  My Protocol   [ Draft ▸ Active ]     History ▾   [ Publish ]        │
├──────────────────────────────────┬─────────────────────────────────┤
│  INTERVENTIONS            [ + add]│  HISTORY / VERSIONS             │
│  • Rapamycin 6→8 mg weekly Mon    │  v4  today  dose 6→8mg  "raise" │
│      pattern: pulsed on:[Mon]     │  v3  Jul 2  added metformin     │
│      ⚠ dose check: within range   │  v2  Jun 10 baseline import     │
│  • Metformin 500mg 2×/day         │  v1  Jun 10 created             │
│                                   │  [ diff v3 ↔ v4 ]               │
│  SYSTEM PROPOSES (Accept/Reject)  │                                 │
│  + add creatinine, eGFR (safety)  │  measurements bind to the       │
│  + add lymphocytes (efficacy)     │  version active on their date   │
│  [ Accept all ] [ Reject all ]    │                                 │
└──────────────────────────────────┴─────────────────────────────────┘
```

---

## W6 · Daily Log (30 seconds; 4-state adherence + wellness)

```
┌────────────────────────────────────────────────────────────────────┐
│  Today   Mon 4 Aug            adherence today 100% · streak 12d      │
├────────────────────────────────────────────────────────────────────┤
│  MORNING            ✓ taken  ◐ partial  ⤫ skipped  ○ forgot         │
│   Rapamycin 8mg     (•) ( ) ( ) ( )                                 │
│   Omega-3 4 caps    (•) ( ) ( ) ( )                                 │
│  EVENING                                                            │
│   Metformin 500mg   ( ) ( ) ( ) (•)   ← forgot                      │
│                                                                     │
│  WELLNESS   mood ●●●●○  energy ●●●○○  sleep 7.5h  quality ●●●●○      │
│  note: ____________________________________                        │
│                                              [ Save ]               │
└────────────────────────────────────────────────────────────────────┘
```

---

## W7 · For My Doctor (handover sheet)

```
┌────────────────────────────────────────────────────────────────────┐
│  Protocol sheet — @fabio — generated 4 Aug 2026     [PDF] [link]    │
├────────────────────────────────────────────────────────────────────┤
│  TAKING NOW              dose      since        why measured         │
│   Rapamycin 8mg/wk Mon   8 mg      Jun 10       mTOR; watch lipids,  │
│                                                 lymphocytes, liver   │
│   Metformin 500mg 2×/d   500 mg    Jul 2        glucose control      │
│  MONITORED   ApoB↑, ALT/AST stable, creatinine (overdue ⚠),         │
│              lymphocytes −18%, fasting glucose normal               │
│  OPEN ALERTS ⚠ creatinine overdue 34 days while on rapamycin        │
│  Legible without an account.                                        │
└────────────────────────────────────────────────────────────────────┘
```

---

## Open layout questions for review
- Dashboard default: organ-system grid (above) vs a single headline number first? (I chose grid; biological age is one tile, not the hero.)
- Where does the **cohort comparison** live — inside each dashboard tile, or a dedicated "vs cohort" tab?
- Copy-flow: is the acknowledge-the-risk option (W2, 3rd radio) acceptable, or must real baseline values be mandatory with no acknowledge-only bypass?
