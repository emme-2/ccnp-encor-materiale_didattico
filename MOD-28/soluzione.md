# Soluzione Commentata — MOD-28: IP Multicast — PIM & Auto-RP

> **Uso:** Riservato al docente — non distribuire agli studenti prima del termine del lab.
> **Stato:** Configurazioni essenziali incluse. Sezione espansa IN SVILUPPO.

> ⚠️ IN SVILUPPO — disponibile nella prossima versione.

---

## Configurazioni Essenziali per Task

### T1 — PIM Dense Mode (R1, R2, R3)

```
! ── R1 ─────────────────────────────────────────────────────────
ip multicast-routing
!
interface Ethernet0/0.12
 ip pim dense-mode
interface Ethernet0/0.13
 ip pim dense-mode
interface Ethernet0/0.100
 ip pim dense-mode
```

```
! ── R2 ─────────────────────────────────────────────────────────
ip multicast-routing
!
interface Ethernet0/0.12
 ip pim dense-mode
interface Ethernet0/0.23
 ip pim dense-mode
```

```
! ── R3 ─────────────────────────────────────────────────────────
ip multicast-routing
!
interface Ethernet0/0.13
 ip pim dense-mode
interface Ethernet0/0.23
 ip pim dense-mode
interface Ethernet0/0.300
 ip pim dense-mode
```

> **Nota:** `ip multicast-routing` e' il prerequisito assoluto. Senza di esso,
> il comando `ip pim dense-mode` viene accettato ma nessuna mroute viene creata.

---

### T3 — IGMP join-group (R5)

```
! ── R5 ─────────────────────────────────────────────────────────
! ip routing e' gia' nel cfg iniziale
interface Ethernet0/0.300
 ip igmp join-group 239.1.1.1
```

> **Nota IOU:** su IOU, `ip igmp join-group` richiede `ip routing` abilitato
> sul device. R5 ha `ip routing` nel cfg iniziale per questo motivo.
> Con `no ip routing`, il comando non e' disponibile.

---

### T5 — Switch a PIM-SM + RP statico

```
! ── R1, R2, R3 — sequenza per ogni interfaccia PIM ─────────────
! (no dense-mode prima, poi sparse-mode)
interface <if>
 no ip pim dense-mode
 ip pim sparse-mode
!
! RP statico — configurare su tutti e tre i router
ip pim rp-address 2.2.2.2
```

> **Nota:** la transizione DM→SM puo' causare la perdita temporanea del join IGMP
> su R5. Se `show ip mroute` su R3 non mostra e0/0.300 nell'OIL, ripetere
> `ip igmp join-group 239.1.1.1` su R5 e0/0.300.

---

### T7 — Auto-RP (R2 come Candidate RP e Mapping Agent)

```
! ── Tutti i router — cambiare a sparse-dense-mode ──────────────
! Necessario per risolvere il bootstrap problem di Auto-RP
interface <if>
 no ip pim sparse-mode
 ip pim sparse-dense-mode
!
! ── R1, R2, R3 — rimuovere RP statico ──────────────────────────
no ip pim rp-address 2.2.2.2
!
! ── R2 — Candidate RP + Mapping Agent ──────────────────────────
! scope 10 = TTL massimo degli annunci (10 hop)
ip pim send-rp-announce Loopback0 scope 10
ip pim send-rp-discovery Loopback0 scope 10
```

> **Nota bootstrap:** `sparse-dense-mode` fa si' che i gruppi 224.0.1.39 e
> 224.0.1.40 (usati da Auto-RP) vengano trattati come Dense Mode, risolvendo
> il problema del pollo-e-uovo. In alternativa: `ip pim autorp listener` su
> tutti i router mantiene le interfacce in SM puro.

> **Nota elezione MA:** se ci sono piu' Candidate RP per lo stesso gruppo,
> il Mapping Agent sceglie quello con l'indirizzo IP piu' alto.

---

## Output di Riferimento Chiave

### show ip mroute su R3 — dopo T7 (Auto-RP attivo, traffico in corso)

```
R3#show ip mroute 239.1.1.1
IP Multicast Routing Table
Flags: D - Dense, S - Sparse, B - Bidir Group, s - SSM Group, C - Connected,
       L - Local, P - Pruned, R - RP-bit set, F - Register flag, T - SPT-bit set,
       J - Join SPT, M - MSDP created entry, E - Extranet,
       X - Proxy Join Timer Running, A - Candidate for MSDP Advertisement,
       U - URD, I - Received Source Specific Host Report
Outgoing interface flags: H - Hardware switched, A - Assert winner
 Timers: Uptime/Expires
 Interface state: Interface, Next-Hop or VCD, State/Mode

(*,239.1.1.1), 00:05:23/00:02:37, RP 2.2.2.2, flags: S T
  Incoming interface: Ethernet0/0.13, RPF nbr 10.0.13.1
  Outgoing interface list:
    Ethernet0/0.300, Forward/Sparse-Dense, 00:05:23/00:01:37

(192.168.1.100,239.1.1.1), 00:04:11/00:02:49, flags: T
  Incoming interface: Ethernet0/0.13, RPF nbr 10.0.13.1
  Outgoing interface list:
    Ethernet0/0.300, Forward/Sparse-Dense, 00:04:11/00:01:37
```

**Interpretazione:**
- Flag **T** su (\*,G): SPT switchover avvenuto — R3 riceve gia' dal source tree
- Flag **T** su (S,G): entry SPT attiva verso 192.168.1.100
- IIF e0/0.13 in entrambe: percorso diretto R3→R1 (non passa piu' per R2/RP)

### show ip pim rp mapping su R1 — dopo T7

```
R1#show ip pim rp mapping
PIM Group-to-RP Mappings

Group(s) 224.0.0.0/4
  RP 2.2.2.2 (?), v2v1
    Info source: 2.2.2.2, via Auto-RP
    Uptime: 00:03:47, expires: 00:02:13
```

**Info source 2.2.2.2** indica che R2 e' sia il Mapping Agent sia il Candidate RP.

---

## Note Varianti & Alternative

- **BSR invece di Auto-RP:** In ambienti multi-vendor preferire BSR (RFC 5059): `ip pim bsr-candidate Lo0 0` + `ip pim rp-candidate Lo0`. Non richiede sparse-dense-mode.
- **PIM-SSM (Source Specific Multicast):** range 232.0.0.0/8 — non richiede RP, il receiver specifica anche la sorgente con IGMPv3. Piu' sicuro contro attacchi di join fraudolenti.
- **Bidir-PIM:** ottimizzazione per molte-a-molte (conferenza): albero bidirezionale radicato nell'RP, non si crea mai un SPT. Configurazione: `ip pim bidir-enable` + `ip pim rp-address X.X.X.X bidir`.
- **`ip pim autorp listener`:** alternativa a sparse-dense-mode per il bootstrap di Auto-RP. Mantiene le interfacce in SM puro ma abilita il forwarding DM solo per i gruppi 224.0.1.x.
