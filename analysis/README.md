# Competitive landscape — biohacking / longevity software

This folder holds the **landscape database** for biohack.it: a normalised, comparable
inventory of the biohacking, longevity and health-tracking software named by two
preliminary AI landscape passes.

## Provenance

Everything here derives from two shared conversations, both captured **2026-08-20**,
each answering the prompt *"analisi di tutti i software che esistono per biohacking e biohacker"*:

- **Claude** — https://claude.ai/share/70b73ac1-2843-460c-895b-e678453bfa66
- **ChatGPT** — https://chatgpt.com/share/6a8d627d-ea84-83ed-b7ea-9c057b6d2c54

Verbatim captures live in [`sources/claude-landscape.md`](sources/claude-landscape.md)
and [`sources/chatgpt-landscape.md`](sources/chatgpt-landscape.md). These are the **only**
authoritative input. Nothing in the database was invented beyond them; fields the sources
do not support are set to `null` / `"unknown"` rather than guessed. ChatGPT explicitly
flagged its answer as **"V1 serious research, not frozen"** — so licence, pricing, region
and status should be treated as indicative and verified per-claim before any external use.

## Files

| File | What it is |
|------|------------|
| `competitors.json` | **Machine-readable source of truth.** One object per product/platform/library/infrastructure (89 objects: 88 competitors + one `biohack.it` reference row). Full schema below. |
| `competitors.csv` | Flattened view for spreadsheets. Capabilities become `cap_*` columns with `1` / `0` / blank (blank = unknown). Derived from the JSON — do not hand-edit; regenerate instead. |
| `sources/*.md` | The two verbatim source captures. |
| `../docs/analysis/competitive-landscape.html` | The **unlisted** visual report (see below). |

## `competitors.json` schema

Each entry carries: `name`, `aka[]`, `category`, `one_liner`,
`license{open_source, spdx_or_detail}`, `open_data`, `commercial_model`, `pricing_note`,
`target`, `hosting`, `data_standards[]`,
`capabilities{}` (booleans/`null` for wearables, labs, genomics, microbiome, imaging,
medications, supplements, nutrition, symptoms, timeline, n_of_1, causal_inference,
biological_clocks, ai_reasoning, api, data_export, self_hosting),
`intervention_biomarker_link`, `biohacker_os_closeness` (0–5), `region_focus`, `status`,
`source[]` (which pass named it), `source_urls[]`, `notes`.

`category` is one of: consumer-tracker, peptide-tracker, lab-first-commercial,
bioage-leaderboard, phr-aggregator, quantified-self, participatory-research,
aging-clock-library, bioinformatics, wetlab-eln, wearable-infra, medical-infra, cgm,
sleep, nutrition, genomics, microbiome, neurofeedback, biohacker-os.

The final object, `biohack.it`, is a **reference row** filled from the project positioning
spec (not from the two sources) so the report can show where biohack.it sits.

## The report (unlisted)

`../docs/analysis/competitive-landscape.html` is a self-contained, print-clean, light-only
page in the biohack.it brand (Jost display + Georgia body, fonts inlined, no external
assets). It is **UNLISTED**: intentionally *not* linked from `docs/index.html` nav/footer
or anywhere public. It is reachable only by direct URL:

```
https://biohack.it/analysis/competitive-landscape.html
```

Do not add a link to it from any public page.

## Regenerating

There is no committed build script yet. The report and CSV were generated from
`competitors.json` plus the three `@font-face` blocks pulled verbatim from
`docs/index.html`. If a generator is later added, it belongs here as e.g.
`analysis/build_report.py`, reading `competitors.json` as its input and writing both
`competitors.csv` and `docs/analysis/competitive-landscape.html`. Until then, treat
`competitors.json` as the edit surface and re-derive the other two artefacts from it.

## Not done yet — pending joint step

This is the **landscape / DB** deliverable only. The comparative **SWOT of biohack.it vs
these tools** — strengths/weaknesses read through the non-profit + biohacker-target lens
(open data by default, standards-coding, computable-and-public intervention→biomarker,
AGPL) — is a **separate, pending** step and has **not** been done here.
