---
modulo: MOD-10
titolo: MPLS LDP & Fondamenta
area: AREA 4 — MPLS
tipo: LAB
codici_syllabus: 2.1
ore: 2h
stato: QUASI COMPLETO
fonte: LAB04 (split)
---
# MOD-10 — MPLS LDP & Fondamenta

## Deliverable
- [x] workbook.md
- [x] soluzione.md
- [ ] slide.pptx   _(generare da template master_slide.pptx)_
- [x] cfg/         pe1-cfg (OSPF only) · p1-cfg (OSPF only) · p2-cfg (OSPF+MPLS) · pe2-cfg (OSPF+MPLS)

## Nota cfg
P2 e PE2 hanno MPLS LDP pre-configurato (studente configura solo PE1 e P1).
Backbone VLAN: PE1↔P1=VLAN13, P1↔P2=VLAN34, P2↔PE2=VLAN24.
Tutti i router connessi tramite sub-interfacce su e0/0.