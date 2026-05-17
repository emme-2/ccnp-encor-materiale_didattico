# MOD-31 — cfg iniziali

| File | Dispositivo | Ruolo |
|------|-------------|-------|
| r1-cfg | R1 | Target — ACL e CoPP applicati qui |
| r2-cfg | R2 | Attaccante/Tester (fonte del traffico di test) |

**Stato iniziale pre-caricato:**
- IP e OSPF configurati su R1 e R2
- SSH v2 configurato su R1 (username admin/Cisco@123)
- VTY: transport input ssh telnet (Telnet verrà bloccato dalle ACL in T2)
- IPv6 sulle interfacce (address-family ipv6 per test ACL IPv6 in T3)
- Nessuna ACL configurata
- Nessuna CoPP configurata