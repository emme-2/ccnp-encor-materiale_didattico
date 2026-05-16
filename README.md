# CCNP ENCOR 350-401 — Materiale Didattico Standard

Corso di certificazione Cisco CCNP ENCOR 350-401 · Ambiente: GNS3 IOU L2/L3
Repository standardizzata per erogazione multi-classe. Struttura aggiornata 2026-05-14.

---

## Struttura Repository

```
MATERIALE DIDATTICO ENCOR/
├── README.md              ← questo file
├── MAPPATURA_LAB.md       ← inventario + proposta moduli + gap analysis
├── ROADMAP.md             ← piano di sviluppo e priorità
├── CCNP_ENCOR_Programma_v2.docx
├── TEMPLATE/
│   ├── workbook_template.md
│   └── master_slide.pptx
├── MOD-01/ … MOD-35/     ← 35 moduli autonomi
└── _ARCHIVIO_LABxx/       ← materiale originale classe Mar–Mag 2026
```

---

## Tabella Moduli — 35 Moduli / 58.5h totali

| MOD | Area | Titolo | Tipo | Codici | Ore | Stato |
|-----|------|--------|------|--------|-----|-------|
| [MOD-01](MOD-01/README.md) | OSPF | OSPFv2 Fondamenta | LAB | 3.2.a · 3.2.b | 2h | WORKBOOK ✅ |
| [MOD-02](MOD-02/README.md) | OSPF | OSPFv2 Aree & Summarization | LAB | 3.2.a · 3.2.b | 2h | WORKBOOK ✅ |
| [MOD-03](MOD-03/README.md) | OSPF | OSPFv3 Dual-Stack | LAB | 3.2.b | 1.5h | WORKBOOK ✅ |
| [MOD-04](MOD-04/README.md) | OSPF | OSPF Troubleshooting | LAB | 1.10.a–d | 2h | DA SVILUPPARE |
| [MOD-05](MOD-05/README.md) | BGP | BGP Fondamenta | LAB | 3.2.c · 1.11.a/b | 2h | WORKBOOK ✅ |
| [MOD-06](MOD-06/README.md) | BGP | BGP Traffic Engineering | LAB | 1.11.c–e | 2h | WORKBOOK ✅ |
| [MOD-07](MOD-07/README.md) | BGP | BGP Route Reflector & IPv6 BGP | TEORIA | 1.11.d | 1.5h | DA SVILUPPARE |
| [MOD-08](MOD-08/README.md) | Route Manipulation | Route Manipulation & PBR | LAB | 3.2.d · 1.2 · 1.6 | 2h | DA SVILUPPARE |
| [MOD-09](MOD-09/README.md) | Route Manipulation | Redistribuzione & Loop Prevention | LAB | 1.3 · 1.4 · 1.5 | 2h | DA SVILUPPARE |
| [MOD-10](MOD-10/README.md) | MPLS | MPLS LDP & Fondamenta | LAB | 2.1 | 2h | COMPLETO ✅ |
| [MOD-11](MOD-11/README.md) | MPLS | MPLS L3VPN | LAB | 2.2 | 2h | COMPLETO ✅ |
| [MOD-12](MOD-12/README.md) | MPLS | MPLS L2VPN | LAB | 2.2 | 1.5h | COMPLETO ✅ |
| [MOD-13](MOD-13/README.md) | Layer 2 | EtherChannel LACP | LAB | 3.1.a · 3.1.b | 1.5h | COMPLETO ✅ |
| [MOD-14](MOD-14/README.md) | Layer 2 | Spanning Tree | LAB | 3.1.c | 1.5h | COMPLETO ✅ ✦ |
| [MOD-15](MOD-15/README.md) | FHRP | FHRP — HSRP, VRRP & GLBP | LAB | 1.1.b · 3.4.c | 2h | COMPLETO ✅ ✦ |
| [MOD-16](MOD-16/README.md) | FHRP | IP SLA & SPAN | LAB | 4.3 · 4.4 | 2h | COMPLETO ✅ ✦ |
| [MOD-17](MOD-17/README.md) | Overlay & VPN | VRF-Lite & GRE Tunneling | LAB | 2.2 | 2h | COMPLETO ✅ |
| [MOD-18](MOD-18/README.md) | Overlay & VPN | IPSec IKEv2 & VTI | LAB | 2.3 | 2h | COMPLETO ✅ ✦ |
| [MOD-19](MOD-19/README.md) | Overlay & VPN | DMVPN Phase 1/2/3 | LAB | 2.3 | 2h | COMPLETO ✅ ✦ |
| [MOD-20](MOD-20/README.md) | Overlay & VPN | LISP, VXLAN & SD-Access | TEORIA | 2.3 | 1.5h | COMPLETO ✅ |
| [MOD-21](MOD-21/README.md) | SD-WAN/SD-Access | SD-WAN | TEORIA | 1.3 | 1.5h | DA SVILUPPARE |
| [MOD-22](MOD-22/README.md) | SD-WAN/SD-Access | SD-Access | TEORIA | 1.4 | 1.5h | DA SVILUPPARE |
| [MOD-23](MOD-23/README.md) | Wireless | Wireless RF & Fondamenta | TEORIA | 3.3.a | 1.5h | DA SVILUPPARE |
| [MOD-24](MOD-24/README.md) | Wireless | Wireless Deployment & WLC | TEORIA | 3.3.b–e | 1.5h | DA SVILUPPARE |
| [MOD-25](MOD-25/README.md) | Wireless | Wireless Security | TEORIA | 5.4 | 1.5h | DA SVILUPPARE |
| [MOD-26](MOD-26/README.md) | QoS | QoS MQC & CoPP | LAB | 1.5.a · 1.5.b | 2h | COMPLETO ✅ |
| [MOD-27](MOD-27/README.md) | IP Services | NAT, PAT & NTP | LAB | 3.4.a · 3.4.b | 2h | DA SVILUPPARE |
| [MOD-28](MOD-28/README.md) | IP Services | Multicast — PIM & Auto-RP | LAB | 3.3 · 3.4.d | 2h | COMPLETO ✅ |
| [MOD-29](MOD-29/README.md) | IP Services | Network Assurance | LAB | 4.1–4.6 | 2h | COMPLETO ✅ |
| [MOD-30](MOD-30/README.md) | Security | Device Security & AAA | LAB | 5.1 | 2h | DA SVILUPPARE |
| [MOD-31](MOD-31/README.md) | Security | ACL, CoPP & Infrastructure Security | LAB | 5.2 | 2h | DA SVILUPPARE |
| [MOD-32](MOD-32/README.md) | Automation | EEM & Python Base | LAB | 6.1 · 6.2 · 6.6 | 2h | COMPLETO ✅ |
| [MOD-33](MOD-33/README.md) | Automation | Netmiko & Nornir | LAB | 6.2 · 6.3 | 2h | COMPLETO ✅ |
| [MOD-34](MOD-34/README.md) | Automation | Ansible & Git | LAB | 6.7 | 2h | COMPLETO ✅ |
| [MOD-35](MOD-35/README.md) | Automation | API & RESTCONF | TEORIA | 6.4 · 6.5 | 1.5h | COMPLETO ✅ |

**Legenda stato:**
- ✅ COMPLETO — workbook + soluzione + cfg pronti (o nota_docente per TEORIA)
- QUASI COMPLETO ⚠️ — workbook + soluzione presenti; mancano solo i cfg TFTP
- WORKBOOK ✅ — workbook completo; soluzione e cfg in sviluppo
- DA SVILUPPARE — nessun materiale sorgente, sviluppo ex-novo richiesto
- ✦ — usa cfg/topologia condivisa dal modulo padre (vedi MVP_DELIVERY.md per dettagli)

---

## Deliverable Standard per Modulo LAB

| File | Descrizione |
|------|-------------|
| `README.md` | Metadati, checklist deliverable, note |
| `workbook.md` | Workbook studenti (8 sezioni standard) |
| `slide.pptx` | Slide teoria (generare da `TEMPLATE/master_slide.pptx`) |
| `cfg/` | File cfg IOS per TFTP (`copy tftp://192.168.122.1/ENCOR/MOD-nn/...`) |
| `soluzione.md` | Configurazioni complete commentate (solo docente) |

## Deliverable Standard per Modulo TEORIA

| File | Descrizione |
|------|-------------|
| `README.md` | Metadati, checklist deliverable |
| `note_docente.md` | Outline slide, script docente |
| `slide.pptx` | Slide teoria (generare da template) |

---

## Archivi Originali

Le cartelle `_ARCHIVIO_LABxx/` contengono il materiale originale prodotto per la classe Mar–Mag 2026.
Non modificare — riferimento storico per estrarre contenuti durante la standardizzazione.

| Archivio | MOD sorgente |
|----------|--------------|
| `_ARCHIVIO_LAB01/` | MOD-01, 02, 03 (vuota — file spostati) |
| `_ARCHIVIO_LAB03/` | MOD-05, 06 (vuota — file spostati) |
| `_ARCHIVIO_LAB04/` | MOD-10, 11, 12 (vuota — file spostati) |
| `_ARCHIVIO_LAB06/` | MOD-17, 18, 19, 20 (vuota — file spostati) |
| `_ARCHIVIO_LAB07/` | MOD-13–16, 26, 31 (vuota — file spostati) |
| `_ARCHIVIO_LAB09/` | MOD-28, 29, 30 (vuota — file spostati) |
| `_ARCHIVIO_LAB10/` | MOD-32–35 (vuota — file spostati) |