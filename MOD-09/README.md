---
modulo: MOD-09
titolo: PBR & Route Manipulation Avanzata
area: AREA 3 — ROUTE MANIPULATION
tipo: LAB
codici_syllabus: 1.2 · 1.6 · 3.2.d
ore: 2h
stato: COMPLETO
prerequisiti: MOD-08 · MOD-05 · MOD-01
---
# MOD-09 — PBR & Route Manipulation Avanzata

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

- **T1** — PBR base: ACL estesa + route-map PBR + ip policy inbound su interfaccia (set ip next-hop)
- **T2** — PBR condizionale: verify-availability + IP SLA + track (fallback automatico)
- **T3A** — Administrative Distance: distance bgp, preferenza tra protocolli
- **T3B** — Floating Static Route: backup route con AD > protocollo primario
- **T3C** — IP SLA + Track: rotta statica condizionale installata/rimossa dinamicamente
- **T4** — Troubleshooting: ACL errata, interfaccia PBR sbagliata, floating static non flottante

## Topologia

Identica a MOD-08: 7 device ISP-A · WAN-A · CORE · WAN-B · ISP-B · LAN-A · LAN-B  
Le cfg di partenza sono lo stato finale di MOD-08 (redistribuzione + tag già configurati)  
PBR applicato su CORE Eth0/0.34 (inbound da LAN-A): traffico guest 10.99.0.0/24 → WAN-B