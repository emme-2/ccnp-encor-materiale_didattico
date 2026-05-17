---
modulo: MOD-08
titolo: Redistribuzione BGP↔OSPF & Prefix Filtering
area: AREA 3 — ROUTE MANIPULATION
tipo: LAB
codici_syllabus: 1.3 · 1.4 · 1.5 · 3.2.d
ore: 2h
stato: COMPLETO
prerequisiti: MOD-05 · MOD-06
---
# MOD-08 — Redistribuzione BGP↔OSPF & Prefix Filtering

**Stato:** COMPLETO ✅

## Deliverable

| File | Stato |
|------|-------|
| workbook.md | ✅ |
| soluzione.md | ✅ |
| cfg/ispa-cfg | ✅ |
| cfg/ispb-cfg | ✅ |
| cfg/wana-cfg | ✅ |
| cfg/wanb-cfg | ✅ |
| cfg/core-cfg | ✅ |
| cfg/lana-cfg | ✅ |
| cfg/lanb-cfg | ✅ |
| slide.pptx | ❌ da sviluppare |

## Contenuto

- **T1** — Prefix-list: filtrare prefissi di routing (ge/le, seq, implicit deny)
- **T2** — Route-map: struttura e uso in contesto redistribuzione (vs BGP neighbor policy di MOD-06)
- **T3** — Redistribuzione OSPF→BGP su CORE (redistribute ospf, route-map, origin incomplete)
- **T4** — Redistribuzione BGP→OSPF su CORE (metric-type E1/E2, keyword subnets, seed metric)
- **T5** — Tagging & Loop Prevention (set tag, match tag deny, dual-redistribution anti-loop)

## Topologia

7 device: ISP-A (AS100) · WAN-A (AS65001) · CORE (AS65000) · WAN-B (AS65002) · ISP-B (AS200) · LAN-A · LAN-B  
OSPF area 0 su: WAN-A, WAN-B, CORE, LAN-A, LAN-B  
CORE è il punto di redistribuzione BGP↔OSPF