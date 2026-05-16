# Workbook Studenti — MOD-17: VRF-Lite & GRE Tunneling

**Area:** AREA 7 — OVERLAY & VPN | **Ore:** 2h | **Codici syllabus:** 4.1, 4.2, 4.3

---

## 1. TOPOLOGIA

### Diagramma logico

```
                  ┌───────────────────────────────────────────────────────┐
                  │                ISP  (Simulated Internet)               │
                  │  Lo0: 192.0.2.253/32                                   │
                  │  e0/0.10  192.0.2.1      VLAN 10 → HUB                │
                  │  e0/0.20  198.51.100.1   VLAN 20 → SP1                │
                  │  e0/0.30  203.0.113.1    VLAN 30 → SP2                │
                  └───────┬──────────────────┬───────────────┬─────────────┘
              VLAN10 /30  │      VLAN20 /30  │   VLAN30 /30  │
                          │                  │               │
              ┌───────────┴──┐   ┌───────────┴──┐  ┌────────┴──────┐
              │     HUB      │   │     SP1       │  │     SP2       │
              │ Lo0:         │   │ Lo0:          │  │ Lo0:          │
              │ 192.0.2.254  │   │ 198.51.100.254│  │ 203.0.113.254 │
              │ Lo1 CUST-A:  │   │ Lo1 CUST-A:   │  │ Lo1 CUST-A:   │
              │ 10.1.1.1/32  │   │ 10.1.2.1/32   │  │ 10.1.3.1/32   │
              │ Lo2 CUST-B:  │   │ Lo2 CUST-B:   │  │ Lo2 CUST-B:   │
              │ 10.2.1.1/32  │   │ 10.2.2.1/32   │  │ 10.2.3.1/32   │
              └──────────────┘   └───────────────┘  └───────────────┘

  Overlay GRE P2P — VRF CUST-A (studenti configurano):
    Tu101  HUB ←→ SP1   172.16.101.0/30  (.1 HUB  .2 SP1)
    Tu102  HUB ←→ SP2   172.16.102.0/30  (.1 HUB  .2 SP2)

  Overlay GRE P2P — VRF CUST-B (pre-configurato con 4 bug):
    Tu201  HUB ←→ SP1   172.16.201.0/30  (.1 HUB  .2 SP1)
    Tu202  HUB ←→ SP2   172.16.202.0/30  (.1 HUB  .2 SP2)

  SP1 <─────────────── nessun tunnel diretto ───────────────> SP2
  (traffico SP1↔SP2 transita sempre per HUB — limite del design P2P)
```

### Piano di indirizzamento — Underlay (Global Table)

| VLAN | Segmento | Router A | IP A | Router B | IP B | Subnet |
|------|----------|----------|------|----------|------|--------|
| 10 | ISP ↔ HUB | ISP e0/0.10 | 192.0.2.1 | HUB e0/0.10 | 192.0.2.2 | 192.0.2.0/30 |
| 20 | ISP ↔ SP1 | ISP e0/0.20 | 198.51.100.1 | SP1 e0/0.20 | 198.51.100.2 | 198.51.100.0/30 |
| 30 | ISP ↔ SP2 | ISP e0/0.30 | 203.0.113.1 | SP2 e0/0.30 | 203.0.113.2 | 203.0.113.0/30 |

### Loopback — Global Table (tunnel source)

| Router | Interfaccia | IP / Mask | Nota |
|--------|-------------|-----------|------|
| HUB | Loopback0 | 192.0.2.254/32 | Tunnel source HUB |
| SP1 | Loopback0 | 198.51.100.254/32 | Tunnel source SP1 |
| SP2 | Loopback0 | 203.0.113.254/32 | Tunnel source SP2 |
| ISP | Loopback0 | 192.0.2.253/32 | Management ISP |

### Loopback — VRF CUST-A (da configurare dagli studenti)

| Router | Interfaccia | VRF | IP / Mask |
|--------|-------------|-----|-----------|
| HUB | Loopback1 | CUST-A | 10.1.1.1/32 |
| SP1 | Loopback1 | CUST-A | 10.1.2.1/32 |
| SP2 | Loopback1 | CUST-A | 10.1.3.1/32 |

### Loopback — VRF CUST-B (pre-configurato con errori in Part 1)

| Router | Interfaccia | VRF | IP Corretto | IP nel cfg | Errore |
|--------|-------------|-----|-------------|-----------|--------|
| HUB | Loopback2 | CUST-B | 10.2.1.1/32 | 10.2.2.1/32 | IP sbagliato |
| SP1 | Loopback2 | CUST-B | 10.2.2.1/32 | — | vrf forwarding mancante |
| SP2 | Loopback2 | CUST-B | 10.2.3.1/32 | 10.2.3.1/32 | Corretto |

### Tunnel GRE P2P

| Tunnel | Da | A | VRF | Subnet | IP HUB/A | IP Spoke/B |
|--------|----|---|-----|--------|----------|------------|
| Tu101 | HUB | SP1 | CUST-A | 172.16.101.0/30 | 172.16.101.1 | 172.16.101.2 |
| Tu102 | HUB | SP2 | CUST-A | 172.16.102.0/30 | 172.16.102.1 | 172.16.102.2 |
| Tu201 | HUB | SP1 | CUST-B | 172.16.201.0/30 | 172.16.201.1 | 172.16.201.2 |
| Tu202 | HUB | SP2 | CUST-B | 172.16.202.0/30 | 172.16.202.1 | 172.16.202.2 |

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sarà in grado di:

- [ ] Verificare la raggiungibilità underlay tra router attraverso la global routing table
- [ ] Definire una VRF con sintassi moderna (`vrf definition` + `address-family ipv4`)
- [ ] Assegnare un'interfaccia a una VRF rispettando l'ordine corretto dei comandi
- [ ] Spiegare perché `tunnel source/destination` usano la global table mentre l'interfaccia tunnel è in VRF
- [ ] Creare un tunnel GRE P2P in VRF con tunnel source su Loopback
- [ ] Configurare route statiche VRF-aware con la keyword `vrf`
- [ ] Diagnosticare e correggere i 4 bug pre-configurati su CUST-B (Part 1 e Part 2)
- [ ] Interpretare l'output di `show ip route vrf`, `show interface Tunnel`, `show vrf`, `show ip vrf interfaces`

**Codici syllabus:** 4.1 (VRF-Lite), 4.2 (GRE Tunneling), 4.3 (Static Routing in VRF)

---

## 3. LAB SETUP

### Configurazioni TFTP da caricare

```
! Su ogni router — caricare il file corrispondente
HUB# copy tftp://192.168.122.1/ENCOR/MOD-17/hub-cfg running-config
SP1# copy tftp://192.168.122.1/ENCOR/MOD-17/sp1-cfg running-config
SP2# copy tftp://192.168.122.1/ENCOR/MOD-17/sp2-cfg running-config
ISP# copy tftp://192.168.122.1/ENCOR/MOD-17/isp-cfg running-config
```

### Prerequisiti

- GNS3 avviato con topologia MOD-17/LAB06
- Tutti e 4 i router IOU L3 avviati e accessibili via console
- TFTP server attivo su 192.168.122.1 (host GNS3)

### Verifica pre-lab

```
HUB# show ip interface brief
HUB# show ip route
HUB# ping 192.0.2.1
```

---

## 4. TASK LIST

| # | Task | Descrizione | Durata |
|---|------|-------------|--------|
| T0.1 | Ping ISP verso spoke | Verifica raggiungibilità underlay diretta | 5 min |
| T0.2 | Verifica underlay HUB | Default route e sub-interface attive | 3 min |
| T0.3 | Ping Lo0 fine-a-fine | HUB Lo0 → SP1 Lo0 e SP2 Lo0 via ISP | 2 min |
| T1.1 | VRF CUST-A su HUB/SP1/SP2 | Definizione VRF con RD per router | 5 min |
| T1.2 | Lo1 in VRF CUST-A | Assegnazione interfaccia + IP overlay | 5 min |
| T1.3 | Verifica tabella VRF | Solo /32 locale in VRF CUST-A | 3 min |
| T1.4 | Fix bug VRF CUST-B | 2 errori pre-configurati: IP errato + VRF mancante | 10 min |
| T2.1 | Tu101 HUB↔SP1 CUST-A | GRE P2P in VRF, verifica UP | 8 min |
| T2.2 | Tu102 HUB↔SP2 CUST-A | GRE P2P in VRF, verifica UP | 5 min |
| T2.3 | Verifica tutti i tunnel UP | `show ip int brief \| inc Tunnel` | 3 min |
| T2.4 | Fix bug tunnel CUST-B | 2 errori su Tu201 e Tu202 | 10 min |
| T3.1 | Route statiche HUB | Verso Lo1 SP1 via Tu101, Lo1 SP2 via Tu102 | 5 min |
| T3.2 | Route statiche SP1 | Verso Lo1 HUB e SP2 (entrambe via Tu101) | 5 min |
| T3.3 | Route statiche SP2 | Verso Lo1 HUB e SP1 (entrambe via Tu102) | 5 min |
| T3.4 | Ping end-to-end CUST-A | Tutti i 6 path Lo1↔Lo1 | 5 min |
| T3.5 | Traceroute SP1→SP2 | Conferma transito via HUB | 2 min |

---

## 5. DETTAGLIO TASK

---

### PART 0 — Verifica Underlay

> Durata stimata: 10 min — Nessuna configurazione richiesta.
> L'underlay (sub-interface + default route) è pre-caricato via TFTP. Verificare prima di procedere.

#### TEORIA

L'**underlay** è la rete IP fisica/reale su cui viaggeranno i pacchetti GRE incapsulati. Nel nostro ambiente:

- Ogni router ha una **sub-interface 802.1Q** su `e0/0` collegata a ISP tramite trunk GNS3
- Ogni router ha una **Loopback0** come indirizzo stabile: non va mai down finché il router è acceso
- ISP ha route statiche /32 verso le Loopback0 degli spoke per permettere il ritorno dei pacchetti
- Ogni spoke ha una **default route** verso ISP

La scelta di usare **Loopback0 come tunnel source** è intenzionale: garantisce stabilità del tunnel anche se un link fisico flappa — il tunnel rimane up finché l'underlay ISP è raggiungibile da qualsiasi percorso.

#### TASK T0.1 — Verifica raggiungibilità ISP verso spoke

```
ISP# ping 192.0.2.2
ISP# ping 198.51.100.2
ISP# ping 203.0.113.2
ISP# ping 192.0.2.254
ISP# ping 198.51.100.254
ISP# ping 203.0.113.254
```

#### TASK T0.2 — Verifica underlay su HUB

```
HUB# show ip interface brief
HUB# show ip route
```

#### TASK T0.3 — Ping Lo0 fine-a-fine via ISP

```
HUB# ping 198.51.100.254 source Loopback0
HUB# ping 203.0.113.254 source Loopback0
```

#### VERIFICA

```
HUB# show ip route | include 0.0.0.0|192.0.2
S*   0.0.0.0/0 [1/0] via 192.0.2.1
C    192.0.2.0/30 is directly connected, Ethernet0/0.10
L    192.0.2.2/32 is directly connected, Ethernet0/0.10
C    192.0.2.254/32 is directly connected, Loopback0
```

> **Checkpoint Part 0:** Tutti i ping underlay riuscono (`!!!!!`). Default route presente. Loopback0 raggiungibile da tutti i router. Nessuna VRF ancora configurata.

---

### PART 1 — VRF Definition + Loopback

#### TEORIA

**VRF (Virtual Routing and Forwarding)** crea una tabella di routing separata all'interno dello stesso router fisico. Il traffico di VRF diverse è completamente isolato: due interfacce in VRF diverse non si "vedono", anche se sullo stesso dispositivo.

**Perché si usa VRF?**

Un provider che trasporta traffico di piu' clienti sullo stesso router deve tenerli separati. Nel nostro lab, CUST-A e CUST-B sono due clienti distinti che condividono HUB, SP1, SP2 — senza VRF i loro prefissi si mescolerebbero nella stessa tabella.

**Route Distinguisher (RD):** etichetta univoca a 64 bit in formato `AS:numero`. Viene aggiunta ai prefissi VPNv4 per renderli unici anche quando due VRF usano lo stesso spazio di indirizzamento privato (es. 10.x.x.x). In un lab **VRF-Lite** (senza MPLS, senza MP-BGP) l'RD e' richiesto dalla sintassi IOS ma non viene utilizzato per distribuire route tra router.

**Sintassi moderna IOS (da 12.4 in poi):**
```
! NON usare "ip vrf NOME" — sintassi deprecata
vrf definition NOME-VRF
 rd X:Y
 address-family ipv4
 exit-address-family
```

**Regola critica — ordine dei comandi:**
```
! ORDINE CORRETTO: VRF prima, poi IP
interface Loopback1
 vrf forwarding CUST-A           ! 1. assegna VRF — rimuove IP eventuale
 ip address 10.1.1.1 255.255.255.255  ! 2. poi configura IP

! ORDINE SBAGLIATO: IOS rimuove l'IP quando si aggiunge la VRF
interface Loopback1
 ip address 10.1.1.1 255.255.255.255
 vrf forwarding CUST-A           ! rimuove automaticamente l'IP sopra!
 ! => interfaccia senza IP — errore silenzioso
```

#### TASK T1.1 — Definire VRF CUST-A su HUB, SP1, SP2

Configurare su ogni router la VRF CUST-A con l'RD corrispondente:

| Router | RD |
|--------|----|
| HUB | 1:1 |
| SP1 | 1:2 |
| SP2 | 1:3 |

```
HUB(config)# vrf definition CUST-A
HUB(config-vrf)# rd 1:1
HUB(config-vrf)# address-family ipv4
HUB(config-vrf-af)# exit-address-family
```

Ripetere su SP1 (rd 1:2) e SP2 (rd 1:3).

#### VERIFICA T1.1

```
HUB# show vrf
```

Output atteso:
```
  Name              Default RD      Protocols  Interfaces
  CUST-A            1:1             ipv4
  CUST-B            2:1             ipv4       Lo2, Tu201, Tu202, Tu210
```

#### TASK T1.2 — Assegnare Lo1 a VRF CUST-A

```
HUB(config)# interface Loopback1
HUB(config-if)# vrf forwarding CUST-A
HUB(config-if)# ip address 10.1.1.1 255.255.255.255
```

Ripetere su SP1 con IP 10.1.2.1 e su SP2 con IP 10.1.3.1.

> SP2 ha gia' VRF CUST-A e Loopback1 pre-configurati. Verificare con `show ip route vrf CUST-A`.

#### VERIFICA T1.2

```
HUB# show ip vrf interfaces
HUB# show ip interface Loopback1
```

Output atteso:
```
HUB# show ip vrf interfaces
Interface   IP-Address      VRF             Protocol
Lo1         10.1.1.1        CUST-A          up
```

#### TASK T1.3 — Verifica tabella routing VRF CUST-A

```
HUB# show ip route vrf CUST-A
```

Output atteso (solo la /32 locale — nessuna route verso altri spoke):
```
Routing Table: CUST-A
      10.0.0.0/32 is subnetted, 1 subnets
C        10.1.1.1 is directly connected, Loopback1
```

#### TASK T1.4 — Trovare e correggere i bug pre-configurati su VRF CUST-B

Ci sono **2 bug** nelle configurazioni pre-caricate. Usare i comandi di verifica per identificarli prima di leggere la diagnosi.

**Bug 1 — HUB Loopback2: IP address errato**

```
HUB# show ip route vrf CUST-B
```

Cosa c'e' di anomalo? Confronta con la tabella di indirizzamento prevista.

```
! Diagnosi attesa:
HUB# show ip route vrf CUST-B
      10.0.0.0/32 is subnetted, 1 subnets
C        10.2.2.1 is directly connected, Loopback2
! PROBLEMA: 10.2.2.1 appartiene a SP1, non a HUB (corretto: 10.2.1.1)
! Duplicato nella VRF — SP1 ha lo stesso indirizzo
```

Fix:
```
HUB(config)# interface Loopback2
HUB(config-if)# ip address 10.2.1.1 255.255.255.255
```

**Bug 2 — SP1 Loopback2: vrf forwarding mancante**

```
SP1# show ip interface Loopback2
SP1# show ip route vrf CUST-B
SP1# show ip route | include 10.2.2
```

```
! Diagnosi attesa:
SP1# show ip interface Loopback2
  VRF: not set       ← BUG: deve essere CUST-B

SP1# show ip route | include 10.2.2
C    10.2.2.1/32 is directly connected, Loopback2   ← in global table, SBAGLIATO
```

Fix:
```
SP1(config)# interface Loopback2
SP1(config-if)# vrf forwarding CUST-B
! IOS rimuove automaticamente l'IP — ridigitarlo subito dopo:
SP1(config-if)# ip address 10.2.2.1 255.255.255.255
```

#### VERIFICA finale Part 1

```
HUB# show ip route vrf CUST-B
SP1# show ip route vrf CUST-B
SP2# show ip route vrf CUST-B
```

Ogni router deve mostrare solo la propria /32 come `C` (connected).

> **Checkpoint Part 1:** VRF CUST-A e CUST-B definite. Loopback1/2 nella VRF corretta su tutti i router. show ip route vrf mostra le /32 locali. Nessun ping inter-router VRF ancora possibile — mancano i tunnel.

---

### PART 2 — GRE Tunnel in VRF

#### TEORIA

**GRE (Generic Routing Encapsulation, protocollo IP 47)** incapsula un pacchetto IP originale dentro un nuovo header IP, creando un tunnel virtuale tra due endpoint. GRE e' semplice: non cifra, non autentica — si occupa solo dell'incapsulamento. La cifratura e' compito di IPSec (MOD-18).

**Struttura del pacchetto GRE:**
```
┌─────────────────┬─────────────┬───────────────────────────────┐
│ Outer IP header │  GRE header │  Inner packet (VRF CUST-A)    │
│ Lo0 HUB → Lo0   │  proto 47   │  es. 10.1.x.x → 10.1.y.y     │
│ SP1 (underlay)  │             │  (overlay VRF)                 │
└─────────────────┴─────────────┴───────────────────────────────┘
```

**Principio chiave: due tabelle, un tunnel**

```
tunnel source Loopback0          ! IP nella GLOBAL TABLE → underlay
tunnel destination 198.51.100.254 ! IP nella GLOBAL TABLE → underlay
vrf forwarding CUST-A             ! L'interfaccia tunnel e' nella VRF → overlay
```

Il router usa la **global table** per instradare i pacchetti GRE fisicamente verso la destinazione (come arrivano all'altro router). Il **payload GRE** trasporta indirizzi e traffico della VRF overlay. Questo meccanismo si chiama **lookup ricorsivo**: prima si consulta la global per il destination del tunnel, poi la VRF per il routing interno.

> **Nota pratica:** il line protocol del tunnel sale a UP non appena l'underlay e' raggiungibile, anche senza route nella VRF. GRE non verifica la raggiungibilita' dei prefissi overlay.

#### TASK T2.1 — Creare Tunnel101 su HUB e SP1 (VRF CUST-A)

**Su HUB:**
```
HUB(config)# interface Tunnel101
HUB(config-if)# description !! GRE CUST-A HUB<->SP1
HUB(config-if)# vrf forwarding CUST-A
HUB(config-if)# ip address 172.16.101.1 255.255.255.252
HUB(config-if)# tunnel source Loopback0
HUB(config-if)# tunnel destination 198.51.100.254
HUB(config-if)# tunnel mode gre ip
HUB(config-if)# no shutdown
```

**Su SP1:**
```
SP1(config)# interface Tunnel101
SP1(config-if)# description !! GRE CUST-A SP1<->HUB
SP1(config-if)# vrf forwarding CUST-A
SP1(config-if)# ip address 172.16.101.2 255.255.255.252
SP1(config-if)# tunnel source Loopback0
SP1(config-if)# tunnel destination 192.0.2.254
SP1(config-if)# tunnel mode gre ip
SP1(config-if)# no shutdown
```

#### VERIFICA T2.1

```
HUB# show interface Tunnel101
HUB# ping vrf CUST-A 172.16.101.2
```

Output atteso:
```
Tunnel101 is up, line protocol is up
  VRF: CUST-A
  Internet address is 172.16.101.1/30
  Tunnel source 192.0.2.254 (Loopback0), destination 198.51.100.254
  Tunnel protocol/transport GRE/IP
```

#### TASK T2.2 — Creare Tunnel102 su HUB (VRF CUST-A)

```
HUB(config)# interface Tunnel102
HUB(config-if)# description !! GRE CUST-A HUB<->SP2
HUB(config-if)# vrf forwarding CUST-A
HUB(config-if)# ip address 172.16.102.1 255.255.255.252
HUB(config-if)# tunnel source Loopback0
HUB(config-if)# tunnel destination 203.0.113.254
HUB(config-if)# tunnel mode gre ip
HUB(config-if)# no shutdown
```

> SP2 ha gia' Tu102 VRF CUST-A pre-configurato con tunnel protection IPSec (reference Part 4 di MOD-18). Verificare con `show interface Tunnel102`.

#### TASK T2.3 — Verifica line protocol UP su tutti i tunnel

```
HUB# show ip interface brief | include Tunnel
SP1# show ip interface brief | include Tunnel
SP2# show ip interface brief | include Tunnel
```

Tutti i tunnel devono mostrare stato `up up`.

#### TASK T2.4 — Trovare e correggere i bug sui tunnel CUST-B

**Bug 3 — SP1 Tunnel201: tunnel destination errato**

```
SP1# show interface Tunnel201
SP1# ping vrf CUST-B 172.16.201.1
```

```
! Diagnosi attesa:
Tunnel source 198.51.100.254 (Loopback0)
Tunnel destination 203.0.113.254     ← BUG: punta a SP2, deve essere HUB
! ping 172.16.201.1 → ..... (fallisce)
```

Fix:
```
SP1(config)# interface Tunnel201
SP1(config-if)# tunnel destination 192.0.2.254
```

Verifica: `SP1# ping vrf CUST-B 172.16.201.1` → `!!!!!`

**Bug 4 — HUB Tunnel202: tunnel source su sub-interface fisica**

```
HUB# show interface Tunnel202
```

```
! Diagnosi attesa:
Tunnel source 192.0.2.2 (Ethernet0/0.10)   ← BUG: non e' Loopback0
! Se e0/0.10 flappa, il tunnel cade anche se l'underlay ISP e' raggiungibile
! via un altro percorso. Contro le best practice: il tunnel source deve essere
! una Loopback per garantire stabilita'.
```

Fix:
```
HUB(config)# interface Tunnel202
HUB(config-if)# tunnel source Loopback0
```

#### VERIFICA finale Part 2

```
HUB# show ip interface brief | include Tunnel
```

Output atteso (tutti up/up):
```
Tunnel101   172.16.101.1  YES manual  up  up
Tunnel102   172.16.102.1  YES manual  up  up
Tunnel201   172.16.201.1  YES manual  up  up
Tunnel202   172.16.202.1  YES manual  up  up
```

> **Checkpoint Part 2:** Tutti i tunnel GRE in line protocol UP. Ping sugli IP tunnel riuscito (`HUB# ping vrf CUST-A 172.16.101.2`). Non ci sono ancora route verso i loopback degli spoke.

---

### PART 3 — Routing Statico in VRF

#### TEORIA

In una VRF, le route statiche devono essere associate esplicitamente alla VRF con la keyword `vrf`. Il next-hop o l'interfaccia di uscita devono essere raggiungibili nella stessa VRF.

```
! Sintassi route statica VRF-aware
ip route vrf NOME-VRF RETE MASCHERA {next-hop-IP | interfaccia-uscita}

! Esempio HUB: route verso SP1 Lo1 tramite Tunnel101
ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel101
```

**Design P2P e il limite del routing statico:**

Ogni router ha tunnel GRE diretti solo verso HUB (SP1 ha Tu101, SP2 ha Tu102). Non esiste un tunnel SP1↔SP2 diretto. Conseguenza:

```
Traffico SP1 Lo1 → SP2 Lo1:
  SP1 → [Tu101] → HUB → [Tu102] → SP2    (2 hop, via HUB)

Con DMVPN Phase 2 (MOD-19):
  SP1 → [Tu110 mGRE] → SP2               (1 hop, diretto)
```

Questo traceroute a 2 hop sara' la prova visiva alla fine del task — e la motivazione principale per introdurre DMVPN.

#### TASK T3.1 — Route statiche VRF CUST-A su HUB

```
HUB(config)# ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel101
HUB(config)# ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel102
```

#### VERIFICA T3.1

```
HUB# show ip route vrf CUST-A
```

Output atteso:
```
Routing Table: CUST-A
      10.0.0.0/32 is subnetted, 3 subnets
C        10.1.1.1 is directly connected, Loopback1
S        10.1.2.1 [1/0] via Tunnel101, directly connected
S        10.1.3.1 [1/0] via Tunnel102, directly connected
      172.16.0.0/30 is subnetted, 2 subnets
C        172.16.101.0 is directly connected, Tunnel101
C        172.16.102.0 is directly connected, Tunnel102
```

#### TASK T3.2 — Route statiche VRF CUST-A su SP1

```
SP1(config)# ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel101
SP1(config)# ip route vrf CUST-A 10.1.3.1 255.255.255.255 Tunnel101
```

> SP1→HUB e SP1→SP2 usano entrambe Tu101 perche' non esiste un tunnel diretto SP1↔SP2. HUB fa il forwarding del traffico verso SP2.

#### TASK T3.3 — Route statiche VRF CUST-A su SP2

```
SP2(config)# ip route vrf CUST-A 10.1.1.1 255.255.255.255 Tunnel102
SP2(config)# ip route vrf CUST-A 10.1.2.1 255.255.255.255 Tunnel102
```

#### TASK T3.4 — Ping end-to-end VRF CUST-A

```
HUB# ping vrf CUST-A 10.1.2.1 source Loopback1
HUB# ping vrf CUST-A 10.1.3.1 source Loopback1
SP1# ping vrf CUST-A 10.1.1.1 source Loopback1
SP1# ping vrf CUST-A 10.1.3.1 source Loopback1
SP2# ping vrf CUST-A 10.1.1.1 source Loopback1
SP2# ping vrf CUST-A 10.1.2.1 source Loopback1
```

Tutti i ping devono ritornare `!!!!!`.

#### TASK T3.5 — Traceroute SP1→SP2 via HUB

```
SP1# traceroute vrf CUST-A 10.1.3.1 source Loopback1
```

Output atteso:
```
Type escape sequence to abort.
Tracing the route to 10.1.3.1
VRF info: (vrf in name/id, vrf out name/id)
  1  172.16.101.1  msec msec msec     ← IP tunnel HUB (hop intermedio!)
  2  10.1.3.1      msec msec msec     ← SP2 Lo1
```

Il primo hop e' l'IP tunnel di HUB — conferma che SP1→SP2 transita per HUB con questo design P2P. In MOD-19 (DMVPN Phase 2) questa traccia mostrera' un solo hop diretto.

> **Checkpoint Part 3:** Ping VRF CUST-A funzionanti su tutti i 6 path. Traceroute SP1→SP2 mostra HUB come hop intermedio. Il design P2P e' operativo ma non scalabile — motivazione per DMVPN.

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa | Diagnosi | Fix |
|---------|-------|----------|-----|
| `show ip route vrf CUST-A` non mostra /32 locale | `vrf forwarding` mancante su Lo1 oppure IP configurato prima della VRF | `show ip interface Lo1` → `VRF: not set` | `vrf forwarding CUST-A` poi ridigitare IP |
| Tunnel line protocol DOWN | Underlay non raggiungibile — Lo0 destinazione non pingabile | `ping <tunnel-dest>` dalla global table | Verificare default route e ISP |
| Tunnel UP ma ping VRF fallisce | Route statica VRF mancante o con next-hop errato | `show ip route vrf CUST-A` — manca la /32 di destinazione | Aggiungere/correggere `ip route vrf CUST-A` |
| `show ip route vrf CUST-B` su HUB mostra 10.2.2.1 | HUB Lo2 ha IP sbagliato (di SP1 invece di HUB) | `show ip route vrf CUST-B` → 10.2.2.1 duplicato | `ip address 10.2.1.1 255.255.255.255` su HUB Lo2 |
| SP1 Lo2 non appare in tabella VRF CUST-B | `vrf forwarding CUST-B` mancante — Lo2 e' in global table | `show ip interface Lo2` → `VRF: not set` | `vrf forwarding CUST-B` poi ridigitare IP |
| Tunnel201 SP1 non comunica con HUB | `tunnel destination` punta a SP2 (203.0.113.254) invece di HUB | `show interface Tu201` → destination 203.0.113.254 | `tunnel destination 192.0.2.254` |
| Tunnel202 HUB perde connettivita' al link flap | `tunnel source` usa Ethernet0/0.10 invece di Lo0 | `show interface Tu202` → source Ethernet0/0.10 | `tunnel source Loopback0` |
| Ping vrf CUST-A OK ma ping senza source fallisce | Source dell'ICMP e' in global table, non in VRF | `ping vrf CUST-A 10.1.2.1` senza source → timeout | Usare sempre `source Loopback1` nei ping VRF |

---

## 7. SOLUZIONI

> **Attenzione:** questa sezione e' riservata al docente. Non distribuire agli studenti prima del lab.

Vedi file `MOD-17/soluzione.md` per la configurazione completa e i fix dei bug.

---

## 8. RIEPILOGO & EXAM TIPS

### Concetti chiave

- **VRF-Lite** crea tabelle di routing virtuali indipendenti sullo stesso router fisico, senza richiedere MPLS ne' MP-BGP
- **RD (Route Distinguisher)** e' obbligatorio nella sintassi `vrf definition` ma non distribuisce route — questo e' compito di MP-BGP in ambienti MPLS/L3VPN
- **`vrf forwarding` DEVE precedere `ip address`**: IOS rimuove automaticamente l'IP esistente quando si assegna la VRF — questo e' il bug piu' comune all'esame pratico
- **GRE usa la global table per tunnel source/destination (underlay)** e la **VRF per l'interfaccia tunnel (overlay)** — il meccanismo e' il lookup ricorsivo
- **Route statiche VRF-aware:** la keyword `vrf` e' obbligatoria — senza di essa la route finisce nella global table
- **Design P2P:** SP1↔SP2 passano sempre per HUB — DMVPN risolve con tunnel multipoint (MOD-19)

### Domande tipo CCNP ENCOR

1. Un router IOS deve isolare il traffico di due clienti sulla stessa piattaforma hardware senza MPLS. Quale tecnologia e' corretta?
   - A) VPN routing/forwarding con MP-BGP
   - **B) VRF-Lite con `vrf definition`** ← corretto
   - C) Policy-Based Routing
   - D) NAT Overload per cliente

2. Quale output indica che Loopback2 NON e' nella VRF configurata?
   - A) `show vrf` — Lo2 assente dall'elenco interfacce
   - **B) `show ip interface Lo2` → `VRF: not set`** ← comando piu' diretto
   - C) `show ip route vrf CUST-B` — assenza della /32 di Lo2
   - D) Tutte le precedenti sono valide

3. Un tunnel GRE ha line protocol UP ma il ping VRF sull'IP tunnel fallisce. Causa piu' probabile?
   - A) tunnel source errato (underlay non funziona)
   - **B) Route statica VRF mancante o errata** ← corretto — GRE e' UP, il problema e' nel routing overlay
   - C) tunnel mode sbagliato
   - D) MTU mismatch GRE

4. In `show interface Tunnel202` si legge `Tunnel source 192.0.2.2 (Ethernet0/0.10)`. Qual e' il rischio?
   - **A) Se e0/0.10 va down il tunnel cade, anche se l'ISP e' raggiungibile via altro path** ← corretto
   - B) Nessun rischio — qualsiasi interfaccia puo' essere tunnel source
   - C) Il tunnel non supporta GRE su sub-interface
   - D) L'IP del source deve coincidere con il destination

5. Qual e' il comando per vedere tutte le interfacce assegnate a VRF con i relativi IP?
   - A) `show vrf`
   - **B) `show ip vrf interfaces`** ← corretto
   - C) `show ip interface brief vrf CUST-A`
   - D) `show ip route vrf CUST-A`
