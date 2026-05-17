# MAPPATURA LAB — CCNP ENCOR 350-401
Generato: 2026-05-12 | Aggiornato: 2026-05-17 | Riferimento programma: CCNP_ENCOR_Programma_v2.docx (v1.2, 11 sessioni · 43h · Mar–Mag 2026)

> **Uniformazione Fase 2 completata 2026-05-17:** tutti i workbook LAB (MOD-01÷MOD-19, MOD-26÷MOD-31) aggiornati con topologie Mermaid, cfg inline e nota piattaforme. Anomalie residue: MOD-18/MOD-19 senza cfg standalone propri (vedi QA_REPORT.md BLK-01/02).

---

## Sezione 1 — Inventario LAB Attuali

| LAB | Sessione programma | Topic principale | Sotto-argomenti | Codici syllabus | File presenti | Stato |
|-----|--------------------|-----------------|-----------------|-----------------|---------------|-------|
| **LAB01** | S1 · Ven 13 Mar | OSPFv2 Multi-Area & OSPFv3 Dual-Stack | Multi-area (0,15,25,99) · DR/BDR · ABR summarization · stub/totally-stub · virtual-link · OSPFv3 native IPv6 · OSPFv3 Address Families (dual-stack) | 3.2.a · 3.2.b | `LAB01_OSPF_ENCOR.docx` (workbook) · `Script_Docente_Sessione1_OSPF.docx` | **PARZIALE** — mancano: cfg TFTP · slide · soluzione commentata |
| *(nessuna cartella)* | S2 · Ven 20 Mar | OSPF Troubleshooting Avanzato | Neighbor failure diagnostics · virtual-link · path preference · convergenza | 1.10.a–d | — | **DA SVILUPPARE** — nessun materiale studente |
| **LAB03** | S3 · Mer 1 Apr | BGP Configurazione & Traffic Engineering | iBGP full-mesh · eBGP dual-peering · network stmt vs redistribute (Origin i vs ?) · route-map · prefix-list · Local Preference · AS-Path Prepend · Community · soft-reconfiguration inbound · default route (2 metodi) | 3.2.c · 1.11.a–e | `LAB03_BGP_ENCOR.docx` (workbook) · `Script_Docente_Sessione3_BGP.docx` | **PARZIALE** — mancano: cfg TFTP · slide · soluzione commentata |
| *(nessuna cartella)* | S4 · Ven 10 Apr | Route Manipulation, PBR & Redistribuzione | Redistribuzione OSPF↔EIGRP · tagging anti-loop · Policy-Based Routing | 1.2–1.6 · 3.2.d | — | **DA SVILUPPARE** — nessun materiale |
| **LAB04** | S5 · Mer 15 Apr | MPLS Fondamenta, L3VPN & L2VPN | LDP (FEC/LIB/LFIB/PHP) · MP-BGP per VPNv4 · L3VPN (VRF/RD/RT/CE-PE eBGP) · L2VPN xconnect pseudowire | 2.1 · 2.2 *(extra)* | `LAB04_MPLS.docx` (workbook) · `LAB04_Soluzione_Commentata.docx` | **PARZIALE** — mancano: cfg TFTP · slide (6 router: PE1, P1, P2, PE2, CE1, CE2) |
| **LAB06** | S6+S7 · 16-21 Apr | Virtualizzazione & Overlay | VRF definition · GRE P2P (VRF-aware) · IKEv2 proposal/policy/keyring/profile · IPSec VTI (tunnel protection) · DMVPN Phase 1 & Phase 2 · Named EIGRP VRF-aware · LISP (teoria) · VXLAN (teoria) | 2.1 · 2.2 · 2.3 | `hub-cfg` · `isp-cfg` · `sp1-cfg` · `sp2-cfg` · `LAB06_cfgs.zip` · `S06_Workbook_Studenti_v2.docx` · `S06_Workbook_Studenti.docx` (v1) · `S06_Soluzione_Commentata.docx` · `S06_Guida_Docente.docx` · `S06_Slide_Studenti.pptx` | **COMPLETO** ✅ — il materiale più completo del corso |
| **LAB07** | *(S8 · Lun 27 Apr)* ⚠️ | Layer 2 · FHRP · IP SLA · SPAN · QoS MQC · CoPP | EtherChannel LACP · STP tuning/protezione (PortFast, BPDU Guard, Root Guard) · HSRP v2 · IP SLA + Object Tracking · failover live · Local SPAN · RSPAN cross-switch · ERSPAN (teoria) · QoS MQC (classificazione/marking/LLQ/policing/shaping) · CoPP | 3.1.a · 3.1.b · 3.1.c · 3.4.c · 4.3 · 4.4 · 1.5.a/b · 5.2.b | `ENCOR_S7_Workbook_Studenti-v2.docx` · `ENCOR_S7_Workbook_Studenti.docx` (v1) · `ENCOR_S7_Slide_Teoria-v2.pptx` · `ENCOR_S7_Slide_Teoria.pptx` (v1) · `ENCOR_S7_Soluzione_Commentata-v2.docx` · `ENCOR_S7_Soluzione_Commentata.docx` (v1) · `r1-cfg` · `sw1-cfg` · `sw2-cfg` | **COMPLETO** ✅ — workbook + slide + soluzione + cfg tutti in v2 |
| *(nessuna cartella LAB08)* | S8 nel programma | — | — | — | — | Cartella assente; il contenuto S8 è in LAB07 (anomalia naming) |
| **LAB09** | S9 · Mer 6 Mag | IP Services & Network Assurance | PIM Dense Mode (flood-and-prune) · PIM Sparse Mode · RP statico · Auto-RP (Candidate RP + Mapping Agent) · IGMP join-group · Flexible NetFlow v5 (bonus) · AAA RADIUS + fallback locale (bonus extra) | 3.3 · 4.1–4.6 | `ENCOR_S9_Workbook_Studenti-v2.docx` · `ENCOR_S9_Workbook_Studenti.docx` (v1) · `ENCOR_S9_Slide_Teoria v2.pptx` · `ENCOR_S9_Slide_Teoria.pptx` (v1) · `r1-cfg` · `r2-cfg` · `r3-cfg` · `r4-cfg` · `r5-cfg` | **PARZIALE** — manca soluzione commentata |
| *(nessuna cartella LAB10/S10)* | S10 · Ven 8 Mag | Security | CoPP · AAA/FreeRADIUS · NGFW/TrustSec/MACsec (teoria) | 5.1 · 5.2 · 5.3 · 5.4 | — (CoPP in LAB07 T10; AAA bonus in LAB09 T10) | **DA SVILUPPARE** — no lab dedicato |
| **LAB10** | S11 · Mar 12 Mag | Automation & Programmability | EEM Applet · Python base + JSON · Netmiko · Nornir · Ansible (cisco.ios collection) · venv/pip · Git · RESTCONF (teoria, no IOU) | 6.1–6.7 | `ENCOR_LAB10_Workbook_Studenti.docx` · `ENCOR_LAB10_Slide_Teoriche.pptx` · `ENCOR_LAB10_Soluzione_Commentata.docx` · `ENCOR-LAB10-repo.zip` | **COMPLETO** ✅ — workbook + slide + soluzione + repo zip |

---

## Sezione 2 — Proposta Moduli Standard

Criteri applicati:
- LAB06 (4 parti distinte su 2 sessioni) → split in 2 moduli autonomi
- LAB07 (5 aree tematiche, 11 task, >3h) → split in 3 moduli
- LAB09 (multicast + NetFlow/AAA bonus) → split in 2 moduli
- LAB01, LAB03, LAB04, LAB10 → 1 modulo ciascuno
- Sessioni S2 e S4 senza materiale → moduli DA SVILUPPARE

| MOD | Nome Modulo | Topic coperti | Codici syllabus | LAB sorgente | Ore stimate | Stato deliverable |
|-----|-------------|--------------|-----------------|--------------|-------------|-------------------|
| **MOD-01** | OSPFv2 Fondamenta | Sub-interface 802.1Q · OSPF processo/Router-ID · DR/BDR election · network type P2P · troubleshooting adiacenze (3 misconfig) · costo | 3.2.a · 3.2.b | LAB01 (split) | 2h | Workbook ✅ · Script docente ✅ · Cfg ❌ · Slide ❌ · Soluzione ❌ |
| **MOD-02** | OSPFv2 Aree & Summarization | ABR multi-area · area range · stub/totally-stub · virtual link · ASBR redistribuzione e summary-address | 3.2.a · 3.2.b | LAB01 (split) | 2h | Workbook ✅ · Cfg ❌ · Slide ❌ · Soluzione ❌ |
| **MOD-03** | OSPFv3 Dual-Stack | OSPFv3 native IPv6 (no network cmd) · link-local · LSA Type 8/9 · summarization IPv6 · OSPFv3 Address Families (IPv4+IPv6) | 3.2.b | LAB01 (split) | 1.5h | Workbook ✅ · Cfg ❌ · Slide ❌ · Soluzione ❌ |
| **MOD-05** | BGP Fondamenta | iBGP full-mesh · eBGP dual-peering · network stmt vs redistribute (Origin i vs ?) · route-map · prefix-list · soft-reconfiguration inbound | 3.2.c · 1.11.a · 1.11.b | LAB03 | 2h | Workbook ✅ · Cfg ❌ · Slide ❌ · Soluzione ❌ |
| **MOD-06** | BGP Traffic Engineering | Default route (2 metodi) · Local Preference · AS-Path Prepend · BGP Community | 1.11.c · 1.11.d · 1.11.e | LAB03 | 2h | Workbook ✅ · Cfg ❌ · Slide ❌ · Soluzione ❌ |
| **MOD-04** | Route Manipulation, PBR & Redistribuzione | Redistribuzione OSPF↔EIGRP · tagging anti-loop · Policy-Based Routing | 3.2.d · 1.2–1.6 | *(da sviluppare)* | 4h | Tutto DA SVILUPPARE |
| **MOD-05** | MPLS — LDP, L3VPN & L2VPN | LDP backbone · MP-BGP VPNv4 · L3VPN (VRF/RD/RT) · L2VPN xconnect pseudowire | 2.1 · 2.2 | LAB04 | 4h | Workbook ✅ · Soluzione ✅ · Cfg ❌ · Slide ❌ |
| **MOD-06** | Virtualizzazione — VRF, GRE & IPSec IKEv2 | VRF definition · GRE P2P VRF-aware · IKEv2 · IPSec VTI (tunnel protection) | 2.2 · 2.3 | LAB06 (Parts 1–4) | 4h | Workbook ✅ · Soluzione ✅ · Cfg ✅ · Slide ✅ · Guida docente ✅ |
| **MOD-07** | DMVPN Phase 1 & Phase 2 + Named EIGRP | mGRE · NHRP · DMVPN Hub-and-Spoke · DMVPN Spoke-to-Spoke · Named EIGRP VRF-aware | 2.2 · 2.3 | LAB06 (Parts 5–6) | 4h | Workbook ✅ · Soluzione ✅ · Cfg ✅ · Slide ✅ |
| **MOD-08** | Layer 2 — EtherChannel LACP & STP | EtherChannel LACP (active/passive) · STP root/sec · PortFast · BPDU Guard · Root Guard | 3.1.a · 3.1.b · 3.1.c | LAB07 (T1–T2) | 2h | Workbook ✅ · Soluzione ✅ · Cfg ✅ · Slide ✅ |
| **MOD-09** | FHRP, IP SLA & SPAN | HSRP v2 · IP SLA + Object Tracking · failover live · Local SPAN · RSPAN · ERSPAN (teoria) | 3.4.c · 4.3 · 4.4 | LAB07 (T3–T7) | 3h | Workbook ✅ · Soluzione ✅ · Cfg ✅ · Slide ✅ |
| **MOD-10** | QoS MQC & CoPP | Classificazione/marking · DSCP · LLQ · policing · shaping · Control Plane Policing | 1.5.a · 1.5.b · 5.2.b | LAB07 (T9–T10) | 2h | Workbook ✅ · Soluzione ✅ · Cfg ✅ · Slide ✅ |
| **MOD-11** | IP Multicast — PIM & Auto-RP | PIM-DM (flood-and-prune) · PIM-SM · RP statico · Auto-RP (Candidate RP + Mapping Agent) · IGMP | 3.3.a · 3.3.b | LAB09 (T1–T8) | 3h | Workbook ✅ · Slide ✅ · Cfg ✅ · Soluzione ✅ (parziale, espansione in corso) |
| **MOD-12** | Network Assurance — NetFlow & Tools | Flexible NetFlow v5: Flow Record/Monitor/Exporter · SNMPv2c · SNMPv3 · Catalyst Center (teoria) | 4.1–4.6 | LAB09 (T9–BONUS) | 2h | Workbook ✅ · Slide ✅ · Cfg ✅ · Soluzione ✅ (parziale, espansione in corso) |
| **MOD-13** | Security — AAA, CoPP & Feature Security | AAA locale + RADIUS/FreeRADIUS · CoPP *(v. MOD-10)* · NGFW/TrustSec/MACsec (teoria) · REST API security | 5.1 · 5.2 · 5.3 · 5.4 | LAB09 T10 + LAB07 T10 + *(da sviluppare)* | 4h | Parzialmente in LAB07/LAB09 · Lab dedicato DA SVILUPPARE |
| **MOD-14** | Automation & Programmability | EEM Applet · Python base · Netmiko · Nornir · Ansible cisco.ios · JSON · Git · RESTCONF (teoria) | 6.1–6.7 | LAB10 | 3.5h | Workbook ✅ · Slide ✅ · Soluzione ✅ · Repo ✅ |
| **MOD-32** | EEM & Python Base | EEM Applet (syslog/timer events, action cli/syslog) · Python venv/pip · json module (load/loads/dump/dumps) · Paramiko backup | 6.1 · 6.2 · 6.6 | LAB10 (split standardizzato) | 2h | Workbook ✅ · Soluzione ✅ · Cfg ❌ · Slide ❌ |
| **MOD-33** | Netmiko & Nornir | Netmiko ConnectHandler · send_command · send_config_set · exception handling · Nornir InitNornir · inventory YAML · nr.run() · F() filter | 6.2 · 6.3 | LAB10 (split standardizzato) | 2h | Workbook ✅ · Soluzione ✅ · Cfg ❌ · Slide ❌ |
| **MOD-34** | Ansible & Git | Ansible agentless · inventory INI · ios_command · ios_config · ios_facts · idempotency · Git init/add/commit/push/branch workflow | 6.7 | LAB10 (split standardizzato) | 2h | Workbook ✅ · Soluzione ✅ · Cfg ❌ · Slide ❌ |
| **MOD-35** | API & RESTCONF (TEORIA) | REST API fundamentals · Auth Basic/Token/OAuth 2.0 · DNA Center API · YANG · RESTCONF RFC 8040 · NETCONF vs RESTCONF vs SNMP | 6.4 · 6.5 | LAB10 (teoria) | 1.5h | Note docente ✅ · Slide (outline in note_docente.md) ❌ |

**Totale ore stimate:** 55h su 18 moduli — aggiornato 2026-05-14 con MOD-32/33/34/35

---

## Sezione 3 — Gap Analysis

Argomenti del syllabus ENCOR 350-401 non coperti (o coperti solo teoricamente) da nessun LAB pratico esistente.

| Codice | Argomento | Tipo gap | Sessione riferimento | Note |
|--------|-----------|----------|----------------------|------|
| 1.1 | Enterprise network design principles (2-tier/3-tier, spine-leaf, campus) | Lab assente | — | Argomento teorico, non necessita lab pratico |
| 1.2 *(WLAN)* | WLAN deployment design: AP placement, RF coverage, channel planning | **Lab assente** | — | Nessuna sessione wireless nel programma attuale |
| 1.3 | On-premises vs cloud infrastructure | Lab assente | — | Teorico; eventuale demo dCloud |
| **1.4** | **SD-WAN** (Cisco vManage, vBond, vSmart, vEdge) | **Demo dCloud** | — | Nessun lab GNS3 possibile · demo dCloud come fallback |
| **1.5** | **SD-Access** (Cisco DNA/Catalyst Center, LISP, VXLAN) | **Demo dCloud** | — | Nessun lab GNS3 · LISP/VXLAN già solo teoria in LAB06 |
| 1.7 | Hardware vs software switching (CEF, Cisco Express Forwarding) | Lab assente | — | Teoria; verificabile con `show ip cef` in lab esistenti |
| **1.10.a–d** | **OSPF Troubleshooting** (neighbor failure, adjacency types, path preference) | **Workbook assente** | S2 | Script docente esiste (LAB01) ma no workbook studenti, no cfg, no soluzione |
| **1.11.f–g** | BGP: IPv6 BGP (MP-BGP IPv6 AF), route reflection | **Parzialmente assente** | S3 | LAB03 copre iBGP full-mesh ma non route reflector né IPv6 BGP |
| **3.2.d + 1.2–1.6** | **Redistribuzione OSPF↔EIGRP, tagging anti-loop, PBR** | **Lab completamente assente** | S4 | Nessun materiale; tema critico per l'esame |
| **3.3 Wireless** | 802.11 standards · CAPWAP · AP operating modes · WLC config · wireless roaming · RF fundamentals | **Completamente assente** | — | Nessuna sessione wireless nel corso; richiede hardware reale o simulatore dedicato (EVE-NG/emulato) |
| 3.3 *(wireless security)* | WPA2/WPA3 · 802.1X wireless · PSK vs Enterprise | **Assente** | S10 | Parte del dominio wireless mancante |
| 3.4.a–b | VRRP · GLBP (First Hop Redundancy) | **Parzialmente assente** | S8 | LAB07 copre solo HSRP; VRRP e GLBP non inclusi |
| **4.2** | **NETCONF** (YANG model, `<get>`, `<edit-config>`) | **Assente (teorico)** | S11 | Non disponibile su IOU; solo RESTCONF/teoria in LAB10 |
| 4.5 | Cisco DNA/Catalyst Center workflows (device discovery, provisioning) | Assente | S9 | Teoria slide; no hands-on |
| **5.3** | REST API security (OAuth, token, TLS) | **Assente** | S10 | Non sviluppato; accennato in LAB10 automation |
| 5.4 | Wireless security features (802.1X, RADIUS wireless, WPA3) | **Assente** | S10 | Dipende dalla copertura wireless mancante |
| **NAT** | Network Address Translation (static, PAT, NAT overload) | **Non menzionato** | — | Argomento d'esame; non compare in nessuna sessione |
| **NTP** | Network Time Protocol (NTP server/client, authentication) | **Non menzionato** | — | Tipicamente in IP Services; assente da tutti i lab |
| **SNMP** | SNMPv2c/v3 (community, trap, inform) | **Non menzionato** | — | 4.6 nei codici S9 ma non sviluppato nel workbook LAB09 |

**Priorità sviluppo** (impatto esame):
1. 🔴 **Route Manipulation / PBR / Redistribuzione** (S4) — topic core, 0% copertura
2. 🔴 **OSPF Troubleshooting** (S2) — tema di peso, solo script docente
3. 🟠 **Wireless** — 15–20% del peso esame, completamente assente
4. 🟠 **Security lab dedicato** (S10) — CoPP e AAA sparsi, no lab integrato
5. 🟡 **NAT / NTP / SNMP** — topic frequenti nelle domande, non inclusi
6. 🟡 **VRRP / GLBP** — HSRP già coperto; aggiunta rapida a MOD-09

---

## Sezione 4 — Note e Raccomandazioni

### A. Anomalie di Nomenclatura

| Anomalia | Descrizione | Impatto | Azione raccomandata |
|----------|-------------|---------|---------------------|
| **LAB07 ≠ S7** | La cartella LAB07 contiene materiale per S8 (EtherChannel, HSRP, QoS). Internamente il workbook si chiama "Sessione 7". | Confusione nella mappatura sessione↔cartella | Rinominare in **LAB08** (o aggiungere indicazione S8 nel nome file) al momento della standardizzazione |
| **LAB10 ≠ S10** | Cartella LAB10 = Sessione 11 (Automation). Sessione 10 (Security) non ha cartella. I file interni fanno riferimento a ENCOR-LAB11. | Gap non evidente dallo struttura cartelle | Rinominare in **LAB11** e creare **LAB10** vuoto per Security |
| **Salto numerico LAB** | Mancano LAB02, LAB05, LAB08 (nel gap); presenti LAB01, LAB03, LAB04, LAB06, LAB07, LAB09, LAB10 | La numerazione non è progressiva né allineata alle sessioni | Decidere: allineamento LABnn=Sn oppure numerazione tematica MOD-nn |

### B. Coesistenza V1/V2 (file duplicati)

Tre cartelle contengono versioni v1 e v2 dello stesso documento:
- **LAB06**: `S06_Workbook_Studenti.docx` (v1) + `S06_Workbook_Studenti_v2.docx` (v2)
- **LAB07**: v1 + v2 per workbook, slide, soluzione (6 file totali)
- **LAB09**: v1 + v2 per workbook e slide (4 file totali)

**Raccomandazione**: nel processo di standardizzazione, mantenere **solo la versione finale** (v2), archiviare o eliminare la v1. Per il materiale standardizzato adottare il suffisso versione solo nel changelog interno (git tag), non nel nome file.

### C. Lacune Specifiche per LAB

| LAB | Deliverable mancanti | Priorità completamento |
|-----|---------------------|------------------------|
| LAB01 | Cfg TFTP (R1–R7) · Slide teoria · Soluzione commentata | 🟠 Alta (S1 = prima sessione) |
| LAB03 | Cfg TFTP (R1–R6) · Slide teoria · Soluzione commentata | 🟠 Alta (BGP è topic critico) |
| LAB04 | Cfg TFTP (PE1/P1/P2/PE2/CE1/CE2) · Slide teoria | 🟡 Media |
| LAB09 | Soluzione commentata | 🟡 Media |

### D. CoPP: Topic Duplicato tra Moduli

Il **Control Plane Policing** (codice 5.2.b) è presente in LAB07 Task T10 (QoS MQC deck) ed è anche parte di S10 Security. Al momento della standardizzazione, decidere:
- **Opzione A**: CoPP rimane in MOD-10 (QoS) come task finale, MOD-13 Security fa riferimento incrociato
- **Opzione B**: CoPP si sposta in MOD-13 Security, MOD-10 si limita a QoS MQC

### E. AAA: Topic Duplicato tra Moduli

Il **Task T10** di LAB09 (AAA con RADIUS + fallback locale) è un task bonus che copre parte di S10 (5.1). Al momento della standardizzazione, questo task andrebbe estratto e integrato nel lab Security dedicato (MOD-13) piuttosto che restare come bonus in MOD-11/MOD-12.

### F. LISP e VXLAN

Attualmente in LAB06 workbook v2 sono elencati come topic (nel titolo) ma sviluppati solo come teoria nel deck slide, senza task pratici. La nota operativa in CLAUDE.md è coerente: *"LISP/VXLAN → solo teoria e diagrammi, nessun lab pratico"*. Nel materiale standardizzato, inserire una slide dedicata per ciascuno (Tipo 05 Diagramma + Tipo 04 Teoria Concetto) senza creare task laboratoriali.

### G. RESTCONF in LAB10

LAB10 include RESTCONF come argomento teorico con la nota esplicita che non è disponibile su IOU. Il repo zip include probabilmente script Python/Netmiko/Ansible operativi su IOU. Il materiale standardizzato deve rendere chiaro questo vincolo nella sezione Lab Setup (prerequisiti) di MOD-14.

### H. Stato Svolgimento al 12-05-2026

Secondo il programma v2:
- ● **Svolte** (S1–S7): LAB01, LAB03, LAB04, LAB06 (×2)
- LAB07 corrisponde a S8 (27 Apr) che era indicata come ○ nel documento del 13 Mar — verificare se effettivamente svolta
- ○ **Da svolgere o appena svolte** (S8–S11): LAB07 (S8), LAB09 (S9 · 6 Mag), S10 (8 Mag), LAB10 (S11 · 12 Mag = oggi)

---

*Fine MAPPATURA_LAB.md — aggiornare dopo ogni modifica alla struttura delle cartelle o completamento di un deliverable.*
