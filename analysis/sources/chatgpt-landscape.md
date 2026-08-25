# Source — ChatGPT preliminary landscape (captured 2026-08-20)

Shared conversation: https://chatgpt.com/share/6a8d627d-ea84-83ed-b7ea-9c057b6d2c54
Author prompt: "analisi di tutti i software che esistono per biohacking e biohacker".

> Verbatim capture of ChatGPT's answer (as rendered ~2026-08). Reference material;
> not authoritative. ChatGPT flags this as a "V1 serious research, not frozen".

## Framing
Distinguere biohacking da fitness tracking. Un vero software da biohacker dovrebbe:
acquisire → normalizzare → interpretare → formulare ipotesi → proporre interventi → misurare l'intervento → confrontare prima/dopo → aggiornare l'ipotesi. Open Humans definisce quest'area "personal science" (fino a esperimenti N-of-1).

## Mappa del mercato (categoria · software · cosa fanno · quanto "biohacker" ★/5)
- Health data aggregator · **Guava** · wearable + cartelle cliniche + labs + sintomi + farmaci + documenti · ★★★★☆
- Professional health dashboard · **Heads Up Health** · labs + wearable + medical devices + EHR + AI · ★★★★☆
- Quantified Self · **Exist.io** · salute, sonno, attività, produttività, mood, calendario · ★★★★☆
- Personal science · **Open Humans** · repository dati + API + ricerca personale + N-of-1 · ★★★★★
- Biomarker optimization · **InsideTracker** · sangue + DNA + wearable + raccomandazioni · ★★★★☆
- Genomic optimization · **SelfDecode** · DNA + labs + rischi + interventi · ★★★★☆
- HRV / autonomic · **Welltory** · HRV, stress, attività, wearable · ★★★☆☆
- HRV research/training · **HRV4Training** · HRV + stress + performance · ★★★★☆
- Apple Watch optimization · **Bevel** · recovery, strain, sleep · ★★★☆☆
- Apple Watch optimization · **Athlytic** · recovery, exertion, sleep, training · ★★★☆☆
- Nutrition · **Cronometer** · macro/micronutrienti + biomarkers + wearable · ★★★☆☆
- Symptom/self-experiment · **Bearable** · sintomi, interventi, correlazioni · ★★★★☆
- Wearable infrastructure · **Terra** · API unificata wearable/sensori/labs · ★★★★★ (infrastruttura)
- Medical data infrastructure · **Metriport** · FHIR/EHR/medical data open source · ★★★★★ (infrastruttura)
- Medical data API · **Human API** · medical records + labs + pharmacy + wearable · ★★★★☆
- CGM ecosystem · **Levels, Signos** · glucosio + pasti + esercizio · ★★★☆☆
- Sleep ecosystems · **Oura, WHOOP, Eight Sleep** · sonno/recovery/readiness · ★★★☆☆
- Genomics specialist · **Promethease/SNPedia** · interpretazione varianti · ★★★★☆
- DIY/data-science · **Python/R/Jupyter** · analisi arbitrariamente sofisticata · ★★★★★
- Bioinformatics · **VEP, OpenCRAVAT, PLINK** · WGS/VCF/PRS/variant analysis · ★★★★★ (biohacker avanzato)

## Deep dives
1. **Guava** — "personal health OS": cartelle cliniche, esami, farmaci, diagnosi, wearable, pressione, glucosio, sintomi, sonno, alimentazione, umore, attività, ciclo, PDF, CCDA, DICOM, dati genetici, CSV, tutti sulla stessa timeline con ricerca di relazioni. API in early access. Forte: parte dalla persona, non dal wearable. Limite: molto orientata al sistema sanitario USA (poco utile per un europeo).
2. **Heads Up Health** — quello che userebbe una longevity clinic. Vende a longevity programs, biohacking centers, concierge medicine, functional medicine, wellness clinics. Aggrega labs/wearable/devices/EHR + AI, outcome anche a livello di coorte. Limite: costruito per il professionista (500 pazienti), non per l'auto-sperimentatore.
3. **Exist.io** — erede del Quantified Self. Importa Apple Health, Fitbit, Garmin, Oura, Withings, Strava + calendario, GitHub, RescueTime, Todoist, Toggl, Last.fm, screen time, mood. Motore di correlazioni, non sistema di sperimentazione.
4. **Open Humans** — filosoficamente il più vicino. data → dataset → hypothesis → experiment → research. Supporta Oura, Fitbit, Google Fit, Apple Health, 23andMe, AncestryDNA, genome/exome, Nightscout, microbiome, OpenAPS, custom files. Ospita progetti di self-research. Storage privato, permessi granulari.
5. **InsideTracker** — biohacking consumer: blood + DNA + wearable → optimization, range personalizzati, raccomandazioni; InnerAge (età biologica da sangue). Limite: "ottimizza questo biomarker", non inferenza causale su interventi multipli.
6. **SelfDecode** — 1.500+ DNA reports, 4.000+ lab markers, 200M+ varianti, polygenic risk scores, lab+DNA, suggerimenti esami/supplementi/lifestyle/nutrizione, monitoraggio dinamico. Luglio 2026: usa DNA + risultati precedenti per suggerire quali biomarker misurare. Limite: genotype → risk → recommendation, non hypothesis → intervention → measurement → causal inference.
7. **Bearable** — symptom/N-of-1 tracker: interventi → comportamenti → sintomi → outcome, correlazioni. "Cosa cambia quando faccio X?".
8. **Welltory** — HRV-centrico (Apple Health, Health Connect, Samsung Health). Non è medical app, non acquisisce medical data.
9. **HRV4Training** — HRV verticale, sensori BT (Polar H7/H10), studi di validazione. Serio per biohacking sportivo.
10. **Athlytic / Bevel** — intelligence sopra Apple Health (Recovery/Exertion/Sleep). "WHOOP senza WHOOP". Ottima UX, non software da biohacker in senso stretto.
11. **Cronometer** — database nutrizionale ideale: micronutrienti, vitamine, minerali, aminoacidi, lipidi; scambia via Health Connect glucosio, pressione, HRV, SpO2, sonno, peso.
12. **Terra** — infrastruttura, unified health API. Centinaia di sorgenti: Garmin, Fitbit, Oura, WHOOP, Apple Health, Google Fit, Samsung, Withings, Polar, Dexcom, Cronometer, Strava, Eight Sleep + CGM + blood biomarkers. Streaming realtime e webhook.
13. **Metriport** — medical data, open source, FHIR-native: EHR, clinical history, C-CDA, PDF, FHIR R4, healthcare networks.
14. **Human API** — aggrega medical records, labs, pharmacy, wearable in REST API. Concorrente parziale di Terra/Metriport.

## Secondo universo (usato dal biohacker avanzato)
- Genomica: 23andMe, SelfDecode, Promethease, SNPedia, openSNP, PLINK, VEP, OpenCRAVAT, bcftools, Gene.iobio
- Microbiome: Biomesight, Ombre, Viome
- CGM: Dexcom, Libre, Levels, Signos, January AI, Nightscout
- Sonno: Oura, WHOOP, Eight Sleep, Sleep Cycle, AutoSleep
- Metabolismo/cardio: Cardiogram, Qardio, Withings, Garmin, Apple Health
- Nutrizione: Cronometer, MacroFactor, MyFitnessPal, ZOE
- Brain/neurofeedback: Muse, BrainHQ, Sens.ai
- Blood/longevity: InsideTracker, Function Health, SiPhox, Superpower
- Estremo: Python + Jupyter + R (per il tecnicamente capace, ancora il più potente)

## I buchi identificati
- Il livello superiore "Biohacker OS" (personal biology → timeline → AI → hypothesis/experiments/literature → N-of-1 → conclusions) non è realizzato bene da nessuno.
- Mancano gli **esperimenti** strutturati (Hypothesis/Intervention/Confounders/Endpoints/Baseline/Experiment/Washout + analisi N-of-1).
- Manca la **causal inference** (cross-correlation, lagged variables, within-person regression, change-point detection, interrupted time series, ABAB, Bayesian updating, confounder adjustment, dose-response, multiple comparison correction).
- Manca il territorio **farmaci** (modello meccanicistico metformina/SGLT2/GLP-1/rapamicina + interazioni + letteratura).
- Manca il **longitudinal medical knowledge graph** (biomarker collegati biologicamente + PubMed/trials/pathways).
- Manca il calcolo automatico delle **biological clocks** (PhenoAge, Levine, BioAge, Klemera-Doubal, GrimAge, DunedinPACE, organ-specific) con contributo per-biomarker.

## Classifica concettuale (top 10 da studiare)
1 Open Humans · 2 Heads Up Health · 3 Guava · 4 SelfDecode · 5 InsideTracker · 6 Exist.io · 7 Bearable · 8 Terra · 9 Metriport · 10 Cronometer. Poi Oura/WHOOP/Bevel/Athlytic per la UX.

## V2 update (seconda risposta, dataset di 64 prodotti)
Correzione: la categoria "Biohacker OS" sta nascendo nel 2026.
- **Outliyr** — si presenta come self-experimentation OS: baseline, esperimenti N-of-1, wearable, labs, genetica/epigenetica, supplement stack, "AI Personal Scientist", MCP verso ChatGPT/Claude.
- **Trialist** — esperimenti N-of-1 localmente sopra Apple Health.
- **Protocol** — converte un claim sanitario in un esperimento personale di 21 giorni.
- **Aurboda** — personal data warehouse PostgreSQL interrogabile via MCP.
- **Open Wearables** — equivalente open-source/self-hosted di Terra.
- **Android Health Connect** — struttura anche medical-record data.
Aggiornamenti commerciali: Function Health 160+ test annuali + imaging; Superpower biomarker+wearable+AI+protocolli; Levels ora glucose+food+sleep+activity+labs+DEXA+health records.

Le 5 primitive dati proposte: **Observation → Intervention → Hypothesis → Experiment → Finding** (più potente di user → biomarkers → graphs).

EU/EHDS: regolamento in vigore 26 marzo 2025, fasi operative dal 2029; labs/imaging/discharge dal 2031 + dati genomici per uso secondario. Opportunità: progettare EU-native (provenance, consent, interoperability, audit, export, ownership) invece che US-first adattato a GDPR.

Build vs buy per un ipotetico Biohacker OS: comprare il layer di ingestion (Terra/Open Wearables/Metriport), sviluppare l'IP: personal biological model + intervention engine + experiment engine + evidence engine + AI reasoning.

Cautela dichiarata: V1, non versione da congelare; il livello successivo è una claim-level evidence matrix (ogni capability collegata alla fonte, con verified_on, prezzo, paese, API, status live/beta/coming-soon/deprecated).
