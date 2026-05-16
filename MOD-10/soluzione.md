# Soluzione Commentata — MOD-10: MPLS LDP & Fondamenta

> **USO RISERVATO ISTRUTTORE** — Distribuire agli studenti solo dopo il completamento del lab.

---

## Configurazione completa P1

```
! === P1 — MPLS LDP ===
!
! LDP usa il loopback come transport address per la sessione TCP.
! "force" sovrascrive immediatamente il router-id anche se LDP è già avviato.
!
mpls label protocol ldp
mpls ldp router-id Loopback0 force
!
! mpls ip su Eth0/0.13 → abilita LDP discovery su questo link (hello UDP 646)
! LDP stringerà sessione TCP con PE1 (loopback 1.1.1.1)
interface Ethernet0/0.13
 mpls ip
!
! mpls ip su Eth0/0.34 → abilita LDP discovery verso P2 (loopback 4.4.4.4)
interface Ethernet0/0.34
 mpls ip
```

## Configurazione completa PE1

```
! === PE1 — MPLS LDP ===
!
! PE1 ha un solo link backbone (verso P1).
! Stessa logica di P1: loopback0 come transport, mpls ip sull'interfaccia.
!
mpls label protocol ldp
mpls ldp router-id Loopback0 force
!
interface Ethernet0/0.13
 mpls ip
```

> **P2 e PE2:** già configurati nelle cfg di partenza — nessuna modifica richiesta.

---

## Output show attesi e commentati

### show mpls ldp neighbor (PE1)

```
PE1# show mpls ldp neighbor
    Peer LDP Ident: 3.3.3.3:0; Local LDP Ident 1.1.1.1:0
        State: Oper; Msgs sent/rcvd: 12/12; Downstream
        Up time: 00:02:14
        LDP discovery sources:
          Ethernet0/0.13
        Addresses bound to peer LDP Ident:
          10.0.13.2   3.3.3.3
```

Commento:
- `State: Oper` = sessione LDP attiva (TCP 646 stabilita tra loopback)
- Peer è `3.3.3.3` (P1) — l'LDP Ident è il loopback, non l'IP del link
- `Downstream` = distribuzione label in modalità Downstream Unsolicited (default IOS)

### show mpls interfaces (P1)

```
P1# show mpls interfaces
Interface              IP            Tunnel   BGP Static Operational
Ethernet0/0.13         Yes (ldp)     No       No  No     Yes
Ethernet0/0.34         Yes (ldp)     No       No  No     Yes
```

Commento:
- Colonna `IP` = tipo di protocollo di distribuzione label (ldp)
- Colonna `Operational = Yes` conferma che LDP è attivo sull'interfaccia
- Se `Operational` fosse `No`: verificare che OSPF sia Up su quel link

### show mpls forwarding-table (PE1 — estratto)

```
PE1# show mpls forwarding-table
Local  Outgoing    Prefix              Bytes     Outgoing   Next Hop
Label  Label or    or Tunnel Id        Switched  interface
       Tunnel-Id
16     Pop label   3.3.3.3/32          0         Et0/0.13   10.0.13.2
17     16          2.2.2.2/32          0         Et0/0.13   10.0.13.2
18     17          4.4.4.4/32          0         Et0/0.13   10.0.13.2
```

Commento:
- `Local Label` = label che PE1 usa quando riceve traffico per quel FEC in ingresso
- `Outgoing Label` = label che PE1 impone al pacchetto uscente verso P1
- `Pop label` per 3.3.3.3/32 = PE1 è penultimo hop rispetto a P1 → PHP
- La label 16 per 2.2.2.2/32 è quella che P1 ha assegnato localmente a quel FEC

### show mpls ldp bindings (PE1 — estratto)

```
PE1# show mpls ldp bindings
  lib entry: 1.1.1.1/32, rev 4
        local binding:  label: imp-null
        remote binding: lsr: 3.3.3.3:0, label: 22
  lib entry: 2.2.2.2/32, rev 8
        local binding:  label: 17
        remote binding: lsr: 3.3.3.3:0, label: 16
```

Commento:
- `imp-null` (implicit-null = valore 3) su 1.1.1.1/32: PE1 annuncia PHP ai suoi vicini.
  P1 farà POP invece di SWAP quando manda pacchetti destinati a 1.1.1.1.
- Per 2.2.2.2/32: PE1 alloca label locale 17; P1 ha comunicato label 16.
  PE1 usa label 16 in outgoing (è ciò che P1 si aspetta di ricevere).

### ping 2.2.2.2 source Loopback0 (PE1)

```
PE1# ping 2.2.2.2 source Loopback0 repeat 5
Type escape sequence to abort.
Sending 5, 100-byte ICMP Echos to 2.2.2.2, timeout is 2 seconds:
Packet sent with a source address of 1.1.1.1
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 2/3/4 ms
```

### traceroute 2.2.2.2 source Loopback0 (PE1)

```
PE1# traceroute 2.2.2.2 source Loopback0
Tracing the route to 2.2.2.2
  1  10.0.13.2 [MPLS: Label 16 Exp 0] 4 msec 2 msec 2 msec
  2  10.0.34.2 [MPLS: Label 16 Exp 0] 2 msec 2 msec 2 msec
  3  2.2.2.2 4 msec 2 msec 2 msec
```

Commento PHP:
- Hop 1 (P1 @ 10.0.13.2): riceve pacchetto con label, fa SWAP verso label di P2
- Hop 2 (P2 @ 10.0.34.2): penultimo hop → riceve imp-null da PE2, fa POP, manda a PE2 senza label outer
- Hop 3 (PE2 @ 2.2.2.2): riceve ICMP puro IP, risponde — nessuna label visibile

---

## Note su varianti e alternative

**Explicit-null vs implicit-null:**
Di default IOS usa implicit-null (PHP). Se si vuole preservare il campo EXP
(DSCP MPLS) sul pacchetto che arriva al PE, configurare:
```
PE1(config)# mpls ldp explicit-null
```
Con explicit-null il penultimo hop invia la label 0 invece di fare POP.
Il PE egress riceve ancora una label (la 0) e può leggere il campo EXP per QoS,
ma deve fare un lookup aggiuntivo.

**Verifica LDP per singolo FEC:**
```
PE1# show mpls ldp bindings 2.2.2.2 32
```
Utile per isolare problemi su un prefisso specifico senza scorrere l'intera LIB.

**Traceroute LSP (MPLS-specific):**
```
PE1# traceroute mpls ipv4 2.2.2.2/32
```
Usa echo MPLS invece di ICMP TTL. Verifica che l'LSP sia valido end-to-end.
Fallisce se non esiste un LSP anche se il ping IP funziona via OSPF puro.