# MOD-08 — cfg iniziali

| File | Device | Ruolo |
|------|--------|-------|
| ispa-cfg | ISP-A | AS 100 — annuncia 100.0.0.0/8 via eBGP verso WAN-A |
| ispb-cfg | ISP-B | AS 200 — annuncia 200.0.0.0/8 via eBGP verso WAN-B |
| wana-cfg | WAN-A | AS 65001 — transit tra ISP-A e CORE; OSPF area 0 con CORE |
| wanb-cfg | WAN-B | AS 65002 — transit tra ISP-B e CORE; OSPF area 0 con CORE |
| core-cfg | CORE | AS 65000 — punto di redistribuzione BGP↔OSPF (da configurare nei task) |
| lana-cfg | LAN-A | Solo OSPF — Lo1: 10.10.0.1/24 (prod), Lo2: 10.99.0.1/24 (guest) |
| lanb-cfg | LAN-B | Solo OSPF — Lo1: 10.20.0.1/24 (prod) |

**Stato iniziale pre-caricato:**
- OSPF area 0 attivo tra: WAN-A, WAN-B, CORE, LAN-A, LAN-B (loopback passive)
- eBGP attivo: ISP-A↔WAN-A, WAN-A↔CORE, CORE↔WAN-B, WAN-B↔ISP-B
- ISP-A annuncia 100.0.0.0/8; ISP-B annuncia 200.0.0.0/8
- **Nessuna redistribuzione configurata** (da fare nei task T3/T4/T5)
- Nessun prefix-list, nessuna route-map, nessun tag
- `ip ospf network point-to-point` su Lo1 e Lo2 di LAN-A e Lo1 di LAN-B (annuncio /24 corretto)
