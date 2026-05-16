# Soluzione Commentata — MOD-05: BGP Fondamenta

> **Uso:** riservato al docente
> **Prerequisiti cfg:** caricare r1-cfg … r6-cfg da TFTP
> AS 65001 (ISP R1-R3): OSPF 1 + iBGP full-mesh + eBGP R1↔R4 PRE-CONFIGURATI
> AS 65000 (Customer R4-R6): OSPF + interfacce ma NESSUN processo BGP

---

## Task T1 — OSPF IGP in AS 65000

### Configurazione R4

```
R4(config)# router ospf 1
R4(config-router)# router-id 4.4.4.4
! router-id esplicito come loopback: convenzione x.x.x.x per leggibilità
R4(config-router)# network 4.4.4.4 0.0.0.0 area 0
! wildcard 0.0.0.0 = host route: solo il loopback esatto
R4(config-router)# network 192.168.45.0 0.0.0.3 area 0
R4(config-router)# network 192.168.46.0 0.0.0.3 area 0
R4(config-router)# passive-interface Loopback0
! loopback: no hello, ma il prefisso viene annunciato nella LSDB
```

### Configurazione R5

```
R5(config)# router ospf 1
R5(config-router)# router-id 5.5.5.5
R5(config-router)# network 5.5.5.5 0.0.0.0 area 0
R5(config-router)# network 192.168.45.0 0.0.0.3 area 0
R5(config-router)# network 192.168.56.0 0.0.0.3 area 0
R5(config-router)# passive-interface Loopback0
```

### Configurazione R6

```
R6(config)# router ospf 1
R6(config-router)# router-id 6.6.6.6
R6(config-router)# network 6.6.6.6 0.0.0.0 area 0
R6(config-router)# network 192.168.46.0 0.0.0.3 area 0
R6(config-router)# network 192.168.56.0 0.0.0.3 area 0
R6(config-router)# passive-interface Loopback0
```

> 💡 **Nota didattica:** l'IGP deve convergere PRIMA di configurare BGP. Le sessioni iBGP usano i loopback come source (update-source Loopback0). Se OSPF non annuncia i loopback, TCP verso il peer BGP fallisce con connessione rifiutata. Verificare `ping 5.5.5.5 source Loopback0` da R4 prima di procedere.

### Verifica T1

```
R4# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
5.5.5.5           1   FULL/DR         00:00:39    192.168.45.2    Et0/0.45
6.6.6.6           1   FULL/DR         00:00:38    192.168.46.2    Et0/0.46

R4# ping 5.5.5.5 source Loopback0
!!!!!
R4# ping 6.6.6.6 source Loopback0
!!!!!
```

---

## Task T2 — iBGP full-mesh in AS 65000

### Configurazione R4

```
R4(config)# router bgp 65000
R4(config-router)# bgp router-id 4.4.4.4
R4(config-router)# neighbor 5.5.5.5 remote-as 65000
! remote-as uguale al proprio: sessione iBGP
R4(config-router)# neighbor 5.5.5.5 update-source Loopback0
! usa Loopback0 come source TCP: stabile anche se un link fisico va down
R4(config-router)# neighbor 5.5.5.5 next-hop-self
! sostituisce il next-hop eBGP (172.16.14.1) con il loopback di R4
! senza questo, R5 e R6 non possono raggiungere 172.16.14.1 → route non valida
R4(config-router)# neighbor 6.6.6.6 remote-as 65000
R4(config-router)# neighbor 6.6.6.6 update-source Loopback0
R4(config-router)# neighbor 6.6.6.6 next-hop-self
```

### Configurazione R5

```
R5(config)# router bgp 65000
R5(config-router)# bgp router-id 5.5.5.5
R5(config-router)# neighbor 4.4.4.4 remote-as 65000
R5(config-router)# neighbor 4.4.4.4 update-source Loopback0
R5(config-router)# neighbor 4.4.4.4 next-hop-self
R5(config-router)# neighbor 6.6.6.6 remote-as 65000
R5(config-router)# neighbor 6.6.6.6 update-source Loopback0
R5(config-router)# neighbor 6.6.6.6 next-hop-self
```

### Configurazione R6

```
R6(config)# router bgp 65000
R6(config-router)# bgp router-id 6.6.6.6
R6(config-router)# neighbor 4.4.4.4 remote-as 65000
R6(config-router)# neighbor 4.4.4.4 update-source Loopback0
R6(config-router)# neighbor 4.4.4.4 next-hop-self
R6(config-router)# neighbor 5.5.5.5 remote-as 65000
R6(config-router)# neighbor 5.5.5.5 update-source Loopback0
R6(config-router)# neighbor 5.5.5.5 next-hop-self
```

> 💡 **Nota didattica:** `next-hop-self` è fondamentale. Senza, la route in BGP table ha `*` (no best) perché il next-hop eBGP (172.16.14.1) non è raggiungibile dai router interni. In `show ip bgp` il `*>` mancante è il segnale diagnostico chiave.

### Verifica T2

```
R4# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
5.5.5.5         4 65000      xx      xx        x    0    0  xx:xx:xx        0
6.6.6.6         4 65000      xx      xx        x    0    0  xx:xx:xx        0
172.16.14.1     4 65001      xx      xx        x    0    0  xx:xx:xx        1

R6# show ip bgp
   Network          Next Hop            Metric LocPrf Weight Path
*> 1.1.1.1/32       4.4.4.4              0    100      0 65001 i
! next-hop = 4.4.4.4 (loopback R4) grazie a next-hop-self
```

---

## Task T3 — Peering mancante R3↔R5

### Diagnosi

```
! Su R5: nessun peer eBGP verso ISP (solo R4 e R6 iBGP):
R5# show ip bgp summary
! Non compare nessun neighbor verso 172.16.35.x

! Verificare che il link fisico e0/0.35 esista e sia up:
R5# show interface ethernet 0/0.35
R5# ping 172.16.35.1
! Se ping risponde → link up, manca solo la configurazione BGP

! Verificare su R3:
R3# show ip bgp summary
! Manca 172.16.35.2 tra i neighbor
```

### Configurazione

```
! Su R3 (AS 65001):
R3(config)# router bgp 65001
R3(config-router)# neighbor 172.16.35.2 remote-as 65000
! eBGP diretto — TTL=1 è sufficiente, ebgp-multihop non necessario

! Su R5 (AS 65000):
R5(config)# router bgp 65000
R5(config-router)# neighbor 172.16.35.1 remote-as 65001
```

> 💡 **Nota didattica:** eBGP usa TTL=1 di default. I peer devono essere direttamente connessi (un hop). In iBGP il TTL è 255, quindi le sessioni via loopback attraverso l'IGP funzionano. Confondere le regole TTL di eBGP e iBGP è un errore frequente nell'esame.

### Verifica T3

```
R5# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
4.4.4.4         4 65000      xx      xx        x    0    0  xx:xx:xx        x
6.6.6.6         4 65000      xx      xx        x    0    0  xx:xx:xx        x
172.16.35.1     4 65001      xx      xx        x    0    0  xx:xx:xx        1

R6# show ip bgp 1.1.1.1
! Due path verso 1.1.1.1: via R4 (eBGP R1↔R4) e via R5 (eBGP R3↔R5)
```

---

## Task T4 — Annunci BGP: network statement vs redistribute

### Parte A — network statement (Origin IGP = i)

```
R4(config)# router bgp 65000
R4(config-router)# network 4.4.4.4 mask 255.255.255.255
! 'mask' obbligatoria su IOS: specifica la subnet esatta
! La route 4.4.4.4/32 deve esistere nel RIB (è il loopback connected)
R4(config-router)# network 192.168.45.0 mask 255.255.255.252
! 192.168.45.0/30 è nel RIB come connected → OK
```

### Parte B — redistribute connected (Origin Incomplete = ?)

```
R4(config)# router bgp 65000
R4(config-router)# redistribute connected
! redistribuisce TUTTE le rotte connected incluse sub-interface e loopback
! Origin = ? (Incomplete): sorgente non-BGP → meno preferito di Origin IGP (i)
```

### Cleanup (da fare prima di T5)

```
R4(config)# router bgp 65000
R4(config-router)# no redistribute connected
```

### Verifica T4

```
R4# show ip bgp
   Network          Next Hop            Metric LocPrf Weight Path
*> 1.1.1.1/32       172.16.14.1              0             0 65001 i
*> 4.4.4.4/32       0.0.0.0                  0         32768 i   ← network stmt
*> 192.168.45.0/30  0.0.0.0                  0         32768 i   ← network stmt
*> 192.168.46.0/30  0.0.0.0                  0         32768 ?   ← redistribute
! 'i' = Origin IGP | '?' = Origin Incomplete
! Weight 32768 = annunci originati localmente
```

---

## Task T5 — Filtro con prefix-list e route-map

### Configurazione R4 — filtro outbound verso R1

```
! Definire i prefissi ammessi:
R4(config)# ip prefix-list CUSTOMER-OUT seq 10 permit 4.4.4.4/32
R4(config)# ip prefix-list CUSTOMER-OUT seq 20 permit 192.168.45.0/30
R4(config)# ip prefix-list CUSTOMER-OUT seq 30 deny 0.0.0.0/0 le 32
! deny finale esplicito: best practice per leggibilità (IOS aggiunge un deny implicito)

! Route-map che usa la prefix-list:
R4(config)# route-map FILTER-TO-ISP permit 10
R4(config-route-map)# match ip address prefix-list CUSTOMER-OUT
R4(config-route-map)# exit

! Applicare outbound verso R1:
R4(config)# router bgp 65000
R4(config-router)# neighbor 172.16.14.1 route-map FILTER-TO-ISP out

! Propagare immediatamente senza hard reset:
R4# clear ip bgp 172.16.14.1 soft out
```

> 💡 **Nota didattica:** una route-map senza clausola `match` fa passare tutto (permit implicito). Una prefix-list senza deny finale blocca il resto implicitamente. L'ordine `seq` è importante: il primo match vince. Errore comune: dimenticare il deny finale e avere una route-map "permit senza match" che passa tutto.

### Verifica T5

```
R4# show ip bgp neighbors 172.16.14.1 advertised-routes
   Network          Next Hop            Metric LocPrf Weight Path
*> 4.4.4.4/32       0.0.0.0                  0         32768 i
*> 192.168.45.0/30  0.0.0.0                  0         32768 i
Total number of prefixes 2
```

---

## Task T6 — Soft-reconfiguration inbound

### Configurazione

```
R5(config)# router bgp 65000
R5(config-router)# neighbor 172.16.35.1 soft-reconfiguration inbound
! Memorizza tutte le route ricevute pre-policy nella Pre-Policy RIB
! Costo: memoria proporzionale al numero di prefissi ricevuti dal peer

! Aggiornare la view senza abbattere la sessione:
R5# clear ip bgp 172.16.35.1 soft in
```

### Verifica T6

```
! Route pre-policy (tutti i prefissi ricevuti da R3 prima dei filtri):
R5# show ip bgp neighbors 172.16.35.1 received-routes

! Route post-policy (installate nella BGP table):
R5# show ip bgp

! Soft reset bilaterale (inbound + outbound):
R5# clear ip bgp 172.16.35.1 soft
```

> 💡 **Nota didattica:** `clear ip bgp X` (hard reset) abbatte la sessione TCP → interrompe il traffico. In produzione usare sempre il soft reset. `soft-reconfiguration inbound` è il prerequisito per `show received-routes`: senza, IOS restituisce errore ("Inbound soft reconfiguration not enabled").

---

## Note Varianti & Alternative

**Route Reflector vs full-mesh:** il full-mesh iBGP scala male (N*(N-1)/2 sessioni). In AS con molti router usare Route Reflector (MOD-07). In questo modulo il full-mesh è intenzionale per insegnare la regola split-horizon iBGP.

**Peer groups:** per configurazioni iBGP con molti peer identici, usare `neighbor PEER-GROUP peer-group` per raggruppare la configurazione e ridurre le righe di config senza cambiare il comportamento.

**network mask vs network classful:** su IOS, `network 4.4.4.4` senza `mask` usa la maschera classful (/8 per indirizzi classe A!). Usare SEMPRE `network X.X.X.X mask Y.Y.Y.Y` per evitare comportamenti inaspettati.
