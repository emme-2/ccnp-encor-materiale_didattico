# Soluzione Commentata — MOD-19: DMVPN Phase 1, Phase 2 & Phase 3

> **Uso:** riservato al docente — non distribuire agli studenti
> **Prerequisito:** MOD-18 completato — IKEv2 + IPSec operative su Tu101/Tu102

---

## Indice bug pre-configurati CUST-B (Part 5)

| # | Router | Dove | Errore | Effetto |
|---|--------|------|--------|---------|
| Bug 5 | HUB | Tunnel210 | `tunnel mode gre multipoint` mancante (default: gre ip P2P) | HUB non accetta registrazioni NHRP — 0 spoke registrati |
| Bug 6 | SP1 | Tunnel210 | `ip nhrp network-id 211` invece di 210 | SP1 in cloud NHRP diverso — registration silenziosamente ignorata |
| Bug 7 | SP2 | Tunnel210 | `ip nhrp nhs 172.16.210.2` (IP tunnel SP1, non HUB) + map errato | SP2 tenta registrazione verso SP1 — mai completata |

> Ordine diagnostico obbligatorio: Bug 5 → Bug 6 → Bug 7. Il Bug 5 blocca la visibilita' degli altri.

---

## PART 5 — Preparazione e Tunnel CUST-A

### Shutdown tunnel P2P e route statiche

```
! HUB
interface Tunnel101
 shutdown
interface Tunnel102
 shutdown
no ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel101
no ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel102

! SP1
interface Tunnel101
 shutdown

! SP2 — Tu102 era gia' con tunnel protection — verificare stato
! SP2# show ip interface brief | include Tunnel102
```

### Soluzione CUST-A — HUB Tunnel110 mGRE

```
interface Tunnel110
 description !! DMVPN CUST-A cloud — HUB NHS
 vrf forwarding CUST-A
 ip address 172.16.110.1 255.255.255.0
 tunnel source Loopback0
 tunnel mode gre multipoint         ! OBBLIGATORIO — accetta N spoke dinamici
 ip nhrp network-id 110             ! identifica il cloud — uguale su tutti
 ip nhrp map multicast dynamic      ! replica multicast (EIGRP hello) verso spoke registrati
 ip nhrp redirect                   ! Phase 2: avvisa spoke di shortcut disponibili
 tunnel protection ipsec profile IPSEC-PROF
 no shutdown
```

### Soluzione CUST-A — SP1 Tunnel110

```
interface Tunnel110
 description !! DMVPN CUST-A cloud — SP1 NHC
 vrf forwarding CUST-A
 ip address 172.16.110.11 255.255.255.0
 tunnel source Loopback0
 tunnel mode gre multipoint
 ip nhrp network-id 110
 ip nhrp nhs 172.16.110.1              ! IP tunnel del NHS (HUB)
 ip nhrp map 172.16.110.1 192.0.2.254 ! mapping statico: tunnel IP HUB → NBMA HUB (Lo0)
 ip nhrp map multicast 192.0.2.254    ! multicast (EIGRP) verso HUB
 ip nhrp shortcut                      ! Phase 2: installa route NHRP dirette
 tunnel protection ipsec profile IPSEC-PROF
 no shutdown

! Route statiche temporanee (Phase 1) — rimosse in Part 6
ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel110
ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel110
```

### Soluzione CUST-A — SP2 Tunnel110

```
interface Tunnel110
 description !! DMVPN CUST-A cloud — SP2 NHC
 vrf forwarding CUST-A
 ip address 172.16.110.12 255.255.255.0
 tunnel source Loopback0
 tunnel mode gre multipoint
 ip nhrp network-id 110
 ip nhrp nhs 172.16.110.1
 ip nhrp map 172.16.110.1 192.0.2.254
 ip nhrp map multicast 192.0.2.254
 ip nhrp shortcut
 tunnel protection ipsec profile IPSEC-PROF
 no shutdown

ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel110
ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel110
```

### Fix Bug 5 — HUB Tunnel210

```
! Diagnosi:
! HUB# show interface Tunnel210
!   Tunnel protocol/transport GRE/IP   (manca "Multipoint")
! HUB# show dmvpn → 0 peer

HUB(config)# interface Tunnel210
HUB(config-if)# tunnel mode gre multipoint

! Verifica:
! HUB# show interface Tunnel210 | include Multipoint → Multipoint: Yes
```

### Fix Bug 6 — SP1 Tunnel210

```
! Diagnosi:
! SP1# show dmvpn → 0 peer
! HUB# show ip nhrp → SP1 assente (cloud NHRP id 211 ≠ 210 su HUB)

SP1(config)# interface Tunnel210
SP1(config-if)# ip nhrp network-id 210

! Verifica:
! HUB# show dmvpn → SP1 appare con Attrb D
```

### Fix Bug 7 — SP2 Tunnel210

```
! Diagnosi:
! SP2# show ip nhrp → nessuna entry (NHS non raggiungibile)
! SP2# show dmvpn → 0 peer
! ip nhrp nhs 172.16.210.2 = IP tunnel SP1 (non e' un NHS!)

SP2(config)# interface Tunnel210
SP2(config-if)# no ip nhrp nhs 172.16.210.2
SP2(config-if)# no ip nhrp map 172.16.210.2 203.0.113.254
SP2(config-if)# no ip nhrp map multicast 203.0.113.254
SP2(config-if)# ip nhrp nhs 172.16.210.1
SP2(config-if)# ip nhrp map 172.16.210.1 192.0.2.254
SP2(config-if)# ip nhrp map multicast 192.0.2.254

! Verifica finale:
! HUB# show dmvpn (Tu210)
! # Ent  Peer NBMA Addr    Peer Tunnel Add  State  UpDn   Attrb
! 2      198.51.100.254    172.16.210.11    NHRP   00:01  D
!        203.0.113.254     172.16.210.12    NHRP   00:00  D
```

---

## PART 6 — Named EIGRP VRF-aware

### Soluzione — HUB (CUST-A AS1 + CUST-B AS2)

```
router eigrp LAB-ENCOR
 !
 address-family ipv4 vrf CUST-A autonomous-system 1
  af-interface default
   passive-interface            ! default sicuro — no EIGRP su interfacce non esplicite
  exit-af-interface
  af-interface Tunnel110
   no passive-interface         ! attiva EIGRP su Tu110
   no split-horizon             ! CRITICO: HUB ri-annuncia route spoke→altri spoke
   no next-hop-self             ! CRITICO: preserva next-hop originale per shortcut Phase 2
   hello-interval 20            ! best practice WAN DMVPN: hello piu' lungo
   hold-time 60
  exit-af-interface
  network 172.16.110.0 0.0.0.255  ! cloud DMVPN CUST-A
  network 10.1.1.0 0.0.0.255      ! Lo1 HUB
  eigrp router-id 10.1.1.1
 exit-address-family
 !
 address-family ipv4 vrf CUST-B autonomous-system 2
  af-interface Tunnel210
   no passive-interface
   no split-horizon
   no next-hop-self
   hello-interval 20
   hold-time 60
  exit-af-interface
  network 172.16.210.0 0.0.0.255
  network 10.2.1.0 0.0.0.255
  eigrp router-id 10.2.1.1
 exit-address-family
```

### Soluzione — SP1 (CUST-A AS1 + CUST-B AS2)

```
router eigrp LAB-ENCOR
 address-family ipv4 vrf CUST-A autonomous-system 1
  af-interface Tunnel110
   no passive-interface
   hello-interval 20
   hold-time 60
   ! split-horizon e next-hop-self: DEFAULT su spoke — non modificare
  exit-af-interface
  network 172.16.110.0 0.0.0.255
  network 10.1.2.0 0.0.0.255
  eigrp router-id 10.1.2.1
 exit-address-family
 !
 address-family ipv4 vrf CUST-B autonomous-system 2
  af-interface Tunnel210
   no passive-interface
   hello-interval 20
   hold-time 60
  exit-af-interface
  network 172.16.210.0 0.0.0.255
  network 10.2.2.0 0.0.0.255
  eigrp router-id 10.2.2.1
 exit-address-family
```

> SP2: stessa struttura di SP1. Cambiare `network 10.1.2.0` → `10.1.3.0` (CUST-A) e `10.2.2.0` → `10.2.3.0` (CUST-B). Router-id: 10.1.3.1 e 10.2.3.1.

### Rimozione route statiche CUST-A prima di abilitare EIGRP

```
HUB(config)# no ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel110
HUB(config)# no ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel110
SP1(config)# no ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel110
SP1(config)# no ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel110
SP2(config)# no ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel110
SP2(config)# no ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel110
```

### Verifica EIGRP e Phase 2

```
HUB# show eigrp address-family ipv4 vrf CUST-A neighbors
HUB# show eigrp af-interfaces vrf CUST-A
SP1# show ip route vrf CUST-A
SP1# ping vrf CUST-A 10.1.3.1 source Loopback1 repeat 10
SP1# show ip nhrp detail | include 10.1.3
SP1# traceroute vrf CUST-A 10.1.3.1 source Loopback1
```

Output atteso traceroute Phase 2:
```
  1  10.1.3.1   msec msec msec   ← 1 hop diretto — no HUB
```

Output atteso `show ip nhrp` dopo Phase 2:
```
10.1.3.1/32 via 172.16.110.12
  Type: dynamic, Flags: router nhop rib nho
  NBMA address: 203.0.113.254   ← Lo0 di SP2
```

---

## PART 7 — DMVPN Phase 3

### Configurazione Phase 3 — HUB aggiunta summary

```
router eigrp LAB-ENCOR
 address-family ipv4 vrf CUST-A autonomous-system 1
  af-interface Tunnel110
   ip summary-address eigrp 1 10.1.0.0 255.255.0.0
   ! HUB annuncia 10.1.0.0/16 invece delle /32 specifiche di ciascun spoke
   ! Gli spoke non ricevono piu' route /32 EIGRP per gli altri spoke
   ! Il traffico verso spoke remoti colpisce il summary → HUB → Traffic Indication
  exit-af-interface
 exit-address-family
```

### Verifica Phase 3

```
! Baseline PRIMA (Phase 2):
SP1# show ip route vrf CUST-A | count
! Annotare numero righe

! DOPO summary (Phase 3):
SP1# show ip route vrf CUST-A | include 10.1
D    10.1.0.0/16 [90/...] via 172.16.110.1, Tunnel110   ! solo il summary

! Clear NHRP e test:
SP1# clear ip nhrp
SP1# ping vrf CUST-A 10.1.3.1 source Loopback1 repeat 20
! Prime 1-3 risposte mancanti (Traffic Indication) — poi !!!!!

! Dopo il primo ping:
SP1# show ip nhrp | include 10.1.3
10.1.3.1/32 via 172.16.110.12   Type: dynamic   ! installata da Traffic Indication

SP1# traceroute vrf CUST-A 10.1.3.1 source Loopback1
  1  10.1.3.1   ← 1 hop diretto (identico a Phase 2)

SP1# show ip route vrf CUST-A | count
! Numero righe inferiore a Phase 2 — scalabilita' migliorata
```

---

## Note varianti e alternative

**Phase 2 vs Phase 3 — quando scegliere**

Phase 2 e' piu' semplice da configurare e debug ma scala meno bene: con N spoke, ogni spoke riceve N route /32 nella tabella EIGRP. Phase 3 scala linearmente: 1 summary per cloud indipendentemente da N.

Regola pratica:
- Fino a ~50 spoke: Phase 2 va bene
- Oltre 50 spoke o con molte VRF: Phase 3

**EIGRP hello-interval su DMVPN**

Il valore default di EIGRP hello su LAN e' 5 secondi (hold-time 15). Su link WAN/DMVPN si preferisce hello 20/hold 60 per ridurre i falsi flap in caso di latenza variabile del cloud. Questo e' una best practice ma non modifica il comportamento funzionale in lab.

**IPSec su DMVPN mGRE**

`tunnel protection ipsec profile IPSEC-PROF` funziona con mGRE perche' il profilo IPSec si applica a ciascuna SA per spoke, non all'intera interfaccia come farebbe un crypto map. Ogni spoke ha una SA IPSec separata (SPI distinto) anche se condividono la stessa interfaccia Tunnel110 sul HUB.
