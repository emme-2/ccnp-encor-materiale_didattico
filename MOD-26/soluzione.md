# Soluzione Commentata — MOD-26: QoS MQC

**Uso:** riservato al docente | **Syllabus:** 1.5.a · 1.5.b | **Verificata su:** GNS3 IOU L3

---

## T1 + T2 — ACL di classificazione e Class-map

### R1 — ACL estese per classificazione traffico

```
! ACL VOICE: SIP (segnalazione VoIP) + RTP (media audio/video)
! SIP usa porta 5060 (TCP e UDP); RTP usa range UDP 16384-32767 (RFC 3550)
ip access-list extended ACL-VOICE
 permit tcp any any eq 5060
 permit udp any any eq 5060
 permit udp any any range 16384 32767
 ! Nota: 'any any' = da qualsiasi sorgente a qualsiasi destinazione
 ! In produzione si restringerebbe alla subnet VoIP specifica

! ACL MGMT: Telnet (23) + SSH (22) — accesso gestionale ai device
ip access-list extended ACL-MGMT
 permit tcp any any eq 22
 permit tcp any any eq 23
```

### R1 — Class-map

```
! CM-VOICE: match-any perché SIP può essere TCP o UDP (tre ACE distinte)
class-map match-any CM-VOICE
 match access-group name ACL-VOICE
 ! match-any: il pacchetto è classificato se almeno una ACE dell'ACL matcha

class-map match-any CM-MGMT
 match access-group name ACL-MGMT

! DATA non ha class-map — verrà catturato da class-default nella policy
! IOS valuta le class-map in ordine top-down nella policy:
! 1. CM-VOICE → 2. CM-MGMT → 3. class-default (tutto il resto = DATA)
```

---

## T3 — Child Policy (PM-CHILD)

```
policy-map PM-CHILD
 class CM-VOICE
  set dscp ef
  ! Marking DSCP EF (decimal 46, binario 101110)
  ! EF = Expedited Forwarding: massima priorità, latenza minima
  ! Il marking avviene qui: i dispositivi downstream riconosceranno la classe
  priority percent 30
  ! LLQ (Low Latency Queuing) = coda strict-priority
  ! 30% della banda shaped = 30% di 10 Mbps = 3 Mbps garantiti per VOICE
  ! Il traffico VOICE > 3 Mbps viene DROPPATO immediatamente (policed)
  ! Non c'è buffer: latenza zero per il traffico entro il limite
  ! Use case: VoIP — intollerante a latenza e jitter, tollerante al drop se eccede

 class CM-MGMT
  set dscp cs2
  ! CS2 (decimal 16, binario 010000) = Class Selector 2
  ! Priorità media-bassa: management plane non deve avere alta priorità
  police rate 512000 bps
   conform-action transmit
   exceed-action drop
   ! Police 512 kbps: taglia netto il traffico management
   ! conform = pacchetto entro 512 kbps → trasmetti
   ! exceed = pacchetto oltre 512 kbps → droppa immediatamente (no buffer)
   ! Use case: limitare SSH/Telnet che non devono saturare il link WAN

 class class-default
  ! class-default cattura TUTTO il traffico non classificato = DATA
  set dscp af21
  ! AF21 (decimal 18, binario 010010) = Assured Forwarding 2-1
  ! Priorità media: dati aziendali importanti ma non real-time
  bandwidth percent 40
  ! CBWFQ (Class-Based Weighted Fair Queuing): garantisce 40% = 4 Mbps
  ! Se DATA supera 4 Mbps: pacchetti ACCODATI (non droppati) con WFQ
  ! Use case: dati aziendali, ERP, backup — tollerante a latenza, non al drop
```

---

## T4 — Parent Policy (PM-WAN-PARENT) e applicazione

```
policy-map PM-WAN-PARENT
 class class-default
  ! class-default nella parent: cattura TUTTO il traffico outbound
  shape average 10000000
  ! Shaping a 10 Mbps: simula il CIR del link WAN verso il provider
  ! Token bucket: pacchetti > 10 Mbps vengono BUFFERIZZATI
  ! Introduce delay (buffer delay) — accettabile per DATA
  ! VOICE non soffre perché è nella child LLQ: servita con priorità dentro il bucket
  ! La parent "apre" la finestra da 10 Mbps; la child decide come dividerla
  service-policy PM-CHILD
  ! Annida PM-CHILD dentro il bucket di shaping
  ! priority/bandwidth/police nella child operano rispetto a 10 Mbps shaped
  ! NON rispetto alla velocità fisica dell'interfaccia

! Applicazione alla WAN interface — outbound
interface ethernet 0/0
 service-policy output PM-WAN-PARENT
 ! 'output': agisce sul traffico in uscita verso WAN/Internet
 ! È il punto dove tutto converge — QoS applicata una volta per tutti i flussi
```

---

## Output atteso dei comandi di verifica

### R1# show policy-map interface ethernet 0/0 (pre-traffico)

```
Ethernet0/0

  Service-policy output: PM-WAN-PARENT

    Class-map: class-default (match-any)
      0 packets, 0 bytes
      5 minute offered rate 0000 bps, drop rate 0000 bps
      Traffic Shaping
          Target/Average   Byte Limit  Sustain  Excess  Interval  Increment
          10000000/10000000 62500       250000   250000  25        3125

      Service-policy : PM-CHILD

        Class-map: CM-VOICE (match-any)
          0 packets, 0 bytes
          5 minute offered rate 0000 bps, drop rate 0000 bps
          Match: access-group name ACL-VOICE
          set dscp ef
          Weighted Fair Queueing
            Strict Priority
            Output Queue: Conversation 24
            Bandwidth 30 (%)   3000 (kbps) Burst 75000 (Bytes)
            (pkts matched/bytes matched) 0/0
            (total drops/bytes drops) 0/0

        Class-map: CM-MGMT (match-any)
          0 packets, 0 bytes
          5 minute offered rate 0000 bps, drop rate 0000 bps
          Match: access-group name ACL-MGMT
          set dscp cs2
          police:
              rate 512000 bps, burst 16000 byte
            conformed 0 packets, 0 bytes; actions: transmit
            exceeded 0 packets, 0 bytes; actions: drop

        Class-map: class-default (match-any)
          0 packets, 0 bytes
          5 minute offered rate 0000 bps, drop rate 0000 bps
          set dscp af21
          Weighted Fair Queueing
            Output Queue: Conversation 264
            Bandwidth 40 (%)   4000 (kbps)
            (pkts matched/bytes matched) 0/0
```

### Dopo traffico ICMP da PC1 (ping 1.1.1.1 repeat 100)

```
        Class-map: class-default (match-any)
          100 packets, 6400 bytes     ← ICMP finisce in class-default
          ...
          set dscp af21
          Weighted Fair Queueing
            (pkts matched/bytes matched) 100/6400
```

I pacchetti ICMP di VPCS finiscono in `class-default` perché VPCS non marca DSCP (default = 0) e ICMP non matcha ACL-VOICE né ACL-MGMT. Questo è il comportamento corretto e atteso — buon punto di discussione con gli studenti.

---

## Note Varianti & Alternative

### Verifica della struttura gerarchica con show

```
! Visualizza la struttura statica di tutta la policy (senza traffico)
R1# show policy-map PM-WAN-PARENT
R1# show policy-map PM-CHILD

! Visualizza policy applicata con contatori dinamici (richiede traffico)
R1# show policy-map interface ethernet 0/0

! Reset dei contatori
R1# clear counters ethernet 0/0
```

### priority vs priority percent

`priority kbps` specifica banda assoluta; `priority percent` specifica percentuale della banda shaped. In una child policy con shaping a 10 Mbps:

```
priority 3000      ! = 3000 kbps = 3 Mbps (assoluto)
priority percent 30 ! = 30% di 10 Mbps = 3 Mbps (relativo)
```

Preferire `percent` nelle child policy — se si cambia il CIR WAN nella parent, le proporzioni si aggiornano automaticamente.

### Rimozione della policy per riconfigurare

```
! Rimuovere service-policy prima di modificare la policy-map
R1(config)# interface ethernet 0/0
R1(config-if)# no service-policy output PM-WAN-PARENT

! Modificare la policy
R1(config)# policy-map PM-CHILD
R1(config-pmap)# class CM-VOICE
...

! Riapplicare
R1(config)# interface ethernet 0/0
R1(config-if)# service-policy output PM-WAN-PARENT
```

### Aggiunta di NBAR per classificazione applicativa

In alternativa alle ACL, è possibile usare NBAR (Network Based Application Recognition) per match dinamico:
```
class-map match-any CM-HTTP
 match protocol http
 ! NBAR identifica HTTP anche su porte non standard
 ! Non richiede ACL — analizza il payload del pacchetto
```

NBAR introduce overhead CPU — valutare in ambienti ad alta frequenza di traffico.

### Errori frequenti degli studenti

1. **`priority percent` senza parent shaping**: IOS rifiuta il comando o non funziona correttamente. La `priority percent` è sempre relativa alla banda shaped dalla parent — senza parent, IOS non sa su quale valore calcolare il percentuale.

2. **Service-policy applicata in `input` invece di `output`**: la QoS viene applicata al traffico in ingresso da WAN (che comunque IOU non gestisce pienamente). La policy WAN va sempre in `output` sull'interfaccia WAN.

3. **ACL standard invece di extended**: `match access-group name` accetta anche ACL standard, ma queste non possono matchare per porta — tutto il traffico da/verso qualsiasi IP viene classificato. Usare sempre ACL extended.

4. **Doppia application di service-policy**: se esiste già una policy sull'interfaccia, IOS la rifiuta con errore. Sempre `no service-policy output` prima di applicare la nuova.

5. **class-default nella child dimenticata**: senza `class-default` nella child policy, il traffico DATA non ha trattamento definito — ottiene il trattamento default FIFO, che può essere iniquo rispetto alle altre classi. Configurare sempre la `class-default`.
