# MOD-09 — cfg iniziali

| File | Device | Ruolo |
|------|--------|-------|
| ispa-cfg | ISP-A | AS 100 — annuncia 100.0.0.0/8 (invariato da MOD-08) |
| ispb-cfg | ISP-B | AS 200 — annuncia 200.0.0.0/8 (invariato da MOD-08) |
| wana-cfg | WAN-A | AS 65001 — transit tra ISP-A e CORE (invariato da MOD-08) |
| wanb-cfg | WAN-B | AS 65002 — transit tra ISP-B e CORE (invariato da MOD-08) |
| core-cfg | CORE | AS 65000 — **stato finale MOD-08** (redistribuzione + tag preconfigurati); PBR da configurare nei task |
| lana-cfg | LAN-A | Lo1: 10.10.0.1/24 (prod), Lo2: 10.99.0.1/24 (guest — oggetto del PBR) |
| lanb-cfg | LAN-B | Lo1: 10.20.0.1/24 (prod) |

**Stato iniziale pre-caricato:**
- Redistribuzione BGP↔OSPF con loop prevention (tag 100) già configurata su CORE
- Prefix-list INTERNAL-ONLY e ISP-PREFIXES già configurate su CORE
- Route-map OSPF-TO-BGP e BGP-TO-OSPF già configurate e attive su CORE
- LAN-A e LAN-B raggiungono ISP-A/ISP-B tramite redistribuzione MOD-08
- **Nessun PBR configurato** — da fare in T1/T2
- **Nessuna floating static, IP SLA, track** — da fare in T3B/T3C
