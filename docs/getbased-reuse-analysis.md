# getbased → biohack.it
## Analisi e strategia di riuso

*4 agosto 2026. Fonti: `github.com/elkimek/get-based`, `docs.getbased.health`, ispezione dell'app in esecuzione. Companion a `hackingbiology-project-spec.md` v0.3.*

---

## 0. Il fatto che cambia tutto

**Licenza: AGPL-3.0-or-later.** La stessa che hai già scelto nelle slide.

È la prima volta, in tutta questa rassegna competitiva, che il riuso non è una questione di ispirazione ma di `git clone`. ProtocolEngine, MyAgingTests, Lucis, SiPhox, TestResult, BloodGPT e Lamplit sono tutti banche dati proprietarie da studiare e non toccare. **getbased si può prendere.**

L'unico obbligo AGPL §13 — chi esegue una versione modificata come servizio di rete deve offrirne il sorgente — è già il tuo piano.

---

## 1. Cos'è

Piattaforma personale di health intelligence organizzata su **cinque lenti**: Labs, Genome, Body, Light, Insight. Gratuita, open source, **local-first**: nessun account, nessun server, tutto in `localStorage` + IndexedDB, cifrato AES-256-GCM, con sync opzionale end-to-end via CRDT (Evolu) e mnemonic a 24 parole.

Stato del progetto: 1.303 commit, 90 release, ultima v1.7.7, 71 stelle, 12 fork, 10 issue aperte, CI su ogni PR, test Node + Vitest + Playwright/Puppeteer. Manutentore sostanzialmente singolo. JavaScript 90%, CSS 8,5%.

**Stack**: nessun bundler. Moduli ES nativi caricati dal browser, Chart.js 4.4.7, pdf.js, transformers.js + OPFS per il RAG locale, PWA installabile, deploy su Vercel con tre sole funzioni serverless (share cifrato, proxy OAuth/CAMS, versione). Architettura a **6 livelli** con regola esplicita di non-import intra-livello.

**Sei provider AI a scelta**, incluso locale (Ollama, LM Studio, Jan, llama.cpp) e "porta il tuo endpoint". Con un modello locale il costo è zero e nulla lascia la macchina.

---

## 2. Il disallineamento architetturale, detto subito

getbased è **radicalmente individuale**: nessun account, nessuna identità, nessun server, dati che non escono dal browser.
biohack.it è **radicalmente collettivo**: coorti, confronto tra pari, aggregazione, open data.

Sono premesse opposte, e non è un difetto di nessuno dei due. Significa però una cosa precisa: **non si forka getbased per "aggiungerci la community"**. Il local-first non è un dettaglio implementativo, è il centro del loro design — e l'assenza di codici condivisi (§4) rende i loro dati non aggregabili per costruzione.

Il riuso va quindi impostato **a livello di componente, non di prodotto**. Che è poi l'esito migliore possibile: il layer individuale è esattamente la parte di biohack.it che costa tanto e differenzia poco.

---

## 3. Cosa riusare — inventario per valore

### Tier A — codice e dati da prendere quasi così come sono

**A1. `js/schema.js` — il catalogo dei biomarcatori.**
Ispezionato dall'app in esecuzione:
- `MARKER_SCHEMA`: **124 marcatori in 18 categorie** (Biochemistry, Hormones, Electrolytes & Minerals, Lipid Panel, Iron Metabolism, Proteins & Inflammation, Thyroid, Vitamins, Diabetes/Glucose, Tumor Markers, Coagulation, Hematology CBC, WBC Differential, Bone Metabolism, Urinalysis, Body Composition, Bone Density, Calculated Ratios). Ogni marcatore: `name`, `unit`, `refMin`, `refMax`, `desc`
- `SPECIALTY_MARKER_DEFS`: **194 marcatori specialistici** (OAT, acidi grassi, DUTCH, HTMA, DEXA)
- `UNIT_CONVERSIONS`: **61 conversioni** SI↔US con `factor` / `type` / `usUnit`
- `OPTIMAL_RANGES`: **67 marcatori** con range ottimale distinto dal range di riferimento
- `PHASE_RANGES`: range **fase-dipendenti del ciclo** per estradiolo, progesterone, LH, FSH

Da solo vale mesi di curation, ed è già strutturato sui **due dei tre range** che avevamo progettato (riferimento + ottimale). ApoB e ApoA-I ci sono già.

**A2. Pipeline di import referti** (`pdf-import.js` + 7 moduli satellite).
Estrazione testo → **obfuscazione PII** (regex + sanitizer locale in streaming, con diff viewer) → parsing AI → mappatura sullo schema → **modal di revisione** con filtri e mapping → persistenza con **rollback**. In più `import-benchmarks.js`: un banco di prova che esegue il parser su un referto sintetico di 68 risultati con chiave di risposta verificata, per **confrontare i modelli su accuratezza e velocità**. Avevamo in piano di costruire tutto questo.

**A3. Marcatori calcolati ed età biologica.**
PhenoAge (Levine 2018) e Bortz (2023) combinati con breakdown per componente; HOMA-IR, BUN/creatinina, deficit di acqua libera, TG/HDL, LDL/HDL, ApoB/ApoA-I, NLR, PLR, De Ritis, hs-CRP/HDL. Formule chiuse, deterministiche, con gestione delle unità.

**A4. Trend alert.** Regressione lineare con soglie su pendenza e R², più rilevamento dei salti improvvisi e dei valori critici fuori range.

**A5. Grafici.** Cinque plugin Chart.js: bande di riferimento, range ottimale, bande di fase del ciclo e — la cosa che ci serve di più — **timeline di integratori e farmaci sovrapposta al grafico del biomarcatore**. È letteralmente il nostro "intervento × biomarcatore", già disegnato.

**A6. Modulo DNA.** 47 SNP curati in 13 categorie, aplotipo APOE, 39 aplogruppi mtDNA, parser per sei provider (23andMe, AncestryDNA, MyHeritage, FTDNA, Living DNA, Illumina) — **tutto parsato nel browser, nulla sul server**. Coincide con il nostro M9 "genomica minimale", e la loro garanzia di privacy è più forte di quella che avevamo scritto noi.

### Tier B — prendere il design, riscrivere il codice

**B1. La "AI surfaces map".** Pubblicano un documento canonico di dove gira l'AI e dove no, con una sezione intitolata *"What is NOT AI (so you can trust the numbers)"*. È il nostro principio già enunciato — ma loro ne hanno fatto **un artefatto pubblico**. Da adottare come deliverable di progetto: è probabilmente il singolo documento migliore da mettere in mano a un medico scettico.

**B2. Caching per fingerprint dei verdetti AI.** Ogni verdetto è cachato contro un hash dei dati sottostanti: se i dati non cambiano non parte alcuna chiamata; se cambiano compare un CTA *"il tuo setup è cambiato, rigenera"*. Costo dichiarato per verdetto: **0,003-0,01 $**. È la risposta concreta e misurata al nostro vincolo di costo LLM.

**B3. La forma del verdetto.** Pallino colorato + tip ≤18 parole + dettaglio di 1-4 frasi che cita i tuoi numeri + pulsante di rigenerazione. I colori sono verde / giallo / rosso / **grigio = dati insufficienti per giudicare**. Il grigio è il nostro principio "si ferma invece di indovinare", già implementato.

**B4. Biology Scores + Coverage Planner.** Punteggi per dominio, "context checks", e una pianificazione della **copertura** che dice quali sistemi sono sotto-testati. È il nostro indicatore di completezza, con in più il passo successivo: dall'indicatore alla proposta di cosa misurare.

**B5. Nove context card** (dieta, sonno, esercizio, stress, luce e circadiano, ambiente, storia medica, obiettivi, EMF) con dot AI di coerenza rispetto agli obiettivi dichiarati. Alimenta il nostro M13.

**B6. Agent Access via MCP.** Token read-only revocabile, contesto cifrato spinto a un gateway leggero, per-profilo, interrogabile da Claude Code, Cursor, Cline, bot Nostr. **Idea forte per noi**: il biohacker interroga i propri dati con il proprio agente. È anche esattamente il pezzo che alle conferenze hacker fa la differenza tra "un'altra app di salute" e "un progetto hacker".

**B7. Inserimento manuale di prima classe, con sanity check sui valori fuori range.** Già previsto in M2; loro l'hanno.

**B8. Condivisione profilo con link temporaneo protetto da password.** La nostra "vista per il medico" senza account e senza registrazione del medico.

**B9. Multi-provider AI con opzione locale.** Porta il costo a zero per chi vuole e disinnesca in anticipo l'obiezione privacy. Le opzioni di pagamento in Bitcoin/Cashu sono culturalmente allineate al tuo pubblico, ma le terrei opzionali.

### Tier C — da non prendere

- **Lo storage local-first come unica opzione.** Incompatibile con coorti e open data. Nel nostro caso diventa una *modalità*, non l'architettura.
- **Zero-bundler con moduli ES nativi e chiamate cross-layer via `window.fn()`.** Funziona benissimo per un manutentore singolo; per un progetto con contributori esterni e un backend è fragile.
- **L'assenza di codifica LOINC** (§4).
- **La superficie di raccomandazione prodotti con disclosure affiliati.** Fuori dalla nostra linea sul conflitto d'interesse.
- **La lente Light & Sun.** Enorme e tecnicamente notevole — ricostruzione spettrale Bird-Riordan, %MED, 8 strumenti di misura via fotocamera — ma fuori scope. Da tenere come modulo opzionale futuro, non da portare ora.

---

## 4. Il buco da colmare, che è anche il nostro contributo upstream

Lo schema di getbased è **indicizzato per stringhe** (`lipids.apoB`), non per codici. Non ho trovato LOINC né UCUM: le unità sono gestite con tabelle di conversione proprie.

Per l'uso individuale va benissimo. Per l'aggregazione tra persone e laboratori diversi — cioè per tutto ciò che rende biohack.it diverso da getbased — **non basta** (vedi `bloodwork-layer-analysis.md` §5).

Quindi: prendiamo il loro catalogo e ci costruiamo sopra il **layer di mappatura LOINC + UCUM + metodo/assay**, e lo restituiamo upstream come contributo. È un contributo che a loro serve e che a noi costa poco, ed è il modo giusto di entrare in un progetto AGPL invece di limitarsi a prenderne il codice.

---

## 5. Tre strategie, e quale scegliere

**Opzione 1 — Fork.** Si forka `get-based`, si tiene il client, si aggiunge un backend di sync e aggregazione più il layer community.
*Pro*: si eredita tutto, subito. *Contro*: codebase JS senza bundler nello stile di un singolo autore, divergenza difficile da rimergiare, e la premessa local-first che combatte contro il server per sempre.

**Opzione 2 — Vendorizzare i dati e portare gli algoritmi. ← raccomandata**
Si prendono come dipendenza AGPL-compatibile: `schema.js` completo, conversioni di unità, marcatori calcolati, PhenoAge/Bortz, rilevamento trend, tabelle SNP, e il *design* della pipeline di import con la sua modal di revisione. Si costruisce sopra il nostro backend (Django + Postgres, §8.1 dello spec). Si contribuisce upstream la mappatura LOINC.
*Pro*: mantiene la nostra architettura, risparmia comunque mesi. *Contro*: la UI non è gratis.

**Opzione 3 — Complemento.** Non si ricostruisce affatto il layer individuale: si raccomanda getbased come dashboard personale e biohack.it fa solo il layer collettivo, ingerendo i loro export JSON o via Agent Access/MCP.
*Pro*: costo minimo. *Contro*: si perde il controllo dell'onboarding e del Blood Layer, che abbiamo appena eletto a prodotto della Fase 1.

**Raccomandazione: Opzione 2, preceduta da una conversazione.** Discord e Nostr sono pubblici, la licenza è la stessa, i valori sono gli stessi (privacy, open source, niente account, niente pubblicità). Un manutentore che scrive una "AI surfaces map" e documenta cosa *non* è AI è esattamente il tipo di persona con cui vale la pena parlare prima di forkare.

---

## 6. Effetto sul piano e sul budget

Il Blood Layer, che nella v0.3 è diventato il prodotto della Fase 1, era anche il blocco di lavoro più grosso dei 35k. **Una quota consistente esiste già sotto licenza compatibile**: catalogo marcatori, conversioni, marcatori calcolati, età biologica, trend, grafici con overlay, parsing DNA, e il disegno della pipeline di import.

Il budget si riallòca verso il layer collettivo — coorti, aggregazione, safety rule, open data, comunità — che è precisamente la parte che nessuno dei sette attori mappati ha costruito.

Va aggiunto un lavoro nuovo e non banale che prima non c'era: **la mappatura LOINC/UCUM del catalogo ereditato**, e l'audit di compatibilità AGPL su tutto ciò che si importa (`THIRD_PARTY_LICENSES.md` va letto prima, non dopo).

---

## 7. Nota operativa

Nel browser usato per l'analisi getbased ha già dati caricati, inclusa un'importazione DNA. Non li ho esplorati né riportati. Se quel browser è condiviso o sincronizzato, vale la pena ricordarsene: sono dati locali, cifrati solo se hai impostato una passphrase.

---

## 8. Nuove domande aperte

27. Opzione 1, 2 o 3 per il riuso di getbased — e si scrive al manutentore prima o dopo aver deciso?
28. Il layer individuale di biohack.it supporta una **modalità local-first** alla getbased (dati che non lasciano il browser, contributo alla coorte come scelta esplicita e separata)? Sarebbe la risposta più forte all'obiezione privacy, ma raddoppia le modalità di storage da mantenere.
29. Agent Access / MCP: lo mettiamo in roadmap? È basso costo, alto impatto culturale sul pubblico hacker, e nessun concorrente commerciale lo farà mai.
30. La mappatura LOINC del catalogo ereditato si contribuisce upstream o resta nostra? (La risposta giusta è upstream, ma va deciso e detto.)
