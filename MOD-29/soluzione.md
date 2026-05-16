# Soluzione Commentata — MOD-29: Network Assurance — NetFlow & SNMP

> **Uso:** Riservato al docente — non distribuire agli studenti prima del termine del lab.
> **Stato:** Configurazioni essenziali incluse. Sezione espansa IN SVILUPPO.

> ⚠️ IN SVILUPPO — disponibile nella prossima versione.

---

## Configurazioni Essenziali per Task

### NF.1 — Flexible NetFlow su R1 (configurazione completa)

```
! ── Flow Record ──────────────────────────────────────────────────
flow record ENCOR-RECORD
 description Analisi traffico IP - MOD29
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match interface input
 collect transport source-port
 collect transport destination-port
 collect counter bytes long
 collect counter packets long
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
```

```
! ── Flow Exporter ────────────────────────────────────────────────
flow exporter ENCOR-EXPORT
 description Export verso VM GNS3
 destination 192.168.122.1
 transport udp 9996
 export-protocol netflow-v5
```

```
! ── Flow Monitor ─────────────────────────────────────────────────
flow monitor ENCOR-MON
 description MOD29 Network Assurance
 record ENCOR-RECORD
 exporter ENCOR-EXPORT
 cache timeout active 60
 cache timeout inactive 30
```

```
! ── Applicazione su interfaccia ──────────────────────────────────
interface Ethernet0/0.100
 ip flow monitor ENCOR-MON input
```

> **Nota sull'exporter:** La destinazione 192.168.122.1 e' la VM GNS3 raggiunta
> tramite l'interfaccia di management. Su IOU, l'export avviene se il router
> ha una route verso 192.168.122.0/24. Se non presente, aggiungere una route
> statica o verificare la connettivita' della VM. L'assenza del collector non
> impedisce il popolamento della cache locale.

> **Nota sul record:** Il campo `match interface input` e' opzionale ma utile
> per distinguere i flow per interfaccia quando il monitor e' applicato su
> piu' interfacce contemporaneamente.

---

### SNMP.1 — SNMPv2c su R1 (configurazione completa)

```
! Community strings
snmp-server community ENCOR-RO ro
snmp-server community ENCOR-RW rw
!
! Metadati del device (buona pratica operativa)
snmp-server contact admin@encorlab.local
snmp-server location GNS3-Lab-R1
!
! Host per le trap
snmp-server host 192.168.122.1 version 2c ENCOR-RO
!
! Trap selezionate (limitare le trap riduce il rumore)
snmp-server enable traps snmp linkdown linkup
snmp-server enable traps ospf state-change
```

> **Nota community rw:** In produzione, la community read-write deve essere
> diversa dalla ro, conosciuta solo dagli amministratori, e dovrebbe essere
> protetta con una ACL standard:
> ```
> ip access-list standard SNMP-RW-ACL
>  permit 192.168.122.0 0.0.0.255
>  deny any
> snmp-server community ENCOR-RW rw SNMP-RW-ACL
> ```

---

### SNMP.2 — SNMPv3 su R1 (configurazione completa)

```
! Gruppo con livello di sicurezza massimo (authPriv)
snmp-server group ENCOR-GROUP v3 priv
!
! Utente con autenticazione SHA e cifratura AES128
! Le password non compaiono in show running-config
snmp-server user ENCOR-USER ENCOR-GROUP v3 auth sha Cisco123! priv aes 128 Cisco123!
!
! Host per le trap v3
snmp-server host 192.168.122.1 version 3 priv ENCOR-USER
```

> **Nota engine ID:** L'Engine ID e' unico per dispositivo e cambia al reload
> su IOU. Questo invalida le credenziali USM. In produzione su IOS reale
> l'engine ID e' stabile. Per rendere l'engine ID fisso su IOU:
> ```
> snmp-server engineID local 0102030405060708090A0B0C
> ```
> Configurare prima dell'utente e non modificare successivamente.

---

## Output di Riferimento Chiave

### show flow monitor ENCOR-MON cache — con traffico ICMP e TCP attivo

```
R1#show flow monitor ENCOR-MON cache
Cache type:                               Normal
Cache size:                                 4096
Current entries:                               2

Flows added:                                   2
Flows aged:                                    0

  IPV4 SRC ADDR    IPV4 DST ADDR    PROT  INPUT IF   trns src-port  trns dst-port  bytes pkts
  ===============  ===============  ====  =========  =============  =============  ===== ====
  192.168.1.100    192.168.3.100    0x01  Et0/0.100              0              0  89600  700
  192.168.1.100    10.0.12.2        0x01  Et0/0.100              0              0   1280   10
```

**Interpretazione:**
- PROT 0x01 = ICMP (protocollo 1)
- Due entry separate perche' i campi `match ipv4 destination address` sono diversi
- Porte = 0 per ICMP (non ha porte TCP/UDP)
- bytes e pkts crescono ad ogni poll con il ping attivo

### show snmp user — output atteso dopo configurazione SNMPv3

```
R1#show snmp user

User name: ENCOR-USER
Engine ID: 800000090300C401XXXXXXXXXX
storage-type: nonvolatile    active
Authentication Protocol: SHA
Privacy Protocol: AES128
Group-name: ENCOR-GROUP
```

---

## Note Varianti & Alternative

- **NetFlow v9 invece di v5 nell'exporter:** `export-protocol netflow-v9` — piu' flessibile, supporta template dinamici. Richiede un collector compatibile v9 (es. ntopng, Elastiflow).
- **IPFIX (RFC 5101):** versione standardizzata RFC di Flexible NetFlow. Configurazione identica ma `export-protocol ipfix`. Raccomandato per ambienti multi-vendor.
- **Sampled NetFlow:** per link ad alto traffico, ridurre il carico del router con il campionamento:
  ```
  flow monitor ENCOR-MON
   sampler ENCOR-SAMPLER
  !
  flow sampler ENCOR-SAMPLER
   mode random 1 out-of 100
  ```
- **SNMPv3 con view restrittiva:** limitare la MIB accessibile per singolo utente:
  ```
  snmp-server view ENCOR-VIEW mib-2 included
  snmp-server view ENCOR-VIEW ciscoMgmt included
  snmp-server group ENCOR-GROUP v3 priv read ENCOR-VIEW
  ```
- **RESTCONF/NETCONF:** alternativa moderna a SNMP per la gestione programmatica dei router. Non disponibile su IOU — trattare come teoria. Approfondito in MOD-14.