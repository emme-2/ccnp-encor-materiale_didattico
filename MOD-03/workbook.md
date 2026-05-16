# Workbook Studenti — MOD-03: OSPFv3 Dual-Stack

**Area:** AREA 1 — OSPF | **Ore:** 1.5h | **Codici syllabus:** 3.2.b

---

## 1. TOPOLOGIA

### Diagramma logico

```
                        [Switch1 — IOU L2]
          ┌──────┬──────┬──────┬──────┬──────┬──────┐
          R1     R2     R3     R4     R5     R6

Stessa topologia fisica di MOD-01/02 — dual-stack IPv4 + IPv6 su ogni segmento.

Aree OSPFv3 (identiche alle aree OSPFv2):
  Area 0:  R3, R4, R5, R6 — VLAN 3456, 34, 36, 45, 56
  Area 15: R1 ↔ R5 — VLAN 51
  Area 25: R2 ↔ R5 — VLAN 52
```

### Tabella di indirizzamento IPv6

| Router | Interfaccia    | VLAN | IPv6 Global             | Link-Local   | Area OSPF |
|--------|----------------|------|-------------------------|--------------|-----------|
| R1     | e0/0.51        | 51   | 2001:db8:15::1/64       | fe80::1      | Area 15   |
| R1     | Lo15           | —    | 2001:db8:1:15::1/64     | —            | Area 15   |
| R2     | e0/0.52        | 52   | 2001:db8:25::1/64       | fe80::2      | Area 25   |
| R2     | Lo25           | —    | 2001:db8:2:25::1/64     | —            | Area 25   |
| R3     | e0/0.3456      | 3456 | 2001:db8:0::3/64        | fe80::3      | Area 0    |
| R3     | e0/0.34        | 34   | 2001:db8:34::3/64       | fe80::3      | Area 0    |
| R3     | e0/0.36        | 36   | 2001:db8:36::3/64       | fe80::3      | Area 0    |
| R4     | e0/0.3456      | 3456 | 2001:db8:0::4/64        | fe80::4      | Area 0    |
| R4     | e0/0.34        | 34   | 2001:db8:34::4/64       | fe80::4      | Area 0    |
| R4     | e0/0.45        | 45   | 2001:db8:45::4/64       | fe80::4      | Area 0    |
| R5     | e0/0.51        | 51   | 2001:db8:15::5/64       | fe80::5      | Area 15   |
| R5     | e0/0.52        | 52   | 2001:db8:25::5/64       | fe80::5      | Area 25   |
| R5     | e0/0.3456      | 3456 | 2001:db8:0::5/64        | fe80::5      | Area 0    |
| R5     | e0/0.45        | 45   | 2001:db8:45::5/64       | fe80::5      | Area 0    |
| R5     | e0/0.56        | 56   | 2001:db8:56::5/64       | fe80::5      | Area 0    |
| R6     | e0/0.3456      | 3456 | 2001:db8:0::6/64        | fe80::6      | Area 0    |
| R6     | e0/0.36        | 36   | 2001:db8:36::6/64       | fe80::6      | Area 0    |
| R6     | e0/0.56        | 56   | 2001:db8:56::6/64       | fe80::6      | Area 0    |

> **Piano IPv6 loopback aggiuntive R1:** 2001:db8:1:150::1/64, 2001:db8:1:151::1/64, 2001:db8:1:152::1/64 (Area 15)
> **Piano IPv6 loopback aggiuntive R2:** 2001:db8:2:250::1/64, 2001:db8:2:251::1/64, 2001:db8:2:252::1/64 (Area 25)

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sara' in grado di:

- [ ] Abilitare IPv6 unicast routing e configurare indirizzi IPv6 globali e link-local statici sulle sub-interface
- [ ] Configurare OSPFv3 standard (IPv6 native) per processo e interfaccia, comprendendo le differenze rispetto a OSPFv2
- [ ] Analizzare la LSDB OSPFv3 e identificare i nuovi tipi di LSA (Type 8, 9)
- [ ] Configurare OSPFv3 Address Families (AF) per trasportare simultaneamente IPv4 e IPv6 in un singolo processo ospfv3
- [ ] Confrontare OSPFv3 standard e OSPFv3 AF: differenze di configurazione, verifica e comportamento

**Codici syllabus coperti:** 3.2.b

---

## 3. LAB SETUP

### Prerequisiti

- **MOD-01 completato:** sub-interface configurate, adiacenze OSPFv2 operative
- IPv4 funzionante su tutti i segmenti — verificare con ping prima di procedere
- Tutti i router IOU devono supportare `ipv6 unicast-routing` (standard su IOU L3)

### File cfg da caricare via TFTP

```
configure replace tftp://192.168.122.1/ENCOR/MOD-03/r1-cfg
configure replace tftp://192.168.122.1/ENCOR/MOD-03/r2-cfg
configure replace tftp://192.168.122.1/ENCOR/MOD-03/r3-cfg
configure replace tftp://192.168.122.1/ENCOR/MOD-03/r4-cfg
configure replace tftp://192.168.122.1/ENCOR/MOD-03/r5-cfg
configure replace tftp://192.168.122.1/ENCOR/MOD-03/r6-cfg
```

> **NOTA:** I file cfg TFTP non sono ancora disponibili. Placeholder — saranno generati nella prossima versione del modulo. Se si proviene direttamente da MOD-01, la configurazione IPv4 OSPFv2 e' gia' presente — aggiungere solo la configurazione IPv6 e OSPFv3.

### Verifica pre-lab

```
! Verificare che il processo OSPFv2 sia funzionante:
R5# show ip ospf neighbor
! Atteso: R1 (Area 15), R2 (Area 25), R3/R4/R6 (Area 0) tutti in FULL

! Verificare connettivita' IPv4:
R1# ping 10.0.0.4
R4# ping 10.1.15.1

! Verificare che IPv6 non sia ancora configurato:
R3# show ipv6 interface brief
! Atteso: nessuna interfaccia IPv6 attiva
```

---

## 4. TASK LIST

| # | Task | Codice syllabus | Tempo stimato |
|---|------|-----------------|---------------|
| **T1** | Prerequisiti IPv6 e indirizzamento sub-interface | 3.2.b | 15 min |
| **T2** | OSPFv3 standard (IPv6 native) — Core e spoke area | 3.2.b | 20 min |
| **T3** | Loopback IPv6 e summarization OSPFv3 | 3.2.b | 15 min |
| **T4** | OSPFv3 Address Families: dual-stack IPv4+IPv6 | 3.2.b | 25 min |

---

## 5. DETTAGLIO TASK

---

### T1 — Prerequisiti IPv6 e indirizzamento sub-interface

#### TEORIA

**IPv6 unicast routing**

Il routing IPv6 e' disabilitato per default su IOS. Va abilitato globalmente con:

```
ipv6 unicast-routing
```

Senza questo comando, il router processa i pacchetti IPv6 ricevuti ma non li instrada.

**Indirizzi link-local**

Ogni interfaccia IPv6 ha automaticamente un indirizzo link-local (fe80::/10), derivato dal MAC address (EUI-64). In ambienti IOU, questo indirizzo e' spesso uguale tra le interfacce perche' il MAC viene derivato in modo simile.

OSPFv3 usa i link-local come indirizzo sorgente per i pacchetti Hello e come next-hop nelle rotte. E' buona pratica configurare link-local **statici** per rendere i log e la tabella neighbor leggibili:

```
interface ethernet 0/0.3456
  ipv6 address fe80::3 link-local   ! manuale, facile da leggere
  ipv6 address 2001:db8:0::3/64
```

**Differenze di indirizzamento IPv6 vs IPv4**

| Aspetto | IPv4 | IPv6 |
|---------|------|------|
| Indirizzo link-local | Non standard (169.254.x.x solo APIPA) | Obbligatorio su ogni interfaccia IPv6 |
| Notazione | x.x.x.x | xxxx:xxxx:xxxx::x (abbreviabile) |
| Maschera di rete | Classful o CIDR (/24, /30) | Solo prefisso (/64 su LAN, /128 su loopback) |
| Broadcast | Si' (224.0.0.5 per OSPF) | No broadcast — solo multicast (FF02::5, FF02::6) |

#### TASK

**Step 1 — Abilitare IPv6 unicast routing su tutti i router**

```
! Ripetere su R1, R2, R3, R4, R5, R6:
Rx(config)# ipv6 unicast-routing
```

**Step 2 — Configurare indirizzi IPv6 su R3 (esempio di riferimento)**

```
R3(config)# interface ethernet 0/0.3456
R3(config-subif)# ipv6 address 2001:db8:0::3/64
R3(config-subif)# ipv6 address fe80::3 link-local
R3(config-subif)# exit

R3(config)# interface ethernet 0/0.34
R3(config-subif)# ipv6 address 2001:db8:34::3/64
R3(config-subif)# ipv6 address fe80::3 link-local
R3(config-subif)# exit

R3(config)# interface ethernet 0/0.36
R3(config-subif)# ipv6 address 2001:db8:36::3/64
R3(config-subif)# ipv6 address fe80::3 link-local
R3(config-subif)# exit
```

**Step 3 — Replicare su R4, R5, R6, R1, R2 (usare la tabella di indirizzamento)**

```
! R4: e0/0.3456 → 2001:db8:0::4/64, fe80::4 / e0/0.34 → 2001:db8:34::4/64 / e0/0.45 → 2001:db8:45::4/64
! R5: e0/0.3456 → 2001:db8:0::5/64 / e0/0.51 → 2001:db8:15::5/64 / e0/0.52 → 2001:db8:25::5/64
!     e0/0.45 → 2001:db8:45::5/64 / e0/0.56 → 2001:db8:56::5/64
! R6: e0/0.3456 → 2001:db8:0::6/64 / e0/0.36 → 2001:db8:36::6/64 / e0/0.56 → 2001:db8:56::6/64
! R1: e0/0.51 → 2001:db8:15::1/64, fe80::1
! R2: e0/0.52 → 2001:db8:25::1/64, fe80::2
```

#### VERIFICA

```
R3# show ipv6 interface brief
Ethernet0/0.3456   [up/up]
    FE80::3
    2001:DB8:0::3
Ethernet0/0.34     [up/up]
    FE80::3
    2001:DB8:34::3
Ethernet0/0.36     [up/up]
    FE80::3
    2001:DB8:36::3

! Test ping IPv6 tra router adiacenti:
R3# ping 2001:db8:0::4
! Atteso: !!!!!  (success rate 100%)
```

---

### T2 — OSPFv3 standard (IPv6 native)

#### TEORIA

**OSPFv3 vs OSPFv2: differenze chiave**

| Aspetto | OSPFv2 | OSPFv3 |
|---------|--------|--------|
| Protocollo trasportato | Solo IPv4 | Solo IPv6 (native); IPv4+IPv6 con AF |
| Indirizzo sorgente Hello | IPv4 dell'interfaccia | IPv6 link-local (FE80::x) |
| Configurazione area | `network x.x.x.x wildcard area N` | `ipv6 ospf 100 area N` per interfaccia |
| Comando globale | `router ospf 100` | `ipv6 router ospf 100` |
| Abilitazione interfaccia | `network` statement o `ip ospf 100 area N` | `ipv6 ospf 100 area N` (solo per interfaccia) |
| LSA aggiuntivi | Type 1, 2, 3, 4, 5, 7 | Type 1, 2, 3, 4, 5, 7 + Type 8 (Link) + Type 9 (Intra-Prefix) |
| Router-ID | IPv4 (obbligatorio) | IPv4 (obbligatorio anche senza IPv4 config) |

> **Punto critico:** in OSPFv3 native NON esiste il comando `network`. L'abilitazione e' sempre per interfaccia con `ipv6 ospf <process> area <area-id>`.

**LSA Type 8 e Type 9 in OSPFv3**

OSPFv3 separa le informazioni di topologia (link) dai prefissi annunciati:
- **Type 8 (Link LSA):** portata link-locale — indirizzi link-local e globali della singola interfaccia
- **Type 9 (Intra-Area-Prefix LSA):** sostituisce le informazioni di prefisso che in OSPFv2 erano nel Type 1 (Router LSA) e Type 2 (Network LSA)

Questa separazione rende OSPFv3 piu' flessibile per trasportare multiple address family (vedi T4).

**Multicast OSPFv3**

| Indirizzo | Uso |
|-----------|-----|
| FF02::5 | AllSPFRouters — equivalente di 224.0.0.5 |
| FF02::6 | AllDRRouters — equivalente di 224.0.0.6 |

#### TASK

**Step 1 — Configurare il processo OSPFv3 su R3**

```
R3(config)# ipv6 router ospf 100
R3(config-rtr)# router-id 3.3.3.3
R3(config-rtr)# exit

! Abilitare le interfacce in OSPFv3 (metodo obbligatorio — no network statement):
R3(config)# interface ethernet 0/0.3456
R3(config-subif)# ipv6 ospf 100 area 0
R3(config-subif)# exit
R3(config)# interface ethernet 0/0.34
R3(config-subif)# ipv6 ospf 100 area 0
R3(config-subif)# exit
R3(config)# interface ethernet 0/0.36
R3(config-subif)# ipv6 ospf 100 area 0
R3(config-subif)# exit
```

**Step 2 — Configurare OSPFv3 su R4**

```
R4(config)# ipv6 router ospf 100
R4(config-rtr)# router-id 4.4.4.4
R4(config-rtr)# exit
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

**Step 3 — Configurare OSPFv3 su R5 (ABR)**

```
R5(config)# ipv6 router ospf 100
R5(config-rtr)# router-id 5.5.5.5
R5(config-rtr)# exit

! Core Broadcast e Core Ring (Area 0):
R5(config)# interface ethernet 0/0.3456
R5(config-subif)# ipv6 ospf 100 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.45
R5(config-subif)# ipv6 ospf 100 area 0
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.56
R5(config-subif)# ipv6 ospf 100 area 0
R5(config-subif)# exit

! Spoke area:
R5(config)# interface ethernet 0/0.51
R5(config-subif)# ipv6 ospf 100 area 15
R5(config-subif)# exit
R5(config)# interface ethernet 0/0.52
R5(config-subif)# ipv6 ospf 100 area 25
R5(config-subif)# exit
```

**Step 4 — Configurare OSPFv3 su R6, R1, R2**

```
! R6 (Area 0):
R6(config)# ipv6 router ospf 100
R6(config-rtr)# router-id 6.6.6.6
R6(config-rtr)# exit
! [abilitare e0/0.3456, e0/0.36, e0/0.56 in area 0]

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

#### VERIFICA

```
R5# show ipv6 ospf neighbor
OSPFv3 Router with ID (5.5.5.5) (Process ID 100)

Neighbor ID     Pri   State           Dead Time   Interface ID    Interface
3.3.3.3           0   FULL/DROTHER    00:00:39    4               Et0/0.3456
4.4.4.4         255   FULL/DR         00:00:38    4               Et0/0.3456
6.6.6.6         100   FULL/BDR        00:00:37    4               Et0/0.3456
1.1.1.1           1   FULL/           00:00:37    4               Et0/0.51
2.2.2.2           1   FULL/           00:00:36    4               Et0/0.52

R5# show ipv6 route ospf
OI  2001:DB8:15::/64 [110/20] via FE80::1, Et0/0.51
OI  2001:DB8:25::/64 [110/20] via FE80::2, Et0/0.52

R3# show ipv6 ospf database
! Verificare presenza di LSA Type 1, 8 (Link LSA), 9 (Intra-Area-Prefix)
```

---

### T3 — Loopback IPv6 e summarization OSPFv3

#### TEORIA

**Loopback IPv6 in OSPFv3**

Le loopback IPv6 vengono abilitate come qualsiasi interfaccia:

```
interface loopback 15
  ipv6 address 2001:db8:1:15::1/64
  ipv6 ospf 100 area 15
```

A differenza di OSPFv2, non e' necessario il `ip ospf network point-to-point` per annunciare il prefisso corretto — OSPFv3 usa il Type 9 (Intra-Area-Prefix LSA) che trasporta il prefisso reale dell'interfaccia, compreso quello di una loopback.

**Summarization inter-area in OSPFv3**

La sintassi e' analoga a OSPFv2 ma nel contesto del processo `ipv6 router ospf`:

```
ipv6 router ospf 100
  area 15 range 2001:db8:1::/48   ! aggrega tutti i /64 di Area 15 in un /48
  area 25 range 2001:db8:2::/48
```

#### TASK

**Step 1 — Configurare loopback IPv6 su R1**

```
R1(config)# interface loopback 15
R1(config-if)# ipv6 address 2001:db8:1:15::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit

R1(config)# interface loopback 150
R1(config-if)# ipv6 address 2001:db8:1:150::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit

R1(config)# interface loopback 151
R1(config-if)# ipv6 address 2001:db8:1:151::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit

R1(config)# interface loopback 152
R1(config-if)# ipv6 address 2001:db8:1:152::1/64
R1(config-if)# ipv6 ospf 100 area 15
R1(config-if)# exit
```

**Step 2 — Configurare loopback IPv6 su R2 (Area 25)**

```
! R2: Lo25, Lo250, Lo251, Lo252 con indirizzi 2001:db8:2:25::1/64 ecc.
! Abilitare in ipv6 ospf 100 area 25
```

**Step 3 — Verificare le rotte senza summarization**

```
R4# show ipv6 route ospf
! Atteso: OI 2001:DB8:1:15::/64, OI 2001:DB8:1:150::/64, OI 2001:DB8:1:151::/64 ...
```

**Step 4 — Configurare area range su R5**

```
R5(config)# ipv6 router ospf 100
R5(config-rtr)# area 15 range 2001:db8:1::/48
R5(config-rtr)# area 25 range 2001:db8:2::/48
R5(config-rtr)# exit
```

**Step 5 — Verificare la summarization**

```
R4# show ipv6 route ospf
! Le singole /64 spariscono; compare solo OI 2001:DB8:1::/48 e OI 2001:DB8:2::/48
```

#### VERIFICA

```
R4# show ipv6 route ospf
IPv6 Routing Table - default - 15 entries
OI  2001:DB8::/64   [110/20] via FE80::5, Et0/0.3456    ! Core Broadcast (da R5)
OI  2001:DB8:1::/48 [110/20] via FE80::5, Et0/0.3456    ! Summary Area 15
OI  2001:DB8:2::/48 [110/20] via FE80::5, Et0/0.3456    ! Summary Area 25
! Le singole /64 di R1 e R2 non compaiono in Area 0

R5# show ipv6 ospf database summary
! Verificare: 1 solo LSA Type 3 per prefisso summary verso Area 0
```

---

### T4 — OSPFv3 Address Families: dual-stack IPv4+IPv6

#### TEORIA

**OSPFv3 AF (RFC 5838): cos'e' e perche' si usa**

La modalita' **Address Families** unifica il routing IPv4 e IPv6 in un singolo processo `ospfv3`, usando lo stesso meccanismo di trasporto OSPFv3 (basato su link-local IPv6) per entrambe le family:

| Aspetto | OSPFv2 + OSPFv3 separati | OSPFv3 AF |
|---------|--------------------------|-----------|
| Processi | 2 (router ospf + ipv6 router ospf) | 1 (router ospfv3) |
| Adiacenze | 2 separate per segmento | 1 adiacenza condivisa per segmento |
| LSDB | Separata per protocollo | Separata per AF (`ospfv3 ipv4 database` / `ospfv3 ipv6 database`) |
| Abilitazione interfaccia | `ip ospf area` e `ipv6 ospf area` | `ospfv3 <pid> ipv4 area N` + `ospfv3 <pid> ipv6 area N` |
| Verifica | `show ip ospf neighbor` + `show ipv6 ospf neighbor` | `show ospfv3 neighbor` (unico) |
| Complessita' config | Piu' semplice per chi conosce OSPFv2 | Piu' compatta, un solo processo da gestire |

**Struttura di configurazione OSPFv3 AF**

```
router ospfv3 100
  router-id 4.4.4.4
  address-family ipv4 unicast   ! AF per IPv4
  exit-address-family
  address-family ipv6 unicast   ! AF per IPv6
  exit-address-family

interface ethernet 0/0.3456
  ospfv3 100 ipv4 area 0        ! abilita IPv4 AF
  ospfv3 100 ipv6 area 0        ! abilita IPv6 AF
```

> **Migrazione:** se si parte da OSPFv2 + OSPFv3 separati (come nei task precedenti), i processi `router ospf 100` e `ipv6 router ospf 100` vanno rimossi prima di configurare `router ospfv3 100`. Non possono coesistere con lo stesso process-id sullo stesso router.

**LSA in OSPFv3 AF**

Ogni AF ha la propria LSDB. Le adiacenze (e quindi i Type 1, 2, 8) sono condivise tra le AF dello stesso link; i prefissi (Type 3, 9) sono separati per AF.

#### TASK

**Step 1 — Rimuovere i processi OSPFv2 e OSPFv3 separati**

```
! Su ogni router (R3, R4, R5, R6, R1, R2):
Rx(config)# no router ospf 100
Rx(config)# no ipv6 router ospf 100
```

> **Attenzione:** rimuovere questi processi interrompe temporaneamente tutte le adiacenze. E' normale — vengono ripristinate durante la configurazione AF.

**Step 2 — Configurare OSPFv3 AF su R4 (esempio di riferimento)**

```
R4(config)# router ospfv3 100
R4(config-router)# router-id 4.4.4.4
R4(config-router)# address-family ipv4 unicast
R4(config-router-af)# exit-address-family
R4(config-router)# address-family ipv6 unicast
R4(config-router-af)# exit-address-family
R4(config-router)# exit

! Abilitare le interfacce per ENTRAMBE le AF:
R4(config)# interface ethernet 0/0.3456
R4(config-subif)# ospfv3 100 ipv4 area 0
R4(config-subif)# ospfv3 100 ipv6 area 0
R4(config-subif)# exit

R4(config)# interface ethernet 0/0.34
R4(config-subif)# ospfv3 100 ipv4 area 0
R4(config-subif)# ospfv3 100 ipv6 area 0
R4(config-subif)# exit

R4(config)# interface ethernet 0/0.45
R4(config-subif)# ospfv3 100 ipv4 area 0
R4(config-subif)# ospfv3 100 ipv6 area 0
R4(config-subif)# exit
```

**Step 3 — Replicare su R3, R6 (Area 0)**

```
! R3: stessa struttura con e0/0.3456, e0/0.34, e0/0.36 in area 0 (entrambe le AF)
! R6: stessa struttura con e0/0.3456, e0/0.36, e0/0.56 in area 0 (entrambe le AF)
```

**Step 4 — Configurare R5 come ABR (OSPFv3 AF)**

```
R5(config)# router ospfv3 100
R5(config-router)# router-id 5.5.5.5
R5(config-router)# address-family ipv4 unicast
R5(config-router-af)# exit-address-family
R5(config-router)# address-family ipv6 unicast
R5(config-router-af)# exit-address-family
R5(config-router)# exit

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

**Step 5 — Configurare R1 e R2 (OSPFv3 AF)**

```
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

**Step 6 — Verificare il dual-stack**

```
! Verifica adiacenze (condivise tra le AF):
R5# show ospfv3 neighbor

! Verifica LSDB separata per AF:
R5# show ospfv3 100 ipv4 database
R5# show ospfv3 100 ipv6 database

! Verifica rotte IPv4 via ospfv3:
R1# show ip route ospf

! Verifica rotte IPv6 via ospfv3:
R1# show ipv6 route ospf
```

#### VERIFICA

```
R5# show ospfv3 neighbor
OSPFv3 100 address-family ipv4

Neighbor ID     Pri   State           Dead Time   Interface
3.3.3.3           0   FULL/DROTHER    00:00:38    Et0/0.3456
4.4.4.4         255   FULL/DR         00:00:37    Et0/0.3456
6.6.6.6         100   FULL/BDR        00:00:36    Et0/0.3456
1.1.1.1           1   FULL/           00:00:39    Et0/0.51
2.2.2.2           1   FULL/           00:00:38    Et0/0.52

OSPFv3 100 address-family ipv6
! Stessi neighbor — adiacenza condivisa

R4# show ip route ospf
O IA  10.1.15.0/30 [110/20] via 10.0.0.5, Et0/0.3456
O IA  10.1.25.0/30 [110/20] via 10.0.0.5, Et0/0.3456
! Rotte IPv4 apprese via processo OSPFv3 AF

R4# show ipv6 route ospf
OI  2001:DB8:15::/64 [110/20] via FE80::5, Et0/0.3456
OI  2001:DB8:25::/64 [110/20] via FE80::5, Et0/0.3456
! Rotte IPv6 apprese via stesso processo OSPFv3 AF

R5# show ospfv3 100 ipv4 database
! LSDB IPv4 separata

R5# show ospfv3 100 ipv6 database
! LSDB IPv6 separata
```

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa probabile | Diagnosi | Fix |
|---------|----------------|----------|-----|
| Nessuna adiacenza OSPFv3 | `ipv6 unicast-routing` non abilitato | `show ipv6 interface brief` → no indirizzi link-local | `ipv6 unicast-routing` su tutti i router |
| Neighbor presente ma nessuna rotta IPv6 | Interfaccia abilitata in OSPFv3 ma `ipv6 address` non configurato | `show ipv6 interface brief` → nessun global unicast | Aggiungere `ipv6 address 2001:db8::x/64` sull'interfaccia |
| Link-local duplicate tra interfacce | IOU assegna lo stesso EUI-64 su interfacce diverse | `show ipv6 interface` → FE80 uguale su piu' interfacce | `ipv6 address fe80::x link-local` con indirizzi diversi per router |
| `show ospfv3 neighbor` vuoto dopo rimozione ospf/ipv6 ospf | `router ospfv3 100` non ancora configurato o interfacce non abilitate | `show ospfv3` → nessun processo attivo | Configurare `router ospfv3 100` e abilitare le interfacce con `ospfv3 100 ipv4/ipv6 area N` |
| Rotte IPv4 assenti nel RIB dopo OSPFv3 AF | Interfaccia abilitata solo per IPv6 AF ma non per IPv4 AF | `show ospfv3 100 ipv4 interface brief` → interfaccia assente | Aggiungere `ospfv3 100 ipv4 area N` sull'interfaccia mancante |
| `ospfv3` e `router ospf` coesistono, adiacenze instabili | Due processi attivi per IPv4 sullo stesso router | `show ip protocols` → due processi OSPF | Rimuovere `router ospf 100` prima di usare OSPFv3 AF |
| OSPFv3 neighbor in INIT | Configurazione asimmetrica (es. un lato usa `ipv6 ospf`, l'altro `ospfv3`) | `show ipv6 ospf interface` vs `show ospfv3 interface` | Uniformare il metodo di configurazione (tutti OSPFv3 AF o tutti OSPFv3 standard) |

---

## 7. SOLUZIONI

> **NOTA:** Le soluzioni complete commentate sono disponibili nel file `soluzione.md` di questo modulo.

---

## 8. RIEPILOGO & EXAM TIPS

**Punti chiave del modulo:**

1. In OSPFv3 native non esiste il comando `network` — l'abilitazione e' sempre per interfaccia con `ipv6 ospf <pid> area N`. Dimenticarlo e' l'errore piu' comune dei candidati CCNP.
2. OSPFv3 usa gli indirizzi **link-local** come sorgente dei pacchetti Hello e come next-hop nelle route. Configurare link-local statici (`fe80::x`) rende i log molto piu' leggibili.
3. **OSPFv3 AF** (`router ospfv3`) e' un'evoluzione che trasporta sia IPv4 che IPv6 in un singolo processo. Un'unica adiacenza per link, LSDB separata per AF. Usare `show ospfv3 neighbor` (senza ipv6) per verificare.
4. La coesistenza di `router ospf 100` e `router ospfv3 100` sullo stesso router e' tecnicamente possibile ma sconsigliata — rischio di duplicate adjacency e comportamento imprevedibile.
5. I nuovi tipi LSA di OSPFv3 (Type 8 e Type 9) separano informazioni di link dai prefissi — questo e' il meccanismo che permette alle AF di condividere la topologia ma avere LSDB di prefissi separata.

**Domande tipo CCNP:**

1. In OSPFv3 standard, quale indirizzo viene usato come sorgente dei pacchetti Hello e come next-hop nelle route apprese?
   > **Risposta:** L'indirizzo IPv6 link-local dell'interfaccia (FE80::/10). Le route OSPFv3 mostrano sempre un next-hop link-local, non l'indirizzo global unicast.

2. Qual e' la differenza tra `show ipv6 ospf neighbor` e `show ospfv3 neighbor`?
   > **Risposta:** `show ipv6 ospf neighbor` mostra le adiacenze del processo OSPFv3 standard (solo IPv6). `show ospfv3 neighbor` mostra le adiacenze del processo OSPFv3 AF — le stessa adiacenza viene mostrata sia per la AF IPv4 che per la AF IPv6 del link.

3. Un router ha configurato `ospfv3 100 ipv6 area 0` su un'interfaccia ma non `ospfv3 100 ipv4 area 0`. Cosa succedera' per il traffico IPv4?
   > **Risposta:** Il router formera' adiacenze OSPFv3 e scambiera' prefissi IPv6 via quella interfaccia, ma NON annuncera' ne' ricevera' prefissi IPv4 su quel link. Le rotte IPv4 non saranno redistributed via quella AF.

4. In OSPFv3, perche' e' necessario configurare un Router-ID IPv4 anche su un router che ha solo indirizzamento IPv6?
   > **Risposta:** Il Router-ID in OSPF (v2 e v3) e' sempre un valore a 32 bit in formato IPv4. OSPFv3 eredita questa convenzione. Se non c'e' nessun indirizzo IPv4 configurato, il Router-ID deve essere impostato esplicitamente con `router-id x.x.x.x`, altrimenti il processo non parte.
