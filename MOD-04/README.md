---
modulo: MOD-04
titolo: OSPF Troubleshooting
area: AREA 1 — OSPF
tipo: LAB
codici_syllabus: 1.10.a · 1.10.b · 1.10.c · 1.10.d
ore: 4h
stato: COMPLETO
fonte: sviluppato ex-novo 2026-05-16
---
# MOD-04 — OSPF Troubleshooting

## Deliverable
- [x] workbook.md — 11 task (scenari A/B/C/D), troubleshooting guide, exam tips
- [ ] slide.pptx   _(generare da template master_slide.pptx)_
- [x] cfg/         — r1-cfg · r2-cfg · r3-cfg · r4-cfg · r5-cfg (con errori intenzionali)
- [x] soluzione.md — tabella errori + fix commentati per tutti i task

## Topologia
5 router (R1–R5): Area 0 backbone · Area 1 transit · Area 2 stub  
Link: R1-R2 (VLAN 12) · R2-R3 (VLAN 23) · R1-R4 (VLAN 14) · R3-R4 (VLAN 34) · R4-R5 (VLAN 45)

## Errori Intenzionali nei Cfg
| Scenario | Errore | Router | Task |
|----------|--------|--------|------|
| A | Hello/dead timer mismatch | R1 (hello 10) vs R2 (hello 5) | T1 |
| A | MTU mismatch | R2 ip mtu 1400 su e0/0.23 | T2 |
| A | Area-ID mismatch | R4 e0/0.34 in area 0 invece di area 1 | T3 |
| A | MD5 auth key errata | R1 e0/0.14 ha WRONGPASS | T4 |
| B | Network type mismatch | R4 e0/0.45 broadcast vs R5 P2P | T5 |
| B | Virtual-link (non configurato) | studente configura in T6 | T6 |
| D | ipv6 unicast-routing assente | R2 globale | T10 |
| D | ipv6 ospf area mancante su Lo0 | R3 Loopback0 | T11 |

## Note
- OSPFv3 configurato su R1, parzialmente su R2 (errore T10) e R3 (errore T11)
- Stub area (Area 2): T7 dimostra il blocco Type 5 LSA e l'opzione NSSA
- Rotte E1/E2 pre-configurate su R3 per T8; virtual-link configurato dallo studente in T6