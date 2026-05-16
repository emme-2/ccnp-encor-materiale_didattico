---
modulo: MOD-12
titolo: MPLS L2VPN
area: AREA 4 — MPLS
tipo: LAB
codici_syllabus: 2.2
ore: 1.5h
stato: COMPLETO
fonte: LAB04 (split)
---
# MOD-12 — MPLS L2VPN (xconnect / AToM)

## Deliverable
- [x] workbook.md
- [x] soluzione.md
- [ ] slide.pptx   _(generare da template master_slide.pptx)_
- [x] cfg/         pe1-cfg · p1-cfg · p2-cfg · pe2-cfg · ce1-cfg · ce2-cfg

## Nota cfg
PE1 ha Eth0/0.101 (dot1Q 101) senza IP e senza xconnect — studente aggiunge xconnect.
PE2 ha Eth0/0.202 (dot1Q 202) senza IP e senza xconnect.
VLAN asimmetrica (101↔202) gestita da xconnect — CE non vede la differenza.
VC-ID=101 · peer PE1=1.1.1.1 · peer PE2=2.2.2.2.