# Soluzione Commentata — MOD-07: BGP Route Reflector & IPv6 BGP

---

## T2 — Configurazione Route Reflector

### R1 — Route Reflector

```
R1# configure terminal

R1(config)# router bgp 65001
R1(config-router)# address-family ipv4

! Dichiara R2 come client del RR:
! R1 rifletterà le route apprese da R2 verso R3 e R4 (e viceversa)
R1(config-router-af)# neighbor 2.2.2.2 route-reflector-client

! Stesso per R3:
R1(config-router-af)# neighbor 3.3.3.3 route-reflector-client

! Stesso per R4:
R1(config-router-af)# neighbor 4.4.4.4 route-reflector-client

! cluster-id identifica questo cluster di reflection.
! Default = Router-ID di R1 (1.1.1.1), lo esplicitiamo per chiarezza.
! Se ci sono 2 RR per ridondanza nello stesso cluster, devono avere lo stesso cluster-id.
R1(config-router-af)# bgp cluster-id 1.1.1.1

R1(config-router-af)# exit
R1(config-router)# end
```

### R2 — Rimozione sessioni full-mesh non necessarie

```
R2# configure terminal
R2(config)# router bgp 65001

! Rimuove la sessione diretta verso R3: non serve più, il RR (R1) riflette per noi.
! Il comando "no neighbor" rimuove automaticamente anche le sub-config (address-family, update-source, ecc.)
R2(config-router)# no neighbor 3.3.3.3 remote-as 65001

! Rimuove la sessione diretta verso R4: stessa motivazione
R2(config-router)# no neighbor 4.4.4.4 remote-as 65001

R2(config-router)# end
```

### R3 — Rimozione sessioni full-mesh non necessarie

```
R3# configure terminal
R3(config)# router bgp 65001

! R3 non ha più bisogno di sessioni dirette verso R2 e R4
R3(config-router)# no neighbor 2.2.2.2 remote-as 65001
R3(config-router)# no neighbor 4.4.4.4 remote-as 65001

R3(config-router)# end
```

### R4 — Rimozione sessioni full-mesh non necessarie

```
R4# configure terminal
R4(config)# router bgp 65001

! R4 non ha più bisogno di sessioni dirette verso R2 e R3
R4(config-router)# no neighbor 2.2.2.2 remote-as 65001
R4(config-router)# no neighbor 3.3.3.3 remote-as 65001

R4(config-router)# end
```

### Verifica stato finale T2

```
! Verifica che R1 sia RR per R2:
R1# show ip bgp neighbors 2.2.2.2 | include reflector
! Output atteso: "Route Reflector Client"

! Verifica che R2 abbia solo 1 sessione iBGP:
R2# show ip bgp summary
! Output atteso: solo 1.1.1.1 in AS65001

! Verifica propagazione: R4 vede 5.5.5.5/32 riflesso da R1
R4# show ip bgp 5.5.5.5
! Output atteso:
!   65002
!     172.16.15.2 from 1.1.1.1 (1.1.1.1)
!       Originator: 1.1.1.1, Cluster list: 1.1.1.1
```

---

## T3 — MP-BGP: Address-Family IPv6

### R1 — Abilitazione AF IPv6 come RR

```
R1# configure terminal
R1(config)# router bgp 65001
R1(config-router)# address-family ipv6

! Attiva la sessione IPv6 verso R2 nell'AF ipv6.
! La sessione TCP rimane su IPv4 (loopback 2.2.2.2), ma trasporta NLRI IPv6.
R1(config-router-af)# neighbor 2.2.2.2 activate

! R2 è client del RR anche per l'AF IPv6:
R1(config-router-af)# neighbor 2.2.2.2 route-reflector-client

! Il next-hop IPv6 di R5 (2001:db8:5::5) non è raggiungibile da R2/R3/R4.
! next-hop-self sostituisce il next-hop con il loopback IPv6 di R1 (2001:db8:1::1).
R1(config-router-af)# neighbor 2.2.2.2 next-hop-self

! Stessa configurazione per R3 e R4:
R1(config-router-af)# neighbor 3.3.3.3 activate
R1(config-router-af)# neighbor 3.3.3.3 route-reflector-client
R1(config-router-af)# neighbor 3.3.3.3 next-hop-self
R1(config-router-af)# neighbor 4.4.4.4 activate
R1(config-router-af)# neighbor 4.4.4.4 route-reflector-client
R1(config-router-af)# neighbor 4.4.4.4 next-hop-self

! Attiva anche verso R5 (eBGP, scambia prefissi IPv6):
R1(config-router-af)# neighbor 172.16.15.2 activate

! Annuncia il loopback IPv6 di R1 nell'AF ipv6:
! La route deve essere nella routing table IPv6 (lo è: connected su Lo0).
R1(config-router-af)# network 2001:db8:1::1/128

R1(config-router-af)# exit
R1(config-router)# end
```

### R2 — Abilitazione AF IPv6 come client

```
R2# configure terminal
R2(config)# router bgp 65001
R2(config-router)# address-family ipv6

! Attiva la sessione verso il RR (R1) per l'AF ipv6:
R2(config-router-af)# neighbor 1.1.1.1 activate

! Annuncia il loopback IPv6 di R2:
R2(config-router-af)# network 2001:db8:2::2/128

R2(config-router-af)# exit
R2(config-router)# end
```

### R3 — Abilitazione AF IPv6 come client

```
R3# configure terminal
R3(config)# router bgp 65001
R3(config-router)# address-family ipv6
R3(config-router-af)# neighbor 1.1.1.1 activate
R3(config-router-af)# network 2001:db8:3::3/128
R3(config-router-af)# exit
R3(config-router)# end
```

### R4 — Abilitazione AF IPv6 come client

```
R4# configure terminal
R4(config)# router bgp 65001
R4(config-router)# address-family ipv6
R4(config-router-af)# neighbor 1.1.1.1 activate
R4(config-router-af)# network 2001:db8:4::4/128
R4(config-router-af)# exit
R4(config-router)# end
```

### R5 — Abilitazione AF IPv6 (eBGP)

```
R5# configure terminal
R5(config)# router bgp 65002
R5(config-router)# address-family ipv6

! Attiva la sessione verso R1 nell'AF ipv6:
R5(config-router-af)# neighbor 172.16.15.1 activate

! Annuncia il loopback IPv6 di R5:
R5(config-router-af)# network 2001:db8:5::5/128

R5(config-router-af)# exit
R5(config-router)# end
```

### Verifica stato finale T3

```
! Verifica che R1 abbia i neighbor attivi nell'AF ipv6:
R1# show bgp ipv6 unicast summary
! Atteso: 4 neighbor (R2/R3/R4 iBGP + R5 eBGP), tutti Established

! Verifica i prefissi IPv6 in tabella BGP su R1:
R1# show bgp ipv6 unicast
! Atteso: 2001:db8:1::/128 ... 2001:db8:5::/128

! Su R4: verifica che 2001:db8:5::5/128 sia presente con next-hop = 2001:db8:1::1
R4# show bgp ipv6 unicast 2001:db8:5::5/128
! Atteso: next-hop 2001:db8:1::1 (R1 grazie a next-hop-self)

! Verifica installazione nella routing table IPv6:
R4# show ipv6 route bgp
```

---

## Note e Varianti

### RR Ridondante

In produzione si configurano 2 RR per ridondanza. Entrambi devono avere lo **stesso cluster-id** per evitare che le route riflesse da RR1 vengano scartate da RR2 (che vedrebbe un cluster-id diverso nella Cluster-List).

```
! Su entrambi gli RR del cluster:
router bgp 65001
 address-family ipv4
  bgp cluster-id 10.0.0.1   ! stesso valore su entrambi
```

### Confederazioni BGP

Alternativa al RR per reti molto grandi: divide l'AS in sotto-AS (confederazioni). Più complesso da gestire; nella pratica il RR è quasi sempre preferito.

### AF IPv6 su sessione TCP IPv6

In alternativa alla sessione TCP IPv4, è possibile usare direttamente indirizzi IPv6 come peer:
```
neighbor 2001:db8:2::2 remote-as 65001
address-family ipv6
 neighbor 2001:db8:2::2 activate
```
Questo richiede raggiungibilità IPv6 tra i peer (ad esempio via OSPFv3 o link-local). Nella maggior parte degli IOU lab, il trasporto su IPv4 con AF ipv6 è più semplice.
