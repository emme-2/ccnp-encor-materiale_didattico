# MVP DELIVERY — Materiale CCNP ENCOR 350-401

> Prodotto: 2026-05-14 · Versione: 1.0-MVP

---

## Tabella Stato Moduli

| MOD | Titolo | Area | Workbook | Soluzione | Cfg | Pronto |
|-----|--------|------|:--------:|:---------:|:---:|:------:|
| MOD-01 | OSPFv2 Fondamenta | Routing | ✅ | ✅ | ✅ | ✅ |
| MOD-02 | OSPFv2 Aree & Summarization | Routing | ✅ | ✅ | ✅ | ✅ |
| MOD-03 | OSPFv3 Dual-Stack | Routing | ✅ | ✅ | ✅ | ✅ |
| MOD-04 | OSPF Troubleshooting | Routing | ✅ | ✅ | ✅ | ✅ |
| MOD-05 | BGP Fondamenta | Routing | ✅ | ✅ | ✅ | ✅ |
| MOD-06 | BGP Traffic Engineering | Routing | ✅ | ✅ | ✅ | ✅ |
| MOD-07 | BGP Route Reflector & IPv6 BGP | Routing | ⬜ | ⬜ | ⬜ | ❌ |
| MOD-08 | Route Manipulation & PBR | Routing | ⬜ | ⬜ | ⬜ | ❌ |
| MOD-09 | Redistribuzione & Loop Prevention | Routing | ⬜ | ⬜ | ⬜ | ❌ |
| MOD-10 | MPLS LDP & Fondamenta | MPLS | ✅ | ✅ | ✅ | ✅ |
| MOD-11 | MPLS L3VPN | MPLS | ✅ | ✅ | ✅ | ✅ |
| MOD-12 | MPLS L2VPN (AToM) | MPLS | ✅ | ✅ | ✅ | ✅ |
| MOD-13 | EtherChannel LACP | Layer 2 | ✅ | ✅ | ✅ | ✅ |
| MOD-14 | Spanning Tree RSTP/MST | Layer 2 | ✅ | ✅ | ✅ | ✅ |
| MOD-15 | FHRP: HSRP, VRRP & GLBP | FHRP | ✅ | ✅ | ✅ | ✅ |
| MOD-16 | IP SLA, SPAN & RSPAN | Assurance | ✅ | ✅ | ✅ | ✅ |
| MOD-17 | VRF-Lite & GRE Tunneling | VPN | ✅ | ✅ | ✅ | ✅ |
| MOD-18 | IPSec IKEv2 (VTI) | VPN | ✅ | ✅ | ✅² | ✅ |
| MOD-19 | DMVPN Phase 1/2/3 | VPN | ✅ | ✅ | ✅² | ✅ |
| MOD-20 | LISP, VXLAN & SD-Access | Arch. | n/a | n/a | n/a | ✅ |
| MOD-21 | SD-WAN | SD-WAN | ⬜ | ⬜ | n/a | ❌ |
| MOD-22 | SD-Access | SD-Access | ⬜ | ⬜ | n/a | ❌ |
| MOD-23 | Wireless RF & Fondamenta | Wireless | ⬜ | ⬜ | n/a | ❌ |
| MOD-24 | Wireless Deployment & WLC | Wireless | ⬜ | ⬜ | n/a | ❌ |
| MOD-25 | Wireless Security | Wireless | ⬜ | ⬜ | n/a | ❌ |
| MOD-26 | QoS MQC & CoPP | QoS | ✅ | ✅ | ✅ | ✅ |
| MOD-27 | NAT, PAT & NTP | IP Services | ⬜ | ⬜ | ⬜ | ❌ |
| MOD-28 | Multicast PIM & Auto-RP | Multicast | ✅ | ✅ | ✅ | ✅ |
| MOD-29 | NetFlow & SNMP | Assurance | ✅ | ✅ | ✅ | ✅ |
| MOD-30 | AAA & RADIUS | Security | ⬜ | ⬜ | n/a | ❌ |
| MOD-31 | ACL, CoPP & Infrastructure Sec. | Security | ⬜ | ⬜ | ⬜ | ❌ |
| MOD-32 | EEM & Python Base | Automation | ✅ | ✅ | n/a | ✅ |
| MOD-33 | Netmiko & Nornir | Automation | ✅ | ✅ | n/a | ✅ |
| MOD-34 | Ansible & Git | Automation | ✅ | ✅ | n/a | ✅ |
| MOD-35 | RESTCONF/NETCONF (Teoria) | Automation | n/a | n/a | n/a | ✅ |

**Legenda:** ✅ presente · ⬜ mancante · ⚠️ parziale · ❌ non sviluppato · n/a non applicabile  
¹ Cfg dedicati in `MOD-xx/cfg/` — contengono lo stato cumulativo dei lab precedenti (ogni modulo include le config dei moduli che lo precedono nella sequenza)  
² Usa cfg iniziali da `MOD-17/cfg/` come punto di partenza — indicato esplicitamente nel workbook

---

## Moduli Consegnabili MVP — 23 moduli

Pronti per consegna immediata agli studenti (workbook + soluzione + cfg):

| MOD | Titolo | Cfg disponibili |
|-----|--------|-----------------|
| **MOD-01** | OSPFv2 Fondamenta | `MOD-01/cfg/` — r1-cfg … r7-cfg |
| **MOD-02** | OSPFv2 Aree & Summarization | `MOD-02/cfg/` — r1-cfg … r7-cfg |
| **MOD-03** | OSPFv3 Dual-Stack | `MOD-03/cfg/` — r1-cfg … r6-cfg |
| **MOD-05** | BGP Fondamenta | `MOD-05/cfg/` — r1-cfg … r6-cfg |
| **MOD-06** | BGP Traffic Engineering | `MOD-06/cfg/` — r1-cfg … r6-cfg |
| **MOD-10** | MPLS LDP & Fondamenta | `MOD-10/cfg/` — pe1-cfg · p1-cfg · p2-cfg · pe2-cfg |
| **MOD-11** | MPLS L3VPN | `MOD-11/cfg/` — pe1-cfg · p1-cfg · p2-cfg · pe2-cfg · ce1-cfg · ce2-cfg |
| **MOD-12** | MPLS L2VPN (AToM) | `MOD-12/cfg/` — pe1-cfg · p1-cfg · p2-cfg · pe2-cfg · ce1-cfg · ce2-cfg |
| **MOD-13** | EtherChannel LACP | `MOD-13/cfg/` — r1-cfg · sw1-cfg · sw2-cfg |
| **MOD-14** | Spanning Tree RSTP/MST | `MOD-14/cfg/` — sw1-cfg · sw2-cfg (Po1 pre-conf) |
| **MOD-15** | FHRP: HSRP, VRRP & GLBP | `MOD-15/cfg/` — sw1-cfg · sw2-cfg · r1-cfg (Po1+STP pre-conf) |
| **MOD-16** | IP SLA, SPAN & RSPAN | `MOD-16/cfg/` — sw1-cfg · sw2-cfg (Po1+STP+HSRP pre-conf) |
| **MOD-17** | VRF-Lite & GRE Tunneling | `MOD-17/cfg/` — hub-cfg · isp-cfg · sp1-cfg · sp2-cfg |
| **MOD-18** | IPSec IKEv2 (VTI) | cfg di partenza da `MOD-17/cfg/` (indicato nel workbook) |
| **MOD-19** | DMVPN Phase 1/2/3 | cfg di partenza da `MOD-17/cfg/` (indicato nel workbook) |
| **MOD-20** | LISP, VXLAN & SD-Access | solo teoria — note_docente.md completo (18 slide) |
| **MOD-26** | QoS MQC & CoPP | `MOD-26/cfg/` — r1-cfg |
| **MOD-28** | Multicast PIM & Auto-RP | `MOD-28/cfg/` — r1-cfg … r5-cfg |
| **MOD-29** | NetFlow & SNMP | `MOD-29/cfg/` — r1-cfg … r5-cfg |
| **MOD-32** | EEM & Python Base | automation — nessun cfg IOU necessario |
| **MOD-33** | Netmiko & Nornir | automation — nessun cfg IOU necessario |
| **MOD-34** | Ansible & Git | automation — nessun cfg IOU necessario |
| **MOD-35** | RESTCONF/NETCONF | solo teoria — note_docente.md completo (21 slide) |

---

## ✅ COMPLETO — MOD-04 (completato 2026-05-16)

| MOD | Titolo | Cfg | Soluzione | Note |
|-----|--------|-----|-----------|------|
| **MOD-04** | OSPF Troubleshooting | r1–r5-cfg | soluzione.md | 9 errori intenzionali distribuiti su R1/R2/R3/R4; 11 task su scenari A/B/C/D; OSPFv3 su R1–R3 |

### DECISION LOG — Scelte topologiche MOD-04

**Topologia (5 router, 5 link P2P):**
- Area 0: R1, R2, R3 (backbone core) + R4 loopback
- Area 1: link R3-R4 (area transit per virtual-link)
- Area 2: link R4-R5 (stub area)
- R4 è ABR triple: Area 0 / Area 1 / Area 2
- Errori distribuiti su segmenti diversi per coprire tutti i casi di neighbor failure
- R5 non ha errori: il network type mismatch si manifesta su R4 (broadcast) vs R5 (P2P)
- Virtual-link non pre-configurato: T6 è un "implement + debug" task guidato
- OSPFv3 su R1-R2-R3 (Area 0) — R2 e R3 con errori per T10/T11
- Redistribuzione su R3 (E1/E2) + R4 (rotta in stub area) per T7/T8
- Chiave MD5 corretta su R4, errata su R1: l'errore è sul lato che lo studente controlla per primo

---

## ✅ COMPLETO — MOD-01/02/03/05/06 (completati 2026-05-14)

| MOD | Titolo | Cfg | Soluzione | Note |
|-----|--------|-----|-----------|------|
| **MOD-01** | OSPFv2 Fondamenta | r1–r7-cfg | soluzione.md | Misconfig intenzionali su R4 (area 1) e R5 (MD5 key errata) |
| **MOD-02** | OSPFv2 Aree & Summarization | r1–r7-cfg | soluzione.md | Stato finale MOD-01 come partenza |
| **MOD-03** | OSPFv3 Dual-Stack | r1–r6-cfg | soluzione.md | OSPFv2+IPv6 addr precfg; OSPFv3 da configurare |
| **MOD-05** | BGP Fondamenta | r1–r6-cfg | soluzione.md | eBGP R3↔R5 intenzionalmente mancante (task T3) |
| **MOD-06** | BGP Traffic Engineering | r1–r6-cfg | soluzione.md | Stato finale MOD-05 come partenza; nessun TE preconfigurato |

### DECISION LOG — Scelte topologiche

**MOD-01/02/03 (topologia OSPF — 7 router):**
- AS: nessuno (pure OSPF, no BGP)
- Router-ID convention: `x.x.x.x` (R1=1.1.1.1 … R7=7.7.7.7)
- Sub-interface VLAN scheme: 4x = R4 side, 5x = R5 side (es. VLAN 45 = link R4-R5)
- Area backbone: Area 0 (R3/R4/R5/R6 core ring)
- Area 15: stub, ABR=R5, IR=R1 (loopbacks Lo15, Lo150, Lo151, Lo152)
- Area 25: totally-stub, ABR=R5, IR=R2 (loopbacks Lo25)
- Area 99: ASBR redistribute su R3 (rotte statiche 172.16.x.x/28)
- Virtual-link: attraverso Area 15 (R1 ↔ R5)
- MOD-01 cfg: R3 senza OSPF (studente configura T1); R4 con area 1 sbagliata; R5 con MD5 key errata
- MOD-02 cfg: stato finale MOD-01 (OSPF Area 0 completo su tutti i 7 router)
- MOD-03 cfg: IPv4 OSPFv2 + indirizzi IPv6 su sub-interface; nessun OSPFv3 preconfigurato

**MOD-05/06 (topologia BGP — 6 router, 2 AS):**
- AS 65001: ISP (R1, R2, R3) — OSPF 1 + iBGP full-mesh preconfigurati
- AS 65000: Customer (R4, R5, R6) — OSPF 1 da configurare (T1); iBGP da configurare (T2)
- eBGP link primario: R1↔R4 via VLAN 14 (172.16.14.0/30) — preconfigurato su R4 in MOD-05
- eBGP link secondario: R3↔R5 via VLAN 35 (172.16.35.0/30) — intenzionalmente mancante in MOD-05 (task T3)
- Customer interni: 192.168.45.0/30 (R4-R5), 192.168.46.0/30 (R4-R6), 192.168.56.0/30 (R5-R6)
- BGP network statements in MOD-06 starting state: R4 annuncia 4.4.4.4/32 e 192.168.45.0/30
- MOD-06 cfg: nessuna route-map / prefix-list / community / local-pref — studente configura il TE

---

## Esclusi dalla Consegna MVP

Moduli al momento non sviluppati (solo struttura placeholder):

| MOD | Titolo | Motivazione |
|-----|--------|-------------|
| ~~MOD-04~~ | ~~OSPF Troubleshooting~~ | ✅ Completato 2026-05-16 |
| MOD-07 | BGP Route Reflector | Nessun sorgente; dipende da completamento MOD-05/06 |
| MOD-08 | Route Manipulation & PBR | Gap critico syllabus — 0% materiale; alta priorità roadmap |
| MOD-09 | Redistribuzione | Dipende da MOD-05/07/08; sviluppo successivo |
| MOD-21 | SD-WAN | Solo demo dCloud; nessun lab GNS3 possibile |
| MOD-22 | SD-Access | Solo demo dCloud; coperto parzialmente in MOD-20 |
| MOD-23 | Wireless RF | Richiede hardware reale o emulatore; assente dal corso 2026 |
| MOD-24 | Wireless Deployment | Come MOD-23 |
| MOD-25 | Wireless Security | Come MOD-23 |
| MOD-27 | NAT, PAT & NTP | Menzionati nel gap analysis; sviluppo da schedulare |
| MOD-30 | AAA & RADIUS | Bonus in LAB09; richiede container FreeRADIUS dedicato |
| MOD-31 | ACL & Infrastructure Sec. | Gap critico syllabus; dipende da topologia dedicata |

---

## Nota per gli Studenti

> **Pacchetto Materiale Didattico — CCNP ENCOR 350-401**
>
> Questo pacchetto contiene il materiale di laboratorio per il corso di certificazione
> Cisco CCNP ENCOR 350-401.
>
> **Come usare i workbook:**
>
> - Ogni modulo è autonomo: contiene teoria, istruzioni operative e verifica
> - Le configurazioni iniziali si caricano via TFTP:
>   ```
>   Router# copy tftp: running-config
>   Address or name of remote host? 192.168.122.1
>   Source filename? ENCOR/MOD-xx/device-cfg
>   ```
> - Il path TFTP esatto è indicato nella sezione **3 — LAB SETUP** di ogni workbook
> - Leggi sempre la sezione **TEORIA** prima di iniziare i task: spiega il *perché*
>   prima del *come*
> - Usa i comandi di **VERIFICA** dopo ogni task per confermare il risultato atteso
> - In caso di problemi consulta la **TROUBLESHOOTING GUIDE** prima di chiedere aiuto
>
> **Ambiente lab:**
>
> - Piattaforma: GNS3 con IOU L2 (switch) e IOU L3 (router)
> - I link logici sono sub-interfacce 802.1Q su `e0/0` — **non modificare** le
>   sub-interfacce di management
> - Server TFTP: `192.168.122.1` — accessibile dalla rete di management GNS3
> - Servizi esterni (FreeRADIUS, ntopng): container sulla VM GNS3 —
>   indirizzo `192.168.122.x` come indicato nel workbook
>
> **Note sui moduli:**
>
> - I moduli contrassegnati come *solo teoria* (MOD-20, MOD-35) non hanno
>   configurazioni lab: il docente mostrerà le demo live
> - MOD-01, MOD-02, MOD-03, MOD-05, MOD-06 sono completi: workbook + cfg + soluzione disponibili
> - I moduli di automation (MOD-32–34) richiedono Python 3.x e Ansible installati
>   sulla VM GNS3 — verificare con il docente prima di iniziare
