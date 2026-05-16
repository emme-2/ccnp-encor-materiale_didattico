# Soluzione Commentata — MOD-04: OSPF Troubleshooting

> **RISERVATO DOCENTE** — Non distribuire agli studenti prima del completamento del lab.  
> Versione: 1.0 | Data: 2026-05-16

---

## Tabella Errori Intenzionali

| Device | Interfaccia | Errore intenzionale | Sintomo atteso | Task |
|--------|-------------|---------------------|----------------|------|
| R1 | e0/0.12 | hello-interval 10, dead-interval 40 | Adiacenza R1–R2 DOWN: mismatch con R2 (hello 5/dead 20) | T1 |
| R2 | e0/0.12 | hello-interval 5, dead-interval 20 | Adiacenza R1–R2 DOWN: mismatch con R1 (hello 10/dead 40) | T1 |
| R2 | e0/0.23 | ip mtu 1400 | Adiacenza R2–R3 bloccata in EXSTART: MTU mismatch (R3 = 1500) | T2 |
| R4 | e0/0.34 | ip ospf 1 area 0 (errato: doveva essere area 1) | Adiacenza R3–R4 DOWN: area-ID mismatch | T3 |
| R1 | e0/0.14 | ip ospf message-digest-key 1 md5 WRONGPASS | Adiacenza R1–R4 DOWN: MD5 auth fallisce | T4 |
| R4 | e0/0.45 | ip ospf network broadcast | Adiacenza R4–R5: neighbor non FULL, mismatch con R5 (P2P) | T5 |
| — | — | Virtual-link non configurato | Task guidato: studente tenta con RID errato, poi corregge | T6 |
| R2 | globale | ipv6 unicast-routing assente | OSPFv3 non attivo: nessun neighbor IPv6 | T10 |
| R3 | Lo0 | ipv6 ospf area non configurato su Lo0 | Prefisso 2001:db8:3::3/128 assente dalla IPv6 routing table | T11 |

---

## T1 — Fix: Hello/Dead Timer Mismatch R1–R2

### Diagnosi

```
R1# show ip ospf interface Ethernet0/0.12
  Timer intervals configured, Hello 10, Dead 40, Wait 40

R2# show ip ospf interface Ethernet0/0.12
  Timer intervals configured, Hello 5, Dead 20, Wait 20
```

R1 usa hello=10/dead=40; R2 usa hello=5/dead=20. Devono essere identici.

### Fix

```
R2(config)# interface Ethernet0/0.12
R2(config-if)# ip ospf hello-interval 10
R2(config-if)# ip ospf dead-interval 40
```

### Output Post-Fix

```
R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
2.2.2.2           0   FULL/  -        00:00:39    10.0.12.2       Ethernet0/0.12
```

**Nota docente:** gli studenti potrebbero abbassare R1 a hello=5 — entrambi i fix sono validi; il timer standard P2P è 10/40.

---

## T2 — Fix: MTU Mismatch R2–R3

### Diagnosi

```
R2# show ip ospf neighbor
Neighbor ID   Pri  State      Dead Time  Address      Interface
3.3.3.3         0  EXSTART/-  00:00:32   10.0.23.2    Ethernet0/0.23

R2# show interfaces Ethernet0/0.23 | include MTU
  MTU 1400 bytes

R3# show interfaces Ethernet0/0.23 | include MTU
  MTU 1500 bytes
```

`ip mtu 1400` su R2 imposta la MTU OSPF a 1400. R3 riceve DBD con MTU=1400, confronta con la propria (1500) → scarta il DBD → EXSTART bloccato.

### Fix

```
R2(config)# interface Ethernet0/0.23
R2(config-if)# no ip mtu 1400
```

Alternativa (workaround — non raccomandato):
```
R2(config-if)# ip ospf mtu-ignore
R3(config-if)# ip ospf mtu-ignore
```

### Output Post-Fix

```
R2# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
1.1.1.1         0  FULL/-  ...        10.0.12.1    Ethernet0/0.12
3.3.3.3         0  FULL/-  00:00:38   10.0.23.2    Ethernet0/0.23
```

---

## T3 — Fix: Area-ID Mismatch R3–R4

### Diagnosi

```
R3# show ip ospf interface Ethernet0/0.34
  Area 1, Process ID 1

R4# show ip ospf interface Ethernet0/0.34
  Area 0, Process ID 1
```

R3 è corretto (Area 1); R4 ha erroneamente Area 0 su questa interfaccia.

```
R3# debug ip ospf adj
! Log: OSPF: Rcv DBD from 4.4.4.4 on Ethernet0/0.34,
!      area 0 does not match our area 1
```

### Fix

```
R4(config)# interface Ethernet0/0.34
R4(config-if)# ip ospf 1 area 1
```

### Output Post-Fix

```
R4# show ip ospf
  This router is an area border router.
  Number of areas in this router is 3. Area 0 Area 1 Area 2

R3# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
4.4.4.4         0  FULL/-  00:00:38   10.0.34.2    Ethernet0/0.34
```

---

## T4 — Fix: MD5 Authentication Mismatch R1–R4

### Diagnosi

```
R1# debug ip ospf adj
%OSPF-4-BADAUTH: Bad authentication from 10.0.14.2, interface Ethernet0/0.14

R1# show run interface Ethernet0/0.14
 ip ospf message-digest-key 1 md5 WRONGPASS

R4# show run interface Ethernet0/0.14
 ip ospf message-digest-key 1 md5 OSPF_KEY_R14
```

### Fix

```
R1(config)# interface Ethernet0/0.14
R1(config-if)# no ip ospf message-digest-key 1 md5 WRONGPASS
R1(config-if)# ip ospf message-digest-key 1 md5 OSPF_KEY_R14
```

### Output Post-Fix

```
R1# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
2.2.2.2         0  FULL/-  ...        10.0.12.2    Ethernet0/0.12
4.4.4.4         0  FULL/-  00:00:38   10.0.14.2    Ethernet0/0.14

R1# show ip route ospf
O     2.2.2.2/32 [110/11] via 10.0.12.2
O     3.3.3.3/32 [110/21] via 10.0.12.2
O     4.4.4.4/32 [110/11] via 10.0.14.2
O IA  5.5.5.5/32 [110/21] via 10.0.14.2
O E2  192.168.100.0/24 [110/20] via 10.0.23.2
O E1  192.168.200.0/24 [110/30] via 10.0.23.2
```

---

## T5 — Fix: Network Type Mismatch R4–R5

### Diagnosi

```
R4# show ip ospf interface Ethernet0/0.45
  Network Type BROADCAST, Cost: 10

R5# show ip ospf interface Ethernet0/0.45
  Network Type POINT_TO_POINT, Cost: 10
```

R4 broadcast = tenta DR election; R5 P2P = non partecipa. L'adiacenza non converge.

### Fix

```
R4(config)# interface Ethernet0/0.45
R4(config-if)# ip ospf network point-to-point
```

### Output Post-Fix

```
R4# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
5.5.5.5         0  FULL/-  00:00:38   10.0.45.2    Ethernet0/0.45

R5# show ip route
O*IA  0.0.0.0/0 [110/11] via 10.0.45.1
O IA  1.1.1.1/32 [110/31] via 10.0.45.1
O IA  2.2.2.2/32 [110/31] via 10.0.45.1
O IA  3.3.3.3/32 [110/31] via 10.0.45.1
O IA  4.4.4.4/32 [110/21] via 10.0.45.1
O     5.5.5.5/32 is directly connected, Loopback0
! Nessuna O E2 / O E1 — stub area filtra Type 5 LSA
```

---

## T6 — Virtual-Link R3↔R4

### Configurazione Errata (sintomo)

```
R3(config-router)# area 1 virtual-link 5.5.5.5

R3# show ip ospf virtual-links
Virtual Link OSPF_VL0 to router 5.5.5.5 is down
! DOWN: nessun router con RID 5.5.5.5 in Area 1
```

### Fix

```
R3(config)# router ospf 1
R3(config-router)# no area 1 virtual-link 5.5.5.5
R3(config-router)# area 1 virtual-link 4.4.4.4

R4(config)# router ospf 1
R4(config-router)# area 1 virtual-link 3.3.3.3
```

### Output Post-Fix

```
R3# show ip ospf virtual-links
Virtual Link OSPF_VL0 to router 4.4.4.4 is up
  Transit area 1, via interface Ethernet0/0.34, Cost of using 10
  Adjacency State FULL (Hello suppressed)

R3# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
2.2.2.2         0  FULL/-  ...        10.0.23.1    Ethernet0/0.23
4.4.4.4         0  FULL/-  ...        10.0.34.2    Ethernet0/0.34
4.4.4.4         0  FULL/-  -          10.0.34.2    OSPF_VL0
```

**Nota docente:** il virtual-link usa il Router-ID dell'endpoint, non l'IP dell'interfaccia. L'area di transito (Area 1) deve essere normal (non stub/NSSA). Il Dead Time `-` è normale: il virtual-link è un demand circuit che sopprime gli hello periodici.

---

## T7 — Stub Area e Rotte Esterne

### Diagnosi

```
R5# show ip ospf database
! Sezione "Type-5 AS External Link States": assente

R5# show ip route 172.16.4.0
! Nessuna rotta specifica

R5# show ip route 0.0.0.0
O*IA  0.0.0.0/0 [110/11] via 10.0.45.1
! R5 raggiunge 172.16.4.0 tramite la default route generata dall'ABR
```

**Spiegazione:** Area 2 è stub → Type 5 LSA bloccati. L'ABR (R4) genera automaticamente un Type 3 LSA con 0.0.0.0/0. Il comportamento è corretto.

### Fix Opzionale: NSSA

```
R4(config)# router ospf 1
R4(config-router)# no area 2 stub
R4(config-router)# area 2 nssa

R5(config)# router ospf 1
R5(config-router)# no area 2 stub
R5(config-router)# area 2 nssa
```

```
R5# show ip ospf database nssa-external
  Type-7 AS External Link States (Area 2)
  Link ID       ADV Router  Age  Seq#  Tag
  172.16.4.0    4.4.4.4     ...  ...   0

R5# show ip route 172.16.4.0
O N2  172.16.4.0/24 [110/20] via 10.0.45.1
```

---

## T8 — E1 vs E2 Path Preference

### Output Atteso

```
R1# show ip route ospf | include 192.168
O E2  192.168.100.0/24 [110/20] via 10.0.12.2  ← costo fisso ovunque
O E1  192.168.200.0/24 [110/30] via 10.0.12.2  ← 20 ext + 10 int (R1→R2→R3)

R4# show ip route ospf | include 192.168
O E2  192.168.100.0/24 [110/20] via 10.0.34.2  ← ancora 20 (costo fisso)
O E1  192.168.200.0/24 [110/40] via 10.0.34.2  ← 20 ext + 20 int (R4→R3 via Area 1)
```

**Punto chiave:** E2 non riflette la topologia interna — stesso costo da qualsiasi punto. E1 cresce con la distanza dall'ASBR, riflettendo il costo reale del percorso.

**Preferenza di tipo:** E1 > E2. Per la stessa destinazione, E1 è sempre scelto su E2.

---

## T9 — Cost Manipulation

### Forza Path via R4

```
R1(config)# interface Ethernet0/0.12
R1(config-if)# ip ospf cost 100

R1# show ip route 3.3.3.3
  Known via "ospf 1", distance 110, metric 21
  * 10.0.14.2 (R4), metric 21 = 10(R1-R4) + 10(R4-R3) + 1(Lo0)
! Path via R2 ora: 100+10+1=111 — scartato
```

### O vs O IA — Non modificare con il costo

```
R1# show ip route ospf
O    2.2.2.2/32 [110/11]  ← O: intra-area, priorità tipo 1
O IA 4.4.4.4/32 [110/11]  ← O IA: inter-area, priorità tipo 2
```

Anche se entrambi costano 11, O è sempre preferito su O IA. La preferenza è di tipo, non numerica.

### Ripristino

```
R1(config)# interface Ethernet0/0.12
R1(config-if)# no ip ospf cost
```

---

## T10 — Fix: OSPFv3 Neighbor Non Si Forma

### Diagnosi

```
R2# show ipv6 ospf
! Nessun output / processo non attivo

R2# show run | include ipv6 unicast
! Nessuna riga
```

### Fix

```
R2(config)# ipv6 unicast-routing
R2(config)# ipv6 cef
R2(config)# interface Ethernet0/0.12
R2(config-if)# ipv6 address 2001:db8:12::2/64
R2(config-if)# ipv6 ospf 1 area 0
R2(config)# interface Loopback0
R2(config-if)# ipv6 address 2001:db8:2::2/128
R2(config-if)# ipv6 ospf 1 area 0
R2(config)# ipv6 router ospf 1
R2(config-rtr)# router-id 2.2.2.2
```

### Output Post-Fix

```
R1# show ipv6 ospf neighbor
Neighbor ID   Pri  State   Dead Time  Interface ID  Interface
2.2.2.2         1  FULL/-  00:00:37   x             Ethernet0/0.12
```

---

## T11 — Fix: Prefisso IPv6 Assente (R3 Loopback)

### Diagnosi

```
R3# show ipv6 ospf interface brief
Interface    PID  Area  Cost  State  Nbrs
Et0/0.23     1    0     10    P2P    1/1
! Lo0 non appare — non partecipa a OSPFv3

R3# show run interface Loopback0
 ipv6 address 2001:db8:3::3/128
 ! manca: ipv6 ospf 1 area 0
```

### Fix

```
R3(config)# interface Loopback0
R3(config-if)# ipv6 ospf 1 area 0
```

### Output Post-Fix

```
R1# show ipv6 route ospf
OI  2001:db8:2::2/128 [110/11] via FE80::..., Ethernet0/0.12
OI  2001:db8:3::3/128 [110/11] via FE80::..., Ethernet0/0.12
OI  2001:db8:23::/64  [110/20] via FE80::..., Ethernet0/0.12
```

---

## Configurazioni Finali Post-Fix (Riferimento Docente)

### R1 — Corretta

```
hostname R1
ip cef
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
 ip ospf 1 area 0
 ipv6 address 2001:db8:1::1/128
 ipv6 ospf 1 area 0
!
interface Ethernet0/0
 no shutdown
!
interface Ethernet0/0.12
 encapsulation dot1Q 12
 ip address 10.0.12.1 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ipv6 address 2001:db8:12::1/64
 ipv6 ospf 1 area 0
!
interface Ethernet0/0.14
 encapsulation dot1Q 14
 ip address 10.0.14.1 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPF_KEY_R14
!
router ospf 1
 router-id 1.1.1.1
!
ipv6 unicast-routing
ipv6 cef
ipv6 router ospf 1
 router-id 1.1.1.1
```

### R2 — Corretta

```
hostname R2
ip cef
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
 ip ospf 1 area 0
 ipv6 address 2001:db8:2::2/128
 ipv6 ospf 1 area 0
!
interface Ethernet0/0
 no shutdown
!
interface Ethernet0/0.12
 encapsulation dot1Q 12
 ip address 10.0.12.2 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ipv6 address 2001:db8:12::2/64
 ipv6 ospf 1 area 0
!
interface Ethernet0/0.23
 encapsulation dot1Q 23
 ip address 10.0.23.1 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ipv6 address 2001:db8:23::1/64
 ipv6 ospf 1 area 0
!
router ospf 1
 router-id 2.2.2.2
!
ipv6 unicast-routing
ipv6 cef
ipv6 router ospf 1
 router-id 2.2.2.2
```

### R3 — Corretta

```
hostname R3
ip cef
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
 ip ospf 1 area 0
 ipv6 address 2001:db8:3::3/128
 ipv6 ospf 1 area 0
!
interface Ethernet0/0
 no shutdown
!
interface Ethernet0/0.23
 encapsulation dot1Q 23
 ip address 10.0.23.2 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ipv6 address 2001:db8:23::2/64
 ipv6 ospf 1 area 0
!
interface Ethernet0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.1 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 1
!
ip route 192.168.100.0 255.255.255.0 Null0
ip route 192.168.200.0 255.255.255.0 Null0
!
router ospf 1
 router-id 3.3.3.3
 area 1 virtual-link 4.4.4.4
 redistribute static subnets route-map OSPF_REDIST
!
ip prefix-list PL_E1 seq 5 permit 192.168.200.0/24
route-map OSPF_REDIST permit 10
 match ip address prefix-list PL_E1
 set metric-type type-1
route-map OSPF_REDIST permit 20
!
ipv6 unicast-routing
ipv6 cef
ipv6 router ospf 1
 router-id 3.3.3.3
```

### R4 — Corretta

```
hostname R4
ip cef
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
 ip ospf 1 area 0
!
interface Ethernet0/0
 no shutdown
!
interface Ethernet0/0.14
 encapsulation dot1Q 14
 ip address 10.0.14.2 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 0
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPF_KEY_R14
!
interface Ethernet0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.2 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 1
!
interface Ethernet0/0.45
 encapsulation dot1Q 45
 ip address 10.0.45.1 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 2
!
ip route 172.16.4.0 255.255.255.0 Null0
!
router ospf 1
 router-id 4.4.4.4
 area 2 stub
 area 1 virtual-link 3.3.3.3
 redistribute static subnets
```

### R5 — Invariata (nessun fix richiesto)

```
hostname R5
ip cef
!
interface Loopback0
 ip address 5.5.5.5 255.255.255.255
 ip ospf 1 area 2
!
interface Ethernet0/0
 no shutdown
!
interface Ethernet0/0.45
 encapsulation dot1Q 45
 ip address 10.0.45.2 255.255.255.252
 ip ospf network point-to-point
 ip ospf 1 area 2
!
router ospf 1
 router-id 5.5.5.5
 area 2 stub
```

---

## Verifica Finale — Rete Funzionante

```
R1# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
2.2.2.2         0  FULL/-  00:00:38   10.0.12.2    Ethernet0/0.12
4.4.4.4         0  FULL/-  00:00:39   10.0.14.2    Ethernet0/0.14

R3# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
2.2.2.2         0  FULL/-  00:00:36   10.0.23.1    Ethernet0/0.23
4.4.4.4         0  FULL/-  00:00:35   10.0.34.2    Ethernet0/0.34
4.4.4.4         0  FULL/-  -          10.0.34.2    OSPF_VL0

R4# show ip ospf neighbor
Neighbor ID   Pri  State   Dead Time  Address      Interface
1.1.1.1         0  FULL/-  00:00:38   10.0.14.1    Ethernet0/0.14
3.3.3.3         0  FULL/-  00:00:37   10.0.34.1    Ethernet0/0.34
3.3.3.3         0  FULL/-  -          10.0.34.1    OSPF_VL1
5.5.5.5         0  FULL/-  00:00:39   10.0.45.2    Ethernet0/0.45

R1# show ip route ospf
O     2.2.2.2/32 [110/11] via 10.0.12.2
O     3.3.3.3/32 [110/21] via 10.0.12.2
O     4.4.4.4/32 [110/11] via 10.0.14.2
O IA  5.5.5.5/32 [110/21] via 10.0.14.2
O IA  10.0.34.0/30 [110/20] via 10.0.14.2
O IA  10.0.45.0/30 [110/20] via 10.0.14.2
O E2  192.168.100.0/24 [110/20] via 10.0.23.2
O E1  192.168.200.0/24 [110/30] via 10.0.23.2

R5# show ip route ospf
O*IA  0.0.0.0/0 [110/11] via 10.0.45.1
O IA  1.1.1.1/32 [110/31] via 10.0.45.1
O IA  2.2.2.2/32 [110/31] via 10.0.45.1
O IA  3.3.3.3/32 [110/31] via 10.0.45.1
O IA  4.4.4.4/32 [110/11] via 10.0.45.1

R1# show ipv6 ospf neighbor
Neighbor ID   Pri  State   Dead Time  Interface ID  Interface
2.2.2.2         1  FULL/-  00:00:38   x             Ethernet0/0.12

R1# show ipv6 route ospf
OI  2001:db8:2::2/128 [110/11] via FE80::..., Ethernet0/0.12
OI  2001:db8:3::3/128 [110/11] via FE80::..., Ethernet0/0.12
OI  2001:db8:23::/64  [110/20] via FE80::..., Ethernet0/0.12
```
