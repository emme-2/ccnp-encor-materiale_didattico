# Soluzione Commentata — MOD-02: OSPFv2 Aree & Summarization

> **Uso:** riservato al docente
> **Prerequisiti cfg:** caricare r1-cfg … r7-cfg da TFTP (stato finale MOD-01 + R1/R2 senza OSPF)

---

## Task T1 — R5 come ABR: Aree 15 e 25

### Configurazione R1 (Area 15)

```
R1(config)# router ospf 100
R1(config-router)# router-id 1.1.1.1
! router-id esplicito obbligatorio prima di abilitare le interfacce
R1(config-router)# exit
!
R1(config)# interface ethernet 0/0.51
R1(config-subif)# ip ospf 100 area 15
! e0/0.51 ha già ip ospf network point-to-point dal cfg iniziale (MOD-01 T4)
```

### Configurazione R2 (Area 25)

```
R2(config)# router ospf 100
R2(config-router)# router-id 2.2.2.2
R2(config-router)# exit
!
R2(config)# interface ethernet 0/0.52
R2(config-subif)# ip ospf 100 area 25
```

### Configurazione R5 — aggiunta spoke area

```
R5(config)# interface ethernet 0/0.51
R5(config-subif)# ip ospf 100 area 15
! e0/0.51 già ha P2P; ora entra nell'area 15
R5(config-subif)# exit
!
R5(config)# interface ethernet 0/0.52
R5(config-subif)# ip ospf 100 area 25
R5(config-subif)# exit
!
R5(config)# router ospf 100
R5(config-router)# no passive-interface ethernet 0/0.51
R5(config-router)# no passive-interface ethernet 0/0.52
! rimuovere passive-interface dalle spoke per abilitare gli hello
```

> 💡 **Nota didattica:** R5 diventa ABR automaticamente quando appartiene a più di un'area. Verificare con `show ip ospf` → riga "It is an area border router". Se non appare, controllare che almeno un'interfaccia sia in area 0 e almeno una in un'altra area.

### Verifica T1

```
R5# show ip ospf
 It is an area border router
 Number of areas in this router is 3. 3 normal 0 stub 0 nssa

R5# show ip ospf neighbor
! Atteso: R1 FULL su e0/0.51, R2 FULL su e0/0.52, R3/R4/R6 FULL su e0/0.3456

R1# show ip route ospf
O IA  10.0.0.0/29 [110/20] via 10.1.15.2, Et0/0.51
O IA  10.1.25.0/30 [110/20] via 10.1.15.2, Et0/0.51
! Le rotte O IA indicano route inter-area apprese via R5 (ABR)
```

---

## Task T2 — Loopback e summarization inter-area

### Configurazione loopback R1 (Area 15)

```
R1(config)# interface loopback 15
R1(config-if)# ip address 192.168.15.1 255.255.255.0
R1(config-if)# ip ospf 100 area 15
R1(config-if)# ip ospf network point-to-point
! P2P su loopback: annuncia /24 anziché il /32 di default
R1(config-if)# exit
!
R1(config)# interface loopback 150
R1(config-if)# ip address 10.15.0.1 255.255.255.0
R1(config-if)# ip ospf 100 area 15
R1(config-if)# ip ospf network point-to-point
R1(config-if)# exit
!
R1(config)# interface loopback 151
R1(config-if)# ip address 10.15.1.1 255.255.255.0
R1(config-if)# ip ospf 100 area 15
R1(config-if)# ip ospf network point-to-point
R1(config-if)# exit
!
R1(config)# interface loopback 152
R1(config-if)# ip address 10.15.2.1 255.255.255.0
R1(config-if)# ip ospf 100 area 15
R1(config-if)# ip ospf network point-to-point
R1(config-if)# exit
```

### Configurazione loopback R2 (Area 25)

```
R2(config)# interface loopback 25
R2(config-if)# ip address 192.168.25.1 255.255.255.0
R2(config-if)# ip ospf 100 area 25
R2(config-if)# ip ospf network point-to-point
R2(config-if)# exit
!
R2(config)# interface loopback 250
R2(config-if)# ip address 10.25.0.1 255.255.255.0
R2(config-if)# ip ospf 100 area 25
R2(config-if)# ip ospf network point-to-point
R2(config-if)# exit
!
R2(config)# interface loopback 251
R2(config-if)# ip address 10.25.1.1 255.255.255.0
R2(config-if)# ip ospf 100 area 25
R2(config-if)# ip ospf network point-to-point
R2(config-if)# exit
!
R2(config)# interface loopback 252
R2(config-if)# ip address 10.25.2.1 255.255.255.0
R2(config-if)# ip ospf 100 area 25
R2(config-if)# ip ospf network point-to-point
R2(config-if)# exit
```

### Configurazione area range su R5 (ABR)

```
R5(config)# router ospf 100
R5(config-router)# area 15 range 10.15.0.0 255.255.252.0
! /22 aggrega: 10.15.0.0/24, 10.15.1.0/24, 10.15.2.0/24 (e 10.15.3.0/24 non usata)
R5(config-router)# area 25 range 10.25.0.0 255.255.252.0
```

> 💡 **Nota didattica:** `area range` funziona solo se i prefissi dell'area sono contigui e rientrano nel range. 10.15.0.0/22 copre .0/24, .1/24, .2/24 e .3/24. Il buco (.3/24 non assegnato) è normale ma va documentato: i router in Area 0 vedranno il summary e non sapranno che il .3/24 è non allocato.

### Verifica T2

```
! Prima della summarization — R4 vede 3 rotte separate:
R4# show ip route ospf
O IA  10.15.0.0/24 [110/20] via 10.0.0.5 ...
O IA  10.15.1.0/24 [110/20] via 10.0.0.5 ...
O IA  10.15.2.0/24 [110/20] via 10.0.0.5 ...

! Dopo area range su R5 — un solo summary:
R4# show ip route ospf
O IA  10.15.0.0/22 [110/20] via 10.0.0.5 ...
! Le singole /24 scompaiono: riduzione LSDB Area 0
```

---

## Task T3 — Stub Area 15 e Totally-Stub Area 25

### Configurazione Area 15 come Stub

```
! Su R5 (ABR):
R5(config)# router ospf 100
R5(config-router)# area 15 stub
! R5 inietta automaticamente LSA Type 3 con 0.0.0.0/0 verso Area 15
R5(config-router)# exit

! Su R1 (router interno):
R1(config)# router ospf 100
R1(config-router)# area 15 stub
! TUTTI i router dell'area devono avere il flag stub — mismatch abbatte l'adiacenza
```

### Configurazione Area 25 come Totally-Stub

```
! Su R5 (ABR) — solo qui il no-summary:
R5(config)# router ospf 100
R5(config-router)# area 25 stub no-summary
! no-summary blocca anche i Type 3 (inter-area) verso Area 25
! l'ABR inietta solo la default 0.0.0.0/0

! Su R2 (router interno) — SOLO stub, mai no-summary sui router interni:
R2(config)# router ospf 100
R2(config-router)# area 25 stub
```

> 💡 **Nota didattica:** `no-summary` va SOLO sull'ABR. Se configurato su un router interno, IOS lo accetta silenziosamente ma lo ignora — fonte di confusione in troubleshooting. Errore comune nell'esame: applicare `no-summary` su entrambi invece che solo sull'ABR.

### Verifica T3

```
R1# show ip route ospf
O*IA 0.0.0.0/0 [110/11] via 10.1.15.2, Et0/0.51   ! default route (stub)
O IA 10.0.0.0/29 [110/20] via 10.1.15.2, Et0/0.51  ! inter-area visibili (non totally)

R2# show ip route ospf
O*IA 0.0.0.0/0 [110/11] via 10.1.25.2, Et0/0.52    ! UNICA rotta OSPF (totally-stub)

R2# show ip ospf database
! Solo: Type 1 (R2) + un singolo Type 3 (0.0.0.0/0) + Type 2 se presente
```

---

## Task T4 — Virtual Link attraverso Area 15

> **Prerequisito:** Area 15 deve essere NORMAL per essere transit area. Se stub configurato in T3, rimuovere prima:
> ```
> R5(config-router)# no area 15 stub
> R1(config-router)# no area 15 stub
> ```

### Setup R7

```
hostname R7
no ip domain-lookup
!
interface ethernet 0/0
 no ip address
 no shutdown
!
interface ethernet 0/0.17
 encapsulation dot1Q 17
 ip address 10.1.17.2 255.255.255.252
 description P2P_to_R1_Area99
 ip ospf 100 area 99
 ip ospf network point-to-point
 no shutdown
!
router ospf 100
 router-id 7.7.7.7
```

### Setup R1 — aggiungere Area 99

```
R1(config)# interface ethernet 0/0.17
R1(config-subif)# ip ospf 100 area 99
R1(config-subif)# ip ospf network point-to-point
R1(config-subif)# exit
!
R1(config)# router ospf 100
R1(config-router)# no passive-interface ethernet 0/0.17
```

### Configurazione Virtual Link

```
! Su R5 (ABR Area 0 / Area 15):
R5(config)# router ospf 100
R5(config-router)# area 15 virtual-link 1.1.1.1
! configurare con il ROUTER-ID del peer (R1), NON con l'IP dell'interfaccia fisica

! Su R1 (ABR Area 15 / Area 99):
R1(config)# router ospf 100
R1(config-router)# area 15 virtual-link 5.5.5.5
! configurare con il ROUTER-ID di R5
```

> 💡 **Nota didattica:** il Virtual Link usa i router-id come identificatori. Errore tipico: specificare l'IP dell'interfaccia (es. 10.1.15.2) invece del router-id (5.5.5.5). Il VL risulta configurato ma va immediatamente in DOWN. Verificare sempre `show ip ospf virtual-links` — stato UP con "Transit area N" confirma il funzionamento.

### Verifica T4

```
R5# show ip ospf virtual-links
Virtual Link OSPF_VL0 to router 1.1.1.1 is up
  Transit area 15, via interface Et0/0.51
  Cost: 10

R5# show ip ospf neighbor
! R1 appare DUE VOLTE: link fisico (e0/0.51) + VL (OSPF_VL0)

R7# show ip route ospf
O IA  10.0.0.0/29 [110/30] via 10.1.17.1, Et0/0.17
! Prefissi di Area 0 ora visibili da R7

R7# ping 10.0.0.4 source 10.1.17.2
!!!!!

! Verifica effetto stub (se Area 15 è stub il VL va DOWN):
! R5# show ip ospf virtual-links → stato DOWN se transit area è stub
```

---

## Task T5 — ASBR: redistribuzione e summary-address

### Configurazione R1 come ASBR

```
! Rotte statiche simulate verso Null0:
R1(config)# ip route 172.16.10.0 255.255.255.0 Null0
R1(config)# ip route 172.16.11.0 255.255.255.0 Null0
R1(config)# ip route 172.16.12.0 255.255.255.0 Null0
!
! Redistribuzione in OSPF:
R1(config)# router ospf 100
R1(config-router)# redistribute static subnets
! 'subnets' obbligatorio: senza, redistribuisce solo rotte classful (/8, /16, /24)
! le /24 sarebbero redistribuite correttamente, ma il parametro va sempre indicato
```

### Applicare summary-address sull'ASBR

```
R1(config)# router ospf 100
R1(config-router)# summary-address 172.16.0.0 255.255.240.0
! /20 aggrega 172.16.0.0–172.16.15.255
! Le singole /24 spariscono dalla LSDB; compare un solo LSA Type 5 con /20
```

> 💡 **Nota didattica:** `summary-address` (su ASBR) aggrega Type 5 (external). `area range` (su ABR) aggrega Type 3 (inter-area). Sono comandi diversi per scopi diversi. Usare `summary-address` senza avere i prefissi specifici nella LSDB non ha effetto — il router genera il summary solo se almeno un componente è presente.

### Verifica T5

```
R4# show ip route ospf
O E2  172.16.0.0/20 [110/20] via 10.0.0.5, Et0/0.3456
! Le singole /24 non compaiono dopo il summary-address

R5# show ip ospf database external
  Link State ID: 172.16.0.0
  Advertising Router: 1.1.1.1
  Network Mask: /20
  Metric Type: 2 (E2)
  Metric: 20
```

---

## Note Varianti & Alternative

**NSSA:** se un'area periferica deve redistribuire rotte esterne localmente (ASBR dentro l'area), usare `area N nssa`. Le rotte vengono annunciate come Type 7 nell'area e convertite in Type 5 dall'ABR. Area 99 in questa topologia potrebbe diventare NSSA se R7 avesse rotte esterne da redistribuire.

**Area 15 stub vs normal per il Virtual Link:** RFC 2328 vieta l'uso di stub come transit area per VL. In produzione: non assegnare mai stub a un'area che potrebbe servire come transit.

**Cost del Virtual Link:** il VL eredita il costo dell'interfaccia fisica sottostante (VLAN 51, costo 10). Non è configurabile direttamente come una vera interfaccia.
