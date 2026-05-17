# MOD-27 — cfg iniziali

| File | Dispositivo | Ruolo |
|------|-------------|-------|
| r-isp-cfg | R-ISP | Internet simulato (NTP server) |
| r-gw-cfg | R-GW | NAT Gateway (ip nat inside/outside) |
| pc1-cfg | PC1 | Host interno (192.168.1.10) |
| pc2-cfg | PC2 | Host interno (192.168.1.20) |

**Stato iniziale pre-caricato:**
- IP configurati su tutte le interfacce
- ip nat inside / ip nat outside configurati su R-GW
- Default route su R-GW e PC1/PC2
- Route statiche su R-ISP verso pool NAT
- Nessuna configurazione NAT o NTP (da fare nei task)