# HackingBiology / biohack.it

**HackingBiology** è l'**organizzazione** (non-profit). **biohack.it** è il **software** e l'**iniziativa**.

Piattaforma open source (AGPL-3.0) e gratuita dove i biohacker documentano il proprio protocollo
in modo strutturato (cosa prendono/fanno, dosi, timing, cicli) e ne misurano efficacia e sicurezza
tramite biomarcatori, condividendo pubblicamente protocollo e risultati — con una dinamica sociale
tipo "copy-trading" applicata alla salute. Motore etico: riduzione del danno per i principianti.

Fondatore: Fabio. Comunità di riferimento preesistente: [Rapamycin News](https://www.rapamycin.news)
(Discourse). Sito storico dell'organizzazione: https://hackingbiology.com

## Documentazione (`docs/`)

Importata dalla conversazione claude.ai *"Piattaforma biohacking per protocolli e biomarcatori"*
senza upload di file (via browser), più il deck originale dal thread Rapamycin News.

| File | Contenuto | Stato |
|---|---|---|
| `docs/hackingbiology-project-spec.md` | Spec di progetto v0.3 — l'INDICE (service design, moduli M1–M13, analisi tecnica, roadmap, competitivo) | ✅ |
| `docs/getbased-reuse-analysis.md` | Analisi riuso di `get-based` (AGPL) — Tier A/B/C, strategia | ✅ |
| `docs/slides/hacking-biology-project-presentation.pdf` | Deck originale 14 slide (Google Slides pubblico) | ✅ |
| `docs/myagingtests-mappatura-report.md` | Report test pipeline MyAgingTests | ⬜ da importare |
| `docs/protocolengine-analysis.md` | Analisi ProtocolEngine | ⬜ da importare |
| `docs/myagingtests-analysis.md` | Analisi MyAgingTests | ⬜ da importare |
| `docs/bloodwork-layer-analysis.md` | Analisi Blood Layer (Lucis, SiPhox, TestResult, BloodGPT) | ⬜ da importare |
| `docs/lamplit-analysis.md` | Analisi Lamplit | ⬜ da importare |

## Specifica funzionale (OpenSpec)

La specifica funzionale vive in [`openspec/`](openspec/). **Parti da [openspec/REVIEW-GUIDE.md](openspec/REVIEW-GUIDE.md)** per una revisione guidata: 17 capability (domain-model + M1–M13 e affini), 85 requirement / 92 scenari, più flussi di navigazione e wireframe a bassa fedeltà in [`openspec/wireframes/`](openspec/wireframes/). Le decisioni che rivedono lo spec v0.3 e le domande aperte sono raccolte nella review guide.

## Presentazione

Deck in inglese per il **Biohacker track** del TimePie Longevity Forum: [docs/presentation/timepie-forum.html](docs/presentation/timepie-forum.html) (pubblicato come Artifact per revisione condivisa).

## Fonti

- claude.ai chat `79c61f96-5b41-433d-b75c-a898c7339488` (spec + companion analyses)
- Rapamycin News thread: https://www.rapamycin.news/t/hacking-biology-new-member-developing-a-longevity-biohacking-plan-platform/15776
- Slides (Google): `docs.google.com/presentation/d/1_g1nXjKmncs1HnObXAovE6_PRGuHx5psdbx8wN3Pui8`
- Codice da riusare: https://github.com/elkimek/get-based (AGPL-3.0)
