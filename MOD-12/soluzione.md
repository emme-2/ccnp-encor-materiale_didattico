# Soluzione Commentata — MOD-12: MPLS L2VPN (xconnect / AToM)

> **USO RISERVATO ISTRUTTORE** — Distribuire agli studenti solo dopo il completamento del lab.

---

## Configurazione completa PE1

```
! === PE1 — xconnect L2VPN ===
!
! Interfaccia Eth0/0.101: attachment circuit verso CE1 (VLAN 101).
! NON ha ip address: il PE fa solo label switching del frame Ethernet ricevuto.
! xconnect specifica:
!   - peer: loopback dell'altro PE (2.2.2.2)
!   - VC-ID: 101 (deve essere identico su PE2)
!   - encapsulation: mpls (AToM standard)
!
interface Ethernet0/0.101
 encapsulation dot1Q 101
 xconnect 2.2.2.2 101 encapsulation mpls
```

## Configurazione completa PE2

```
! === PE2 — xconnect L2VPN (speculare a PE1) ===
!
! Eth0/0.202: attachment circuit verso CE2 (VLAN 202 — diversa da VLAN 101 lato CE1).
! La VLAN locale può essere diversa: ciò che conta è il VC-ID uguale (101).
! Il peer è il loopback di PE1 (1.1.1.1).
!
interface Ethernet0/0.202
 encapsulation dot1Q 202
 xconnect 1.1.1.1 101 encapsulation mpls
```

> **CE1 e CE2:** nessuna modifica necessaria.
> Eth0/0.101 su CE1 ha già IP 172.16.0.1/24.
> Eth0/0.202 su CE2 ha già IP 172.16.0.2/24.

---

## Output show attesi e commentati

### show xconnect all (PE1)

```
PE1# show xconnect all
Legend:  XC ST=Xconnect State  S1=Segment1 State  S2=Segment2 State
         UP=Up         DN=Down  AD=Admin Down      IA=Inactive
XC ST  Segment 1                    S1 Segment 2                    S2
------+---------------------------------+--+---------------------------------+--
UP     pri ac Et0/0.101:101(Eth)     UP mpls 2.2.2.2:101             UP
```

Commento:
- `XC ST = UP`: xconnect operativo end-to-end
- `S1 = UP`: segmento locale (attachment circuit Et0/0.101) attivo
- `S2 = UP`: segmento MPLS verso 2.2.2.2 con VC-ID 101 attivo
- `(Eth)`: tipo di incapsulamento locale — Ethernet

### show mpls l2transport vc detail (PE1)

```
PE1# show mpls l2transport vc detail
Local interface: Et0/0.101 up, line protocol up, Ethernet up
  Destination address: 2.2.2.2, VC ID: 101, VC status: up
  Output interface: Et0/0.13, imposed label stack {16 21}
!                                                   ↑   ↑
!                                    outer LDP label    inner VC label
!
!  Label 16 = label LDP che P1 ha assegnato per raggiungere 2.2.2.2 (PE2)
!             Verrà scambiata (SWAP) da P1 e P2 lungo il backbone
!  Label 21 = VC label allocata da PE2 per il pseudowire VC-ID 101
!             Interpretata SOLO da PE2 per identificare l'interfaccia di consegna
!
  Create time: 00:05:12, last status change time: 00:05:10
  Signaling protocol: LDP, peer 2.2.2.2:0 ESTABLISHED
  MPLS VC labels: local 23, remote 21
!                        ↑          ↑
!              label che PE1        label che PE2
!              alloca per           alloca per
!              ricevere da PE2      ricevere da PE1
  Group ID: local 0, remote 0
  MTU: local 1500, remote 1500
  Remote interface description:
```

Commento label `local 23, remote 21`:
- PE1 alloca label 23 per ricevere traffico da PE2 (PE2 usa 23 come inner label)
- PE2 alloca label 21 per ricevere traffico da PE1 (PE1 usa 21 come inner label)
- Questo è il meccanismo LDP VC FEC: entrambi i PE si scambiano le proprie VC label
  nella sessione LDP, esattamente come si scambiano le label per i loopback.

### show mpls l2transport vc (PE2 — vista sintetica)

```
PE2# show mpls l2transport vc
Local intf     Local circuit              Dest address    VC id      Status
-------------  -------------------------  --------------  ---------  ----------
Et0/0.202      Eth VLAN 202              1.1.1.1         101        UP
```

### ping 172.16.0.2 source Eth0/0.101 (CE1)

```
CE1# ping 172.16.0.2 source Ethernet0/0.101
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 172.16.0.2, timeout is 2 seconds:
Packet sent with a source address of 172.16.0.1
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 4/5/9 ms
```

---

## Schema data plane — frame walk CE1 → CE2

Percorso fisico: CE1 → PE1 → P1 → P2 → PE2 → CE2

| # | Router | Azione | Label stack |
|---|--------|--------|-------------|
| 1 | CE1 | Invia frame Ethernet (ARP o IP) su 172.16.0.0/24 | `[frame L2 puro]` |
| 2 | PE1 (ingress) | Riconosce l'attachment circuit Et0/0.101 → xconnect VC-ID 101. Push outer LDP (16) + inner VC (21). | `[outer=16][inner=21][frame L2]` |
| 3 | P1 (transit) | Swap outer 16 → label di P2 per 2.2.2.2/32. Non tocca inner. Non vede il frame L2. | `[outer=X][inner=21][frame L2]` |
| 4 | P2 (penultimate — PHP) | Pop outer (implicit-null da PE2). | `[inner=21][frame L2]` |
| 5 | PE2 (egress) | Riceve con solo label 21. Lookup: label 21 → VC-ID 101 → consegna su Et0/0.202 verso CE2. Pop inner. | `[frame L2 puro]` |
| 6 | CE2 | Riceve il frame Ethernet in chiaro su 172.16.0.2. | — |

---

## Confronto VPN label L3VPN vs VC label L2VPN

| Aspetto | L3VPN (MOD-11) | L2VPN xconnect (MOD-12) |
|---------|----------------|-------------------------|
| Protocollo segnalazione inner label | MP-BGP (address-family vpnv4) | LDP (VC FEC Element) |
| Chi alloca inner label | PE egress (per ogni prefisso nella VRF) | PE egress (una label per VC-ID) |
| Inner label identifica | VRF e prefisso IP customer | Interfaccia CE di consegna |
| Outer label | LDP (trasporto backbone) | LDP (trasporto backbone) — identico |
| CE vede | Route BGP remote | Link Ethernet trasparente |
| IP sull'interfaccia PE-CE | Si (nella VRF) | No |

In entrambi i casi il backbone vede solo la label outer LDP.

---

## Note su varianti e alternative

**Modalità Ethernet raw vs VLAN:**
xconnect su IOS supporta diverse modalità di accesso:
- `encapsulation dot1Q <vlan>`: trasporta solo il payload (VLAN tag rimosso)
- Su interfaccia fisica (non subinterface): trasporta il frame completo con tag

Per trasparenza completa del tag VLAN (utile per QinQ o trunk trasparente):
```
interface Ethernet0/0
 xconnect 2.2.2.2 101 encapsulation mpls
```
In questo caso tutto il traffico sull'interfaccia entra nel pseudowire.

**VPLS — estensione multipoint di xconnect:**
xconnect (VPWS) è punto-a-punto. Per connettere più CE alla stessa "Ethernet
virtuale" si usa VPLS (Virtual Private LAN Service), configurato con
`l2 vfi <nome> manual` invece di xconnect. Non in scope di questo lab.

**Verifica segnalazione LDP VC:**
```
PE1# debug mpls l2transport signaling
! Mostra il processo LDP VC FEC — utile se xconnect rimane DN
! Disabilitare dopo il debug: undebug all
```