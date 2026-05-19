# PROGETTO: Materiale Didattico CCNP ENCOR 350-401

> Aggiornato: 2026-05-19

## Contesto
Sviluppo di materiale didattico standard e riutilizzabile per corsi di 
certificazione Cisco CCNP ENCOR 350-401.
Il materiale esistente è stato prodotto per una classe specifica (Mar–Mag 2026)
ed è in fase di standardizzazione per classi future.

## Ambiente Lab di Riferimento
- Piattaforma: GNS3 con IOU L2 e IOU L3
- Servizi esterni (FreeRADIUS, ntopng, ecc.): container sulla VM GNS3
- Rete container: virbr 192.168.122.0/24
- Router IOU fisicamente collegati tramite eth0/0 a switch GNS3. Collegamenti logici realizzati con Sub-Interfaces.
- In futuro, potrei migrare su soluzione basata su containerlab. ad oggi non prioritario.
- TFTP server: 192.168.122.1 — path: /ENCOR/[LABxx]/rx-cfg
- Le configurazioni iniziali dei router si caricano via TFTP all'avvio del lab

## Piattaforme Supportate
Il materiale è progettato per essere fruibile su:
- GNS3 con IOU L2/L3
- ContainerLab con vrnetlab/IOU
- EVE-NG

Le sintassi IOS nei cfg e nei workbook sono compatibili
con tutte e tre le piattaforme. Ogni workbook riporta
in testa questa nota:
> **Piattaforme supportate:** GNS3 · ContainerLab (vrnetlab/IOU) · EVE-NG

## Struttura Cartella Progetto

```
MATERIALE DIDATTICO ENCOR/
├── CLAUDE.md                  ← questo file
├── README.md                  ← documentazione repo (unico README)
├── ROADMAP.md                 ← stato sviluppo e priorità
├── TEMPLATE/
│   ├── workbook_template.md
│   └── master_slide.pptx
├── script/
│   ├── export_pdf.py          ← esporta MD → PDF A4 (workbook + soluzione + note)
│   ├── generate_slides.py     ← genera deck .pptx per tutti i moduli
│   └── generate_template.py   ← genera template workbook/slide
├── EXPORT/                    ← output PDF (gitignored, rigenerare con export_pdf.py)
│   ├── style.css
│   └── PDF/
├── MOD-01/ … MOD-35/          ← 35 moduli autonomi
└── TEMPLATE/
```

## Struttura Moduli

Ogni modulo è un'unità didattica indipendente con:
- 1 o più argomenti del syllabus ENCOR
- Workbook studenti
- Slide/dispense (1 deck per modulo)
- File cfg iniziali per TFTP
- Soluzione commentata

## Deliverable Standard per Modulo
1. Workbook (struttura → vedi sezione dedicata)
2. Slide .pptx (python-pptx, template master)
3. **cfg/** — configurazioni iniziali device
   - File separati per device (es. r1-cfg, pe1-cfg, sw1-cfg)
   - Sintassi IOS compatibile GNS3/ContainerLab/EVE-NG
   - Gli stessi blocchi sono incorporati inline nella
     Sezione 3 del workbook
   - I file in cfg/ NON vanno rimossi dopo l'integrazione
     nel workbook — sono la fonte di riferimento per il docente
4. Soluzione commentata

## Struttura Workbook Standard
1. TOPOLOGIA
   - Diagramma logico con ruoli dei device
   - Piano di indirizzamento (tabella IP/VLAN/AS)
2. OBIETTIVI DELLA SESSIONE
   - Learning outcomes
   - Codici syllabus coperti
3. LAB SETUP
   - **Piattaforme supportate** (nota in testa)
   - **Prerequisiti** (conoscenze e moduli precedenti richiesti)
   - **Configurazione Iniziale** — un blocco per ogni device:
     - Il blocco è copiabile direttamente sul device (paste manuale)
     - Stesso contenuto presente in cfg/ del modulo
     - Formato:
       #### [Hostname]
       hostname X
       ! commenti esplicativi
       comandi
   - **Verifica pre-lab** — comandi e output atteso per confermare
     il punto di partenza
4. TASK LIST (panoramica numerata)
5. DETTAGLIO TASK (per ogni task)
   - TEORIA: riepilogo conciso, max 1 pagina
   - TASK: istruzioni operative step-by-step
   - VERIFICA: comandi attesi + output di riferimento
6. TROUBLESHOOTING GUIDE
   - Errori comuni + come diagnosticarli
7. SOLUZIONI
   - Configurazioni complete commentate
   - Note su varianti/alternative
8. RIEPILOGO & EXAM TIPS
   - 3-5 bullet punti chiave per l'esame
   - Domande tipo CCNP

## Stile Slide
- Font: Gotham (Regular / Medium / Bold)
- Colori:
  - Arancio Magnetico  #EF6A01  → primario, accent, titoli sezione
  - Nero Fondamenta    #000000  → testo, struttura
  - Avorio Neutro      #EDEBDC  → sfondi, aree neutre
  - Giallo Opportunità #FFB600  → highlight, exam tips
- Densità: stile dispensa, preferire più slide leggere a slide dense
- Layout slide: vedi TEMPLATE/master_slide.pptx

## Tipi di Slide (layout)
01 Cover Module     — sfondo nero, titolo arancio, codici avorio
02 Agenda           — sfondo avorio, numerazione arancio
03 Section Header   — sfondo arancio pieno, titolo bianco
04 Teoria Concetto  — sfondo avorio, max 5-6 righe
05 Diagramma        — sfondo bianco/avorio, didascalia sotto
06 Config/Comando   — sfondo nero, monospace bianco, highlight giallo
07 Output Verifica  — sfondo nero, riga attesa in arancio
08 Troubleshooting  — tabella 2 col: Sintomo | Causa+Fix
09 Exam Tips        — sfondo giallo, bullet nero
10 Summary          — sfondo arancio, 3-5 concetti in bianco bold

## Riferimento Programma
- 11 sessioni, 43 ore, Mar–Mag 2026
- Syllabus ufficiale: Cisco ENCOR 350-401

## Note Operative per Claude Code
- I file cfg usano sintassi IOS (non IOS-XE): verificare compatibilità IOU
- RESTCONF non disponibile su IOU → trattare come teoria
- LISP/VXLAN → solo teoria e diagrammi, nessun lab pratico
- SD-WAN / SD-Access → demo dCloud, nessun lab GNS3

### Topologie
- Formato obbligatorio: blocchi Mermaid (fenced code block con tipo `mermaid`)
- Tipo flowchart LR → topologie lineari, WAN, routing
- Tipo graph TB → topologie L2, campus, switching
- Includere sempre: hostname · IP interfacce · ruolo device · tipo link
- NON usare ASCII art in nessun caso

## Script

| Script | Uso |
|--------|-----|
| `script/generate_slides.py` | `python script/generate_slides.py [MOD-XX]` |
| `script/export_pdf.py` | `python script/export_pdf.py [MOD-XX] [--force] [--css-only]` |
| `script/generate_template.py` | generazione template workbook/slide |

`export_pdf.py` richiede: `pip install pymdown-extensions` · Google Chrome installato.
Output PDF in `EXPORT/PDF/` (gitignored).

## Versioning
- v1.0: 35 moduli · Mermaid · cfg inline · multipiattaforma · slide deck
- Changelog: aggiornare ROADMAP.md dopo ogni sessione