# Soluzione Commentata — MOD-01: OSPFv2 Fondamenta

> **Uso:** riservato al docente — non distribuire agli studenti prima del completamento del lab
> **Prerequisiti cfg:** caricare i file `r1-cfg` … `r7-cfg` da TFTP prima di iniziare

---

## Task T1 — Configurazione sub-interface e OSPF base su R3

### Configurazione R3 (da zero)

```
hostname R3
no ip domain-lookup
!
interface ethernet 0/0
 no ip address
 no shutdown
! L'interfaccia fisica padre deve essere up senza IP — è il trunk verso Switch1
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.3 255.255.255.248
 description Core_Broadcast_Area0
 no shutdown
! /29 = 8 indirizzi: .1 network, .2-.6 host (R3=.3, R4=.4, R5=.5, R6=.6), .7 broadcast
!
interface ethernet 0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.1 255.255.255.252
 description P2P_R3-R4_Ring_Area0
 no shutdown
!
interface ethernet 0/0.36
 encapsulation dot1Q 36
 ip address 10.0.36.1 255.255.255.252
 description P2P_R3-R6_Ring_Area0
 no shutdown
!
router ospf 100
 router-id 3.3.3.3
 ! router-id esplicito: evita variazioni al riavvio o cambio IP
 network 10.0.0.0 0.0.0.7 area 0
 ! wildcard 0.0.0.7 copre la /29 del Broadcast segment
 passive-interface default
 ! blocca hello su TUTTE le interfacce per default — pratica sicura
 no passive-interface ethernet 0/0.3456
 ! riabilita gli hello solo sull'interfaccia dove vogliamo adiacenze
```

> 💡 **Nota didattica:** `passive-interface default` + `no passive-interface` selettivo è la best practice di produzione. Evita di inviare hello su loopback e interfacce verso end-user. L'errore più comune è dimenticare `no passive-interface` dopo `passive-interface default` — il router entra in stato WAIT e non forma mai adiacenze.

### Verifica attesa dopo T1

```
R3# show ip ospf interface brief
Interface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C
Et0/0.3456   100   0               10.0.0.3/29        10    WAIT  0/0

! Stato WAIT = normale su broadcast senza neighbor ancora attivi
! Dopo che R4 e R6 si avvieranno → diventerà DROTHER o DR/BDR
```

---

## Task T2 — Troubleshooting adiacenze: diagnostica e correzione

### Missconfiguration presenti nei cfg iniziali

I router R3, R4, R5 hanno tre tipi distinti di errori. R6 è il riferimento corretto.

> **Nota per il docente:** i cfg di partenza di R4 e R5 contengono le missconfiguration descritte. R3 parte senza OSPF (T1 è il task di configurazione). La "missconfiguration su R3" si manifesta se lo studente dimentica `no passive-interface` durante T1.

#### Missconfiguration R3 — passive-interface dimenticato

**Sintomo:** R3 non forma adiacenze su e0/0.3456; `show ip ospf interface e0/0.3456` mostra stato PASSIVE
**Causa:** `passive-interface default` attivo senza `no passive-interface ethernet 0/0.3456`
**Fix:**
```
R3(config)# router ospf 100
R3(config-router)# no passive-interface ethernet 0/0.3456
```

#### Missconfiguration R4 — area errata (area 1 invece di area 0)

**Sintomo:** R6 vede R4 in `debug ip ospf adj` ma l'adiacenza non avanza oltre INIT; area mismatch nei log
**Causa:** `network 10.0.0.0 0.0.0.7 area 1` (area 1 sbagliata)
**Diagnosi:**
```
R4# show running-config | section router ospf
router ospf 100
 router-id 4.4.4.4
 network 10.0.0.0 0.0.0.7 area 1   ← errore: deve essere area 0
```
**Fix:**
```
R4(config)# router ospf 100
R4(config-router)# no network 10.0.0.0 0.0.0.7 area 1
R4(config-router)# network 10.0.0.0 0.0.0.7 area 0
```

> 💡 **Nota didattica:** l'area mismatch blocca l'adiacenza subito dopo lo scambio di Hello. Il router vede il hello del neighbor ma lo rifiuta perché il campo Area ID non corrisponde. Il neighbor compare in `show ip ospf neighbor` in stato INIT o non compare affatto (dipende dalla versione IOS). `debug ip ospf adj` mostra "Mismatched hello parameters from..." con dettaglio area.

#### Missconfiguration R5 — autenticazione MD5 senza corrispondenza

**Sintomo:** R5 non forma adiacenza con R6/R3/R4 su e0/0.3456; `show ip ospf interface e0/0.3456` mostra "Message digest authentication"
**Causa:** `ip ospf authentication message-digest` configurato su R5 ma non sugli altri router
**Diagnosi:**
```
R5# show ip ospf interface ethernet 0/0.3456
  Message digest authentication enabled
  No key configured, use default key id 0  ← o chiave presente ma non matching
```
**Fix:**
```
R5(config)# interface ethernet 0/0.3456
R5(config-subif)# no ip ospf authentication
R5(config-subif)# no ip ospf message-digest-key 1 md5 0 WRONG_KEY
```

> 💡 **Nota didattica:** l'autenticazione mismatch mantiene il neighbor in INIT. I pacchetti Hello vengono scartati silenziosamente se la chiave non corrisponde. `debug ip ospf adj` mostra "Dead" expiry o "Auth type mismatch". Errore classico negli ambienti che migrano da autenticazione area a plain-text o MD5.

### Configurazione R4 completa dopo fix T2

```
hostname R4
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.4 255.255.255.248
 description Core_Broadcast_Area0
 no shutdown
!
interface ethernet 0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.2 255.255.255.252
 description P2P_R3-R4_Ring_Area0
 no shutdown
!
interface ethernet 0/0.45
 encapsulation dot1Q 45
 ip address 10.0.45.1 255.255.255.252
 description P2P_R4-R5_Ring_Area0
 no shutdown
!
router ospf 100
 router-id 4.4.4.4
 network 10.0.0.0 0.0.0.7 area 0
 passive-interface default
 no passive-interface ethernet 0/0.3456
```

### Configurazione R5 completa dopo fix T2

```
hostname R5
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.5 255.255.255.248
 description Core_Broadcast_Area0
 no shutdown
! Rimuovere: ip ospf authentication / ip ospf message-digest-key
!
interface ethernet 0/0.51
 encapsulation dot1Q 51
 ip address 10.1.15.2 255.255.255.252
 description P2P_to_R1_Area15
 no shutdown
!
interface ethernet 0/0.52
 encapsulation dot1Q 52
 ip address 10.1.25.2 255.255.255.252
 description P2P_to_R2_Area25
 no shutdown
!
interface ethernet 0/0.45
 encapsulation dot1Q 45
 ip address 10.0.45.2 255.255.255.252
 description P2P_R4-R5_Ring_Area0
 no shutdown
!
interface ethernet 0/0.56
 encapsulation dot1Q 56
 ip address 10.0.56.1 255.255.255.252
 description P2P_R5-R6_Ring_Area0
 no shutdown
!
router ospf 100
 router-id 5.5.5.5
 network 10.0.0.0 0.0.0.7 area 0
 passive-interface default
 no passive-interface ethernet 0/0.3456
```

### Verifica finale T2

```
R5# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
3.3.3.3           1   FULL/DROTHER    00:00:38    10.0.0.3        Et0/0.3456
4.4.4.4           1   FULL/DR         00:00:36    10.0.0.4        Et0/0.3456
6.6.6.6           1   FULL/BDR        00:00:37    10.0.0.6        Et0/0.3456
! DR/BDR dipende dall'ordine di avvio: conta il numero di FULL
```

---

## Task T3 — Core Ring: ip ospf area e network type P2P

### Configurazione R3 — Ring links

```
R3(config)# interface ethernet 0/0.34
R3(config-subif)# ip ospf 100 area 0
! metodo diretto sull'interfaccia: più esplicito del network statement
R3(config-subif)# ip ospf network point-to-point
! elimina DR/BDR su link con un solo neighbor → convergenza più rapida
R3(config-subif)# ip ospf cost 1000
! costo elevato: il Ring è ridondanza, non percorso preferito
R3(config-subif)# exit
!
R3(config)# interface ethernet 0/0.36
R3(config-subif)# ip ospf 100 area 0
R3(config-subif)# ip ospf network point-to-point
R3(config-subif)# ip ospf cost 1000
R3(config-subif)# exit
!
! Aggiornare il processo OSPF per escludere le Ring da passive:
R3(config)# router ospf 100
R3(config-router)# no passive-interface ethernet 0/0.34
R3(config-router)# no passive-interface ethernet 0/0.36
```

### Configurazione R4 — Ring links

```
R4(config)# interface ethernet 0/0.34
R4(config-subif)# ip ospf 100 area 0
R4(config-subif)# ip ospf network point-to-point
R4(config-subif)# ip ospf cost 1000
R4(config-subif)# exit
!
R4(config)# interface ethernet 0/0.45
R4(config-subif)# ip ospf 100 area 0
R4(config-subif)# ip ospf network point-to-point
R4(config-subif)# ip ospf cost 1000
R4(config-subif)# exit
!
R4(config)# router ospf 100
R4(config-router)# no passive-interface ethernet 0/0.34
R4(config-router)# no passive-interface ethernet 0/0.45
```

### Configurazione R5 — Ring links

```
R5(config)# interface ethernet 0/0.45
R5(config-subif)# ip ospf 100 area 0
R5(config-subif)# ip ospf network point-to-point
R5(config-subif)# ip ospf cost 1000
R5(config-subif)# exit
!
R5(config)# interface ethernet 0/0.56
R5(config-subif)# ip ospf 100 area 0
R5(config-subif)# ip ospf network point-to-point
R5(config-subif)# ip ospf cost 1000
R5(config-subif)# exit
!
R5(config)# router ospf 100
R5(config-router)# no passive-interface ethernet 0/0.45
R5(config-router)# no passive-interface ethernet 0/0.56
```

### Configurazione R6 — Ring links

```
R6(config)# interface ethernet 0/0.36
R6(config-subif)# ip ospf 100 area 0
R6(config-subif)# ip ospf network point-to-point
R6(config-subif)# ip ospf cost 1000
R6(config-subif)# exit
!
R6(config)# interface ethernet 0/0.56
R6(config-subif)# ip ospf 100 area 0
R6(config-subif)# ip ospf network point-to-point
R6(config-subif)# ip ospf cost 1000
R6(config-subif)# exit
!
R6(config)# router ospf 100
R6(config-router)# no passive-interface ethernet 0/0.36
R6(config-router)# no passive-interface ethernet 0/0.56
```

### Verifica T3

```
R3# show ip ospf interface brief
Interface    PID   Area    IP Address/Mask     Cost  State Nbrs F/C
Et0/0.3456   100   0       10.0.0.3/29         10    DR    3/3
Et0/0.34     100   0       10.0.34.1/30        1000  P2P   1/1
Et0/0.36     100   0       10.0.36.1/30        1000  P2P   1/1

R4# show ip ospf interface ethernet 0/0.34
  Network Type POINT_TO_POINT, Cost: 1000
  No designated router on this network
  Neighbor Count is 1, Adjacent neighbor count is 1
    Adjacent with neighbor 3.3.3.3
```

> 💡 **Nota didattica:** `ip ospf cost 1000` sul Ring crea una preferenza chiara: il traffico normale usa il Broadcast segment (costo 10), il Ring è la ridondanza (costo 1000). Senza questo, OSPF potrebbe scegliere path subottimali. In produzione impostare sempre `auto-cost reference-bandwidth 10000` (10Gbps) su tutti i router prima di configurare i costi manuali.

---

## Task T4 — DR/BDR election: analisi e controllo

### Configurazione R4 — DR (priority 255)

```
R4(config)# interface ethernet 0/0.3456
R4(config-subif)# ip ospf priority 255
! 255 = massimo → R4 sarà sempre eletto DR su questo segmento
```

### Configurazione R6 — BDR (priority 100)

```
R6(config)# interface ethernet 0/0.3456
R6(config-subif)# ip ospf priority 100
! 100 > default (1) → R6 sarà BDR
```

### Configurazione R3 e R5 — esclusi da elezione

```
R3(config)# interface ethernet 0/0.3456
R3(config-subif)# ip ospf priority 0
! priority 0 = escluso dall'elezione DR/BDR

R5(config)# interface ethernet 0/0.3456
R5(config-subif)# ip ospf priority 0
```

### Forzare la rielelezione

```
R4# clear ip ospf process
! Rispondere YES — riavvia il processo e forza una nuova elezione
! Attendere 30-60 secondi per la riconvergenza
```

### Configurazione P2P sui link spoke (R1/R2 ↔ R5)

```
! Su R1 (link VLAN 51):
R1(config)# interface ethernet 0/0.51
R1(config-subif)# ip ospf network point-to-point
! Non in OSPF ancora — il network type è impostato ora per MOD-02

! Su R5:
R5(config)# interface ethernet 0/0.51
R5(config-subif)# ip ospf network point-to-point
R5(config)# interface ethernet 0/0.52
R5(config-subif)# ip ospf network point-to-point

! Su R2 (link VLAN 52):
R2(config)# interface ethernet 0/0.52
R2(config-subif)# ip ospf network point-to-point
```

### Verifica finale T4

```
R4# show ip ospf interface ethernet 0/0.3456
  Network Type BROADCAST, Cost: 10
  Designated Router (ID) 4.4.4.4, Interface address 10.0.0.4
  Backup Designated Router (ID) 6.6.6.6, Interface address 10.0.0.6

R4# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
3.3.3.3           0   FULL/DROTHER    00:00:38    10.0.0.3        Et0/0.3456
5.5.5.5           0   FULL/DROTHER    00:00:36    10.0.0.5        Et0/0.3456
6.6.6.6         100   FULL/BDR        00:00:37    10.0.0.6        Et0/0.3456
```

> 💡 **Nota didattica:** modificare la priority NON forza immediatamente la rielelezione — l'elezione OSPF non è preemptive. `clear ip ospf process` è invasivo (interrompe tutte le adiacenze) ma necessario per forzare la nuova elezione. In produzione pianificare una finestra di manutenzione.

---

## Stato finale MOD-01 — Riepilogo configurazione completa

### R3 — stato finale

```
hostname R3
no ip domain-lookup
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.3 255.255.255.248
 description Core_Broadcast_Area0
 ip ospf priority 0
 no shutdown
!
interface ethernet 0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.1 255.255.255.252
 description P2P_R3-R4_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
interface ethernet 0/0.36
 encapsulation dot1Q 36
 ip address 10.0.36.1 255.255.255.252
 description P2P_R3-R6_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
router ospf 100
 router-id 3.3.3.3
 network 10.0.0.0 0.0.0.7 area 0
 passive-interface default
 no passive-interface ethernet 0/0.3456
 no passive-interface ethernet 0/0.34
 no passive-interface ethernet 0/0.36
```

### R4 — stato finale

```
hostname R4
no ip domain-lookup
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.4 255.255.255.248
 description Core_Broadcast_Area0
 ip ospf priority 255
 no shutdown
!
interface ethernet 0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.2 255.255.255.252
 description P2P_R3-R4_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
interface ethernet 0/0.45
 encapsulation dot1Q 45
 ip address 10.0.45.1 255.255.255.252
 description P2P_R4-R5_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
router ospf 100
 router-id 4.4.4.4
 network 10.0.0.0 0.0.0.7 area 0
 passive-interface default
 no passive-interface ethernet 0/0.3456
 no passive-interface ethernet 0/0.34
 no passive-interface ethernet 0/0.45
```

### R5 — stato finale

```
hostname R5
no ip domain-lookup
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.5 255.255.255.248
 description Core_Broadcast_Area0
 ip ospf priority 0
 no shutdown
!
interface ethernet 0/0.51
 encapsulation dot1Q 51
 ip address 10.1.15.2 255.255.255.252
 description P2P_to_R1_Area15
 ip ospf network point-to-point
 no shutdown
!
interface ethernet 0/0.52
 encapsulation dot1Q 52
 ip address 10.1.25.2 255.255.255.252
 description P2P_to_R2_Area25
 ip ospf network point-to-point
 no shutdown
!
interface ethernet 0/0.45
 encapsulation dot1Q 45
 ip address 10.0.45.2 255.255.255.252
 description P2P_R4-R5_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
interface ethernet 0/0.56
 encapsulation dot1Q 56
 ip address 10.0.56.1 255.255.255.252
 description P2P_R5-R6_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
router ospf 100
 router-id 5.5.5.5
 network 10.0.0.0 0.0.0.7 area 0
 passive-interface default
 no passive-interface ethernet 0/0.3456
 no passive-interface ethernet 0/0.45
 no passive-interface ethernet 0/0.56
```

### R6 — stato finale

```
hostname R6
no ip domain-lookup
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.3456
 encapsulation dot1Q 3456
 ip address 10.0.0.6 255.255.255.248
 description Core_Broadcast_Area0
 ip ospf priority 100
 no shutdown
!
interface ethernet 0/0.36
 encapsulation dot1Q 36
 ip address 10.0.36.2 255.255.255.252
 description P2P_R3-R6_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
interface ethernet 0/0.56
 encapsulation dot1Q 56
 ip address 10.0.56.2 255.255.255.252
 description P2P_R5-R6_Ring_Area0
 ip ospf 100 area 0
 ip ospf network point-to-point
 ip ospf cost 1000
 no shutdown
!
router ospf 100
 router-id 6.6.6.6
 network 10.0.0.0 0.0.0.7 area 0
 passive-interface default
 no passive-interface ethernet 0/0.3456
 no passive-interface ethernet 0/0.36
 no passive-interface ethernet 0/0.56
```

---

## Note Varianti & Alternative

**Network statement vs ip ospf area:** Entrambi i metodi coesistono in questo lab (rete didattica). In produzione usare `ip ospf area` per interfaccia — è più esplicito e meno soggetto a errori con wildcard permissivi.

**auto-cost reference-bandwidth:** Non impostato in questo lab perché IOU usa interfacce simulated con la stessa bandwidth. In produzione con link misti (Fast/Giga/10G): impostare `auto-cost reference-bandwidth 10000` (10Gbps) su tutti i router prima di configurare qualsiasi costo manuale.

**Loopback come Router-ID:** la convenzione x.x.x.x (R1=1.1.1.1) è adottata per leggibilità dei log. In produzione usare un indirizzo loopback reale non-routato (es. 192.168.255.x) per il Router-ID.
