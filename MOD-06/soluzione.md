# Soluzione Commentata — MOD-06: BGP Traffic Engineering

> **Uso:** riservato al docente
> **Prerequisiti cfg:** caricare r1-cfg … r6-cfg da TFTP
> Tutti i peering BGP (iBGP + eBGP R1↔R4 + R3↔R5) già established
> Network statements attivi: R1 annuncia 1.1.1.1/32, R4 annuncia 4.4.4.4/32 e 192.168.45.0/30
> Nessuna route-map, prefix-list, community o local-pref pre-configurata

---

## Task T7 — Default Route: Metodo 1 (network 0.0.0.0)

### Configurazione R1 (ISP border)

```
R1(config)# ip route 0.0.0.0 0.0.0.0 Null0
! rotta statica fittizia verso Null0 — prerequisito per il network statement
! in produzione questa route esisterebbe come default verso l'upstream

R1(config)# router bgp 65001
R1(config-router)# network 0.0.0.0
! senza 'mask': annuncia la rete classless 0.0.0.0/0
! la route viene propagata a TUTTI i neighbor di R1 (iBGP e eBGP)
```

> 💡 **Nota didattica:** `network 0.0.0.0` richiede che 0.0.0.0/0 esista nella routing table. La route statica verso Null0 è la tecnica standard nei lab per soddisfare questo prerequisito. In produzione la default esisterebbe già come route verso l'upstream ISP. Se la route sparisce dal RIB, BGP smette di annunciarla — comportamento condizionale implicito.

### Verifica T7

```
R1# show ip bgp 0.0.0.0
BGP routing table entry for 0.0.0.0/0
  Origin IGP, metric 0, localpref 100, valid, local, best

R4# show ip bgp 0.0.0.0
  172.16.14.1 from 172.16.14.1 (1.1.1.1)
    Origin IGP, metric 0, localpref 100, valid, external, best

R4# show ip route 0.0.0.0
B* 0.0.0.0/0 [20/0] via 172.16.14.1, Et0/0.14
! B* = BGP best path (default candidate)
```

---

## Task T8 — Default Route: Metodo 2 (default-originate)

### Rimozione Metodo 1

```
R1(config)# router bgp 65001
R1(config-router)# no network 0.0.0.0
R1(config)# no ip route 0.0.0.0 0.0.0.0 Null0
```

### Configurazione default-originate

```
! R1 → default verso R4 (link VLAN 14):
R1(config)# router bgp 65001
R1(config-router)# neighbor 172.16.14.2 default-originate
! sintetica: BGP genera la default AL VOO per quel neighbor
! NON richiede 0.0.0.0/0 nella routing table locale
! NON appare in 'show ip bgp' di R1 — è un annuncio virtuale

! R3 → default verso R5 (link VLAN 35):
R3(config)# router bgp 65001
R3(config-router)# neighbor 172.16.35.2 default-originate
```

> 💡 **Nota didattica:** differenza fondamentale: `network 0.0.0.0` è globale (annunciata a tutti) e richiede la route nel RIB; `default-originate` è granulare (solo al neighbor specificato) e non richiede la route nel RIB. Nell'esame: "ISP vuole mandare la default solo al Customer via uno specifico link" → risposta: `default-originate`.

### Verifica T8

```
! Su R1 — la default NON appare nella BGP table locale:
R1# show ip bgp
! 0.0.0.0/0 assente

! Su R4 — la default APPARE come ricevuta:
R4# show ip bgp 0.0.0.0
  172.16.14.1 from 172.16.14.1 (1.1.1.1)
    Origin IGP, valid, external, best

! Verifica dettaglio neighbor:
R1# show ip bgp neighbors 172.16.14.2 | include Default
  Default information originated, sending 0.0.0.0/0 to this neighbor
```

---

## Task T9 — Local Preference: traffico uscente da AS65000

### Configurazione R4

```
! Route-map che imposta Local Preference = 200 sulle route ricevute da R1:
R4(config)# route-map SET-LP-HIGH permit 10
R4(config-route-map)# set local-preference 200
! LOCAL PREFERENCE: higher wins, default 100
! propagato SOLO via iBGP — non esce mai dall'AS
R4(config-route-map)# exit

! Applicare INBOUND sulle route ricevute da R1 (eBGP peer):
R4(config)# router bgp 65000
R4(config-router)# neighbor 172.16.14.1 route-map SET-LP-HIGH in
R4(config-router)# end

! Ri-processare le route già ricevute:
R4# clear ip bgp 172.16.14.1 soft in
```

> 💡 **Nota didattica:** Local Preference si configura INBOUND sul border router che riceve la route eBGP. Errore tipico: applicarlo `out` — non ha effetto (Local Preference non è trasportata in update eBGP). R4 impostandolo a 200 per le route via R1, poi propagandole via iBGP a R5 e R6, fa sì che tutti i router Customer preferiscano uscire via R4↔R1.

### Verifica T9

```
R4# show ip bgp 1.1.1.1
BGP routing table entry for 1.1.1.1/32
Paths: (2 available, best #1)
  65001
    172.16.14.1 from 172.16.14.1 (1.1.1.1)
      Origin IGP, localpref 200, valid, external, best
  65001
    172.16.35.1 from 5.5.5.5 (5.5.5.5)
      Origin IGP, localpref 100, valid, internal

R6# show ip bgp 1.1.1.1
! Deve preferire il path via R4 (LocPrf 200) — traffico esce via R4↔R1
   Network          Next Hop   LocPrf Weight Path
*> 1.1.1.1/32       4.4.4.4    200         0 65001 i
*  1.1.1.1/32       5.5.5.5    100         0 65001 i
```

---

## Task T10 — AS-Path Prepend: traffico entrante in AS65000

### Configurazione R5

```
! Route-map con il prepend:
R5(config)# route-map PREPEND permit 10
R5(config-route-map)# set as-path prepend 65000 65000
! aggiunge DUE copie di 65000 all'AS-Path uscente
! AS-Path risultante su R3: "65000 65000 65000" (vs "65000" via R1)
R5(config-route-map)# exit

! Applicare OUTBOUND verso R3 (link VLAN 35 — il link che si vuole rendere meno preferito):
R5(config)# router bgp 65000
R5(config-router)# neighbor 172.16.35.1 route-map PREPEND out
R5(config-router)# end

! Propagare immediatamente:
R5# clear ip bgp 172.16.35.1 soft out
```

> 💡 **Nota didattica:** AS-Path Prepend si configura OUTBOUND sul link che si vuole rendere MENO preferito. Errore comune: configurarlo `in` invece di `out`. Regola mnemonica: "prependo sul link che voglio sfavorire, in uscita verso il peer che deve vedere il path più lungo".

### Verifica T10

```
! Su R3 — deve vedere AS-Path lungo per il prefisso Customer:
R3# show ip bgp 192.168.45.0
  65000 65000 65000
    172.16.35.2 from 172.16.35.2 (5.5.5.5)
      Origin IGP, valid, external

! Su R1 — deve vedere AS-Path corto:
R1# show ip bgp 192.168.45.0
  65000
    172.16.14.2 from 172.16.14.2 (4.4.4.4)
      Origin IGP, valid, external, best

! Su R2 (router ISP internal) — sceglie il path più corto via R1:
R2# show ip bgp 192.168.45.0
! Best path: 65000 (via R1) vs 65000 65000 65000 (via R3)
! Traffico Internet → Customer entra via R1↔R4
```

---

## Task T-EXTRA — BGP Community

### Abilitare il formato leggibile

```
! Su tutti i router:
(config)# ip bgp-community new-format
! senza questo, la community appare come numero intero (es. 4259840200)
! con questo, appare come 65000:200
```

### Customer R5: taggare annunci con community 65000:200

```
R5(config)# route-map PREPEND permit 10
R5(config-route-map)# set community 65000:200
! aggiungere il tag community oltre al prepend già configurato
R5(config-route-map)# set as-path prepend 65000 65000
R5(config-route-map)# exit

! Abilitare l'invio delle community al peer eBGP:
R5(config)# router bgp 65000
R5(config-router)# neighbor 172.16.35.1 send-community
! su IOS alcune versioni abilitano send-community di default per eBGP;
! in produzione dichiararlo esplicitamente

R5# clear ip bgp 172.16.35.1 soft out
```

### ISP R3: matchare la community e applicare prepend aggiuntivo

```
! Definire la community-list per il matching:
R3(config)# ip community-list standard CUST-TE permit 65000:200

! Route-map con match + action:
R3(config)# route-map APPLY-PREPEND permit 10
R3(config-route-map)# match community CUST-TE
R3(config-route-map)# set as-path prepend 65001 65001
! quando ISP vede community 65000:200, aggiunge ulteriore prepend
R3(config-route-map)# exit

! Permit catch-all — senza questa clausola, tutti gli altri prefissi verrebbero negati:
R3(config)# route-map APPLY-PREPEND permit 20
R3(config-route-map)# exit

R3(config)# router bgp 65001
R3(config-router)# neighbor 172.16.35.2 route-map APPLY-PREPEND in
R3# clear ip bgp 172.16.35.2 soft in
```

> 💡 **Nota didattica:** la community permette al Customer di "comunicare" le sue preferenze all'ISP senza configurare direttamente i router ISP ogni volta. Il Customer taglia la community, l'ISP applica la policy corrispondente in autonomia. Questo è il modello operativo reale delle BGP Communities negli accordi di peering.

### Verifica T-EXTRA

```
! Su R3 — community visibile sul prefisso ricevuto da R5:
R3# show ip bgp 192.168.45.0
  65000 65000 65000
    172.16.35.2 from 172.16.35.2 (5.5.5.5)
      Community: 65000:200

! Su R1 — dopo il prepend ISP applicato da R3:
R1# show ip bgp 192.168.45.0
  65001 65001 65000 65000 65000  ← via R3 (con prepend ISP)
    3.3.3.3 from 3.3.3.3
  65000                          ← via R4 (best: AS-Path più corto)
    172.16.14.2 from 172.16.14.2  best
```

---

## Note Varianti & Alternative

**Local Preference condizionale:** `route-map SET-LP-HIGH` senza `match` imposta LocPref 200 su TUTTE le route ricevute dal peer. Per policy più granulari (es. alzare LocPref solo per prefissi specifici), aggiungere un `match ip address prefix-list`.

**AS-Path Prepend e bilanciamento del carico:** se si vuole bilanciamento equo tra i due link eBGP (invece di primary/backup), usare Equal-Cost Multipath BGP con `maximum-paths 2` e configurare path con AS-Path identici. Il prepend rende i path diseguali → utile per policy primary/backup ma non per load-sharing.

**Community no-export:** per bloccare la propagazione di un prefisso oltre i confini dell'AS vicino, taggare con `community no-export`. Utile per prefissi di management che non devono essere propagati a Internet.
