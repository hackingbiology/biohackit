# Navigation & Information Architecture — hypotheses

> These are **hypotheses for us to revise together**, not decisions. They translate the capabilities into screens and flows so we can argue about the shape.

## Top-level information architecture

```
biohack.it
├─ Explore            (public, no account)  ─ browse protocols, profiles, compounds
│   ├─ Protocols       curated + community, filter by goal / hallmark / compound
│   ├─ People          discover by verified specialty (not popularity)
│   └─ Compounds       per-compound page → evidence + who takes it + forum thread
├─ My Dashboard       (account) ─ organ-system view, biological age, alerts
├─ My Protocol        builder · versions/history · publish
├─ Daily Log          30-sec check-off · adherence · wellness
├─ Measurements       import · manual entry · planner (calendar/year/table)
├─ Studies            N-of-1 with pre-registered endpoints
├─ For My Doctor      generate protocol sheet (link + PDF)
└─ Settings           profile · sharing (per-item) · Agent Access tokens
```

Public surfaces (Explore, a public Protocol page, a public Profile) are the acquisition channel and are indexable. Everything a logged-in user creates is **public by default** with per-item withholding; genomics is never on a shareable surface.

## Primary journeys

### J1 — Experienced biohacker, already running a protocol (the realistic T0 user)
```
Sign up ─▶ "You already have a protocol?" ─▶ Declare current interventions
   ─▶ Substance resolution + input/output diff ("8 in, 5 recognised, fix 3")
   ─▶ Mark protocol Active, "in effect since" ≠ "tracked since"
   ─▶ Upload past lab reports (backfill baseline)  ─▶ first charts
   ─▶ System proposes missing efficacy + safety markers (Accept-All/Reject-All)
   ─▶ Publish (public by default)  ─▶ appears in Explore
```
Key: capture a regimen that already exists and arrived through many changes; invite backfill of history and prior changes, never assume a clean start.

### J2 — Beginner who copies (the harm-reduction case)
```
Explore ─▶ open a public Protocol ─▶ see biomarker outcomes + Evidence Badge
   ─▶ "Follow / Copy this protocol"
   ─▶ FORK created (lineage kept)
   ─▶ ⛔ SAFETY GATE: mandatory baseline + inherited safety markers
        └─ cannot Activate until baseline recorded/acknowledged
   ─▶ dose sanity check on any edited dose
   ─▶ Activate ─▶ measurement plan computed ─▶ join cohort + forum thread
```

### J3 — Bring-your-reports onboarding (Blood Layer, zero spend)
```
Sign up ─▶ Upload PDF/photo/CSV ─▶ PII obfuscation (reviewable diff)
   ─▶ deterministic extract (or learned lab template) ─▶ HUMAN REVIEW
        recognised / not-recognised / inferred  ─▶ confirm
   ─▶ dashboard populates ─▶ "first chart in 10 minutes, bought nothing"
```

### J4 — The measurement cycle
```
Planner computes due analytes ─▶ pools into ONE draw (fasting/wash-out honoured)
   ─▶ generate lab request ─▶ user uploads report ─▶ parse ─▶ review
   ─▶ values populate dashboards + curves
   ─▶ Overdue surfaces as SAFETY ("rapamycin 94d, liver panel overdue 34d")
```

### J5 — Protocol changes over time (versioning)
```
Edit dose/cycle ─▶ new version + change event {old→new, when, why}
   ─▶ measurements bind to the version active on their date
   ─▶ history timeline + version diff viewable by user and public viewer
```

### J6 — Doctor handover
```
My Protocol ─▶ "Prepare for my doctor" ─▶ protocol sheet
   (everything taken, doses, timing, since when, markers + rationale, trends, alerts)
   ─▶ share as link + PDF (legible without an account)
```

### J7 — N-of-1 Study
```
New Study ─▶ declare question + ENDPOINT (before T0, timestamped)
   ─▶ timepoints T0..Tn + battery ─▶ overlaid on planner
   ─▶ run ─▶ pre/post read-out vs pre-registered endpoint (null allowed;
      "not determinable" if under-covered)
```

## Cross-cutting UI patterns (reused, from spec §8.5ter)
- 4-step onboarding with persistent progress until complete.
- AI proposals always as a block with **Accept-All / Reject-All** — propose, never impose.
- Explicit legend of item status: recognised / not-recognised / inferred.
- Mandatory human-review step before extracted data enters the system.
- Empty states that teach ("upload a report you already have"), never sell.
- Early snapshot of the result during long waits.
