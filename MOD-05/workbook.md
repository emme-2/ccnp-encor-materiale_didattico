# Workbook Studenti — MOD-05: BGP Fondamenta

**Area:** AREA 2 — BGP | **Ore:** 2h | **Codici syllabus:** 3.2.c · 1.11.a · 1.11.b

---

## 1. TOPOLOGIA

### Diagramma Logico

```
  ┌─────────────── AS 65001 (ISP) ───────────────┐     ┌────────── AS 65000 (Customer) ──────────┐
  │                                               │     │                                          │
  │   Lo0:1.1.1.1     Lo0:2.2.2.2                │     │   Lo0:4.4.4.4     Lo0:5.5.5.5           │
  │      R1 ──────────── R2                       │     │      R4 ──────────── R5                 │
  │      │ \           / │                        │     │      │ \           / │                  │
  │      │  \         /  │                        │     │      │  \         /  │                  │
  │      │   R3──────┘   │           eBGP         │     │      │   R6──────┘   │                  │
  │      │   │  Lo0:     │     ┌─────────────┐    │     │      │   │  Lo0:     │                  │
  │      │   │ 3.3.3.3   │     │ 172.16.14.x │    │     │      │   │ 6.6.6.6   │                  │
  │      │   │           ├─────┤  R1 ↔ R4   ├────┤     ├──────┤   │           │                  │
  │      │   │           │     │ (operativo) │    │     │      │   │           │                  │
  │      │   │           │     └─────────────┘    │     │      │   │           │                  │
  │      │   │           │     ┌─────────────┐    │     │      │   │           │                  │
  │      │   │           ├─────┤ 172.16.35.x ├────┤     ├──────┤   │           │                  │
  │      │   │           │     │  R3 ↔ R5   │    │     │      │   │           │                  │
  │      │   │           │     │ (MANCANTE!) │    │     │      │   │           │                  │
  │      │   │           │     └─────────────┘    │     │      │   │           │                  │
  └──────────────────────┘                        └─────────────────────────────┘
       OSPF 1 + iBGP                                    OSPF 1 + iBGP
       full-mesh (pre-cfg)                              (da configurare)
```

### Piano di Indirizzamento

Tutti i router sono connessi fisicamente allo stesso switch GNS3 tramite `Ethernet0/0`.
I link logici punto-punto sono realizzati con **sub-interface 802.1Q**.
Convenzione VLAN: concatenazione dei numeri dei due router (es. R1–R4 → VLAN 14).

#### Link interni AS 65001 (ISP) — pre-configurati

| Collegamento | VLAN | Sub-interface | IP Lato A | IP Lato B | Ruolo |
|---|---|---|---|---|---|
| R1 — R2 | 12 | Eth0/0.12 / Eth0/0.12 | 10.0.12.1/30 | 10.0.12.2/30 | ISP Internal |
| R1 — R3 | 13 | Eth0/0.13 / Eth0/0.13 | 10.0.13.1/30 | 10.0.13.2/30 | ISP Internal |
| R2 — R3 | 23 | Eth0/0.23 / Eth0/0.23 | 10.0.23.1/30 | 10.0.23.2/30 | ISP Internal |

#### Link eBGP — inter-AS

| Collegamento | VLAN | Sub-interface | IP Lato A | IP Lato B | Stato |
|---|---|---|---|---|---|
| R1 — R4 | 14 | Eth0/0.14 / Eth0/0.14 | 172.16.14.1/30 | 172.16.14.2/30 | **PRE-CONFIGURATO** |
| R3 — R5 | 35 | Eth0/0.35 / Eth0/0.35 | 172.16.35.1/30 | 172.16.35.2/30 | **DA CONFIGURARE** (Task 3) |

#### Link interni AS 65000 (Customer) — da configurare

| Collegamento | VLAN | Sub-interface | IP Lato A | IP Lato B | Ruolo |
|---|---|---|---|---|---|
| R4 — R5 | 45 | Eth0/0.45 / Eth0/0.45 | 192.168.45.1/30 | 192.168.45.2/30 | Customer Internal |
| R4 — R6 | 46 | Eth0/0.46 / Eth0/0.46 | 192.168.46.1/30 | 192.168.46.2/30 | Customer Internal |
| R5 — R6 | 56 | Eth0/0.56 / Eth0/0.56 | 192.168.56.1/30 | 192.168.56.2/30 | Customer Internal |

#### Loopback (identificatori router)

| Router | Loopback0 | AS | Ruolo |
|---|---|---|---|
| R1 | 1.1.1.1/32 | 65001 | ISP border |
| R2 | 2.2.2.2/32 | 65001 | ISP internal |
| R3 | 3.3.3.3/32 | 65001 | ISP border |
| R4 | 4.4.4.4/32 | 65000 | Customer border |
| R5 | 5.5.5.5/32 | 65000 | Customer border |
| R6 | 6.6.6.6/32 | 65000 | Customer internal |

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sarà in grado di:

- [ ] Configurare OSPF come IGP in un Autonomous System cliente
- [ ] Configurare un iBGP full-mesh con `update-source Loopback0` e `next-hop-self`
- [ ] Diagnosticare e ripristinare un peering eBGP mancante tramite troubleshooting metodico
- [ ] Annunciare prefissi BGP con `network statement` e distinguere l'Origin IGP (i) da Origin Incomplete (?)
- [ ] Filtrare gli annunci BGP uscenti con prefix-list e route-map
- [ ] Abilitare e utilizzare `soft-reconfiguration inbound` per il debug non invasivo

**Codici syllabus coperti:** 3.2.c · 1.11.a · 1.11.b

---

## 3. LAB SETUP

### File cfg da caricare via TFTP

All'avvio del lab caricare i file di configurazione iniziale sui rispettivi router:

```
! Su ogni router (sostituire rx con r1, r2, ... r6)
copy tftp://192.168.122.1/ENCOR/MOD-05/rx-cfg running-config
```

> **Nota:** I file cfg TFTP per questo modulo sono in fase di sviluppo (placeholder).
> La configurazione iniziale pre-carica su AS 65001: interfacce, loopback, OSPF 1, iBGP full-mesh R1/R2/R3, e il peering eBGP R1↔R4.

### Cosa e' gia' pre-configurato

| Elemento | Router | Stato |
|---|---|---|
| Interfacce sub-interface + loopback | Tutti | Pre-configurato |
| OSPF 1 (link interni + loopback) | R1, R2, R3 | Pre-configurato |
| iBGP full-mesh (update-source Lo0) | R1, R2, R3 | Pre-configurato |
| eBGP R1 ↔ R4 | R1, R4 | Pre-configurato e operativo |
| OSPF 1 Customer | R4, R5, R6 | **DA CONFIGURARE** |
| iBGP full-mesh Customer | R4, R5, R6 | **DA CONFIGURARE** |
| eBGP R3 ↔ R5 | R3, R5 | **DA CONFIGURARE** |

### Prerequisiti

- GNS3 avviato con topologia MOD-05 caricata
- Connettivita' base verificata (ping tra interfacce direttamente connesse)
- Conoscenza base di OSPF (aree, neighbor, LSA)
- Concetto di Autonomous System e protocollo BGP (teoria introduttiva)

### Verifica pre-lab

Eseguire prima di iniziare i task:

```
! Su R1 — verifica che OSPF ISP sia operativo
R1# show ip ospf neighbor
R1# show ip route ospf

! Su R1 — verifica che iBGP ISP sia operativo
R1# show ip bgp summary

! Su R1 — verifica che il peering eBGP R1-R4 sia Established
R1# show bgp neighbors 172.16.14.2 | include BGP state

! Su R4 — verifica che riceva il prefisso 1.1.1.1/32 via eBGP
R4# show ip bgp
```

Output atteso (R1 `show ip bgp summary`):
```
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
2.2.2.2         4 65001      xx      xx        x    0    0  xx:xx:xx        0
3.3.3.3         4 65001      xx      xx        x    0    0  xx:xx:xx        0
172.16.14.2     4 65000      xx      xx        x    0    0  xx:xx:xx        1
```

---

## 4. TASK LIST

| # | Task | Codici syllabus | Tempo stimato |
|---|---|---|---|
| T1 | OSPF IGP in AS 65000 (Customer) | 3.2.c | 15 min |
| T2 | iBGP full-mesh in AS 65000 | 1.11.a | 20 min |
| T3 | Diagnosi e configurazione peering mancante R3↔R5 | 1.11.a | 20 min |
| T4 | Annunci BGP: network statement vs redistribute (Origin) | 1.11.b | 20 min |
| T5 | Filtro annunci con prefix-list e route-map | 1.11.b | 15 min |
| T6 | Soft-reconfiguration inbound | 1.11.b | 10 min |

**Tempo totale: ~100 min** (buffer: 20 min)

---

## 5. DETTAGLIO TASK

---

### T1 — OSPF IGP in AS 65000

#### TEORIA

**Perche' un IGP prima di BGP?**

BGP utilizza le route IGP per due scopi fondamentali:

1. **Raggiungibilita' dei next-hop iBGP**: in un AS con piu' border router, il next-hop di un prefisso appreso via eBGP (es. 172.16.14.1) deve essere raggiungibile dai router interni. Senza OSPF, R6 non saprebbe come raggiungere 172.16.14.1.
2. **Trasporto iBGP**: le sessioni iBGP usano i loopback come source (`update-source Loopback0`). La raggiungibilita' tra loopback richiede OSPF.

**Regola pratica:** BGP si configura DOPO che l'IGP e' convergente.

**Comandi OSPF essenziali su IOS:**
```
router ospf <process-id>
 network <network> <wildcard> area <area-id>
 passive-interface <interface>   ! loopback: non manda hello
```

#### TASK

Configurare OSPF process 1, area 0, su R4, R5 e R6.
Includere tutti i link interni e i loopback. Dichiarare i loopback come `passive-interface`.

**R4:**
```
R4# configure terminal
R4(config)# router ospf 1
R4(config-router)# network 4.4.4.4 0.0.0.0 area 0
R4(config-router)# network 192.168.45.0 0.0.0.3 area 0
R4(config-router)# network 192.168.46.0 0.0.0.3 area 0
R4(config-router)# passive-interface Loopback0
R4(config-router)# end
```

**R5:**
```
R5# configure terminal
R5(config)# router ospf 1
R5(config-router)# network 5.5.5.5 0.0.0.0 area 0
R5(config-router)# network 192.168.45.0 0.0.0.3 area 0
R5(config-router)# network 192.168.56.0 0.0.0.3 area 0
R5(config-router)# passive-interface Loopback0
R5(config-router)# end
```

**R6:**
```
R6# configure terminal
R6(config)# router ospf 1
R6(config-router)# network 6.6.6.6 0.0.0.0 area 0
R6(config-router)# network 192.168.46.0 0.0.0.3 area 0
R6(config-router)# network 192.168.56.0 0.0.0.3 area 0
R6(config-router)# passive-interface Loopback0
R6(config-router)# end
```

#### VERIFICA

```
! Su R4 — atteso: vicini R5 e R6 in stato FULL
R4# show ip ospf neighbor

! Su R4 — attese: route O per 5.5.5.5, 6.6.6.6 e link remoti
R4# show ip route ospf

! Connettivita' loopback-to-loopback
R4# ping 5.5.5.5 source Loopback0
R4# ping 6.6.6.6 source Loopback0
```

Output atteso (`show ip ospf neighbor` su R4):
```
Neighbor ID     Pri   State           Dead Time   Address         Interface
5.5.5.5           1   FULL/DR         00:00:39    192.168.45.2    Ethernet0/0.45
6.6.6.6           1   FULL/DR         00:00:39    192.168.46.2    Ethernet0/0.46
```

---

### T2 — iBGP full-mesh in AS 65000

#### TEORIA

**La regola Split-Horizon di iBGP**

Un router BGP che apprende un prefisso da un peer iBGP **non lo ri-annuncia ad altri peer iBGP**. Questa regola previene i loop di routing all'interno dell'AS.

Conseguenza: in un AS con N router BGP, ogni router deve avere una sessione iBGP diretta verso tutti gli altri (full-mesh). Per N=3 router, servono 3 sessioni (R4-R5, R4-R6, R5-R6).

**Differenze chiave iBGP vs eBGP:**

| Parametro | eBGP | iBGP |
|---|---|---|
| TTL IP | 1 (default) | 255 |
| Administrative Distance | 20 | 200 |
| Next-hop | Modificato | **Non modificato** (problema!) |
| AS-Path | Aggiunto | Non modificato |

**Il problema del next-hop iBGP:** quando R4 annuncia a R6 via iBGP un prefisso appreso da R1 via eBGP, il next-hop rimane 172.16.14.1 (R1). R6 non ha una route verso 172.16.14.1 (non e' in OSPF Customer). Soluzione: `next-hop-self` fa si' che R4 sostituisca il next-hop con il proprio IP di loopback.

**update-source Loopback0:** le sessioni iBGP usano il loopback come source per stabilita' (il loopback non va mai down).

#### TASK

Configurare iBGP full-mesh tra R4, R5 e R6 usando i loopback come source.

**R4:**
```
R4# configure terminal
R4(config)# router bgp 65000
R4(config-router)# bgp router-id 4.4.4.4
R4(config-router)# neighbor 5.5.5.5 remote-as 65000
R4(config-router)# neighbor 5.5.5.5 update-source Loopback0
R4(config-router)# neighbor 5.5.5.5 next-hop-self
R4(config-router)# neighbor 6.6.6.6 remote-as 65000
R4(config-router)# neighbor 6.6.6.6 update-source Loopback0
R4(config-router)# neighbor 6.6.6.6 next-hop-self
R4(config-router)# end
```

**R5:**
```
R5# configure terminal
R5(config)# router bgp 65000
R5(config-router)# bgp router-id 5.5.5.5
R5(config-router)# neighbor 4.4.4.4 remote-as 65000
R5(config-router)# neighbor 4.4.4.4 update-source Loopback0
R5(config-router)# neighbor 4.4.4.4 next-hop-self
R5(config-router)# neighbor 6.6.6.6 remote-as 65000
R5(config-router)# neighbor 6.6.6.6 update-source Loopback0
R5(config-router)# neighbor 6.6.6.6 next-hop-self
R5(config-router)# end
```

**R6:**
```
R6# configure terminal
R6(config)# router bgp 65000
R6(config-router)# bgp router-id 6.6.6.6
R6(config-router)# neighbor 4.4.4.4 remote-as 65000
R6(config-router)# neighbor 4.4.4.4 update-source Loopback0
R6(config-router)# neighbor 4.4.4.4 next-hop-self
R6(config-router)# neighbor 5.5.5.5 remote-as 65000
R6(config-router)# neighbor 5.5.5.5 update-source Loopback0
R6(config-router)# neighbor 5.5.5.5 next-hop-self
R6(config-router)# end
```

#### VERIFICA

```
! Su R4 — atteso: R5 e R6 in stato Established
R4# show ip bgp summary

! Verifica dettaglio singolo neighbor
R4# show ip bgp neighbors 5.5.5.5 | include BGP state

! Su R6 — verifica che veda gia' il prefisso 1.1.1.1/32 (via iBGP da R4)
R6# show ip bgp
```

Output atteso (`show ip bgp summary` su R4):
```
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
5.5.5.5         4 65000      xx      xx        x    0    0  xx:xx:xx        0
6.6.6.6         4 65000      xx      xx        x    0    0  xx:xx:xx        0
172.16.14.1     4 65001      xx      xx        x    0    0  xx:xx:xx        1
```

> **Nota:** il prefisso 1.1.1.1/32 e' gia' visibile su R4 perche' il peering eBGP R1↔R4 e' pre-configurato.

---

### T3 — Diagnosi e configurazione del peering mancante R3↔R5

#### TEORIA

**Il metodo BGP troubleshooting**

Quando un prefisso non appare dove atteso, seguire la catena:

```
Prefisso su R1 → iBGP a R3 → eBGP a R5 → iBGP a R4/R6
```

Se la catena si spezza, il prefisso si ferma al punto di rottura. Il primo passo e' identificare DOVE si spezza guardando `show ip bgp summary` su ogni router della catena.

**Stati BGP Neighbor:**

| Stato | Significato |
|---|---|
| Idle | BGP non ha tentato di connettersi (o ha fallito e aspetta) |
| Active | BGP sta tentando la connessione TCP (problema: no risposta) |
| OpenSent | TCP connessa, OpenSent inviato |
| Established | Sessione operativa |

**Causa piu' comune di stato Active:** AS remoto errato, IP neighbor errato, ACL che blocca porta 179, MTU mismatch.

#### TASK

**Fase 1 — Diagnosi**

```
! Su R3 — verifica quanti neighbor BGP ha
R3# show ip bgp summary

! Su R5 — stessa verifica
R5# show ip bgp summary

! Su R5 — verifica routing table: c'e' un path verso R3?
R5# show ip route 172.16.35.1

! Su R3 — verifica che l'interfaccia eBGP sia up
R3# show interface Ethernet0/0.35
```

**Fase 2 — Configurazione**

Il link R3–R5 e' gia' fisicamente configurato (sub-interface Eth0/0.35). Mancano solo le istruzioni BGP.

**R3** (AS 65001 — parla con AS 65000):
```
R3# configure terminal
R3(config)# router bgp 65001
R3(config-router)# neighbor 172.16.35.2 remote-as 65000
R3(config-router)# end
```

**R5** (AS 65000 — parla con AS 65001):
```
R5# configure terminal
R5(config)# router bgp 65000
R5(config-router)# neighbor 172.16.35.1 remote-as 65001
R5(config-router)# end
```

> **Nota IOU:** su IOS/IOU il TTL eBGP default e' 1. Poiche' R3 e R5 sono direttamente connessi (un solo hop), `ebgp-multihop` non e' necessario.

#### VERIFICA

```
! Su R3 — atteso: 172.16.35.2 Established
R3# show ip bgp summary
R3# show bgp neighbors 172.16.35.2 | include BGP state

! Su R5 — atteso: 172.16.35.1 Established
R5# show ip bgp summary

! Su R5 — verifica propagazione prefissi: ora deve vedere 1.1.1.1/32
R5# show ip bgp

! Su R6 — verifica che riceva 1.1.1.1/32 via iBGP (da R5)
R6# show ip bgp 1.1.1.1
```

Output atteso (`show ip bgp summary` su R5 dopo la configurazione):
```
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
4.4.4.4         4 65000      xx      xx        x    0    0  xx:xx:xx        x
6.6.6.6         4 65000      xx      xx        x    0    0  xx:xx:xx        x
172.16.35.1     4 65001      xx      xx        x    0    0  xx:xx:xx        1
```

---

### T4 — Annunci BGP: network statement vs redistribute

#### TEORIA

**Due modi per annunciare prefissi in BGP:**

**Metodo 1 — `network` statement:**
- Il router cerca nella routing table la rete esatta con la subnet mask specificata
- Se la trova, la inserisce in BGP con Origin = **i** (IGP)
- Se non la trova, il network statement viene ignorato (silenziosamente!)
- Piu' preciso e controllato

**Metodo 2 — `redistribute`:**
- Prende TUTTE le route dall'IGP (o connected) e le inserisce in BGP
- Origin = **?** (Incomplete) — indica che l'origine non e' ben definita
- Meno controllato: rischio di annunciare prefissi non voluti

**L'attributo Origin nel BGP best-path:**
- Origin IGP (i) e' preferito rispetto a Origin Incomplete (?)
- Visibile nella colonna di sinistra in `show ip bgp` (simbolo `i` o `?`)
- Per l'esame: network statement → origin i; redistribute → origin ?

**Perche' la route deve essere nella routing table?**

Il network statement `network 4.4.4.4 mask 255.255.255.255` funziona solo se `4.4.4.4/32` e' nella routing table di R4 (ad esempio come route Connected del loopback). BGP non crea route: le annuncia.

#### TASK

**Parte A — Annuncio con network statement (origin i)**

Configurare R4 per annunciare il loopback e un link interno via network statement:

```
R4# configure terminal
R4(config)# router bgp 65000
R4(config-router)# network 4.4.4.4 mask 255.255.255.255
R4(config-router)# network 192.168.45.0 mask 255.255.255.252
R4(config-router)# end
```

**Parte B — Annuncio con redistribute connected (origin ?)**

Aggiungere anche una redistribuzione per confronto:

```
R4# configure terminal
R4(config)# router bgp 65000
R4(config-router)# redistribute connected
R4(config-router)# end
```

#### VERIFICA

```
! Su R4 — osservare colonna di sinistra: i = IGP, ? = Incomplete
R4# show ip bgp

! Su R1 — verifica che i prefissi arrivino dall'AS 65000
R1# show ip bgp

! Confronto origin: cerca 4.4.4.4/32 (i) e 192.168.46.0/30 (? da redistribute)
R1# show ip bgp 4.4.4.4
R1# show ip bgp 192.168.46.0
```

Output atteso (`show ip bgp` su R4, parziale):
```
   Network          Next Hop            Metric LocPrf Weight Path
*> 1.1.1.1/32       172.16.14.1              0             0 65001 i
*> 4.4.4.4/32       0.0.0.0                  0         32768 i
*> 192.168.45.0/30  0.0.0.0                  0         32768 i
*> 192.168.46.0/30  0.0.0.0                  0         32768 ?
```

> Nota: `*>` = best path selezionato. La colonna `Path` mostra l'AS-Path; `i` alla fine = Origin IGP, `?` = Origin Incomplete.

**Cleanup (opzionale):** per i task successivi rimuovere il redistribute per evitare annunci indesiderati:
```
R4(config)# router bgp 65000
R4(config-router)# no redistribute connected
```

---

### T5 — Filtro annunci con prefix-list e route-map

#### TEORIA

**Perche' filtrare?**

Annunciare via BGP piu' prefissi del necessario e' una cattiva pratica (BGP route leaking). In scenari reali, il Customer dovrebbe annunciare solo i propri prefissi aggregati, non i link point-to-point interni.

**prefix-list:** definisce un insieme di prefissi (con supporto `ge`/`le` per range di lunghezza). Piu' efficiente delle ACL standard per il matching BGP.

```
ip prefix-list NOME [seq N] {permit|deny} A.B.C.D/LEN [ge M] [le M]
```

**route-map:** strumento piu' potente, permette di combinare match multipli e applicare azioni `set`. Si applica al neighbor con `neighbor X route-map NOME {in|out}`.

**Approccio di questo task:** usare una prefix-list come `match` dentro una route-map applicata outbound verso R1. Permettiamo solo 4.4.4.4/32 e 192.168.45.0/30.

#### TASK

```
R4# configure terminal

! Definire la prefix-list con i prefissi ammessi
R4(config)# ip prefix-list CUSTOMER-OUT seq 10 permit 4.4.4.4/32
R4(config)# ip prefix-list CUSTOMER-OUT seq 20 permit 192.168.45.0/30
R4(config)# ip prefix-list CUSTOMER-OUT seq 30 deny 0.0.0.0/0 le 32

! Creare la route-map che usa la prefix-list
R4(config)# route-map FILTER-TO-ISP permit 10
R4(config-route-map)# match ip address prefix-list CUSTOMER-OUT
R4(config-route-map)# exit

! Applicare la route-map outbound verso R1 (eBGP peer)
R4(config)# router bgp 65000
R4(config-router)# neighbor 172.16.14.1 route-map FILTER-TO-ISP out
R4(config-router)# end

! Forzare il refresh degli annunci verso R1
R4# clear ip bgp 172.16.14.1 soft out
```

#### VERIFICA

```
! Su R4 — verifica che cosa viene annunciato effettivamente a R1
R4# show ip bgp neighbors 172.16.14.1 advertised-routes

! Su R1 — verifica che riceva solo i prefissi permessi
R1# show ip bgp
R1# show ip bgp regexp 65000
```

Output atteso (`advertised-routes` su R4):
```
   Network          Next Hop            Metric LocPrf Weight Path
*> 4.4.4.4/32       0.0.0.0                  0         32768 i
*> 192.168.45.0/30  0.0.0.0                  0         32768 i

Total number of prefixes 2
```

---

### T6 — Soft-reconfiguration inbound

#### TEORIA

**Il problema del policy debug**

Quando si applica una policy inbound (route-map o prefix-list su `neighbor X route-map NOME in`), BGP installa in tabella solo le route che superano il filtro. Le route scartate sono invisibili. Per vederle, esistono due approcci:

1. **Hard reset** (`clear ip bgp X`): abbatte la sessione TCP e la ristabilisce. Invasivo: interrompe il traffico.
2. **Soft reset** (`clear ip bgp X soft`): ri-processa le route senza abbattere la sessione. Non invasivo.

**soft-reconfiguration inbound:** abilita la memorizzazione di tutte le route ricevute dal neighbor PRIMA dell'applicazione delle policy (pre-policy RIB). Consuma piu' memoria ma permette di vedere cosa arriva "grezzo" con `show ip bgp neighbors X received-routes`.

**Workflow debug:**
```
show ip bgp neighbors X received-routes  → prefissi pre-policy (tutti i ricevuti)
show ip bgp                              → prefissi post-policy (quelli installati)
Differenza = prefissi filtrati dalla policy
```

#### TASK

```
! Abilitare soft-reconfiguration inbound su R5 verso R3 (eBGP peer ISP)
R5# configure terminal
R5(config)# router bgp 65000
R5(config-router)# neighbor 172.16.35.1 soft-reconfiguration inbound
R5(config-router)# end

! Aggiornare la view senza hard reset
R5# clear ip bgp 172.16.35.1 soft in
```

#### VERIFICA

```
! Prefissi ricevuti prima di qualsiasi policy (pre-policy)
R5# show ip bgp neighbors 172.16.35.1 received-routes

! Prefissi effettivamente installati in tabella BGP (post-policy)
R5# show ip bgp

! Soft reset senza abbattere la sessione
R5# clear ip bgp 172.16.35.1 soft
```

> **Domanda di riflessione:** se hai applicato un filtro inbound su R5 verso R3, quale differenza ti aspetti tra `received-routes` e `show ip bgp`?

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa probabile | Diagnosi | Fix |
|---|---|---|---|
| Neighbor bloccato in **Active** | AS errato, IP errato, porta 179 bloccata, MTU mismatch | `show ip bgp summary` — verifica IP e AS; `debug ip bgp X events` | Correggere `remote-as` o IP neighbor; verificare ACL |
| Neighbor **Established** ma nessun prefisso ricevuto | Prefix-list o route-map filtra tutto outbound sul peer | `show ip bgp neighbors X advertised-routes` sul sender | Rivedere prefix-list/route-map; `clear ip bgp X soft out` |
| Route presente in BGP ma **non installata** nella routing table | AD 200 (iBGP) perso contro OSPF AD 110 per lo stesso prefisso | `show ip route X` — verifica quale protocollo ha vinto | Rimuovere dal redistribuzione OSPF, o usare `distance bgp` |
| **next-hop unreachable** (route BGP non valid) | `next-hop-self` mancante su iBGP peer | `show ip bgp` — asterisco assente; `show ip route <next-hop>` | Aggiungere `neighbor X next-hop-self` sul border router |
| `received-routes` vuoto dopo soft-reconfiguration | Comando `soft-reconfiguration inbound` non configurato | `show ip bgp neighbors X | include soft` | Aggiungere `neighbor X soft-reconfiguration inbound`; `clear soft in` |
| network statement ignorato (prefisso non appare in BGP) | La rete esatta non e' nella routing table | `show ip route X.X.X.X Y.Y.Y.Y` | Verificare subnet mask; assicurarsi che la route esista |
| Origin **?** invece di **i** | Prefisso annunciato via `redistribute` anziche' `network` | `show ip bgp` — colonna origin | Aggiungere `network` statement esplicito; rimuovere redistribute |

---

## 7. SOLUZIONI

> **SEZIONE IN SVILUPPO** — Le soluzioni complete commentate saranno disponibili nel file `soluzione.md` di questo modulo.

---

## 8. RIEPILOGO & EXAM TIPS

### Punti chiave

1. **iBGP non ri-annuncia a iBGP** → full-mesh obbligatorio (o Route Reflector, che verra' in moduli avanzati)
2. **next-hop-self** e' necessario quando il next-hop eBGP non e' raggiungibile dai router interni all'AS
3. **network statement** → Origin IGP (i) | **redistribute** → Origin Incomplete (?)
4. **soft-reconfiguration inbound** consente il debug delle policy senza hard reset della sessione BGP
5. BGP installa solo la **best path** in routing table; per vedere tutte le path usa `show ip bgp X` con dettaglio

### Exam Tips CCNP ENCOR

> Le seguenti domande sono tipiche del formato esame 350-401:

1. Un router BGP che apprende un prefisso da un peer iBGP:
   - a) Lo ri-annuncia a tutti i peer iBGP
   - b) **Non lo ri-annuncia ad altri peer iBGP**
   - c) Lo ri-annuncia solo se ha `next-hop-self`
   - d) Lo ri-annuncia solo ai peer eBGP

2. Qual e' la Administrative Distance di iBGP?
   - a) 20
   - b) 90
   - c) 110
   - **d) 200**

3. Un network statement BGP viene ignorato se:
   - a) Il prefisso e' un loopback
   - **b) La rete esatta non e' nella routing table del router**
   - c) L'AS number e' errato
   - d) Il neighbor e' in stato Active

4. Quale comando permette di vedere le route ricevute da un peer BGP PRIMA dell'applicazione delle policy inbound?
   - a) `show ip bgp neighbors X routes`
   - **b) `show ip bgp neighbors X received-routes`** (richiede soft-reconfiguration inbound)
   - c) `show ip bgp neighbors X advertised-routes`
   - d) `show ip bgp summary`

5. La differenza tra `clear ip bgp X` e `clear ip bgp X soft` e':
   - a) Nessuna differenza pratica
   - **b) Il primo abbatte la sessione TCP; il secondo ri-processa le route senza abbatterla**
   - c) Il soft e' piu' veloce perche' non aggiorna la routing table
   - d) Il soft funziona solo per eBGP
