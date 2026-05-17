# Soluzione Commentata — MOD-09: PBR & Route Manipulation Avanzata

> **Uso:** riservato al docente — non distribuire agli studenti

---

## T1 — PBR Base: Traffico Guest via WAN-B

```
! Su CORE
! ACL estesa: identifica traffico da rete guest (10.99.0.0/24) verso qualsiasi dest
ip access-list extended ACL-GUEST
 permit ip 10.99.0.0 0.0.0.255 any

! Route-map PBR:
! - seq 10: traffico guest → next-hop WAN-B (10.0.23.1)
! - seq 20: tutto il resto → routing normale (permit senza match = match-all)
route-map PBR-GUEST permit 10
 match ip address ACL-GUEST
 set ip next-hop 10.0.23.1
!
route-map PBR-GUEST permit 20

! Applicazione sull'interfaccia di ingresso da LAN-A
interface Ethernet0/0.34
 ip policy route-map PBR-GUEST
```

> **Nota sulla clausola permit 20:** Senza questa clausola, il traffico non-guest che entra
> su Eth0/0.34 verrebbe droppato dalla route-map (implicit deny). La clausola `permit 20`
> senza match permette il pass-through al routing normale. Questo è un errore molto comune.
>
> **Nota su `set ip next-hop`:** Forza il next-hop anche se il routing table avrebbe scelto
> un percorso diverso. Se 10.0.23.1 non è direttamente raggiungibile (non c'è rotta),
> il pacchetto viene droppato silenziosamente. Usare `verify-availability` (T2) per proteggere.
>
> **Alternativa con `set ip default next-hop`:** `set ip default next-hop 10.0.23.1` userebbe
> WAN-B solo come "gateway of last resort" per il traffico guest — se c'è già una rotta più
> specifica per la destinazione in tabella, quella viene usata al posto di 10.0.23.1.
> Meno comune in questo scenario, ma utile quando si vuole PBR come fallback.

---

## T2 — PBR con verify-availability

```
! IP SLA: probe ICMP verso WAN-B next-hop, ogni 5 secondi
ip sla 1
 icmp-echo 10.0.23.1 source-ip 10.0.23.2
  frequency 5
ip sla schedule 1 life forever start-time now

! Track object: Up se SLA risponde, Down se non risponde
track 1 ip sla 1 reachability

! Route-map aggiornata: verify-availability condiziona il next-hop al track
route-map PBR-GUEST permit 10
 match ip address ACL-GUEST
 set ip next-hop verify-availability 10.0.23.1 1 track 1
!
route-map PBR-GUEST permit 20
```

> **Comportamento con verify-availability:**
> - Track 1 Up: traffico guest → WAN-B (10.0.23.1)
> - Track 1 Down: la clausola seq 10 non applica il set; il traffico passa alla seq 20
>   (permit senza match = routing normale)
>
> **Parametro `1` dopo l'IP:** è il sequence number del next-hop. Si possono definire più
> next-hop alternativi con sequence crescenti:
> ```
> set ip next-hop verify-availability 10.0.23.1 1 track 1
> set ip next-hop verify-availability 10.0.12.1 2 track 2
> ```
> Il router prova in ordine: 10.0.23.1 (se track 1 Up), poi 10.0.12.1 (se track 2 Up).
>
> **source-ip nell'IP SLA:** specificare l'IP dell'interfaccia verso WAN-B (10.0.23.2) garantisce
> che se quella interfaccia cade, il probe fallisca — anche se il router ha altri percorsi
> verso WAN-B. Senza source-ip, IOS usa la best route → il probe potrebbe passare
> anche con WAN-B irraggiungibile dal path diretto.

---

## T3A — Administrative Distance

```
! Su CORE — aumenta AD eBGP da 20 a 150 (OSPF E1 ha AD=110 → OSPF vince)
router bgp 65000
 distance bgp 150 200 200

! Per ripristinare default:
! no distance bgp
```

> **Impatto pratico in questa topologia:** il next-hop fisico non cambia (sia BGP che OSPF
> puntano allo stesso next-hop), quindi il routing effettivo non muta. Il valore didattico
> è mostrare il meccanismo di preferenza.
>
> **Scenario reale:** In una topologia con due ASBR (es. CORE-1 peera con WAN-A, CORE-2 peera
> con WAN-B), manipolare l'AD determina quale ASBR è preferito per raggiungere un prefisso.

---

## T3B — Floating Static Route

```
! Su CORE — backup route verso LAN-A prod, via WAN-B, con AD=200
! AD=200 > OSPF AD=110 → statica resta sommersa finché OSPF ha la rotta
ip route 10.10.0.0 255.255.255.0 10.0.23.1 200
```

> **Verifica del comportamento:** Con OSPF attivo, `show ip route 10.10.0.0` mostra solo la
> rotta OSPF. Dopo shutdown di Eth0/0.34 (link verso LAN-A), OSPF rimuove la rotta e la
> static con AD=200 emerge.
>
> **Errore comune:** usare AD=100 (minore di OSPF 110) → la static route è SEMPRE preferita
> e non è affatto "floating". Per essere floating, AD deve essere maggiore del protocollo primario.
>
> **Nota su next-hop 10.0.23.1:** questo presuppone che WAN-B sia raggiungibile e che il
> traffico verso LAN-A possa tornare via WAN-B (scenario di routing asimmetrico). In lab,
> serve per mostrare il meccanismo; in produzione si userebbe un percorso effettivamente alternativo.

---

## T3C — IP SLA + Track per Rotta Condizionale

```
! IP SLA 2: monitora raggiungibilità ISP-B (200.0.0.1) via WAN-B
ip sla 2
 icmp-echo 200.0.0.1 source-ip 10.0.23.2
  frequency 5
ip sla schedule 2 life forever start-time now

! Track 2: stato basato su raggiungibilità SLA 2
track 2 ip sla 2 reachability

! Rotta statica condizionale: AD=1 → vince su OSPF E1 (AD=110) quando track è Up
! Rimossa automaticamente quando track 2 diventa Down
ip route 200.0.0.0 255.0.0.0 10.0.23.1 1 track 2
```

> **Perché AD=1?** Con AD=1, la static vince su qualsiasi rotta dinamica (eccetto connected=0).
> Quando il track è Down (ISP-B irraggiungibile), la static viene rimossa e OSPF E1 (AD=110)
> emerge come percorso alternativo.
>
> **Differenza da floating static (T3B):**
> - Floating static: failover basato sul link fisico (interfaccia down)
> - IP SLA + track: failover basato sulla raggiungibilità applicativa (host risponde a ICMP?)
> Il secondo è più robusto perché rileva guasti end-to-end (link attivo ma routing rotto).
>
> **Timeout di convergenza:** frequenza=5s → track Down dopo ~2-3 probe falliti (~10-15s).
> Ridurre la frequenza accelera il failover ma aumenta il traffico di management.

---

## Configurazione Finale CORE (MOD-09 completo)

```
hostname CORE
!
no ip domain-lookup
!
interface Loopback0
 ip address 10.255.0.1 255.255.255.255
 ip ospf 1 area 0
!
interface Ethernet0/0
 no shutdown
!
interface Ethernet0/0.12
 encapsulation dot1Q 12
 ip address 10.0.12.2 255.255.255.252
 description to_WAN-A
 ip ospf 1 area 0
!
interface Ethernet0/0.23
 encapsulation dot1Q 23
 ip address 10.0.23.2 255.255.255.252
 description to_WAN-B
 ip ospf 1 area 0
!
interface Ethernet0/0.34
 encapsulation dot1Q 34
 ip address 10.0.34.1 255.255.255.252
 description to_LAN-A
 ip ospf 1 area 0
 ip policy route-map PBR-GUEST
!
interface Ethernet0/0.35
 encapsulation dot1Q 35
 ip address 10.0.35.1 255.255.255.252
 description to_LAN-B
 ip ospf 1 area 0
!
ip access-list extended ACL-GUEST
 permit ip 10.99.0.0 0.0.0.255 any
!
ip prefix-list INTERNAL-ONLY seq 10 permit 10.10.0.0/24
ip prefix-list INTERNAL-ONLY seq 20 permit 10.20.0.0/24
ip prefix-list INTERNAL-ONLY seq 30 deny 0.0.0.0/0 le 32
!
ip prefix-list ISP-PREFIXES seq 10 permit 100.0.0.0/8
ip prefix-list ISP-PREFIXES seq 20 permit 200.0.0.0/8
ip prefix-list ISP-PREFIXES seq 30 deny 0.0.0.0/0 le 32
!
ip sla 1
 icmp-echo 10.0.23.1 source-ip 10.0.23.2
  frequency 5
ip sla schedule 1 life forever start-time now
!
ip sla 2
 icmp-echo 200.0.0.1 source-ip 10.0.23.2
  frequency 5
ip sla schedule 2 life forever start-time now
!
track 1 ip sla 1 reachability
track 2 ip sla 2 reachability
!
route-map OSPF-TO-BGP deny 5
 match tag 100
!
route-map OSPF-TO-BGP permit 10
 match ip address prefix-list INTERNAL-ONLY
!
route-map BGP-TO-OSPF permit 10
 match ip address prefix-list ISP-PREFIXES
 set tag 100
!
route-map PBR-GUEST permit 10
 match ip address ACL-GUEST
 set ip next-hop verify-availability 10.0.23.1 1 track 1
!
route-map PBR-GUEST permit 20
!
ip route 200.0.0.0 255.0.0.0 10.0.23.1 1 track 2
!
router ospf 1
 router-id 10.255.0.1
 passive-interface Loopback0
 redistribute bgp 65000 metric 20 metric-type 1 subnets route-map BGP-TO-OSPF
!
router bgp 65000
 bgp router-id 10.255.0.1
 no bgp default ipv4-unicast
 neighbor 10.0.12.1 remote-as 65001
 neighbor 10.0.23.1 remote-as 65002
 !
 address-family ipv4
  neighbor 10.0.12.1 activate
  neighbor 10.0.23.1 activate
  redistribute ospf 1 route-map OSPF-TO-BGP
 exit-address-family
!
end
```

---

## Note Varianti & Alternative

**PBR con `set interface`:**
Invece di `set ip next-hop`, si può usare `set interface Ethernet0/0.23` per inviare
il traffico sull'interfaccia specifica. Meno preciso (IOS sceglie l'IP come next-hop),
ma utile per link point-to-point dove il next-hop è ovvio.

**ip local policy:**
Se CORE stesso genera traffico (es. ping da CORE) e si vuole applicare PBR anche a quello,
aggiungere `ip local policy route-map PBR-GUEST` a livello globale. Il PBR su interfaccia
non intercetta il traffico generato localmente dal router.

**Dual SLA per ridondanza:**
In produzione si configurano due IP SLA (uno per WAN-A, uno per WAN-B) e due track.
La route-map PBR usa verify-availability con due entry in sequenza:
```
set ip next-hop verify-availability 10.0.23.1 1 track 1   ! WAN-B — preferito
set ip next-hop verify-availability 10.0.12.1 2 track 2   ! WAN-A — fallback
```
Se WAN-B cade, il traffico guest va automaticamente su WAN-A.
