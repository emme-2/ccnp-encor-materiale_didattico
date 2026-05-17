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
| MOD-18 | ✅ questa sessione | ✅ 2026-05-17 | ✅ questa sessione | 4 cfg: snapshot fine MOD-17 (Parts 1-3), no IPSec |
| MOD-19 | ✅ questa sessione | ✅ 2026-05-17 | ✅ questa sessione | 4 cfg: snapshot fine MOD-18 (GRE+IPSec completo) |
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
| A08 | MOD-18 | B2 | Nessun cfg standalone — dipendenza da MOD-17 | Creati 4 cfg: snapshot finale MOD-17 Parts 1-3 (CUST-B fixed, CUST-A GRE P2P, no IPSec) |
| A09 | MOD-19 | B2 | Nessun cfg standalone — dipendenza da MOD-18 | Creati 4 cfg: snapshot finale MOD-18 (tutto MOD-18 + IKEv2/IPSec su HUB e SP1) |

---

## Anomalie Umane — BLOCCANTE

### BLK-01 — MOD-18: Nessun cfg standalone

**Stato:** ✅ RISOLTO — 2026-05-17

**Soluzione applicata:** Creati `MOD-18/cfg/isp-cfg`, `hub-cfg`, `sp1-cfg`, `sp2-cfg` come snapshot dello stato finale di MOD-17 (Parts 1-3 completi): CUST-B bugs 1+2 corretti, CUST-A configurato con VRF + Lo1 + Tu101/Tu102 GRE P2P + route statiche. Nessun IPSec (configurato dagli studenti in MOD-18). Tu210 CUST-B conserva i bug di DMVPN (corretti in MOD-19).

**Contenuto MOD-18/cfg:**
- `isp-cfg` — invariato da MOD-17
- `hub-cfg` — CUST-B bug-1/2 corretti, CUST-A completo, Tu210 bug-3 presente, no IPSec
- `sp1-cfg` — CUST-B bug-1/2 corretti, CUST-A (Tu101 + Lo1), Tu210 bug-3 presente, no IPSec
- `sp2-cfg` — CUST-B corretto, CUST-A con IKEv2/IPSec reference (pre-configurato), route statiche CUST-A aggiunte

### BLK-02 — MOD-19: Nessun cfg standalone

**Stato:** ✅ RISOLTO — 2026-05-17

**Soluzione applicata:** Creati `MOD-19/cfg/isp-cfg`, `hub-cfg`, `sp1-cfg`, `sp2-cfg` come snapshot dello stato finale di MOD-18: tutto il contenuto di MOD-18/cfg + IKEv2/IPSec completo su HUB e SP1 + `tunnel protection ipsec profile IPSEC-PROF` applicato su Tu101 (SP1) e Tu101/Tu102 (HUB). SP2 invariato (aveva già IPSec). Tu210 CUST-B conserva i bug di DMVPN (corretti in MOD-19 T5.9).

**Contenuto MOD-19/cfg:**
- `isp-cfg` — invariato da MOD-17
- `hub-cfg` — tutto di MOD-18 + crypto ikev2/ipsec completo + tunnel protection su Tu101/Tu102, Tu210 bug-3 presente
- `sp1-cfg` — tutto di MOD-18 + crypto ikev2/ipsec completo + tunnel protection su Tu101, Tu210 bug-3 presente
- `sp2-cfg` — identico a MOD-18/sp2-cfg (SP2 non modificato in MOD-18)

---

## Gap Residui

| Gap | Descrizione | Priorità |
|-----|-------------|----------|
| G01 | MOD-18/19: nessun cfg standalone | ✅ Risolto 2026-05-17 |
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

*Aggiornato 2026-05-17 — BLK-01/02 risolti, G01 chiuso, A08/A09 aggiunte*
