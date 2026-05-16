# WBS — Da MVP a v1.0
# Materiale Didattico CCNP ENCOR 350-401

> Creato: 2026-05-16 · Stato: IN CORSO · Versione attuale: MVP (v0.1)

---

## Legenda

| Simbolo | Significato |
|---------|-------------|
| 🤖 CC | Task delegato a Claude Code — lavora in autonomia |
| 👤 Human | Richiede decisione o review umana |
| ✅ | Completato |
| 🔄 | In corso |
| ⬜ | Da fare |

---

## FASE 1 — Contenuto Completo

Obiettivo: tutti i 35 moduli con workbook + soluzione + cfg.

| Step | Task | Chi | Stato | Note |
|------|------|-----|-------|------|
| 1.1 | Sviluppo MOD-04 OSPF Troubleshooting | 🤖 CC | 🔄 | Topologia con errori intenzionali |
| 1.2 | Review MOD-04 | 👤 Human | ⬜ | Verificare correttezza tecnica scenari |
| 1.3 | Sviluppo MOD-08 Route Manipulation & PBR | 🤖 CC | ⬜ | |
| 1.4 | Review MOD-08 | 👤 Human | ⬜ | |
| 1.5 | Sviluppo MOD-09 Redistribuzione & Loop Prevention | 🤖 CC | ⬜ | |
| 1.6 | Review MOD-09 | 👤 Human | ⬜ | |
| 1.7 | Sviluppo MOD-07 BGP Route Reflector & IPv6 | 🤖 CC | ⬜ | |
| 1.8 | Review MOD-07 | 👤 Human | ⬜ | |
| 1.9 | Sviluppo MOD-27 NAT/PAT & NTP | 🤖 CC | ⬜ | |
| 1.10 | Sviluppo MOD-30 AAA & RADIUS | 🤖 CC | ⬜ | Richiede FreeRADIUS container |
| 1.11 | Sviluppo MOD-31 ACL & CoPP | 🤖 CC | ⬜ | |
| 1.12 | Review MOD-27/30/31 | 👤 Human | ⬜ | |
| 1.13 | Sviluppo MOD-21/22 SD-WAN & SD-Access (teoria) | 🤖 CC | ⬜ | Solo note_docente |
| 1.14 | Sviluppo MOD-23/24/25 Wireless (teoria) | 🤖 CC | ⬜ | Solo note_docente |
| 1.15 | Review moduli teoria | 👤 Human | ⬜ | Verifica accuratezza concetti |

---

## FASE 2 — Uniformità e Standard v1.0

Obiettivo: tutti i moduli esistenti allineati al nuovo template.

| Step | Task | Chi | Stato | Note |
|------|------|-----|-------|------|
| 2.1 | Aggiornare sezione 3 LAB SETUP su tutti i 23 moduli esistenti | 🤖 CC | ⬜ | Cfg inline + nota piattaforme |
| 2.2 | Convertire topologie ASCII → Mermaid su tutti i moduli | 🤖 CC | ⬜ | |
| 2.3 | Campionatura qualità workbook (5 moduli a scelta) | 👤 Human | ⬜ | Verifica standard |
| 2.4 | Allineare profondità sezioni Exam Tips e Troubleshooting | 🤖 CC | ⬜ | Su moduli segnalati in 2.3 |
| 2.5 | Verifica cross-reference tra moduli | 👤 Human | ⬜ | Prerequisiti coerenti? |
| 2.6 | Aggiornare MAPPATURA_LAB.md finale | 🤖 CC | ⬜ | |

---

## FASE 3 — Slide Deck

Obiettivo: tutti i 35 moduli con slide .pptx.

| Step | Task | Chi | Stato | Note |
|------|------|-----|-------|------|
| 3.1 | Definire struttura slide per tipo di modulo | 👤 Human + 🤖 CC | ⬜ | Quante slide per sezione tipo |
| 3.2 | Generare master_template.pptx | 🤖 CC | ⬜ | python-pptx, 10 layout |
| 3.3 | Review template visivo | 👤 Human | ⬜ | Font, colori, proporzioni |
| 3.4 | Iterazione template se necessario | 🤖 CC | ⬜ | |
| 3.5 | Generare slide deck MOD-13÷19 (batch 1 — completi) | 🤖 CC | ⬜ | Partendo da workbook |
| 3.6 | Review batch 1 | 👤 Human | ⬜ | Un modulo campione |
| 3.7 | Generare slide deck tutti i rimanenti moduli LAB | 🤖 CC | ⬜ | |
| 3.8 | Generare slide deck moduli TEORIA | 🤖 CC | ⬜ | MOD-07/20/21/22/23/24/25/35 |
| 3.9 | Review finale slide | 👤 Human | ⬜ | |

---

## FASE 4 — Git & GitHub

Obiettivo: repo versionata e distribuibile.

| Step | Task | Chi | Stato | Note |
|------|------|-----|-------|------|
| 4.1 | Creare .gitignore | 🤖 CC | ⬜ | |
| 4.2 | Inizializzare repo locale + branch develop | 🤖 CC | ⬜ | |
| 4.3 | Creare CONTRIBUTING.md | 🤖 CC | ⬜ | Convenzioni commit + workflow |
| 4.4 | Creare README_GITHUB.md | 🤖 CC | ⬜ | Landing page repo |
| 4.5 | Primo commit su develop | 🤖 CC | ⬜ | MVP v0.1 |
| 4.6 | Creare repo Private su GitHub | 👤 Human | ⬜ | |
| 4.7 | Push develop → GitHub | 👤 Human | ⬜ | Dopo step 4.6 |
| 4.8 | Definire flusso releases (ZIP taggate) | 👤 Human | ⬜ | |
| 4.9 | Tag v1.0 e prima Release ZIP | 👤 Human + 🤖 CC | ⬜ | Dopo completamento Fase 1-3 |

---

## Riepilogo Milestone

| Milestone | Fase | Condizione |
|-----------|------|------------|
| **MVP v0.1** | — | ✅ 23 moduli consegnati — 2026-05-14 |
| **Content Complete** | Fine Fase 1 | 35 moduli con workbook + soluzione + cfg |
| **Standard Complete** | Fine Fase 2 | Mermaid + cfg inline + uniformità |
| **Slide Complete** | Fine Fase 3 | 35 slide deck .pptx |
| **v1.0 Release** | Fine Fase 4 | Tag GitHub + Release ZIP |

---

## Decisioni Architetturali Prese

| Decisione | Scelta | Data |
|-----------|--------|------|
| Piattaforme supportate | GNS3 · ContainerLab (vrnetlab/IOU) · EVE-NG | 2026-05-16 |
| Distribuzione cfg | Inline nel workbook + file in cfg/ | 2026-05-16 |
| Caricamento cfg | Paste manuale (no TFTP) | 2026-05-16 |
| Topologie | Mermaid (no ASCII art) | 2026-05-16 |
| Repo GitHub | Private | 2026-05-16 |
| Distribuzione studenti | Release ZIP taggate | 2026-05-16 |
| Branch strategy | main (stabile) + develop (WIP) | 2026-05-16 |
| Slide formato | .pptx via python-pptx | 2026-05-16 |

---

*Aggiornare questo file dopo ogni milestone completato.*
*Changelog dettagliato → ROADMAP.md*
