# Source — Claude preliminary landscape (captured 2026-08-20)

Shared conversation: https://claude.ai/share/70b73ac1-2843-460c-895b-e678453bfa66
Author prompt: "analisi di tutti i software che esistono per biohacking e biohacker".

> Verbatim capture of Claude's answer. Reference material for the competitive
> analysis; not authoritative. biohack.it positioning is set in the specs.

Nota preliminare: "biohacking" copre due mondi diversi, e il software segue la divisione. Il wetlab/DIYbio (ELN, sequenze, protocolli di laboratorio) e la self-quantification/longevity. Assumo il secondo, ma il primo ha una lezione di UX.

## 1. Tracker consumer di protocollo/stack — il segmento più affollato, esploso nel 2025-26
Biohackr, Biomarq, MyStack, Stackd, e tutta la nicchia peptidi (Protocol, PeptIQ, PepStack Pro, Peptide Tracker, Pep AI, Peptify). Pattern ricorrente: dose logging, inventario vial, ricostituzione, half-life, rotazione siti di iniezione, interaction checker, template di protocollo, lab tracker con reference range. Alcuni arrivano già a estrazione AI da referti + trend, con dashboard condivisibile con un coach. Tutti chiusi, dati locali o proprietari, zero open data, zero interoperabilità.

## 2. Piattaforme lab-first commerciali
Function Health, Superpower, SiPhox, Mito, One Twenty, InsideTracker, Lifeforce. Vendono i test e ci costruiscono sopra la dashboard. Function fa 100+ biomarcatori annui più un re-test parziale, con età biologica proprietaria; One Twenty punta su cadenza trimestrale e integrazione wearable. Walled garden per costruzione: il dato è il lock-in.

## 3. Età biologica e leaderboard — la parte "copy trading" già esistente
Rejuvenation Olympics (TruDiagnostic), Longevity World Cup, i Top 100 di NOVOS. Il Longevity World Cup è free e open source, classifica su PhenoAge, con l'idea esplicita di essere un progetto indipendente e non un funnel di marketing, mentre la Rejuvenation Olympics è legata a un unico fornitore di test costosi e ha cambiato più volte criteri e trasparenza. Qui il "profilo pubblico + reputazione" esiste già — ma su un solo numero, non sul protocollo che l'ha prodotto.

## 4. Aggregatori quantified-self e PHR open source — il layer riusabile
Fasten Health (GPL-3, PHR self-hosted, FHIR/Smart-on-FHIR), Mere Medical, Open mHealth, Open Wearables (MIT, unifica Garmin/Oura/Whoop/Apple in una sola API self-hosted), Heads Up Health lato clinica. Da valutare come sotto-strato invece che riscriverlo.

## 5. Ricerca partecipativa n-of-1 — l'antenato ideologico
Open Humans resta l'unico tentativo strutturato: importatori da 23andMe, Fitbit, Withings, VCF generici, e notebook Jupyter condivisibili che permettono esperimenti n=1 riproducibili senza esporre i dati personali. Più Quantified Flu, openSNP, Personal Science Wiki. Vivo ma sostanzialmente fermo.

## 6. Librerie scientifiche riusabili
Biolearn e pyaging per le clock: Biolearn è Python, multi-modalità, con testing automatico contro dati di riferimento, pyaging ne integra decine con backend PyTorch. Più ClockBase, methylCIPHER, BioAge. Codice pronto, licenze permissive.

## 7. Wetlab/DIYbio
protocols.io, Benchling, SciNote, OpenWetWare. Rilevanti non per il dominio ma per il modello: protocollo versionato, forkabile, citabile. È esattamente la metafora git di biohack.it.

## Dove sta il gap
Non manca il tracking del protocollo (ce n'è troppo), né la misura dell'età biologica (idem), né il social (le leaderboard esistono). Manca l'anello che lega intervento → biomarcatore in forma computabile e pubblica. Nessuno dei sette gruppi produce open data riutilizzabile, e nessuno codifica in RxNorm/LOINC/UCUM.

Due osservazioni scomode: (a) il rischio non è tecnico ma di adozione — Open Humans aveva la parte difficile già risolta e non ha raggiunto massa critica; (b) per il 90% degli utenti un tracker chiuso con AI decente è "abbastanza buono", quindi il differenziale open/AGPL parla a una minoranza. Il vantaggio competitivo reale è probabilmente il lato ricerca (il distributed trial), non il lato utente.
