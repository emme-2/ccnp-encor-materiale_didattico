# Soluzione Commentata — MOD-17: VRF-Lite & GRE Tunneling

> **Uso:** riservato al docente — non distribuire agli studenti
> **Prerequisito:** cfg pre-caricati via TFTP (hub-cfg, sp1-cfg, sp2-cfg, isp-cfg)

---

## Indice bug pre-configurati

| # | Part | Router | Dove | Errore | Effetto |
|---|------|--------|------|--------|---------|
| Bug 1 | 1 | HUB | Loopback2 VRF CUST-B | IP 10.2.2.1 → deve essere 10.2.1.1 | Conflitto: stesso IP di SP1 nella VRF |
| Bug 2 | 1 | SP1 | Loopback2 VRF CUST-B | `vrf forwarding CUST-B` mancante → Lo2 in global | La /32 di SP1 non compare in VRF CUST-B |
| Bug 3 | 2 | SP1 | Tunnel201 VRF CUST-B | `tunnel destination 203.0.113.254` → deve essere 192.0.2.254 (HUB) | Tunnel UP ma traffico va verso SP2, non HUB |
| Bug 4 | 2 | HUB | Tunnel202 VRF CUST-B | `tunnel source Ethernet0/0.10` → deve essere Loopback0 | Tunnel instabile se e0/0.10 flappa |

> I Bug 5/6/7 (Tunnel210 DMVPN) sono elencati in MOD-19/soluzione.md.

---

## PART 0 — Verifica Underlay

Nessuna configurazione richiesta. Verificare con:

```
ISP# show ip interface brief | include Ethernet|Loopback
ISP# show ip route

HUB# show ip interface brief
HUB# show ip route
HUB# ping 198.51.100.2           ! SP1 underlay — atteso: !!!!!
HUB# ping 203.0.113.2            ! SP2 underlay — atteso: !!!!!
HUB# ping 198.51.100.254 source Loopback0  ! SP1 Lo0 via ISP
HUB# ping 203.0.113.254 source Loopback0  ! SP2 Lo0 via ISP
```

Output atteso HUB:
```
HUB# show ip route | include 0.0.0.0|192.0.2
S*   0.0.0.0/0 [1/0] via 192.0.2.1
C    192.0.2.0/30 is directly connected, Ethernet0/0.10
L    192.0.2.2/32 is directly connected, Ethernet0/0.10
C    192.0.2.254/32 is directly connected, Loopback0
```

---

## PART 1 — VRF Definition + Loopback

### Soluzione CUST-A — HUB

```
vrf definition CUST-A
 rd 1:1
 address-family ipv4
 exit-address-family
!
interface Loopback1
 description !! VRF CUST-A customer loopback
 vrf forwarding CUST-A
 ip address 10.1.1.1 255.255.255.255
```

### Soluzione CUST-A — SP1

```
vrf definition CUST-A
 rd 1:2
 address-family ipv4
 exit-address-family
!
interface Loopback1
 description !! VRF CUST-A customer loopback
 vrf forwarding CUST-A
 ip address 10.1.2.1 255.255.255.255
```

> SP2 ha VRF CUST-A e Loopback1 (10.1.3.1) gia' pre-configurati. Verificare con `show ip route vrf CUST-A`.

### Fix Bug 1 — HUB Loopback2: IP errato

**Diagnosi:**
```
HUB# show ip route vrf CUST-B
      10.0.0.0/32 is subnetted, 1 subnets
C        10.2.2.1 is directly connected, Loopback2   ! SBAGLIATO — e' l'IP di SP1
```

**Fix:**
```
HUB(config)# interface Loopback2
HUB(config-if)# ip address 10.2.1.1 255.255.255.255
! Non serve ri-assegnare vrf forwarding — e' gia' presente nel cfg
```

### Fix Bug 2 — SP1 Loopback2: vrf forwarding mancante

**Diagnosi:**
```
SP1# show ip interface Loopback2
  VRF: not set    ! BUG: deve essere CUST-B

SP1# show ip route vrf CUST-B
! Assente — Lo2 e' nella global table

SP1# show ip route | include 10.2.2
C    10.2.2.1/32 is directly connected, Loopback2   ! in global, SBAGLIATO
```

**Fix:**
```
SP1(config)# interface Loopback2
SP1(config-if)# vrf forwarding CUST-B
! ATTENZIONE: il comando rimuove automaticamente l'IP — ridigitare subito:
SP1(config-if)# ip address 10.2.2.1 255.255.255.255
```

### Verifica finale Part 1

```
HUB# show vrf
HUB# show ip route vrf CUST-B
SP1# show ip route vrf CUST-B
SP2# show ip route vrf CUST-B
```

Output atteso (ogni router vede solo la propria /32):
```
HUB# show ip route vrf CUST-B
C    10.2.1.1 is directly connected, Loopback2   ! corretto dopo fix

SP1# show ip route vrf CUST-B
C    10.2.2.1 is directly connected, Loopback2   ! ora in VRF

SP2# show ip route vrf CUST-B
C    10.2.3.1 is directly connected, Loopback2   ! pre-corretto
```

---

## PART 2 — GRE Tunnel in VRF

### Soluzione CUST-A — HUB (Tu101 e Tu102)

```
interface Tunnel101
 description !! GRE CUST-A HUB<->SP1
 vrf forwarding CUST-A
 ip address 172.16.101.1 255.255.255.252
 tunnel source Loopback0
 tunnel destination 198.51.100.254
 tunnel mode gre ip
 no shutdown
!
interface Tunnel102
 description !! GRE CUST-A HUB<->SP2
 vrf forwarding CUST-A
 ip address 172.16.102.1 255.255.255.252
 tunnel source Loopback0
 tunnel destination 203.0.113.254
 tunnel mode gre ip
 no shutdown
```

### Soluzione CUST-A — SP1 (Tu101)

```
interface Tunnel101
 description !! GRE CUST-A SP1<->HUB
 vrf forwarding CUST-A
 ip address 172.16.101.2 255.255.255.252
 tunnel source Loopback0
 tunnel destination 192.0.2.254
 tunnel mode gre ip
 no shutdown
```

> SP2 ha Tunnel102 VRF CUST-A gia' pre-configurato (con tunnel protection — reference MOD-18). Verificare: `show interface Tu102`.

### Fix Bug 3 — SP1 Tunnel201: tunnel destination errato

**Diagnosi:**
```
SP1# show interface Tunnel201
  Tunnel source 198.51.100.254 (Loopback0)
  Tunnel destination 203.0.113.254   ! BUG: punta a SP2, non a HUB

SP1# ping vrf CUST-B 172.16.201.1
.....   ! fallisce
```

**Fix:**
```
SP1(config)# interface Tunnel201
SP1(config-if)# tunnel destination 192.0.2.254
```

**Verifica:**
```
SP1# ping vrf CUST-B 172.16.201.1
!!!!!   ! ora funziona
```

### Fix Bug 4 — HUB Tunnel202: tunnel source su sub-interface

**Diagnosi:**
```
HUB# show interface Tunnel202
  Tunnel source 192.0.2.2 (Ethernet0/0.10)   ! BUG: non e' Loopback0
! Rischio: se e0/0.10 flappa, il tunnel cade anche se ISP e' raggiungibile
! via un altro path. Best practice: tunnel source sempre su Loopback.
```

**Fix:**
```
HUB(config)# interface Tunnel202
HUB(config-if)# tunnel source Loopback0
```

### Verifica finale Part 2

```
HUB# show ip interface brief | include Tunnel
```

Output atteso:
```
Tunnel101   172.16.101.1   YES manual  up  up
Tunnel102   172.16.102.1   YES manual  up  up
Tunnel201   172.16.201.1   YES manual  up  up
Tunnel202   172.16.202.1   YES manual  up  up
Tunnel210   172.16.210.1   YES manual  up  up   ! DMVPN — bug in MOD-19
```

---

## PART 3 — Routing Statico in VRF

### Soluzione — HUB

```
! Route verso loopback SP1 (host /32 via Tu101)
ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel101
! Route verso loopback SP2 (host /32 via Tu102)
ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel102
```

### Soluzione — SP1

```
ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel101   ! verso HUB Lo1
ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel101   ! verso SP2 Lo1 — VIA HUB
! Non esiste Tu103 SP1<->SP2. SP1->SP2 transita per HUB.
! Questo e' il limite del design P2P — motivazione per DMVPN (MOD-19).
```

### Soluzione — SP2

```
ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel102   ! verso HUB Lo1
ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel102   ! verso SP1 Lo1 — VIA HUB
```

### Verifica e traceroute

```
HUB# show ip route vrf CUST-A
HUB# ping vrf CUST-A 10.1.2.1 source Loopback1
HUB# ping vrf CUST-A 10.1.3.1 source Loopback1
SP1# ping vrf CUST-A 10.1.3.1 source Loopback1
SP1# traceroute vrf CUST-A 10.1.3.1 source Loopback1
```

Output atteso traceroute:
```
SP1# traceroute vrf CUST-A 10.1.3.1 source Loopback1
  1  172.16.101.1   [HUB tunnel IP]   msec msec msec
  2  10.1.3.1       [SP2 loopback]    msec msec msec
! SP1->SP2 = 2 hop via HUB. DMVPN Phase 2 lo ridurra' a 1 hop diretto.
```

---

## Note varianti e alternative

**Route statiche: next-hop IP vs interfaccia**

Nel workbook si usano le interfacce tunnel come next-hop (`Tunnel101`) invece di un IP specifico. Entrambi funzionano, ma l'interfaccia e' preferita perche':
- Evita ambiguita' nel lookup ricorsivo
- Non richiede che il next-hop IP sia direttamente connesso alla VRF

**VRF-Lite vs MPLS/L3VPN**

VRF-Lite e' scalabile su singolo router ma non distribuisce route VRF tra router automaticamente — serve routing statico o un protocollo per-VRF (EIGRP/OSPF per-VRF, come in MOD-19). MPLS/L3VPN usa MP-BGP con extended community per distribuire automaticamente le route VRF tra PE router — fuori dallo scope ENCOR.

**tunnel mode gre ip — obbligatorio?**

Il comando e' il default su IOS. Specificarlo esplicitamente e' buona pratica didattica e rende il cfg leggibile. All'esame, riconoscere `Tunnel protocol/transport GRE/IP` nell'output di `show interface` e' piu' importante che ricordare se il comando e' default.
