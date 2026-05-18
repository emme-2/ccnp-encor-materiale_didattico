# TEMPLATE — Master Slide Deck
# CCNP ENCOR 350-401 · Materiale Didattico

> File: `master_template.pptx` · Generato da: `generate_template.py`
> Dimensioni: 33.87 × 19.05 cm (16:9 Widescreen)

---

## Palette Colori

| Nome | HEX | Uso |
|------|-----|-----|
| Arancio Magnetico | `#EF6A01` | Primario — accent, titoli sezione, elementi chiave |
| Nero Fondamenta | `#000000` | Testo, struttura, header barre |
| Avorio Neutro | `#EDEBDC` | Sfondi, aree neutre, testo su scuro |
| Giallo Opportunità | `#FFB600` | Highlight, Exam Tips, verifica attesa |
| Bianco | `#FFFFFF` | Testo su sfondi scuri, separatori |

---

## Font

| Ruolo | Font | Peso |
|-------|------|------|
| Titoli sezione | Montserrat | Bold |
| Titoli slide | Montserrat | SemiBold |
| Corpo testo | Montserrat | Regular |
| Codice / Config | Courier New | Regular |

### Come installare Montserrat in PowerPoint (Windows)

1. Scaricare la famiglia completa da [Google Fonts](https://fonts.google.com/specimen/Montserrat)
2. Estrarre il file ZIP
3. Selezionare tutti i file `.ttf`, tasto destro → **Installa per tutti gli utenti**
4. Riaprire PowerPoint — il font apparirà nei menu
5. Se il template mostra font sostitutivi, selezionare tutto (Ctrl+A) e riapplicare Montserrat

> **Nota:** se Montserrat non è installato, PowerPoint usa un fallback (solitamente Calibri o Arial).
> Le dimensioni e il layout non cambiano — solo il carattere visivo.

---

## I 10 Layout — Descrizione e Uso

### Layout 01 — Cover Module
- **Sfondo:** NERO pieno
- **Elementi:** stripe ARANCIO top/bottom, logo placeholder top-right
- **Titolo:** ARANCIO 40pt Bold, centrato verticalmente
- **Uso:** Prima slide di ogni modulo (MOD-XX — Titolo)
- **Campi da personalizzare:** Titolo modulo, sottotitolo (Area · Ore · Syllabus)

### Layout 02 — Agenda
- **Sfondo:** AVORIO
- **Header:** barra NERO, titolo "AGENDA" BIANCO 24pt
- **Corpo:** lista numerata — numeri ARANCIO Bold, testo NERO 20pt
- **Uso:** Seconda slide di ogni modulo — panoramica dei task/sezioni
- **Campi da personalizzare:** 5 righe di argomento

### Layout 03 — Section Header
- **Sfondo:** ARANCIO pieno
- **Titolo:** BIANCO 48pt Bold, centrato
- **Decorazione:** separatore bianco + sottotitolo BIANCO 22pt
- **Uso:** Separatore tra le macro-sezioni del modulo (es. "TEORIA", "TASK", "VERIFICA")

### Layout 04 — Teoria Concetto
- **Sfondo:** AVORIO · bordo sinistro ARANCIO
- **Header:** barra NERO con titolo concetto
- **Corpo:** max 6 righe a 18pt · densità dispensa
- **Key concept box:** fondo arancio tenue in fondo alla slide
- **Uso:** Spiegazione di un singolo concetto teorico

### Layout 05 — Diagramma / Topologia
- **Sfondo:** BIANCO
- **Area diagramma:** rettangolo tratteggiato ARANCIO (80% slide)
- **Didascalia:** NERO 14pt italic in fondo
- **Uso:** Topologie Mermaid esportate come immagine, schemi di rete, diagrammi di flusso
- **Flusso tipico:** incollare immagine nella zona tratteggiata, aggiornare didascalia

### Layout 06 — Config / Comando
- **Sfondo:** NERO
- **Header:** barra ARANCIO, titolo NERO
- **Code box:** sfondo quasi-nero, bordo ARANCIO, monospace Courier New 15pt
- **Highlight riga:** giallo scuro sulla riga di interesse
- **Badge device:** ARANCIO top-right con nome router (R1, SW1, ecc.)
- **Uso:** Mostrare comandi di configurazione IOS con output atteso

### Layout 07 — Output Verifica
- **Sfondo:** NERO
- **Struttura:** come Layout 06 + label "VERIFICA ATTESA" GIALLO
- **Riga evidenziata:** testo ARANCIO + freccia "← atteso"
- **Uso:** Checkpoint di verifica — mostra output esatto che lo studente deve ottenere

### Layout 08 — Troubleshooting
- **Sfondo:** AVORIO
- **Tabella 2 colonne:** SINTOMO (header NERO/BIANCO) | CAUSA+FIX (header ARANCIO/NERO)
- **Righe alternate:** BIANCO / AVORIO
- **Uso:** Guida troubleshooting — errori comuni con diagnosi e fix

### Layout 09 — Exam Tips
- **Sfondo:** GIALLO
- **Header:** barra NERO
- **Contenuto:** icona 📋 + 4 bullet ▶ + box Q&A BIANCO
- **Uso:** Ultima slide prima del Summary — punti chiave per l'esame CCNP

### Layout 10 — Summary / Takeaway
- **Sfondo:** ARANCIO
- **Titolo:** "TAKEAWAY" BIANCO 36pt
- **3 box NERO:** concetti chiave con numero ARANCIO + testo AVORIO
- **Footer:** "CCNP ENCOR 350-401" BIANCO 12pt
- **Uso:** Slide di chiusura modulo — i 3 concetti più importanti

---

## Come Claude Code usa il template

Ogni deck di modulo viene generato con uno script Python dedicato che:

1. Legge il `workbook.md` del modulo (sezioni 1-8)
2. Importa `master_template.pptx` come base dimensionale
3. Crea una nuova presentazione con le stesse dimensioni e palette
4. Genera le slide nell'ordine: Cover → Agenda → Section Header × N → Teoria × N → Config × N → Troubleshooting → Exam Tips → Summary
5. Salva in `MOD-XX/slides/MOD-XX_slides.pptx`

Il template non viene modificato direttamente — è la fonte di verità per colori e layout.
Per aggiornare il template (font, colori, proporzioni), modificare `generate_template.py`
e rigenerare.

---

## Workflow consigliato per personalizzare una slide

1. Aprire `master_template.pptx` in PowerPoint
2. Scegliere la slide del layout corrispondente
3. Duplicarla nel deck del modulo (tasto destro → Copia, poi Incolla nel deck)
4. Sostituire i testi placeholder con il contenuto reale
5. Per le topologie (Layout 05): incollare l'immagine Mermaid renderizzata nell'area tratteggiata
6. Per i code block (Layout 06/07): sostituire il testo monospace con i comandi IOS reali

---

*Generato da `generate_template.py` — rigenerare dopo modifiche alla palette o ai layout.*
