# Soluzione Commentata — MOD-11: MPLS L3VPN

> **USO RISERVATO ISTRUTTORE** — Distribuire agli studenti solo dopo il completamento del lab.

---

## Configurazione completa PE1

```
! === PE1 — VRF + MP-BGP + eBGP verso CE1 ===

! 1. Definizione VRF CUST_A
ip vrf CUST_A
 rd 65000:100
 route-target export 65000:100
 route-target import 65000:100

! 2. Interfaccia verso CE1 in VRF
! NOTA: ip vrf forwarding rimuove l'IP — riassegnarlo immediatamente dopo
interface Ethernet0/0.11
 encapsulation dot1Q 11
 ip vrf forwarding CUST_A
 ip address 192.168.1.2 255.255.255.252
 no shutdown

! 3. MP-BGP iBGP verso PE2 (sessione VPNv4)
router bgp 65000
 bgp router-id 1.1.1.1
 neighbor 2.2.2.2 remote-as 65000
 neighbor 2.2.2.2 update-source Loopback0
 !
 address-family vpnv4
  neighbor 2.2.2.2 activate
  neighbor 2.2.2.2 send-community extended
 exit-address-family
 !
 ! 4. eBGP verso CE1 all'interno della VRF
 address-family ipv4 vrf CUST_A
  neighbor 192.168.1.1 remote-as 65001
  neighbor 192.168.1.1 activate
 exit-address-family
```

## Configurazione completa PE2

```
! === PE2 — VRF + MP-BGP + eBGP verso CE2 (speculare a PE1) ===

ip vrf CUST_A
 rd 65000:100
 route-target export 65000:100
 route-target import 65000:100

interface Ethernet0/0.22
 encapsulation dot1Q 22
 ip vrf forwarding CUST_A
 ip address 192.168.2.2 255.255.255.252
 no shutdown

router bgp 65000
 bgp router-id 2.2.2.2
 neighbor 1.1.1.1 remote-as 65000
 neighbor 1.1.1.1 update-source Loopback0
 !
 address-family vpnv4
  neighbor 1.1.1.1 activate
  neighbor 1.1.1.1 send-community extended
 exit-address-family
 !
 address-family ipv4 vrf CUST_A
  neighbor 192.168.2.1 remote-as 65002
  neighbor 192.168.2.1 activate
 exit-address-family
```

## Configurazione completa CE1

```
! === CE1 — eBGP AS 65001 verso PE1 ===
! CE1 non sa nulla di MPLS o VRF: vede solo una normale sessione eBGP.

router bgp 65001
 bgp router-id 192.168.1.1
 neighbor 192.168.1.2 remote-as 65000
 !
 address-family ipv4
  network 192.168.1.0 mask 255.255.255.252
  neighbor 192.168.1.2 activate
 exit-address-family
```

## Configurazione completa CE2

```
! === CE2 — eBGP AS 65002 verso PE2 ===

router bgp 65002
 bgp router-id 192.168.2.1
 neighbor 192.168.2.2 remote-as 65000
 !
 address-family ipv4
  network 192.168.2.0 mask 255.255.255.252
  neighbor 192.168.2.2 activate
 exit-address-family
```

---

## Output show attesi e commentati

### show bgp vpnv4 unicast summary (PE1)

```
PE1# show bgp vpnv4 unicast summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
192.168.1.1     4 65001      8       8        3    0    0 00:01:10  1
2.2.2.2         4 65000     15      15        3    0    0 00:02:30  1
```

Commento:
- `192.168.1.1` = CE1 (eBGP, AS65001), ha inviato 1 prefisso (192.168.1.0/30)
- `2.2.2.2` = PE2 (iBGP VPNv4), ha inviato 1 prefisso (192.168.2.0/30 da CE2)
- `State/PfxRcd = 1` su entrambi = routing bi-direzionale funzionante

### show bgp vpnv4 unicast vrf CUST_A 192.168.1.0 (PE1)

```
PE1# show bgp vpnv4 unicast vrf CUST_A 192.168.1.0
BGP routing table entry for 65000:100:192.168.1.0/30, version 3
Paths: (1 available, best #1, table CUST_A)
  Local
    192.168.1.1 from 192.168.1.1 (192.168.1.1)
      Origin IGP, metric 0, localpref 100, valid, external, best
      Extended Community: RT:65000:100
      mpls labels in/out 20/nolabel
!                          ↑       ↑
!                  VPN label      nolabel = CE è direttamente connesso
!                  allocata       (nessuna label outgoing verso CE1)
!                  da PE1
```

Commento:
- `mpls labels in/out 20/nolabel`: PE1 alloca VPN label 20 per questo prefisso.
  Quando PE2 manda traffico verso 192.168.1.x, userà label 20 come inner label.
  PE1 riceverà il pacchetto con label 20 e saprà che appartiene a CUST_A,
  uscita verso CE1 — senza fare lookup IP.

### show ip route vrf CUST_A (PE2)

```
PE2# show ip route vrf CUST_A
Routing Table: CUST_A
Gateway of last resort is not set

B   192.168.1.0/30 [200/0] via 1.1.1.1, 00:01:05, label [16 20]
!                                                           ↑   ↑
!                                                  outer LDP   inner VPN
!                  label 16 = trasporto LDP verso 1.1.1.1 (PE1)
!                  label 20 = VPN label allocata da PE1 per 192.168.1.0/30

C   192.168.2.0/30 is directly connected, Ethernet0/0.22
```

Commento: `[16 20]` è il double label stack. P-router vedono solo label 16
(la scambiano con SWAP). PE1 riceve il pacchetto con solo label 20
(PHP di P1 ha rimosso la outer) e la usa per identificare VRF CUST_A.

### show mpls forwarding-table vrf CUST_A (PE2)

```
PE2# show mpls forwarding-table vrf CUST_A
Local  Outgoing    Prefix              Bytes     Outgoing   Next Hop
Label  Label or    or Tunnel Id        Switched  interface
       Tunnel-Id
None   20          192.168.1.0/30[V]   0         Et0/0.24   10.0.24.1
[T]    1.1.1.1/32  0                   Et0/0.24   10.0.24.1
```

Commento:
- Label 20 (inner VPN) verso 192.168.1.0/30 — uscita Et0/0.24 con next-hop P2
- `[T]` = transport label LDP per raggiungere PE1 (1.1.1.1)

### ping 192.168.2.1 source Eth0/0.11 (CE1)

```
CE1# ping 192.168.2.1 source Ethernet0/0.11
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 192.168.2.1, timeout is 2 seconds:
Packet sent with a source address of 192.168.1.1
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 4/5/8 ms
```

---

## Sezione teoria — Data plane packet walk CE2 → CE1

Schema passo-passo del percorso fisico: CE2 → PE2 → P2 → P1 → PE1 → CE1

| # | Router | Azione | Label stack |
|---|--------|--------|-------------|
| 1 | CE2 | Invia IP packet (192.168.2.1 → 192.168.1.1). Default route verso PE2. | `[IP puro]` |
| 2 | PE2 (ingress) | Lookup VRF CUST_A: dst 192.168.1.1 → next-hop 1.1.1.1, VPN label 20. Lookup LDP: label per 1.1.1.1/32 = 16. Push entrambe. | `[outer=16][inner=20][IP]` |
| 3 | P2 (transit) | Swap outer 16 → 22 (label di P1 per 1.1.1.1/32). Non tocca inner. | `[outer=22][inner=20][IP]` |
| 4 | P1 (penultimate — PHP) | Riceve imp-null da PE1 per 1.1.1.1/32. Pop outer. | `[inner=20][IP]` |
| 5 | PE1 (egress) | Riceve solo label 20. Lookup LFIB: label 20 → VRF CUST_A, uscita Et0/0.11. Pop inner. Forward IP nativo. | `[IP puro]` |
| 6 | CE1 | Riceve IP packet in chiaro. | — |

---

## Note su varianti e alternative

**Per-VRF label allocation (scalabilità su grandi VRF):**
Di default IOS alloca una VPN label per ogni prefisso (per-prefix).
Con molte route nella VRF, si può usare per-VRF per ridurre il numero di label:
```
PE1(config)# mpls label mode vrf CUST_A protocol bgp-vpnv4 per-vrf
```
Con per-VRF: il PE egress deve fare un lookup IP nella VRF dopo il pop della
VPN label (un'operazione in più), ma usa una sola label per tutta la VRF.

**Verifica RT sul prefisso specifico:**
```
PE1# show bgp vpnv4 unicast vrf CUST_A 192.168.2.0
! → mostra Extended Community: RT:65000:100
! Se RT manca → send-community extended assente
```

**Reset sessione BGP senza riavvio:**
```
PE1# clear ip bgp 2.2.2.2 soft
```
Utile dopo modifiche a route-target o community senza voler abbattere la sessione.