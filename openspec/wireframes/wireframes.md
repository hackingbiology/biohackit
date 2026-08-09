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
│  1) Provide baseline (REQUIRED):                                    │
│       [ Upload reports ]    or    [ Enter manually ]                │
│  2) [x] I understand and acknowledge the risk   (REQUIRED, logged)  │
│                                                                      │
│         [ Activate ]   ← enabled only when 1 AND 2 are both done    │
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
│ optimal: out  │   not measured │ optimal: in   │ optimal: in        │
│ pctl 78 ♂/age │   8 months —   │ pctl 41 ♂/age │ pctl 22 ♂/age     │
│ vs cohort +3 ▸│   nephrotoxic ⚠│ vs cohort −1 ▸│ vs cohort −4 ▸    │
│ reason: rapa  │               │ reason: rapa  │ reason: goal       │
├───────────────┴───────────────┴───────────────┴────────────────────┤
│ ◔ completeness/freshness · pctl = sex/age-normalized percentile ·   │
│ "vs cohort ▸" = inline ref (A), opens the dedicated "vs cohort"     │
│ view (B) with distribution + n. Index only where coverage suffices. │
└────────────────────────────────────────────────────────────────────┘
```
The kidney tile shows the whole thesis: the same tile that would show efficacy shows the safety gap. Each tile also carries the sex/age-normalized percentile and a lightweight cohort reference that deep-links to the full "vs cohort" view.

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

## Layout decisions (resolved 2026-08-04)
- Dashboard leads with the **headline biological-age Δ**, then the organ-system grid (O5).
- Cohort comparison lives **both** inline on each tile **and** in a dedicated "vs cohort" view (O6).
- Every biomarker also shows its **sex/age-normalized percentile**.
- ~~Copy-flow acknowledge bypass~~ **RESOLVED**: baseline values are required **and** an explicit risk acknowledgment is **also** required — acknowledgment is never a bypass. (W2 updated)
