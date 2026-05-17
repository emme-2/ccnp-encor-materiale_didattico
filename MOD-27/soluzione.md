# Soluzione Commentata — MOD-27: NAT/PAT & NTP

> **Uso:** riservato al docente — non distribuire agli studenti

---

## T1 — Static NAT

### R-GW

```
R-GW# configure terminal

! Mapping statico bidirezionale: 192.168.1.10 <-> 203.0.113.10
! Ogni pacchetto con src=192.168.1.10 uscente sul link outside viene tradotto a 203.0.113.10.
! Ogni pacchetto con dst=203.0.113.10 entrante viene inoltrato a 192.168.1.10.
! Il mapping è permanente: esiste anche in assenza di traffico.
R-GW(config)# ip nat inside source static 192.168.1.10 203.0.113.10

R-GW(config)# end
```

### Verifica T1

```
! Mapping presente anche senza traffico:
R-GW# show ip nat translations
! Pro  Inside global     Inside local     Outside local    Outside global
! ---  203.0.113.10      192.168.1.10     ---              ---

! Ping da R-ISP verso l'IP pubblico statico di PC1:
R-ISP# ping 203.0.113.10 source Loopback0
! Atteso: !!!!!

! Ping da PC1 verso internet:
PC1# ping 8.8.8.8
! Atteso: !!!!!
```

---

## T2 — Dynamic NAT con Pool

### R-GW

```
R-GW# configure terminal

! Rimuovere il NAT statico del task precedente:
R-GW(config)# no ip nat inside source static 192.168.1.10 203.0.113.10

! ACL standard che seleziona gli host della LAN interna:
! Una wildcard 0.0.0.255 copre l'intera subnet 192.168.1.0/24.
R-GW(config)# ip access-list standard ACL-INSIDE
R-GW(config-std-nacl)# permit 192.168.1.0 0.0.0.255
R-GW(config-std-nacl)# exit

! Pool di 3 indirizzi pubblici (203.0.113.10 - .12):
! netmask 255.255.255.248 = /29
R-GW(config)# ip nat pool POOL-PUB 203.0.113.10 203.0.113.12 netmask 255.255.255.248

! Collega ACL al pool: ogni host che corrisponde all'ACL riceve un IP dal pool
R-GW(config)# ip nat inside source list ACL-INSIDE pool POOL-PUB

R-GW(config)# end
```

### Verifica T2

```
! Genera traffico da PC1 e PC2 verso 8.8.8.8:
PC1# ping 8.8.8.8
PC2# ping 8.8.8.8

! Osserva i due mapping distinti (IP diversi del pool):
R-GW# show ip nat translations

R-GW# show ip nat statistics
! Total active translations: 2 (0 static, 2 dynamic, 0 extended)
```

---

## T3 — PAT / NAT Overload

### R-GW

```
R-GW# configure terminal

! Rimuovere Dynamic NAT del task precedente (pool non serve piu'):
R-GW(config)# no ip nat inside source list ACL-INSIDE pool POOL-PUB
R-GW(config)# no ip nat pool POOL-PUB

! PAT: usa l'IP dell'interfaccia outside (203.0.113.2) + porta sorgente.
! "overload" attiva la port translation (PAT).
! L'ACL ACL-INSIDE è già configurata (permit 192.168.1.0/24).
R-GW(config)# ip nat inside source list ACL-INSIDE interface Ethernet0/0.10 overload

R-GW(config)# end
```

### Verifica T3

```
PC1# ping 8.8.8.8 repeat 10
PC2# ping 8.8.8.8 repeat 10

! Entrambi usano 203.0.113.2 come inside global con identifier ICMP diverso:
R-GW# show ip nat translations

R-GW# show ip nat statistics
! Le entry PAT sono classified come "extended" nelle statistiche
```

---

## T4 — NTP

### R-ISP (server stratum 1)

```
R-ISP# configure terminal

! Imposta R-ISP come NTP master con stratum 1:
! In lab, stratum 1 è accettabile. In produzione, sincronizzare a GPS/atomic clock.
R-ISP(config)# ntp master 1

! Attiva autenticazione NTP:
R-ISP(config)# ntp authenticate

! Chiave MD5 con ID 1: deve essere identica su server e client.
R-ISP(config)# ntp authentication-key 1 md5 CISCO123

! Dichiara la chiave 1 come trusted:
R-ISP(config)# ntp trusted-key 1

R-ISP(config)# end
```

### R-GW (client)

```
R-GW# configure terminal

! Abilita autenticazione:
R-GW(config)# ntp authenticate
R-GW(config)# ntp authentication-key 1 md5 CISCO123
R-GW(config)# ntp trusted-key 1

! Punta al server NTP con la chiave 1:
R-GW(config)# ntp server 203.0.113.1 key 1

R-GW(config)# end
```

### Verifica T4

```
! Attendere 1-2 minuti per la sincronizzazione NTP.

R-GW# show ntp status
! Clock is synchronized, stratum 2, reference is 203.0.113.1

R-GW# show ntp associations
! *~203.0.113.1  127.127.1.1   1   xx   64  377
! * = selezionato; ~ = autenticato

R-ISP# show ntp status
! Clock is synchronized, stratum 1, reference is 127.127.1.1
```

---

## Note Varianti & Alternative

### NAT con route-map invece di ACL

In ambienti avanzati, si può usare una route-map invece di una ACL per il NAT:
```
route-map RM-NAT permit 10
 match ip address ACL-INSIDE
 match interface Ethernet0/0.10
ip nat inside source route-map RM-NAT interface Ethernet0/0.10 overload
```
Questo permette di aggiungere condizioni aggiuntive (es. solo traffico uscente su un'interfaccia specifica).

### NTP senza autenticazione

In lab semplici, NTP funziona anche senza autenticazione MD5:
```
! Server:
ntp master 1
! Client:
ntp server 203.0.113.1
```
In produzione, l'autenticazione è raccomandata per prevenire NTP spoofing.

### Pulizia NAT

```
! Cancella tutte le entry NAT attive (utile per reset durante i test):
R-GW# clear ip nat translation *
```
