---
modulo: MOD-11
titolo: MPLS L3VPN
area: AREA 4 — MPLS
tipo: LAB
codici_syllabus: 2.2
ore: 2h
stato: COMPLETO
fonte: LAB04 (split)
---
# MOD-11 — MPLS L3VPN

## Deliverable
- [x] workbook.md
- [x] soluzione.md
- [ ] slide.pptx   _(generare da template master_slide.pptx)_
- [x] cfg/         pe1-cfg · p1-cfg · p2-cfg · pe2-cfg · ce1-cfg · ce2-cfg

## Nota cfg
PE1/PE2 hanno MPLS completo ma NESSUNA VRF/BGP (studente li configura).
Interfacce CE pre-configurate con IP globale — la nota "ip vrf forwarding rimuove l'IP"
è il punto pedagogico chiave di T1.
CE1 Lo0=192.168.10.1/24, CE2 Lo0=192.168.20.1/24 (reti da annunciare via BGP).
VRF: CUST_A · RD/RT: 65000:100 · AS Provider: 65000 · AS CE1: 65001 · AS CE2: 65002.