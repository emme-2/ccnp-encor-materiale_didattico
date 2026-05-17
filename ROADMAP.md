# ROADMAP — Sviluppo Materiale CCNP ENCOR 350-401

> Aggiornare questo file ad ogni sessione di lavoro.
> Per ogni modulo: spostare da "In coda" → "In corso" → "Completato".

---

## Stato Complessivo

- **Completati:** 28 / 35 moduli (MOD-01/02/03/04/05/06/07 + MOD-10–20 + MOD-26/27/28/29/30/31/32–35)
- **In sviluppo:** 0
- **Placeholder con sorgente:** 2 / 35 (MOD-08, 09)
- **Da sviluppare ex-novo:** 5 / 35

---

## Priorità 1 — ✅ COMPLETATI

| MOD | Titolo | Stato | Data |
|-----|--------|-------|------|
| ~~MOD-01~~ | OSPFv2 Fondamenta | ✅ COMPLETO | 2026-05-14 |
| ~~MOD-02~~ | OSPFv2 Aree & Summarization | ✅ COMPLETO | 2026-05-14 |
| ~~MOD-03~~ | OSPFv3 Dual-Stack | ✅ COMPLETO | 2026-05-14 |
| ~~MOD-04~~ | OSPF Troubleshooting | ✅ COMPLETO | 2026-05-16 |
| ~~MOD-05~~ | BGP Fondamenta | ✅ COMPLETO | 2026-05-14 |
| ~~MOD-06~~ | BGP Traffic Engineering | ✅ COMPLETO | 2026-05-14 |
| ~~MOD-07~~ | BGP Route Reflector & IPv6 BGP | ✅ COMPLETO | 2026-05-17 |
| ~~MOD-27~~ | NAT/PAT & NTP | ✅ COMPLETO | 2026-05-17 |
| ~~MOD-30~~ | Device Security & AAA | ✅ COMPLETO | 2026-05-17 |
| ~~MOD-31~~ | ACL & CoPP | ✅ COMPLETO | 2026-05-17 |

---

## Priorità 2 — Prossimi moduli da sviluppare

| MOD | Titolo | Mancante | Priorità |
|-----|--------|----------|----------|
| ~~MOD-07~~ | ~~BGP Route Reflector & IPv6 BGP~~ | ~~tutto~~ | ✅ COMPLETATO 2026-05-17 |
| ~~MOD-27~~ | ~~NAT, PAT & NTP~~ | ~~tutto~~ | ✅ COMPLETATO 2026-05-17 |
| ~~MOD-30~~ | ~~Device Security & AAA~~ | ~~tutto~~ | ✅ COMPLETATO 2026-05-17 |
| ~~MOD-31~~ | ~~ACL & CoPP~~ | ~~tutto~~ | ✅ COMPLETATO 2026-05-17 |
| MOD-08 | Route Manipulation & PBR | tutto (ex-novo) | Alta — gap critico syllabus |
| MOD-09 | Redistribuzione & Loop Prevention | tutto (ex-novo) | Media — dipende MOD-08 |

---

## Priorità 3 — Sviluppo ex-novo (nessun materiale sorgente)

Ordinati per impatto esame:

| MOD | Titolo | Codici | Stima | Dipendenze |
|-----|--------|--------|-------|------------|
| MOD-04 | OSPF Troubleshooting | 1.10.a–d | 6h | MOD-01/02 completati |
| MOD-08 | Route Manipulation & PBR | 3.2.d · 1.2 · 1.6 | 8h | MOD-01/05 completati |
| MOD-09 | Redistribuzione & Loop Prevention | 1.3–1.5 | 8h | MOD-08 completato |
| MOD-27 | NAT, PAT & NTP | 3.4.a · 3.4.b | 6h | — |
| MOD-07 | BGP Route Reflector & IPv6 BGP | 1.11.d | 4h | MOD-05/06 completati |
| MOD-21 | SD-WAN | 1.3 | 4h (teoria) | — |
| MOD-22 | SD-Access | 1.4 | 4h (teoria) | — |
| MOD-23 | Wireless RF & Fondamenta | 3.3.a | 4h (teoria) | — |
| MOD-24 | Wireless Deployment & WLC | 3.3.b–e | 4h (teoria) | MOD-23 completato |
| MOD-25 | Wireless Security | 5.4 | 3h (teoria) | MOD-24 completato |

---

## Log Attività

| Data | MOD | Azione |
|------|-----|--------|
| 2026-05-12 | — | Creazione MAPPATURA_LAB.md (inventario + proposta moduli + gap analysis) |
| 2026-05-14 | ALL | Creazione struttura 35 moduli, spostamento file da LAB→MOD, placeholder workbook/soluzione/cfg/note_docente |
| 2026-05-14 | MOD-01 | Completato: soluzione.md (T1–T4) + cfg r1–r7 (misconfig intenzionali R4/R5) |
| 2026-05-14 | MOD-02 | Completato: soluzione.md (T1–T5) + cfg r1–r7 (stato finale MOD-01) |
| 2026-05-14 | MOD-03 | Completato: soluzione.md (T1–T4) + cfg r1–r6 (OSPFv2+IPv6, no OSPFv3) |
| 2026-05-14 | MOD-05 | Completato: soluzione.md (T1–T6) + cfg r1–r6 (eBGP R3↔R5 mancante in cfg) |
| 2026-05-14 | MOD-06 | Completato: soluzione.md (T7–T-EXTRA) + cfg r1–r6 (stato finale MOD-05) |
| 2026-05-16 | MOD-04 | Completato ex-novo: workbook.md (11 task, scenari A/B/C/D) + soluzione.md + cfg r1–r5 (9 errori intenzionali) |
| 2026-05-17 | MOD-07 | Completato ex-novo: workbook.md (T1-T3) + soluzione.md + cfg r1–r5 (full-mesh AS65001 + R5 AS65002) |
| 2026-05-17 | MOD-27 | Completato ex-novo: workbook.md (T1-T5) + soluzione.md + cfg r-isp/r-gw/pc1/pc2 |
| 2026-05-17 | MOD-30 | Completato ex-novo: workbook.md (T1-T4) + soluzione.md + cfg r1/r2 (FreeRADIUS 192.168.122.100) |
| 2026-05-17 | MOD-31 | Completato ex-novo: workbook.md (T1-T5) + soluzione.md + cfg r1/r2 (OSPF+SSH+ACL+CoPP) |

---

## Prossimi Passi (sessione successiva)

1. **MOD-08** — Route Manipulation & PBR (ex-novo, gap critico syllabus — 0% copertura)
2. **MOD-09** — Redistribuzione & Loop Prevention (dipende da MOD-08)
3. **MOD-21/22** — SD-WAN / SD-Access (solo teoria, demo dCloud)
4. **MOD-23/24/25** — Wireless (teoria + simulatore)