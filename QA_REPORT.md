# QA REPORT — Fase 2 Uniformazione Standard v1.0
# Materiale Didattico CCNP ENCOR 350-401

> Data: 2026-05-17 · Eseguito da: Claude Code · Branch: develop

---

## Sommario

Passaggio QA + uniformazione eseguito in autonomia su tutti i workbook LAB (MOD-01÷MOD-19, MOD-26, MOD-28, MOD-29). Le operazioni eseguite su ogni modulo:

| Operazione | Descrizione | Stato |
|------------|-------------|-------|
| B1 — Piattaforme note | Aggiunta blockquote "Piattaforme supportate" dopo H1 | ✅ Completato su tutti |
| B2 — Cfg inline | Sostituzione sezione TFTP con blocchi inline per device | ✅ Completato (⚠️ 2 BLOCCANTE) |
| B3 — Mermaid topology | Sostituzione ASCII art con diagrammi Mermaid | ✅ Completato su tutti |
| B4 — Troubleshooting ≥3 | Verifica righe minime guida troubleshooting | ✅ Già presenti su tutti |
| B5 — Prerequisiti chain | Allineamento prerequisiti nella catena modulare | ✅ Già presenti / verificati |

---

## Tabella Pre/Post — Modifiche per Modulo

| Modulo | B1 Piattaforme | B2 Cfg Inline | B3 Mermaid | Note |
|--------|:--------------:|:-------------:|:----------:|------|
| MOD-01 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 7 device: R1–R7 |
| MOD-02 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 7 device: R1–R7 |
| MOD-03 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 6 device: R1–R6 (no R7) |
| MOD-04 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 5 device: R1–R5 |
| MOD-05 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 6 device: R1–R6 |
| MOD-06 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 6 device: R1–R6 |
| MOD-07 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | — |
| MOD-08 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 7 device |
| MOD-09 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 7 device |
| MOD-10 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 4 device: PE1/P1/P2/PE2 |
| MOD-11 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 6 device |
| MOD-12 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 6 device |
| MOD-13 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | R1/SW1/SW2 |
| MOD-14 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | SW1/SW2 |
| MOD-15 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | R1/SW1/SW2 |
| MOD-16 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | SW1/SW2 |
| MOD-17 | ✅ questa sessione | ✅ questa sessione | ✅ questa sessione | 4 device: ISP/HUB/SP1/SP2 |
| MOD-18 | ✅ questa sessione | ⚠️ BLOCCANTE | ✅ questa sessione | Nessun cfg proprio: usa MOD-17 |
| MOD-19 | ✅ questa sessione | ⚠️ BLOCCANTE | ✅ questa sessione | Nessun cfg proprio: usa MOD-17/18 |
| MOD-26 | ✅ questa sessione | ✅ questa sessione | ✅ questa sessione | R1 (QoS) |
| MOD-27 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | 4 device |
| MOD-28 | ✅ questa sessione | ✅ questa sessione | ✅ questa sessione | 5 device: R1–R5 |
| MOD-29 | ✅ questa sessione | ✅ questa sessione | ✅ questa sessione | 5 device: R1–R5 |
| MOD-30 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | R1/R2 |
| MOD-31 | ✅ (sessione precedente) | ✅ (sessione precedente) | ✅ (sessione precedente) | R1/R2 |

---

## Anomalie Corrette

| ID | Modulo | Tipo | Descrizione | Fix applicato |
|----|--------|------|-------------|---------------|
| A01 | MOD-02 | B3 | ASCII art multi-router con topologia anello P2P + broadcast VLAN 3456 | Mermaid `flowchart LR` con subgraph aree e nodo switch per segmento broadcast |
| A02 | MOD-05 | B3 | Link eBGP R3↔R5 intenzionalmente dashed (da configurare) | Mermaid con stile `-.->` per link mancante + label "da configurare T3" |
| A03 | MOD-10/11/12 | B2 | Sezione TFTP con nota "ATTENZIONE: cfg non ancora disponibili" | Sostituita con blocchi inline per tutti i device MPLS |
| A04 | MOD-17 | B2 | Hub-cfg con BUG-1/BUG-2/BUG-3 embedded nelle configurazioni | Mantenuti i bug nel cfg inline — coerente con progetto didattico troubleshooting |
| A05 | MOD-17 | B2 | SP1-cfg con BUG-1/BUG-2/BUG-3; SP2-cfg con BUG-4 + IKEv2 reference | Incluso nel cfg inline con commenti "BUG" sulla riga di descrizione |
| A06 | MOD-18 | B2 | Sezione TFTP riferiva cfg MOD-17 (non MOD-18 specifici) | Aggiornato cross-reference a "Sezione 3 di MOD-17/workbook.md" |
| A07 | MOD-26 | B3 | ASCII art con caratteri speciali `──── ` non standard | Sostituita con Mermaid `flowchart LR` |

---

## Anomalie Umane — BLOCCANTE

Le seguenti anomalie richiedono intervento umano e non possono essere risolte automaticamente:

### BLK-01 — MOD-18: Nessun cfg standalone

**Stato:** MOD-18 non ha cfg propri in `MOD-18/cfg/`. La directory contiene solo un `README.md`.

**Causa:** MOD-18 (IPSec IKEv2) parte dallo stato finale di MOD-17 e aggiunge solo configurazioni IPSec. I cfg di partenza sono gli stessi di MOD-17.

**Impatto:** B2 non completabile (nessun contenuto da inlineare). La sezione Lab Setup è stata aggiornata con riferimento cross-module a `MOD-17/workbook.md Sezione 3`.

**Raccomandazione:** Creare `MOD-18/cfg/hub-cfg` / `sp1-cfg` / `sp2-cfg` / `isp-cfg` come snapshot dello stato finale di MOD-17 (VRF + GRE + route statiche, senza IPSec). Questo permetterebbe agli studenti di iniziare MOD-18 senza dipendenza da MOD-17 completato.

### BLK-02 — MOD-19: Nessun cfg standalone

**Stato:** MOD-19 non ha cfg propri in `MOD-19/cfg/`. La directory contiene solo un `README.md`.

**Causa:** MOD-19 (DMVPN) parte dallo stato finale di MOD-18 (GRE + IPSec). La progressione è intenzionale.

**Impatto:** B2 non completabile. La sezione Lab Setup descrive come prerequisito "MOD-18 completato" senza cfg di partenza propri.

**Raccomandazione:** Creare `MOD-19/cfg/` come snapshot dello stato finale di MOD-18 (VRF + GRE P2P + IPSec) come cfg di partenza. Alternativa: mantenere la dipendenza e documentarla esplicitamente come "modulo sequenziale" nel MAPPATURA_LAB.md.

---

## Gap Residui

| Gap | Descrizione | Priorità |
|-----|-------------|----------|
| G01 | MOD-18/19: nessun cfg standalone (vedi BLK-01/02) | Alta |
| G02 | MOD-21/22/23/24/25: non sviluppati (wireless/SD-WAN) | Bassa — fuori scope MVP |
| G03 | Slide .pptx: nessun modulo ha il deck slide generato | Media — Fase 3 WBS |
| G04 | MAPPATURA_LAB.md usa nomenclatura LAB0x (vecchia): non aggiornata alla struttura MOD-xx | Media |

---

## DECISION LOG — Scelte durante la Fase 2

| ID | Decisione | Motivazione |
|----|-----------|-------------|
| D01 | Mantenere bug pre-configurati nel cfg inline MOD-17 | Il troubleshooting è parte integrante dell'obiettivo didattico — i bug devono essere presenti |
| D02 | Includere IKEv2/IPSec reference config di SP2 nel cfg inline MOD-17 | SP2 è pre-configurato come reference in MOD-17 stesso (Part 4 di MOD-17 vi fa riferimento) |
| D03 | Usare `flowchart LR` per tutti i moduli routing/WAN/VPN | Come da regola CLAUDE.md |
| D04 | Usare `graph TB` per moduli L2/campus/switching (MOD-13÷16) | Come da regola CLAUDE.md |
| D05 | MOD-18/19: aggiornare cross-reference anziché bloccare | Non rimuovere i riferimenti corretti — solo rendere esplicita la dipendenza |
| D06 | cfg inline per MOD-29 usa stessa struttura di MOD-28 (topologia identica) | Il workbook stesso dichiara "La topologia e' identica a MOD-28" |

---

## 5 Moduli Campione per Review Umana

I seguenti moduli coprono diversi tipi di topologia e complessità — raccomandati per la review:

| Modulo | Perché campionare |
|--------|------------------|
| **MOD-02** | Topologia OSPF multi-area complessa: broadcast segment + ring P2P + area 99. Mermaid complesso. |
| **MOD-11** | MPLS L3VPN: VRF + MP-BGP + CE-PE. Cfg inline con 6 device. Verifica coerenza con MOD-10. |
| **MOD-17** | VRF-Lite + GRE: cfg inline con 4 bug intenzionali. Verifica che i bug siano correttamente preservati. |
| **MOD-26** | QoS MQC: singolo router con VRF LAB e DHCP su e0/0. Topologia semplice ma cfg non standard. |
| **MOD-28** | Multicast PIM: 5 device, ruoli diversi (FHR/RP/LHR/SENDER/RECEIVER). Verify cfg R4 (no ip routing) e R5 (ip routing + igmp). |

---

*Fine QA_REPORT.md — 2026-05-17*
