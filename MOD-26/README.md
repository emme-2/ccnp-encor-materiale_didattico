---
modulo: MOD-26
titolo: QoS MQC
area: AREA 10 — QoS
tipo: LAB
codici_syllabus: 1.5.a · 1.5.b
ore: 2h
stato: COMPLETO
fonte: LAB07 (split T9)
---
# MOD-26 — QoS MQC & CoPP

## Deliverable
- [x] workbook.md
- [x] soluzione.md
- [ ] slide.pptx   _(generare da template master_slide.pptx)_
- [x] cfg/         r1-cfg

## Nota cfg
R1 ha IP base + OSPF area 0 su e0/1.100 e e0/2.200 — NESSUNA policy QoS.
e0/0 in VRF LAB (DHCP management). Stessa struttura di MOD-13/r1-cfg.
Studente configura ACL, class-map, policy-map child + parent, service-policy su e0/0.