# Soluzione Commentata — MOD-08: Redistribuzione BGP↔OSPF & Prefix Filtering

> **Uso:** riservato al docente — non distribuire agli studenti

---

## T1 — Prefix-list

```
! Su CORE
! INTERNAL-ONLY: prefissi interni da redistribuire verso BGP/ISP
ip prefix-list INTERNAL-ONLY seq 10 permit 10.10.0.0/24
ip prefix-list INTERNAL-ONLY seq 20 permit 10.20.0.0/24
ip prefix-list INTERNAL-ONLY seq 30 deny 0.0.0.0/0 le 32

! ISP-PREFIXES: prefissi ISP da redistribuire verso OSPF/LAN
ip prefix-list ISP-PREFIXES seq 10 permit 100.0.0.0/8
ip prefix-list ISP-PREFIXES seq 20 permit 200.0.0.0/8
ip prefix-list ISP-PREFIXES seq 30 deny 0.0.0.0/0 le 32
```

> **Nota:** La rete 10.99.0.0/24 (LAN-A Lo2) è volutamente esclusa da INTERNAL-ONLY.
> È la rete guest che verrà gestita tramite PBR in MOD-09 — non deve essere redistribuita agli ISP.

---

## T2 — Route-map (struttura base, senza tag)

```
! Su CORE
! OSPF-TO-BGP: filtra quali rotte OSPF passano a BGP
route-map OSPF-TO-BGP permit 10
 match ip address prefix-list INTERNAL-ONLY

! BGP-TO-OSPF: filtra quali rotte BGP passano a OSPF
route-map BGP-TO-OSPF permit 10
 match ip address prefix-list ISP-PREFIXES
```

> **Nota:** Il tag verrà aggiunto in T5. In questa fase le route-map servono solo come filtri.
> Una route-map con match vuoto (nessun `match`) matcherebbe tutto: NON lasciare route-map
> senza match in contesto redistribuzione a meno di voler redistribuire incondizionatamente.

---

## T3 — Redistribuzione OSPF → BGP

```
! Su CORE — sotto router bgp 65000 / address-family ipv4
router bgp 65000
 address-family ipv4
  redistribute ospf 1 route-map OSPF-TO-BGP
```

Verifica risultato:
```
CORE# show ip bgp
   Network         Next Hop      Metric LocPrf Weight Path
*> 10.10.0.0/24   0.0.0.0            20         32768 ?
*> 10.20.0.0/24   0.0.0.0            20         32768 ?
```
Origin `?` (incomplete) è normale per rotte redistribuite — non influenza la propagazione.

> **Nota variante:** `redistribute ospf 1` senza route-map ridistribuisce TUTTO il database OSPF
> in BGP (rotte infrastruttura incluse: 10.0.12.0/30, 10.0.23.0/30, loopback /32...).
> In ambienti di produzione questo è inaccettabile: gli ISP riceverebbero dettagli sulla rete interna.
> Usare sempre una route-map.

---

## T4 — Redistribuzione BGP → OSPF

```
! Su CORE — sotto router ospf 1
router ospf 1
 redistribute bgp 65000 metric 20 metric-type 1 subnets route-map BGP-TO-OSPF
```

Verifica risultato:
```
LAN-A# show ip route ospf
O E1  100.0.0.0/8 [110/30] via 10.0.34.1, 00:01:00, Ethernet0/0.34
O E1  200.0.0.0/8 [110/30] via 10.0.34.1, 00:01:00, Ethernet0/0.34
```
Metrica 30 = seed metric 20 + costo link LAN-A→CORE 10.

> **Errore comune — keyword `subnets` mancante:**
> `redistribute bgp 65000 metric 20 metric-type 1 route-map BGP-TO-OSPF` (senza subnets)
> Non redistribuisce 100.0.0.0/8 perché è una rete classful /8 — in questo caso specifico
> funziona, ma `200.0.0.0/8` è anch'essa classful e funziona. Aggiungere sempre `subnets`
> per sicurezza, specialmente quando i prefissi redistribuiti non sono classful.
>
> **E1 vs E2:** Con E1, LAN-B vedrebbe metrica diversa da LAN-A (distanza CORE diversa).
> Con E2, entrambe vedrebbero metric=20 fissa. Per la selezione del percorso ottimale verso
> l'ASBR in topologie con più ASBR, E1 è preferibile.

---

## T5 — Tagging & Loop Prevention

```
! Su CORE — aggiornamento route-map BGP-TO-OSPF (aggiunge set tag)
route-map BGP-TO-OSPF permit 10
 match ip address prefix-list ISP-PREFIXES
 set tag 100

! Aggiornamento route-map OSPF-TO-BGP (aggiunge deny per tag 100 PRIMA del permit)
route-map OSPF-TO-BGP deny 5
 match tag 100
route-map OSPF-TO-BGP permit 10
 match ip address prefix-list INTERNAL-ONLY
```

> **Perché seq 5 e non seq 1?** La convenzione è lasciare spazio tra le seq per inserire
> future clausole senza dover rinumerare. seq 5 < seq 10 garantisce che la deny venga valutata
> per prima.
>
> **Il flusso con il tag:**
> 1. BGP→OSPF: CORE redistribuisce 100.0.0.0/8 in OSPF → LSA tipo 5 con External Tag: 100
> 2. OSPF→BGP: CORE rivaluta se redistribuire qualcosa da OSPF → trova 100.0.0.0/8
> 3. OSPF-TO-BGP seq 5: `match tag 100` → hit → deny → 100.0.0.0/8 NON entra in BGP
> 4. OSPF-TO-BGP seq 10: `match INTERNAL-ONLY` → LAN prefixes → permit → entrano in BGP
>
> **Scenario con doppio ASBR (avanzato):**
> Se ci fossero due router ASBR (CORE-1 e CORE-2) entrambi con redistribuzione bidirezionale,
> il tag 100 protegge anche da CORE-1 che redistribuisce in OSPF quello che CORE-2 ha già
> redistribuito da BGP e viceversa.

---

## Configurazione Finale Completa — CORE

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
!
interface Ethernet0/0.35
 encapsulation dot1Q 35
 ip address 10.0.35.1 255.255.255.252
 description to_LAN-B
 ip ospf 1 area 0
!
ip prefix-list INTERNAL-ONLY seq 10 permit 10.10.0.0/24
ip prefix-list INTERNAL-ONLY seq 20 permit 10.20.0.0/24
ip prefix-list INTERNAL-ONLY seq 30 deny 0.0.0.0/0 le 32
!
ip prefix-list ISP-PREFIXES seq 10 permit 100.0.0.0/8
ip prefix-list ISP-PREFIXES seq 20 permit 200.0.0.0/8
ip prefix-list ISP-PREFIXES seq 30 deny 0.0.0.0/0 le 32
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

**Includere 10.99.0.0/24 in INTERNAL-ONLY:**
Se si volesse redistribuire anche la rete guest verso gli ISP (scenario insolito), aggiungere:
```
ip prefix-list INTERNAL-ONLY seq 25 permit 10.99.0.0/24
```

**Usare community BGP invece di tag OSPF:**
In topologie full-BGP, si usa `set community` e `match community` per il loop prevention.
Il tag OSPF funziona solo nel dominio OSPF — per loop prevention multi-dominio serve la community BGP.

**redistribute ospf con subnets sempre:**
Anche se i prefissi attuali sono classful, è best practice aggiungere sempre `subnets` in
`redistribute bgp` per evitare sorprese con futuri prefissi non classful.
