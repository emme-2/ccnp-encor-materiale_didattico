# Soluzione Commentata — MOD-03: OSPFv3 Dual-Stack

> **Uso:** riservato al docente
> **Prerequisiti cfg:** caricare r1-cfg … r6-cfg da TFTP
> I cfg contengono: IPv4 + OSPFv2 completo (Area 0/15/25) + indirizzi IPv6 + ipv6 unicast-routing
> Il processo OSPFv3 NON è configurato — lo studente lo configura nei task T2-T4

---

## Task T1 — Prerequisiti IPv6 (pre-configurati nel cfg)

> **Nota:** i cfg TFTP per MOD-03 includono già gli indirizzi IPv6 e `ipv6 unicast-routing` su tutti i router. T1 del workbook descrive cosa è stato pre-configurato. I passi seguenti sono inclusi nella soluzione come riferimento per verifica e ripristino in caso di errore.

### Configurazione IPv6 di riferimento — R3

```
R3(config)# ipv6 unicast-routing
! abilitare il routing IPv6 globalmente — disabilitato di default su IOS
!
R3(config)# interface ethernet 0/0.3456
R3(config-subif)# ipv6 address 2001:db8:0::3/64
R3(config-subif)# ipv6 address fe80::3 link-local
! link-local statico: facile da leggere nei log e nel neighbor table OSPFv3
R3(config-subif)# exit
!
R3(config)# interface ethernet 0/0.34
R3(config-subif)# ipv6 address 2001:db8:34::3/64
R3(config-subif)# ipv6 address fe80::3 link-local
R3(config-subif)# exit
!
R3(config)# interface ethernet 0/0.36
R3(config-subif)# ipv6 address 2001:db8:36::3/64
R3(config-subif)# ipv6 address fe80::3 link-local
R3(config-subif)# exit
```

> 💡 **Nota didattica:** in IOU, il link-local derivato automaticamente (EUI-64) può essere identico su interfacce diverse dello stesso router. Configurare link-local statici (`fe80::3`) rende i log OSPFv3 leggibili — i neighbor appaiono come `FE80::3` invece di `FE80::A8BB:CCFF:FE...`.

---

## Task T2 — OSPFv3 standard (IPv6 native)

### Configurazione R3

```
R3(config)# ipv6 router ospf 100
R3(config-rtr)# router-id 3.3.3.3
! router-id in formato IPv4 obbligatorio anche su router IPv6-only
R3(config-rtr)# exit
!
R3(config)# interface ethernet 0/0.3456
R3(config-subif)# ipv6 ospf 100 area 0
! In OSPFv3 NON esiste il 'network' statement — abilitazione SOLO per interfaccia
R3(config-subif)# exit
R3(config)# interface ethernet 0/0.34
R3(config-subif)# ipv6 ospf 100 area 0
R3(config-subif)# exit
R3(config)# interface ethernet 0/0.36
R3(config-subif)# ipv6 ospf 100 area 0
R3(config-subif)# exit
```

### Configurazione R4

```
R4(config)# ipv6 router ospf 100
R4(config-rtr)# router-id 4.4.4.4
R4(config-rtr)# exit
!
R4(config)# interface ethernet 0/0.3456
R4(config-subif)# ipv6 ospf 100 area 0
R4(config-subif)# exit
R4(config)# interface ethernet 0/0.34
R4(config-subif)# ipv6 ospf 100 area 0
R4(config-subif)# exit
R4(config)# interface ethernet 0/0.45
R4(config-subif)# ipv6 ospf 100 area 0
R4(config-subif)# exit
```

### Configurazione R5 (ABR)

```
R5(config)# ipv6 router ospf 100
R5(config-rtr)# router-id 5.5.5.5
R5(config-rtr)# exit
!
R5(config)# interface ethernet 0/0.3456
R5(config-subif)# ipv6 ospf 100 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.45
R5(config-subif)# ipv6 ospf 100 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.56
R5(config-subif)# ipv6 ospf 100 area 0
R5(config-subif)# exit
!
R5(config)# interface ethernet 0/0.51
R5(config-subif)# ipv6 ospf 100 area 15
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.52
R5(config-subif)# ipv6 ospf 100 area 25
R5(config-subif)# exit
```

### Configurazione R6

```
R6(config)# ipv6 router ospf 100
R6(config-rtr)# router-id 6.6.6.6
R6(config-rtr)# exit
!
R6(config)# interface ethernet 0/0.3456
R6(config-subif)# ipv6 ospf 100 area 0
R6(config-subif)# exit
R6(config)# interface ethernet 0/0.36
R6(config-subif)# ipv6 ospf 100 area 0
R6(config-subif)# exit
R6(config)# interface ethernet 0/0.56
R6(config-subif)# ipv6 ospf 100 area 0
R6(config-subif)# exit
```

### Configurazione R1 e R2

```
! R1 (Area 15):
R1(config)# ipv6 router ospf 100
R1(config-rtr)# router-id 1.1.1.1
R1(config-rtr)# exit
R1(config)# interface ethernet 0/0.51
R1(config-subif)# ipv6 ospf 100 area 15
R1(config-subif)# exit

! R2 (Area 25):
R2(config)# ipv6 router ospf 100
R2(config-rtr)# router-id 2.2.2.2
R2(config-rtr)# exit
R2(config)# interface ethernet 0/0.52
R2(config-subif)# ipv6 ospf 100 area 25
R2(config-subif)# exit
```

### Verifica T2

```
R5# show ipv6 ospf neighbor
Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
3.3.3.3           0   FULL/DROTHER    00:00:39    4               Et0/0.3456
4.4.4.4         255   FULL/DR         00:00:38    4               Et0/0.3456
6.6.6.6         100   FULL/BDR        00:00:37    4               Et0/0.3456
1.1.1.1           1   FULL/           00:00:37    4               Et0/0.51
2.2.2.2           1   FULL/           00:00:36    4               Et0/0.52

R3# show ipv6 ospf database
! Verificare: LSA Type 1 (Router), Type 8 (Link), Type 9 (Intra-Area-Prefix)
! Type 8 e Type 9 sono specifici di OSPFv3 — non esistono in OSPFv2
```

---

## Task T3 — Loopback IPv6 e summarization OSPFv3

### Configurazione loopback IPv6 R1

```
R1(config)# interface loopback 15
R1(config-if)# ipv6 address 2001:db8:1:15::1/64
R1(config-if)# ipv6 ospf 100 area 15
! In OSPFv3 non serve ip ospf network point-to-point per annunciare /64
! Il Type 9 (Intra-Area-Prefix LSA) trasporta il prefisso reale dell'interfaccia
R1(config-if)# exit
!
R1(config)# interface loopback 150
R1(config-if)# ipv6 address 2001:db8:1:150::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit
!
R1(config)# interface loopback 151
R1(config-if)# ipv6 address 2001:db8:1:151::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit
!
R1(config)# interface loopback 152
R1(config-if)# ipv6 address 2001:db8:1:152::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit
```

### Configurazione loopback IPv6 R2

```
R2(config)# interface loopback 25
R2(config-if)# ipv6 address 2001:db8:2:25::1/64
R2(config-if)# ipv6 ospf 100 area 25
R2(config-if)# exit
!
R2(config)# interface loopback 250
R2(config-if)# ipv6 address 2001:db8:2:250::1/64
R2(config-if)# ipv6 ospf 100 area 25
R2(config-if)# exit
!
R2(config)# interface loopback 251
R2(config-if)# ipv6 address 2001:db8:2:251::1/64
R2(config-if)# ipv6 ospf 100 area 25
R2(config-if)# exit
!
R2(config)# interface loopback 252
R2(config-if)# ipv6 address 2001:db8:2:252::1/64
R2(config-if)# ipv6 ospf 100 area 25
R2(config-if)# exit
```

### Configurazione area range su R5 (OSPFv3)

```
R5(config)# ipv6 router ospf 100
R5(config-rtr)# area 15 range 2001:db8:1::/48
! aggrega tutte le /64 di Area 15 (2001:db8:1:xx::/64) in un /48
R5(config-rtr)# area 25 range 2001:db8:2::/48
R5(config-rtr)# exit
```

> 💡 **Nota didattica:** a differenza di OSPFv2, le loopback OSPFv3 NON richiedono `ip ospf network point-to-point` per annunciare il prefisso reale. Il Type 9 (Intra-Area-Prefix LSA) trasporta direttamente il prefisso configurato sull'interfaccia.

### Verifica T3

```
R4# show ipv6 route ospf
OI  2001:DB8::/64   [110/20] via FE80::5, Et0/0.3456
OI  2001:DB8:1::/48 [110/20] via FE80::5, Et0/0.3456   ! Summary Area 15
OI  2001:DB8:2::/48 [110/20] via FE80::5, Et0/0.3456   ! Summary Area 25
! Le singole /64 di R1 e R2 non compaiono — solo i summary /48
```

---

## Task T4 — OSPFv3 AF: dual-stack IPv4+IPv6

### Step 1 — Rimozione processi separati

```
! Su OGNI router (R1, R2, R3, R4, R5, R6):
Rx(config)# no router ospf 100
! rimuove il processo OSPFv2
Rx(config)# no ipv6 router ospf 100
! rimuove il processo OSPFv3 standard
! Tutte le adiacenze cadranno temporaneamente
```

### Configurazione R4 (esempio di riferimento)

```
R4(config)# router ospfv3 100
R4(config-router)# router-id 4.4.4.4
! router-id obbligatorio su ospfv3 — non ereditato da ospf 100
R4(config-router)# address-family ipv4 unicast
R4(config-router-af)# exit-address-family
R4(config-router)# address-family ipv6 unicast
R4(config-router-af)# exit-address-family
R4(config-router)# exit
!
R4(config)# interface ethernet 0/0.3456
R4(config-subif)# ospfv3 100 ipv4 area 0
! abilita la AF IPv4 su questa interfaccia
R4(config-subif)# ospfv3 100 ipv6 area 0
! abilita la AF IPv6 sulla stessa interfaccia
R4(config-subif)# exit
!
R4(config)# interface ethernet 0/0.34
R4(config-subif)# ospfv3 100 ipv4 area 0
R4(config-subif)# ospfv3 100 ipv6 area 0
R4(config-subif)# exit
!
R4(config)# interface ethernet 0/0.45
R4(config-subif)# ospfv3 100 ipv4 area 0
R4(config-subif)# ospfv3 100 ipv6 area 0
R4(config-subif)# exit
```

### Configurazione R3

```
R3(config)# router ospfv3 100
R3(config-router)# router-id 3.3.3.3
R3(config-router)# address-family ipv4 unicast
R3(config-router-af)# exit-address-family
R3(config-router)# address-family ipv6 unicast
R3(config-router-af)# exit-address-family
R3(config-router)# exit
!
! Su e0/0.3456, e0/0.34, e0/0.36: ospfv3 100 ipv4 area 0 + ospfv3 100 ipv6 area 0
```

### Configurazione R5 (ABR con OSPFv3 AF)

```
R5(config)# router ospfv3 100
R5(config-router)# router-id 5.5.5.5
R5(config-router)# address-family ipv4 unicast
R5(config-router-af)# exit-address-family
R5(config-router)# address-family ipv6 unicast
R5(config-router-af)# exit-address-family
R5(config-router)# exit
!
R5(config)# interface ethernet 0/0.3456
R5(config-subif)# ospfv3 100 ipv4 area 0
R5(config-subif)# ospfv3 100 ipv6 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.45
R5(config-subif)# ospfv3 100 ipv4 area 0
R5(config-subif)# ospfv3 100 ipv6 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.56
R5(config-subif)# ospfv3 100 ipv4 area 0
R5(config-subif)# ospfv3 100 ipv6 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.51
R5(config-subif)# ospfv3 100 ipv4 area 15
R5(config-subif)# ospfv3 100 ipv6 area 15
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.52
R5(config-subif)# ospfv3 100 ipv4 area 25
R5(config-subif)# ospfv3 100 ipv6 area 25
R5(config-subif)# exit
```

### Configurazione R6, R1, R2

```
! R6: router ospfv3 100, router-id 6.6.6.6, AF ipv4+ipv6 su e0/0.3456/36/56 area 0

! R1 (Area 15):
R1(config)# router ospfv3 100
R1(config-router)# router-id 1.1.1.1
R1(config-router)# address-family ipv4 unicast
R1(config-router-af)# exit-address-family
R1(config-router)# address-family ipv6 unicast
R1(config-router-af)# exit-address-family
R1(config-router)# exit
R1(config)# interface ethernet 0/0.51
R1(config-subif)# ospfv3 100 ipv4 area 15
R1(config-subif)# ospfv3 100 ipv6 area 15
R1(config-subif)# exit

! R2 (Area 25): stessa struttura con e0/0.52 in area 25
```

> 💡 **Nota didattica:** la coesistenza di `router ospf 100` e `router ospfv3 100` sullo stesso router causa duplicate adjacency e comportamento imprevedibile per IPv4. Rimuovere sempre i processi separati PRIMA di configurare ospfv3 AF. L'adiacenza è condivisa tra le AF — un solo set di Hello per link.

### Verifica T4

```
R5# show ospfv3 neighbor
! Un solo neighbor per link — adiacenza condivisa tra AF IPv4 e IPv6
OSPFv3 100 address-family ipv4
Neighbor ID     Pri   State           ...
4.4.4.4         255   FULL/DR
1.1.1.1           1   FULL/
OSPFv3 100 address-family ipv6
! Stessi neighbor — la topologia è la stessa

R4# show ip route ospf
! Rotte IPv4 via processo ospfv3:
O IA  10.1.15.0/30 [110/20] via 10.0.0.5, Et0/0.3456

R4# show ipv6 route ospf
! Rotte IPv6 via stesso processo ospfv3:
OI  2001:DB8:15::/64 [110/20] via FE80::5, Et0/0.3456

R5# show ospfv3 100 ipv4 database
! LSDB IPv4 separata dalla IPv6

R5# show ospfv3 100 ipv6 database
! LSDB IPv6 separata
```

---

## Note Varianti & Alternative

**OSPFv3 standard vs OSPFv3 AF:** per ambienti IPv6-only, usare OSPFv3 standard (`ipv6 router ospf`). Per dual-stack dove si vuole un solo processo e un'unica adiacenza per link, usare OSPFv3 AF (`router ospfv3`). La scelta ha impatto sul processo di migration: in OSPFv3 AF, rimuovere i processi separati prima di procedere.

**Summarization in OSPFv3 AF:** la summarization `area range` in OSPFv3 AF si configura dentro l'address-family:
```
router ospfv3 100
 address-family ipv6 unicast
  area 15 range 2001:db8:1::/48
 exit-address-family
```
