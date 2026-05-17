# MOD-07 — cfg iniziali

| File | Dispositivo | AS | Ruolo |
|------|-------------|-----|-------|
| r1-cfg | R1 | 65001 | Route Reflector (da configurare in T2) |
| r2-cfg | R2 | 65001 | iBGP client |
| r3-cfg | R3 | 65001 | iBGP client |
| r4-cfg | R4 | 65001 | iBGP client |
| r5-cfg | R5 | 65002 | eBGP peer esterno |

**Stato iniziale pre-caricato:**
- OSPF 1 area 0 attivo su R1-R4
- iBGP full-mesh (6 sessioni) in AS65001
- eBGP R1↔R5
- IPv6 loopback configurati su tutti i router
- Nessun Route Reflector
- Nessuna address-family ipv6 in BGP
