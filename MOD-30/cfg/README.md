# MOD-30 — cfg iniziali

| File | Dispositivo | Ruolo |
|------|-------------|-------|
| r1-cfg | R1 | NAS (device da proteggere e configurare) |
| r2-cfg | R2 | Client SSH/Telnet per i test |

**Nota ambiente:** FreeRADIUS gira come container sulla VM GNS3.
Indirizzo di default: 192.168.122.100.
Modificare nel r1-cfg se l'IP è diverso nel proprio ambiente.

**Stato iniziale pre-caricato:**
- IP configurati su tutte le interfacce
- Nessuna password configurata
- Nessuna configurazione AAA
- SSH non abilitato
- VTY aperte (transport input all) — da hardening in Task T1