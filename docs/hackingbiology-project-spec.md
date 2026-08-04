# HackingBiology / biohack.it
## Documento di progetto — service design, analisi funzionale, analisi tecnica

*Versione 0.3 — consolidato dai memo vocali, dalla presentazione "Hacking Biology — Project Presentation" (14 slide) e dall'analisi competitiva di ProtocolEngine e MyAgingTests, quest'ultima estesa alla mappatura dell'area autenticata.*

**Documenti companion**: `protocolengine-analysis.md`, `myagingtests-analysis.md`, `myagingtests-mappatura-report.md`.

---

## 0. Nota di lettura

Questo documento consolida i memo di progetto in tre livelli distinti, deliberatamente separati perché rispondono a domande diverse e vengono decisi da persone diverse:

1. **Service design** — perché esiste, per chi, che valore produce, dove l'utente incontra il servizio.
2. **Analisi funzionale** — quali moduli software servono e cosa fanno.
3. **Analisi tecnica** — come implementarli riusando il massimo di componenti esistenti.

Il §12 aggiunge il panorama competitivo verificato sul campo, che è ciò che ha determinato buona parte delle scelte nelle sezioni precedenti. Le decisioni ancora aperte sono raccolte nel §11 e non sono state chiuse arbitrariamente.

---

## 1. Executive summary

HackingBiology è una piattaforma open source, offerta come servizio gratuito su `biohack.it`, che permette ai biohacker di **documentare in modo strutturato il proprio protocollo** (cosa fanno, cosa prendono, quando) e di **misurarne efficacia e sicurezza attraverso biomarcatori**, condividendo pubblicamente sia il protocollo sia i risultati.

Tre affermazioni fondano il progetto:

- **Per il biohacker**: oggi il protocollo vive in spreadsheet e prompt di LLM. Non è comparabile, non è seguibile, non è condivisibile con un medico in forma leggibile.
- **Per la comunità**: il valore non è il singolo dato, è la possibilità di *seguire e copiare* chi ottiene risultati, vedendo i suoi biomarcatori pubblici — con la stessa dinamica sociale del copy trading finanziario.
- **Per la ricerca**: l'aggregato di migliaia di protocolli auto-somministrati con baseline e follow-up è un corpo di open data che oggi semplicemente si disperde.

E un vincolo etico che è anche un argomento di prodotto: **i biohacker rischiano già oggi**, senza safeguard. Il principiante che copia un off-label senza sapere che deve monitorare rene e fegato è il caso d'uso in cui la piattaforma salva salute. Questo è lo scopo sociale, ed è la ragione per cui la forma societaria è quella di una non-profit startup con ciclo economico secondario allo scopo.

---

## 2. Il problema

| Chi | Cosa fa oggi | Limite |
|---|---|---|
| Cliniche longevity | Protocollo + panel come servizio a pagamento | Costoso, dato chiuso, non comparabile |
| Startup subscription | Bundle farmaci/supplementi + analytics (spesso orologi epigenetici) | Walled garden, lock-in, dato non esportabile |
| **Aggregatori di evidenza** (ProtocolEngine) | Pipeline AI su PubMed, protocolli graduati per evidenza | Zero dati individuali: dicono cosa la letteratura ha trovato su una popolazione, mai cosa succede a una persona |
| **Laboratori-piattaforma** (MyAgingTests / Clock Foundation) | Kit epigenetico + studi N-of-1 + research hub | N-of-1 isolati e non confrontabili; il modello di coorte è costruito ma **non lo usa nessuno**; tutto converge sull'acquisto del kit |
| Ricerca | Trial clinici rigorosi | Lenti, costosi, vincolati da comitato etico, non coprono l'off-label né i peptidi |
| Biohacker (centinaia di migliaia) | Spreadsheet, forum, LLM | Nessuna struttura, nessuna comparabilità, nessun ritorno verso la ricerca, nessun safeguard |

Il gap non è tecnologico, è **infrastrutturale**: manca il livello comune di rappresentazione del protocollo e del biomarcatore. E manca soprattutto l'aggregazione: un N-of-1 isolato ha potere statistico quasi nullo, mille N-of-1 sullo stesso protocollo sono un'altra cosa.

---

## 3. Stakeholder e proposta di valore

### 3.1 Biohacker esperto (utente primario, protagonista)
Progetta protocolli, si auto-somministra, misura, itera.
**Valore**: strumento serio per gestire il proprio protocollo; scheduling delle misure e degli acquisti; dashboard che risponde al medico; reputazione e visibilità nella comunità; feedback qualificato dai pari sui propri andamenti.

### 3.2 Biohacker principiante / "wannabe" (utente a maggior rischio)
Copia quello che vede fare ad altri.
**Valore**: può *seguire* un protocollo esistente invece di improvvisarlo; eredita automaticamente i biomarcatori di sicurezza associati; entra in un gruppo che sta facendo la stessa cosa e con cui confrontarsi.
**È qui che si concentra la riduzione del danno.**

### 3.3 Comunità (Rapamycin News e affini)
**Valore**: ogni protocollo, ogni composto, ogni intervento ha il suo thread; la discussione smette di essere aneddotica perché è ancorata a dati strutturati e confrontabili. La piattaforma non compete con il forum: lo alimenta e ci punta.

### 3.4 Medici curanti
Non sono utenti registrati: sono **destinatari di un output**.
**Valore**: una vista completa e leggibile — cosa prende il paziente, in che dosaggio, da quando, quali marker sono monitorati e perché, con che andamento. Oggi il medico riceve, nel migliore dei casi, un foglio scritto a mano.

### 3.5 Ricerca e pratica clinica
**Valore**: open data osservazionali su interventi che nessuno finanzierà mai in RCT. Con dichiarazione onesta del livello di attendibilità: dato auto-riportato, non randomizzato, con confounding pesante e selezione all'ingresso. Ha valore come **generatore di ipotesi** e come **sorveglianza post-market di fatto** sull'uso off-label.

### 3.6 Critica medica
Trattata come stakeholder di primo livello e non come rumore: le obiezioni cliniche vanno raccolte, pubblicate e usate come backlog di miglioramento (quali marker aggiungere, quali cutoff di sicurezza, quali avvertenze). È il percorso che rende il progetto credibile all'esterno.

### 3.7 Laboratori di analisi
**Valore**: volume di richieste qualificate e strutturate. Ruolo iniziale: sorgente di referti da importare. Ruolo futuro possibile: partner di panel ottimizzati.

### 3.8 Fornitori / farmacie / compounding
Toccati dal modulo procurement. Nessuna integrazione commerciale nella fase iniziale — è la principale superficie di conflitto d'interesse da tenere pulita se si vuole restare credibili.

### 3.9 Market player (operatori che vendono terapie e servizi)
Le slide li indicano esplicitamente tra i destinatari della piattaforma: soggetti che forniscono prodotti e servizi terapeutici per eseguire il proprio protocollo.
**Valore per loro**: accesso a una domanda strutturata e a un formato standard di protocollo.
**Tensione da governare**: è lo stesso attore che può inquinare il dato. Se un fornitore può influenzare quali protocolli emergono, il valore per la ricerca e la credibilità verso la medicina crollano insieme. Serve una regola esplicita fin dall'inizio — proposta: i market player possono *integrarsi* (pubblicare disponibilità, ricevere richieste), **mai** *classificarsi* (nessun posizionamento a pagamento nel catalogo protocolli, nessun ranking sponsorizzato, etichettatura obbligatoria di ogni contenuto commerciale).

---

## 4. Service design

### 4.1 Journey principali

**A. Il biohacker che struttura ciò che già fa**
Registrazione → import baseline (referti esistenti) → dichiarazione degli interventi in corso → sistema propone i biomarcatori di efficacia e sicurezza mancanti → calendario di misura → protocollo pubblicabile.

**B. Il principiante che copia**
Esplora protocolli → guarda i biomarcatori pubblici di chi lo pratica → "segui questo protocollo" → **checklist obbligatoria di baseline e di safety** prima dell'avvio → procurement → scheduling → primi follow-up → confronto con la coorte che pratica lo stesso protocollo.

**C. Il ciclo di misura**
Il sistema accorpa gli analiti dovuti nelle prossime settimane in **un unico prelievo** → genera la richiesta per il laboratorio → l'utente carica il referto PDF → parsing → validazione umana → i valori popolano le dashboard e le curve.

**D. La visita medica**
Genera "protocol sheet": tutto ciò che prende, dosaggi, timing, da quando, marker monitorati con motivazione, andamenti, allerte aperte. Link pubblico + PDF.

**E. Il contributo alla comunità**
Pubblica il protocollo → thread sul forum → altri lo seguono → si forma una coorte → confronto dei risultati → revisione del protocollo (versionato).

### 4.2 Touchpoint

- Web app responsive (uso principale: desktop per la progettazione, mobile per l'aderenza quotidiana)
- **Profilo pubblico** e **pagina protocollo pubblica** — indicizzabili, sono il canale di acquisizione principale
- Forum Rapamycin News (link bidirezionale protocollo ↔ thread)
- Notifiche/reminder: assunzione, prelievo in scadenza, riordino scorte
- Export medico (PDF / link)
- Endpoint open data (dump + API)
- Import: referti PDF, export Apple Health/Google Fit, CSV

### 4.3 Principi di servizio

1. **Il biohacker è il proprietario del dato.** Export completo sempre, senza attriti.
2. **Pubblico per scelta, mai per default.** Granularità per singolo marker.
3. **La piattaforma descrive, non prescrive.** Suggerisce *cosa misurare*, non *cosa prendere né quanto*. È la linea che tiene insieme etica, responsabilità e posizione regolatoria.
4. **La sicurezza non è opt-in.** Se un composto ha marker di sicurezza noti, seguirne il protocollo li porta con sé.
5. **Ogni affermazione ha una fonte.** Evidenza dichiarata e graduata: umana clinica / umana osservazionale / animale / in vitro / aneddotica di comunità.
6. **Il sistema fallisce in modo rumoroso.** *(Principio nato da un difetto osservato in MyAgingTests: su 8 sostanze inserite, 3 sono sparite in silenzio dall'estrazione.)* Se il parsing non capisce una voce, lo dichiara e chiede; non prosegue mai in silenzio su un protocollo incompleto. Un'analisi di sicurezza su un protocollo amputato è peggio di nessuna analisi, perché sembra completa.
7. **Valore nei primi dieci minuti, a spesa zero.** Il pannello principale deve popolarsi con i referti che l'utente ha già nel cassetto, non con un invito ad acquistare. È la metrica di onboarding del progetto.
8. **Si ferma invece di indovinare.** *(Principio preso da Lamplit, versione predittiva del n. 6.)* Quando la copertura dei dati è insufficiente per un indice sintetico o una previsione onesta, il sistema **non mostra un valore approssimato**: dichiara che non si sa. Vale per gli indici per sistema d'organo, per i trend su due sole misure, per qualsiasi proiezione.
9. **Esistono dati strutturalmente non condivisibili.** Diverso da "privato per default": per alcune categorie — dati genomici in primis — non deve esistere il codice che li pubblica. Nessuna impostazione, nessuna superficie di condivisione, nessun errore possibile.

---

## 5. Modello di dominio

Le entità che reggono tutto il sistema:

- **Person / Profile** — utente, caratteristiche di contesto (età, sesso, e attributi opzionali dichiarati), visibilità.

**Le tre entità che nello spec v0.2 erano fuse, e vanno separate** *(pattern verificato in MyAgingTests, dove la separazione regge bene)*:

- **TestingProtocol** — cosa misuro e quando: insieme versionato di misure e timepoint, stati `Draft | Active | Completed`, condivisibile, derivabile da template.
- **TreatmentPlan** — cosa prendo e faccio: insieme versionato di Intervention, con distinzione `Self-Managed | Physician-Assigned`, stati Active/Paused/Completed.
- **Goal** — cosa voglio ottenere: obiettivi prioritizzati dall'utente (i primi tre pesano nelle analisi), mappati su uno o più **Hallmark of Aging** (framework Schmauck-Medina 2022, già usato nel workbook esistente).

`Protocol` resta come vista composita pubblica — l'unione di TestingProtocol + TreatmentPlan + Goal — con origine `curated | community`, fork/derivazione e thread associato. È ciò che si pubblica, si segue e si copia.

- **Intervention** — unità elementare di ciò che si fa. Ogni intervento porta con sé uno **schema di ciclo**, non la sola frequenza: `pattern` (continuo | pulsato | titolazione | on-off), `on_days` / `off_days`, lunghezza del ciclo, cicli per anno, passi di titolazione. *(Necessità emersa dal test sulla pipeline di MyAgingTests, dove "dasatinib giorni 1-3 di ogni mese" viene appiattito in "Monthly" e il pattern sopravvive solo come nota libera.)* Senza questo schema senolitici, rapamicina settimanale, cicli di TRT e digiuni non sono rappresentabili — cioè non è rappresentabile quello che i biohacker fanno davvero. Sottotipi con configurazioni proprie:
  - *Substance* (farmaco, supplemento, peptide): dose, forma, via, timing, cicli
  - *Exercise*: modalità, volume, intensità, frequenza
  - *Device/Therapy*: HBOT (incluso il protocollo hypoxia-hyperoxia tipo Efrati/Aviv), red light, sauna, cold exposure — parametri specifici
  - *Procedure*: iniezioni peptidiche, infusioni IV, plasmaferesi — richiedono operatore, sede, consenso, e hanno un profilo di rischio diverso dalle pillole
  - *Hormonal*: regolazione ormonale (es. DHEA), con marker di sicurezza obbligatori
  - *Nutrition/Fasting*: schema (16/8, CR 20%, restrizione di metionina/cisteina), finestra, aderenza e deroghe registrate
- **Substance** — entità di catalogo (nome, identificatori esterni, classe, interazioni note, marker di sicurezza associati).
- **Biomarker** — analita o misura, con unità, range di riferimento, ruolo (**efficacy** / **safety** / **baseline**), modalità di raccolta (blood, DEXA, BIA, epigenetico, wearable, funzionale).
- **Measurement** — singolo valore, con data, fonte, laboratorio, metodo, unità, stato di validazione.
- **MeasurementPlan** — regola di cadenza per biomarker in funzione della fase (titolazione / mantenimento) e dell'intervento che la richiede, con **motivazione esplicita**.
- **SafetyRule** — "se assumi X, monitora Y con cadenza Z; soglia di allerta W". È il cuore della funzione di riduzione del danno.
- **Inventory / Purchase** — scorte, lotti, scadenze, lead time, fabbisogno proiettato.
- **DaySchedule** — allocazione delle assunzioni negli slot della giornata sotto vincoli di interazione e biodisponibilità.
- **Cohort** — insieme delle persone che praticano lo stesso protocollo; unità di confronto e di analytics.
- **Study** — *(aggiunto dopo l'analisi di MyAgingTests)* contenitore che rende interpretabile un'auto-sperimentazione: domanda di ricerca ed **endpoint dichiarati prima di iniziare**, protocollo associato, timepoint (T0 baseline, T1…Tn), batteria di test per timepoint, durata, washout, criteri di sospensione, costo stimato, confronto statistico pre/post. La pre-registrazione dell'endpoint costa zero e disinnesca in anticipo l'obiezione principale della medicina.
- **AdherenceLog** — registrazione giornaliera per singola assunzione con **quattro stati**: `preso come previsto | dose parziale | saltato intenzionalmente | dimenticato`. Da qui la percentuale di aderenza giornaliera e cumulativa.
  *Perché è strutturale e non un dettaglio*: senza aderenza un risultato N-of-1 è ininterpretabile — non si distingue "il protocollo non funziona" da "il protocollo non è stato seguito". Ed è il primo filtro di qualità sui dati di coorte: un contributo con aderenza al 35% non può pesare quanto uno al 95%.
- **WellnessCheck** — rilevazione soggettiva quotidiana: umore 1-5, energia 1-5, ore di sonno, qualità del sonno 1-5, note libere. È l'unica serie ad alta frequenza che un biohacker produce senza comprare nulla, e riempie i mesi vuoti tra un prelievo e l'altro.

Relazione chiave, che è poi la risposta alle due domande del medico:
`Substance → SafetyRule → Biomarker → Measurement → Dashboard`
"Cosa prendi" e "come stai" sono la stessa struttura dati letta da due lati.

---

## 6. Analisi funzionale dei moduli

### M1 — Protocol Builder & Library
Creazione, versionamento, fork, pubblicazione dei protocolli. Catalogo curated + community. Mappatura sugli hallmark. Diff tra versioni. Ogni protocollo espone: interventi, schedule, marker di efficacia, marker di sicurezza, livello di evidenza, discussione collegata.

### M2 — Biomarker & Lab Data
*(Espanso dopo l'analisi di Lucis, SiPhox, TestResult.ai e BloodGPT — vedi `bloodwork-layer-analysis.md`. È il modulo di punta della Fase 1.)*

Anagrafica analiti con **codifica LOINC + unità UCUM obbligatorie**, e con **metodo/assay e laboratorio salvati insieme a ogni singola misura** — senza questi metadati i dati di coorte non sono confrontabili e l'open data non vale nulla.

**Tre range per analita, non uno**: range di riferimento del laboratorio (dipende dal metodo), **range ottimale** longevity (dichiarato con la fonte), **soglia di sicurezza** oltre la quale il protocollo si ferma. Sono tre situazioni diverse e vanno mostrate in modo diverso; appiattirle su un range unico è il difetto tipico sia delle piattaforme wellness sia della medicina di routine.

**Pipeline con confine netto**: estrazione, mapping e calcolo delle soglie sono **deterministici e riproducibili** (stesso input, stesso output); l'LLM produce solo la narrazione in linguaggio comune, generata una volta e cachata. *L'LLM scrive le parole, mai i numeri.* È l'unica architettura compatibile con la pubblicazione di open data.

Import da PDF, foto e CSV, con **inserimento manuale di pari dignità** (non tutti hanno il PDF), revisione umana obbligatoria prima dell'inserimento, e fallimento rumoroso su ciò che non è stato capito. **Indicatore di completezza e freschezza per sistema** — "Metabolico: 6 marcatori su 13, ultimo aggiornamento 4 mesi fa" — perché un indice calcolato su due marcatori non vale quanto uno calcolato su quattordici, e dirlo è l'unico modo onesto di gestire un referto povero.

**Il panel non si sceglie, si calcola**:
`Safety Core (~25-30 analiti) + Δ safety rule delle sostanze attive + Δ marker di efficacia degli obiettivi + approfondimenti opzionali`
È il punto di distacco da tutti i concorrenti mappati: loro vendono o interpretano un panel fisso, qui il panel è una funzione del protocollo. Il livello di follow-up si attesta intorno al 60% del completo, in linea con quanto fa Lucis su diecimila persone.

### M3 — Scheduling & Measurement Planner
Motore che, dati gli interventi attivi, calcola **cosa va misurato, quando e perché**; cadenza fitta in avvio/titolazione e diradata in mantenimento; **accorpamento degli analiti in un unico prelievo** (riduce costo e numero di aghi); gestione dei requisiti pre-analitici (digiuno, sospensioni, orario); scheduling delle attività preparatorie e degli acquisti con lead time.

**Lo stato `Overdue` è un elemento di sicurezza, non di comodità.** Un prelievo scaduto è un buco nella sorveglianza: va collegato alle SafetyRule di M7 e formulato come tale — *"rapamicina attiva da 94 giorni, pannello epatico scaduto da 34"* — non come una notifica di calendario. Filtri a due assi (tipo × stato) e tre viste (calendario / anno / tabella), con le timeline degli Study sovrapposte al calendario personale.

### M4 — Pills Management & Procurement
Fabbisogno proiettato dal protocollo → acquisti in batch → magazzino, lotti, scadenze, alert di riordino. Organizzazione delle assunzioni negli slot della giornata **ottimizzando biodisponibilità ed evitando interferenze e sommazione di tossicità** (es. separazione da minerali, cibo/digiuno, distanza tra composti competitivi, carico epatico).

### M5 — Public Dashboard & Doctor View
La vista pubblica: cosa prendi, da quanto, perché; per ogni sostanza i marker che la sorvegliano; le dashboard raggruppate per famiglia di biomarcatori (lipidi, glicemia, rene, fegato, infiammazione, ormoni, composizione corporea, età biologica) con il *motivo* per cui ciascun gruppo è monitorato. Export medico dedicato.

**Metrica di testata**: il delta tra età biologica ed età cronologica, come indicato nelle slide. Attenzione però — è la metrica più comunicativa e la più fragile: gli orologi epigenetici hanno rumore test-retest rilevante e non sono comparabili tra provider. Va mostrata con l'intervallo di incertezza, con il clock e il laboratorio dichiarati, e **non** va usata come metrica di reputazione o di ranking sociale. Diversamente da MyAgingTests, che non ha altro da mettere in testa, qui è *uno* dei biomarcatori: se manca, la dashboard resta comunque piena.

**Vista per sistemi d'organo** *(pattern preso dal report GrimAge)*: scomporre l'andamento per sistema — vascolare, renale, epatico, immunitario, muscolare, cognitivo, polmonare — invece che in un numero unico. Il doppio vantaggio è che **la stessa vista che mostra l'efficacia mostra la sicurezza**: "rene: +0,3 anni" e "stai assumendo un composto nefrotossico e non misuri la creatinina da otto mesi" abitano lo stesso riquadro.

**Confronto a doppia colonna** *(il pezzo che nessun concorrente può costruire)*: per ogni intervento, affiancare *cosa prevede la letteratura* (dall'Evidence Layer, M11) e *cosa mostrano i biomarcatori delle persone che lo praticano* (dalla coorte, M8). "La letteratura dice −2,2 anni; le 340 persone che l'hanno fatto mostrano questo." ProtocolEngine ha solo la prima colonna, MyAgingTests non ha né coorti attive né aggregazione.

### M4bis — Cost tracking
Le slide quantificano il costo reale del protocollo (ordine di grandezza: centinaia di euro/mese di analisi, oltre un migliaio di terapie). Il costo è quindi una variabile di primo livello, non un dettaglio: costo per protocollo, per intervento e per prelievo, proiezione mensile, e "quanto costa seguire questo protocollo" mostrato pubblicamente su ogni protocollo. È anche un potente filtro di realismo per chi vuole copiare.

### M6 — Social & Community
Profili, follow, protocolli seguiti/copiati, coorti, commenti, reputazione basata su completezza e continuità dei dati (**non** su risultati "vincenti" — evitare l'incentivo perverso a esagerare). Integrazione con Rapamycin News: ogni protocollo/composto punta al thread pertinente.

**Lezione decisiva dalla mappatura**: MyAgingTests ha costruito un modello di coorte completo — sei tipi di gruppo, creazione libera, enrollment aperto — e alla verifica risulta *"No Groups Currently Enrolling"*. **Il software di coorte non genera comunità.** La comunità preesiste al software o non arriva. Conseguenza operativa: M6 non va costruito come "funzionalità social da lanciare", ma come **estensione di una comunità che già discute** su Rapamycin News. Prima il link ai thread esistenti, poi le coorti; mai l'inverso.

**Revisione pubblica dei claim**: MyAgingTests ha il flagging, ma è una segnalazione *privata a un team* — e lo stato del loro database mostra che il team non ce la fa. Qui il flag deve essere pubblico, discusso e tracciabile: non "segnala al nostro team" ma "questo claim è contestato da 12 persone, ecco perché".

**Evidence Badge** *(pattern preso da Lamplit — vedi `lamplit-analysis.md`)*: la reputazione non è dichiarata, è **calcolata dal sistema sui dati che ha già**, e il lettore ne vede la derivazione:

> *"Rapamicina 6mg/settimana, 94 giorni, aderenza 91%. ApoB da 78 a 91 mg/dL (+17%), ALT stabile, linfociti −18%. 3 misurazioni, laboratorio unico, referti verificati."*

Nessun claim, solo la derivazione. È ciò che rende un protocollo **copiabile in modo informato**, ed è una soluzione migliore di "reputazione su completezza e continuità" al problema dell'incentivo a esagerare.

**Due assi di reputazione, mai fusi**: la **credenziale professionale verificata** (chi sei) e la **verifica dei dati** (cosa mostrano le tue misure). Un medico può avere la prima e non la seconda; un biohacker esperto il contrario. La comunità dà valore ai dati, il mondo medico alle credenziali, e il progetto ha bisogno di entrambi senza far finta che siano la stessa cosa. Discovery per specialità, non per popolarità.

**Gamification: solo sulla qualità del dato.** Streak sull'aderenza registrata, badge sulla completezza del panel, continuità della documentazione. **Mai** classifiche su esiti di salute — chi ha l'ApoB più basso o l'età biologica migliore — perché è esattamente l'incentivo a inseguire il numero invece della salute.

### M7 — Safety Guardrails
Il modulo che giustifica il progetto: baseline obbligatoria prima di seguire un protocollo, safety marker ereditati automaticamente, allerte su valori critici, avvisi di interazione, escalation esplicita verso "consulta un medico" con il protocol sheet già pronto.

**Dose sanity check** *(lacuna verificata sul campo: MyAgingTests accetta senza un fiato vitamina D3 100.000 UI/die, selenio 2000 mcg e rapamicina 30 mg/die).* Confronto della dose inserita con limite superiore tollerabile, dose terapeutica abituale e dose massima riportata in letteratura, su tre livelli: *fuori dall'uso comune* / *sopra il limite superiore* / *potenzialmente tossica*. Non è una raccomandazione clinica — è la validazione di plausibilità di un campo numerico, applicata a un dosaggio. Intercetta lo zero di troppo, che è l'errore più banale e più pericoloso del principiante.

### M8 — Analytics & Open Data
Aggregazione per coorte, confronto tra chi pratica lo stesso protocollo, stratificazione per caratteristiche, pubblicazione open data anonimizzata, endpoint per ricercatori.

**Regola di rilascio**: si pubblica solo ciò che ha LOINC + UCUM + provenienza dichiarata; il confronto tra persone usa lo **z-score rispetto al range del laboratorio di origine**, non il valore grezzo. Meglio un dataset piccolo e pulito che uno grande e non confrontabile — è la differenza tra essere citati da un ricercatore ed essere ignorati.

### M9 — Genomics (deliberatamente minimale)
Nessun processing di dati grezzi. Link a risorse esterne, import dei soli referti/varianti selezionate, con focus su ciò che è **azionabile** (farmacogenomica: metabolizzatori CYP; APOE). Tutto il resto: fuori scope.

### M10 — Wearables (posticipato, ma la fattibilità non è più in discussione)
Nessuna integrazione diretta in Fase 1: import da file di export. **La mappatura di MyAgingTests ha però chiuso la questione tecnica**: hanno undici connettori (Fitbit, Garmin, Oura, WHOOP, Google Fit, Polar, Suunto, Withings e altri), e nessuno costruisce undici integrazioni a mano — è quasi certamente un aggregatore commerciale (Terra, Vital, Rook). La domanda non è più "si può fare con questo budget" ma solo "quanto costa l'abbonamento". Da verificare in Fase 3, non prima.

### M13 — Daily Log & Adherence
*(Aggiunto dopo la mappatura dell'area autenticata di MyAgingTests, dove è la schermata meglio riuscita dell'intera piattaforma.)*
Check-off giornaliero delle assunzioni **con dose e slot già risolti dal piano**, aderenza a quattro stati (`preso / parziale / saltato intenzionalmente / dimenticato`), wellness check soggettivo, note libere, percentuale di aderenza giornaliera e storico tabellare.
È il modulo che tiene in vita la piattaforma tra un prelievo e l'altro: trenta secondi al giorno contro tre mesi di silenzio. E alimenta due cose che nessun concorrente ha: la **qualità dichiarata** del dato N-of-1 e il peso di ogni contributo nell'aggregazione di coorte. **Fase 1.**

### M11 — Evidence Layer
*(Aggiunto dopo l'analisi di ProtocolEngine — vedi `protocolengine-analysis.md`.)*
Ingestione della letteratura da Europe PMC / PubMed / preprint, estrazione LLM in batch di `EvidenceClaim` (intervento × outcome × studio), grading della **confidence** con fattori pesati ispirati a GRADE e **effect size riportato separatamente** in unità native dell'outcome. Directional evidence con conteggio esplicito degli studi favorevoli, nulli e sfavorevoli. Revisione comunitaria dei claim. Alert quando l'evidenza su un composto in uso cambia.
Il legame `Outcome ←→ Biomarker` è il contributo originale: permette di confrontare ciò che la letteratura prevede con ciò che i biomarcatori delle persone mostrano davvero.

### M12 — Claims Validator
*(Aggiunto dopo l'analisi di MyAgingTests — vedi `myagingtests-analysis.md`.)*
Si incolla l'URL di una pagina prodotto e il sistema verifica le affermazioni contro l'Evidence Layer. Nessun dato personale, nessuna esposizione regolatoria, costo marginale trascurabile. È riduzione del danno a monte — intercetta il principiante quando incontra l'integratore, prima che incontri il protocollo — ed è probabilmente lo strumento con il miglior rapporto valore/costo per l'acquisizione utenti. **Fase 2.**

---

## 7. Dati, privacy, posizione regolatoria

Tre nodi da presidiare fin dall'architettura, non dopo:

**Dati sanitari, GDPR art. 9.** Sono categorie particolari di dati. La pubblicazione è legittima solo su **consenso esplicito, granulare e revocabile**, con default privato. Hosting UE. Pseudonimizzazione nella pipeline analitica. Diritto all'export e alla cancellazione implementati davvero.

**Rischio di qualificazione come dispositivo medico (MDR / MDCG 2019-11).** Un software che *interpreta* dati biologici a fini diagnostici o terapeutici individuali può ricadere nella definizione di MDSW. La mitigazione è di design, non di disclaimer: la piattaforma **registra, organizza, ricorda e mostra**; non calcola dosaggi personalizzati, non emette diagnosi, non raccomanda terapie. I suggerimenti di *cosa misurare* vanno presentati come informativi e ancorati a letteratura citata. Vale la pena un parere legale prima del lancio pubblico, non dopo.

**Contenuto della comunità e responsabilità.** Protocolli community-contributed su off-label e peptidi implicano moderazione, disclaimer, e una policy chiara su cosa non è pubblicabile.

**Open data.** Rilascio aggregato con soglie minime di coorte; attenzione alla re-identificazione (un protocollo molto peculiare identifica una persona). Licenza aperta, schema documentato, versionato.

---

## 8. Analisi tecnica

Il principio guida: **non costruire nulla che esista già**. Il valore differenziale è il modello di dominio e la comunità, non l'infrastruttura.

**Vincolo dichiarato nelle slide: ~35.000 € di investimento sul primo anno di sviluppo, con opex iniziale sotto i 300 €/mese.** Questo non è un dettaglio di budget, è il vincolo che determina l'architettura. Con quella cifra si compra, realisticamente, uno sviluppatore senior per pochi mesi oppure un team piccolissimo assistito da LLM. Conseguenze non negoziabili:
- niente integrazioni wearable custom (confermato: ogni integrazione è un progetto a sé);
- niente app native (PWA);
- niente Kubernetes, niente microservizi: monolite Django su un singolo host gestito;
- ogni componente in tabella §8.1 esiste per non scrivere codice, e va adottato "as is" senza personalizzazioni profonde;
- il forum **non** si costruisce: Rapamycin News è già lì.

Il budget regge la Fase 1 e parte della Fase 2. Le Fasi 3-5 richiedono contributori open source o finanziamento aggiuntivo, e la roadmap va comunicata dicendolo.

### 8.1 Stack proposto

| Livello | Scelta | Perché |
|---|---|---|
| Backend | Python + Django (o FastAPI se si preferisce API-first) | Ecosistema scientifico, admin gratuito per la curation, velocità |
| DB | PostgreSQL (+ TimescaleDB per le serie di misure) | Un solo DB per relazionale, time-series e JSON |
| Frontend | Next.js / React, PWA per il mobile | Un solo codice per web e uso quotidiano su telefono |
| Auth | Keycloak o Authentik | SSO pronto, delega la parte più noiosa |
| Community | **Discourse** (Rapamycin News è già Discourse) | Non si riscrive un forum: SSO via Discourse Connect e link bidirezionale |
| Dashboard | Componenti custom + Metabase per l'analitica interna | Le viste pubbliche devono essere belle e su misura; l'analitica no |
| Deploy | Docker Compose → Kubernetes solo se serve | Il progetto muore di complessità prima che di scala |

### 8.2 Modello dati: la scelta strategica

Adottare **HL7 FHIR** come vocabolario interno per le entità cliniche (`Observation`, `MedicationStatement`, `CarePlan`, `DiagnosticReport`, `Specimen`) e prevedere un export in **OMOP CDM** per il livello ricerca.

Ha un costo iniziale, ma:
- rende i dati immediatamente comprensibili a medici e ricercatori senza traduzione;
- apre l'ecosistema di strumenti OHDSI (ATLAS, analytics standardizzate) senza scriverli;
- è ciò che rende plausibile lo scenario "un'istituzione un giorno lo usa davvero".

### 8.3 Vocabolari e fonti dati esterne

- **Analiti di laboratorio**: LOINC (gratuito, previa registrazione) + UCUM per le unità
- **Farmaci**: RxNorm (US, aperto), ATC/WHO, AIFA per l'Italia
- **Molecole e supplementi**: PubChem, ChEBI, ChEMBL, UNII/FDA GSRS — tutti aperti
- **Interazioni**: DrugBank ha copertura eccellente ma **licenza commerciale**; alternative aperte (DDInter, liste DDI ad alta priorità) coprono meno. Sui supplementi la copertura aperta è scarsa: qui servirà **curation propria + LLM assistita + contributo della comunità**, dichiarando il livello di confidenza. È un asset differenziante e va trattato come tale.
- **Farmacogenomica**: CPIC e PharmGKB, aperti e clinicamente solidi
- **Letteratura**: PubMed/Europe PMC per ancorare le affermazioni
- **Hallmark of aging**: mappatura propria sul framework già usato nel workbook esistente (~206 composti annotati) — è un patrimonio già pronto da riusare come seed del catalogo

### 8.4 Uso dell'LLM, con il vincolo di costo

Tre impieghi, in ordine di valore:

1. **Parsing dei referti** — è l'uso ad alto ROI. Strategia per contenere il costo: OCR locale (Tesseract/docTR) → estrazione strutturata con un modello *piccolo* → **conferma umana** → una volta riconosciuto il formato di un laboratorio, si genera un template deterministico e le importazioni successive da quel laboratorio **non passano più dall'LLM**. Con qualche decina di laboratori mappati, il costo marginale tende a zero.
2. **Assistenza alla curation** — proposta di safety rule, interazioni, mappature. Batch, offline, non a runtime: costo trascurabile e revisione umana obbligatoria.
3. **Ottimizzazione dello schedule** — **non serve un LLM.** È un problema di vincoli: usare un solver (OR-Tools) per l'allocazione delle assunzioni negli slot e un set-cover per l'accorpamento degli analiti in prelievi. Deterministico, spiegabile, gratuito.

Ordine di grandezza realistico: con caching, template appresi e batch, il costo di computazione resta ampiamente sotto la soglia indicata — a condizione di **non** mettere un LLM nel percorso interattivo di ogni pagina.

### 8.5 Wearable e genomica

Wearable: import da file (export Apple Health, Google Fit, CSV Oura/Whoop) in fase 1. **Aggregatore commerciale (Terra, Vital, Rook) in Fase 3**: la mappatura di MyAgingTests, con undici connettori attivi, dimostra che è la strada praticata da chi ha risolto il problema. Resta da negoziare il prezzo, non da valutare la fattibilità.
Genomica: nessun processing di VCF. Link out + import di referti interpretati, limitato all'azionabile.

### 8.5bis Governo del costo LLM: il tetto a crediti

MyAgingTests espone all'utente un sistema a **crediti** (analisi standard 3, analisi approfondita 10, saldo mensile visibile). Anche per un servizio gratuito è il meccanismo più semplice per impedire che il costo degli LLM esploda: rende il consumo prevedibile per il gestore e comprensibile per l'utente, senza paywall. Da adottare con saldo generoso e rigenerazione mensile.

Regola complementare: **nessun LLM nel percorso interattivo di ogni pagina**. Batch, cache, template appresi. Un'analisi che gira in tre minuti è accettabile; una pagina che costa mezzo centesimo a ogni caricamento no.

### 8.5quater Due regole nate dai test sulla pipeline altrui

**L'LLM non scrive mai in colonne vincolate.** Enum chiusi popolati da codice deterministico *dopo* la validazione; il testo libero va in un campo note ampio e separato. Se il modello propone un valore fuori enum, la voce si marca **ambigua** e va in revisione: non si perde e non fa fallire l'inserimento. *(Motivazione empirica: su MyAgingTests lo stesso tipo di input a volte passa e a volte perde voci in silenzio, perché il modello emette una stringa troppo lunga per un campo `varchar(20)`. Il non deterministico era collegato direttamente alla persistenza.)*

**Risoluzione delle entità su codici, non su stringhe inglesi.** Ogni sostanza si risolve su RxNorm / ATC / PubChem / UNII con tabella di sinonimi multilingua (rapamicina = rapamycin = sirolimus). Per un progetto italiano su dominio `.it` è una condizione di esistenza, non una raffinatezza: un protocollo scritto in italiano su MyAgingTests viene interpretato correttamente nelle dosi e poi **non matcha nulla**, quindi il sistema lo accetta e lo ignora.

**Corollario operativo**: a fine estrazione si mostra sempre il **diff tra input e output** — "hai inserito 8 voci, ne ho riconosciute 5, queste 3 non le ho capite". Costa poco e da solo avrebbe intercettato tre dei difetti trovati nei test. E i job lunghi vanno **in coda, idempotenti, con ripresa**: mai timeout con quota consumata e nessun risultato.

### 8.5ter Pattern di interfaccia da riusare

Verificati sul campo e riusabili senza costo di progettazione:

- **Onboarding a 4 step con progresso persistente** in testa alla dashboard, che resta finché non è completo
- **Quick Actions** in colonna, ogni voce con titolo e sottotitolo esplicativo — necessario in una piattaforma densa dove il menu principale non basta
- **Legenda esplicita dello stato di ogni item estratto** (riconosciuto / non riconosciuto / dedotto): l'utente vede cosa il sistema ha capito e cosa ha inventato
- **Proposte AI sempre in blocco con Accept All / Reject All**: mai imporre, sempre proporre
- **Wizard con step di revisione umana obbligatorio** prima che un dato estratto entri nel sistema
- **Snapshot anticipato del risultato** durante le attese lunghe, per ridurre l'abbandono
- **Empty state che insegna, non che vende**: "carica un referto che hai già", mai "ordina il tuo primo test"

### 8.5quinquies Riuso di **getbased** — decisione strutturale

*(Vedi `getbased-reuse-analysis.md`.)* `github.com/elkimek/get-based` è rilasciato in **AGPL-3.0-or-later**, la stessa licenza scelta per questo progetto: è l'unico attore mappato il cui codice si può **prendere**, non solo studiare.

**Da riusare** (Tier A, codice e dati): il catalogo `schema.js` — 124 marcatori in 18 categorie con unità e range di riferimento, 194 marcatori specialistici, 61 conversioni di unità, 67 range ottimali, range fase-dipendenti del ciclo; la pipeline di import referti con obfuscazione PII, modal di revisione e rollback; il banco di prova che valuta i modelli su un referto di riferimento; i marcatori calcolati e l'età biologica (PhenoAge Levine 2018, Bortz 2023, HOMA-IR, rapporti lipidici, NLR, De Ritis); il rilevamento dei trend per regressione lineare; i plugin Chart.js con bande di riferimento, range ottimale e **timeline di farmaci e integratori sovrapposta al grafico**; il parsing DNA in-browser (47 SNP, APOE, 39 aplogruppi mtDNA, 6 provider).

**Da riusare come design** (Tier B): la *AI surfaces map* pubblicata — documento canonico di dove gira l'AI e dove no, da adottare come nostro deliverable; il **caching per fingerprint** dei verdetti AI (0,003-0,01 $ a verdetto, zero chiamate se i dati non cambiano); la forma del verdetto con lo stato **grigio = dati insufficienti**; Biology Scores e Coverage Planner; l'**Agent Access via MCP** con token read-only revocabile.

**Da non prendere**: il local-first come unica opzione (incompatibile con coorti e open data), l'architettura zero-bundler con chiamate `window.fn()` cross-layer, la superficie di raccomandazione prodotti con affiliazioni, e per ora l'intera lente Light & Sun.

**Il buco da colmare, che è anche il nostro contributo upstream**: il loro schema è indicizzato per stringhe, senza LOINC né UCUM. Per l'uso individuale basta; per l'aggregazione tra persone e laboratori no. Costruiamo sopra il layer di mappatura LOINC/UCUM/metodo e lo restituiamo a monte.

**Strategia raccomandata**: vendorizzare dati e algoritmi come dipendenza AGPL-compatibile e costruirci sopra il nostro backend, invece di forkare — preceduto da una conversazione con il manutentore, che è pubblicamente raggiungibile e culturalmente allineato. **Effetto sul budget**: il Blood Layer, prodotto della Fase 1 e blocco di lavoro più grosso dei 35k, esiste in buona parte già; le risorse si riallocano sul layer collettivo, che è la parte che nessuno ha costruito.

### 8.6 Open source e community di sviluppo

Licenza già decisa nelle slide: **AGPL-3.0** per il software — scelta corretta e coerente con la natura non-profit, protegge contro il walled garden altrui. Per i materiali le slide indicano "Common Criteria": presumo si intenda **Creative Commons**, e la licenza specifica va scelta esplicitamente (CC BY-SA per i contenuti, CC0 o ODbL per i dataset open data — sono decisioni diverse e vanno prese separatamente). Repo pubblico dal giorno uno, ADR (architecture decision record) pubblici, dati seed aperti. Il pubblico hacker che segue Fabio è la prima fonte di contributori: il progetto va presentato come infrastruttura open, non come startup.

---

## 9. Roadmap

**Fase 0 — Fondamenta (modello + seed)**
Modello di dominio con le tre entità separate (TestingProtocol / TreatmentPlan / Goal), catalogo composti seed dal workbook esistente con doppio asse **meccanismo d'azione × hallmark**, anagrafica biomarcatori LOINC organizzata per categoria (sangue, epigenetica, clock, infiammatorio, metabolico, immunitario, funzionale, fisico, composito), safety rule per i composti più usati (rapamicina, metformina, statine, GLP-1, testosterone, senolitici). Bootstrap dell'Evidence Layer sul solo sottoinsieme longevity.

**Fase 1 — MVP utile a una persona sola**
Protocol builder, TreatmentPlan, **Daily Log con aderenza a 4 stati e wellness check (M13)**, inserimento manuale delle misure, onboarding "porta i tuoi referti", dashboard privata con vista per sistemi d'organo, protocol sheet per il medico.
Criteri di successo: Fabio abbandona lo spreadsheet, **e un nuovo utente vede il primo grafico dei propri dati entro dieci minuti dalla registrazione, spesa zero**.

**Il Blood Layer (M2) è il prodotto della Fase 1**, e ha un'identità comunicabile per conto suo: *"carica i tuoi referti degli ultimi anni e ottieni la tua storia clinica in grafico, gratis, senza comprare nulla"*. È una frase che si può dire in televisione senza pronunciare la parola biohacking, non ha esposizione regolatoria, funziona con un utente solo e senza comunità. È anche ciò che rende il progetto presentabile a un medico prima ancora di parlargli di rapamicina.

**Fase 2 — MVP utile alla comunità**
Profili e protocolli pubblici, follow/copy, **link ai thread di Rapamycin News prima delle coorti**, guardrail di sicurezza sul protocollo copiato, wizard di import referti con revisione umana, `Overdue` collegato alle safety rule, **Study N-of-1 con pre-registrazione dell'endpoint**, **Claims Validator (M12)**.

**Fase 3 — Operatività quotidiana e terreno vergine**
Pills management, procurement, ottimizzazione degli slot per interazione e biodisponibilità, accorpamento degli analiti in un unico prelievo, valutazione dell'aggregatore wearable.
**Nessuno dei tre attori mappati copre questa fase**: è ingegneria che non ha ancora fatto nessuno.

**Fase 4 — Livello ricerca**
Coorti, **confronto a doppia colonna letteratura vs coorte osservata**, stratificazione, export OMOP, primo rilascio open data.

**Fase 5 — Trial distribuiti grassroots**
Coorti di Study pre-registrati sullo stesso protocollo, con endpoint dichiarati, referto collettivo. È la forma implementabile del "distributed trial" delle slide, ed è ciò che rende il progetto interessante per il mondo istituzionale.

---

## 10. Rischi principali

| Rischio | Mitigazione |
|---|---|
| Qualificazione come dispositivo medico | Posizionamento descrittivo, nessuna raccomandazione personalizzata, parere legale pre-lancio |
| Danno a un utente principiante | Guardrail non disattivabili, baseline obbligatoria, allerte su valori critici |
| Dato auto-riportato di bassa qualità | Preferenza per referti importati, indicatori di completezza, evidenza graduata e dichiarata |
| Over-engineering delle integrazioni (wearable) | Rinvio esplicito, import da file |
| Incentivo perverso a esagerare i risultati | Reputazione su completezza e continuità, non su performance |
| Progetto troppo grande per le risorse disponibili | Fase 1 deve essere utile a un singolo utente, subito |
| Conflitto d'interesse con fornitori | Nessuna monetizzazione sul procurement nella fase iniziale |
| **Perdita silenziosa di dati nell'estrazione** *(osservata dal vivo in un concorrente)* | Fallimento rumoroso, diff visibile tra input e output, revisione umana obbligatoria prima dell'inserimento |
| **Coorti costruite ma vuote** *(osservato: zero gruppi in enrollment nel concorrente)* | Non lanciare funzionalità social a freddo: agganciarsi prima alla comunità esistente su Rapamycin News |
| **Effect size senza unità o mal derivati** | Unità native dell'outcome, mai percentuali ricavate da valori assoluti; confidence separata dall'effect size |

---

## 11. Domande aperte

1. Il confine tra ciò che è pubblico per default e ciò che è privato: profilo intero pubblico, o protocollo pubblico e misure private con opt-in per marker?
2. Modello di sostenibilità economica del ciclo secondario: da dove arrivano i soldi senza toccare il procurement?
   **Candidato emerso da Lamplit**: commissione (loro trattengono il 15%) su **coaching 1:1 e contenuti editoriali** di creator con credenziali verificate, via Stripe. Non tocca procurement né laboratori, quindi non inquina il dato clinico. Vincolo non negoziabile se si percorre questa strada: **protocolli, biomarcatori, safety rule e open data non sono mai vendibili** — si vende il tempo di una persona, non la conoscenza. I "protocolli a pagamento" che Lamplit permette sono in contraddizione diretta con la tesi dell'open data e vanno esclusi.
3. Rapporto formale con Rapamycin News: link, SSO, o partnership?
4. Curation iniziale dei protocolli: chi la fa e con quale processo di revisione?
5. Come si dichiara e si mostra il livello di evidenza in modo comprensibile e non manipolabile?
6. Ambito geografico iniziale: Italia (con AIFA e laboratori italiani) o internazionale in inglese fin da subito? (Le slide sono in inglese: suggerisce internazionale, ma i laboratori e il procurement sono per forza locali.)
7. Peptidi, plasmaferesi, infusioni IV: le slide li includono nel protocollo personale. Dentro o fuori dal **catalogo pubblico copiabile**? Sono le voci a maggior impatto reputazionale e legale, ed è diverso documentare ciò che si fa dal renderlo un protocollo che un principiante può seguire con un click.
8. Chi sviluppa, dentro i 35k: Fabio + LLM, contributori open source, o una commessa a un team?
9. Confine tra il protocollo personale di Fabio (contenuto delle slide 4-14, incluse le note su NRF2 e restrizione di metionina) e il prodotto: il primo è il caso d'uso zero e il seed del catalogo, ma il secondo non deve diventare "la piattaforma del protocollo di Fabio".
10. Ruolo del machine learning citato nelle slide: realistico solo con migliaia di soggetti, e va posizionato come obiettivo di Fase 4-5 e non come promessa iniziale — altrimenti attira esattamente la critica metodologica che si vuole disinnescare.
11. L'Evidence Layer entra in Fase 0 (rallenta l'MVP ma rende i protocolli credibili subito) o in Fase 3?
12. Copertura iniziale dell'ingestione: solo longevity/hallmark, o anche il generalista dove ProtocolEngine è già forte?
13. La revisione comunitaria dei claim è aperta a tutti o riservata a utenti con protocolli documentati?
14. Si scrive a ProtocolEngine e alla Clock Foundation — e se sì, prima o dopo aver mostrato pubblicamente il progetto alla conferenza?
15. La pre-registrazione dell'endpoint è obbligatoria per pubblicare uno Study, o opzionale con badge di qualità?
16. Il Claims Validator si costruisce presto come strumento di acquisizione, accettando di esporsi al conflitto con i venditori di integratori?
17. Quanti clock epigenetici supportare, e come si dichiara l'incomparabilità tra provider diversi?
18. L'aderenza minima sotto la quale un contributo **non** entra nell'aggregazione di coorte: quale soglia, e la si dichiara pubblicamente?
19. I **range ottimali**: da dove si prendono e chi se ne assume la responsabilità editoriale? È il punto di massima esposizione del progetto — un range ottimale è già a un passo dalla raccomandazione clinica.
20. Il Blood Layer si rilascia con un'identità propria, presentabile senza nominare il biohacking, o resta un modulo interno?
21. Si contatta Lucis come partner europeo di laboratorio? 450+ laboratori in Europa e nessun interesse sull'off-label: è complementarità pulita.
22. Soglia minima di metadati per l'open data: LOINC obbligatorio, o si accetta un mapping probabilistico dichiarato come tale?
23. L'Evidence Badge si calcola solo su referti verificati, o anche su dati inseriti a mano dichiarati come tali?
24. La verifica delle credenziali professionali: chi la esegue e con quale processo, in un progetto senza personale dedicato?
25. Si apre la strada dei creator a pagamento, e si accetta la commissione come modello di sostentamento della non-profit?
26. Contattare Panisperna Labs / Lamplit: complementarità sul layer clinico, o rischio di sovrapposizione sullo stesso pubblico italiano?
27. **Riuso di getbased**: fork, vendorizzazione degli algoritmi (raccomandata), o complemento? E si scrive al manutentore prima o dopo aver deciso?
28. Il layer individuale supporta una **modalità local-first** alla getbased — dati che non lasciano il browser, contributo alla coorte come scelta esplicita e separata? È la risposta più forte all'obiezione privacy, ma raddoppia le modalità di storage da mantenere.
29. **Agent Access / MCP** in roadmap? Costo basso, impatto culturale alto sul pubblico hacker, e nessun concorrente commerciale lo farà mai.
30. La mappatura LOINC del catalogo ereditato si contribuisce upstream o resta nostra?

---

## 12. Panorama competitivo

Tre attori mappati sul campo. Le loro scelte hanno determinato buona parte delle decisioni in questo documento.

|  | ProtocolEngine | MyAgingTests (Clock Foundation) | **biohack.it** |
|---|---|---|---|
| Origine | Letteratura | Laboratorio epigenetico | **Comunità** |
| Motore | Pipeline AI su PubMed | Vendita di kit | **Dati longitudinali condivisi** |
| Copertura | Supplementi e habit | Longevity, peptidi, ormoni | **Tutto, incluso off-label e procedure** |
| N-of-1 | No | Sì, ben progettato | Sì, **in coorte** |
| Confronto tra pari | No | No (gruppi vuoti) | **Sì** |
| Community | No | Primitivo costruito, inutilizzato | **Preesistente (Rapamycin News)** |
| Sicurezza | Evitata per design | Parziale, nessuna safety rule per farmaco | **Modulo dedicato (M7)** |
| Dato | Proprietario | Proprietario, non-profit USA | **Open data, AGPL** |
| Conflitto d'interesse | Affiliazioni | Vende i test che consiglia | **Nessuno** |

**Cosa si è preso da ciascuno**: da ProtocolEngine la separazione confidence/effect-size, le unità native e la directional evidence con conteggio degli studi sfavorevoli (M11). Da MyAgingTests la separazione a tre entità, il Daily Log con aderenza a quattro stati, il wellness check, la vista per sistemi d'organo, il wizard con revisione umana, il tetto a crediti e la tassonomia per meccanismo d'azione.

**Cosa si è deciso di non prendere**: il dato. Entrambi i database sono banche dati di soggetti identificabili protette dal diritto sui generis, e quello di MyAgingTests è verificabilmente rotto nel punto che conta di più — effect size a tre ordini di grandezza dal vero, attribuzioni a composti sbagliati, un'estrazione che perde voci in silenzio. Si studia la struttura, si ricostruisce la pipeline da fonti aperte.

**Il verdetto strategico**, che è anche la frase per la conferenza:

> Loro hanno il software e non hanno la comunità. Noi abbiamo la comunità e non abbiamo il software.
> Il secondo problema è molto più risolvibile del primo — e una comunità viva è anche l'unico controllo di qualità che funziona davvero sui dati.

---

*Prossimo aggiornamento previsto: riconciliazione con le slide riviste per la conferenza e chiusura delle domande aperte 1-18.*
