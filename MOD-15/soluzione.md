# Soluzione Commentata — MOD-15: FHRP — HSRP, VRRP & GLBP

**Uso:** riservato al docente | **Syllabus:** 3.4.c | **Verificata su:** GNS3 IOU L2
**Prerequisiti:** MOD-13 (Po1 UP) + MOD-14 (STP configurato)

---

## T1 — HSRPv2 Configurazione completa

### SW1 — Active VLAN 10, Standby VLAN 20

```
interface vlan 10
 standby version 2
 ! HSRPv2: multicast 224.0.0.102, gruppi 0-4095, supporta IPv6
 standby 10 ip 10.10.10.1
 ! VIP VLAN 10: i client usano questo come default gateway
 standby 10 priority 110
 ! Priority più alta vince → SW1 diventa Active su VLAN 10
 standby 10 preempt
 ! Preempt: SW1 riprende il ruolo Active dopo il ripristino dell'uplink
 ! Senza preempt, SW1 resterebbe Standby anche dopo il recovery
 standby 10 timers 1 3
 ! Hello ogni 1s, hold 3s (default: 3s/10s)
 ! Ridotti per convergenza rapida in ambiente di test
exit

interface vlan 20
 standby version 2
 standby 20 ip 10.10.20.1
 standby 20 priority 100
 ! Priority 100 = default: SW1 è Standby su VLAN 20 (SW2 ha 110)
 standby 20 preempt
 standby 20 timers 1 3
```

### SW2 — Active VLAN 20, Standby VLAN 10

```
interface vlan 10
 standby version 2
 standby 10 ip 10.10.10.1
 standby 10 priority 100
 standby 10 preempt
 standby 10 timers 1 3
exit

interface vlan 20
 standby version 2
 standby 20 ip 10.10.20.1
 standby 20 priority 110
 ! SW2 è Active su VLAN 20
 standby 20 preempt
 standby 20 timers 1 3
```

---

## T2 — IP SLA + Object Tracking

### SW1 — monitoraggio uplink R1↔SW1

```
! Probe ICMP verso R1 Loopback0 — usa l'interfaccia SVI VLAN 10
! come source: garantisce che il probe percorra lo stesso path del traffico reale
ip sla 1
 icmp-echo 1.1.1.1 source-interface vlan 10
 frequency 5
 ! Probe ogni 5 secondi: compromesso tra reattività e carico CPU
exit

! Scheduling: parte immediatamente e non scade mai
ip sla schedule 1 life forever start-time now

! Object Tracking: traduce lo stato della probe in Up/Down
track 1 ip sla 1 reachability
! 'reachability' = binario Up/Down (la probe ha risposto o no)
! Alternativa: 'ip sla 1 state' per monitorare il return code specifico

! Collegamento a HSRP: se Track 1 va Down, decrementa priority di 20
interface vlan 10
 standby 10 track 1 decrement 20
 ! Normal: 110. Track Down: 110 - 20 = 90 < 100 (SW2) → failover
```

### SW2 — monitoraggio uplink R1↔SW2

```
ip sla 1
 icmp-echo 1.1.1.1 source-interface vlan 20
 ! Usa SVI VLAN 20 come source: monitoraggio specifico per il link R1↔SW2
 frequency 5
exit

ip sla schedule 1 life forever start-time now
track 1 ip sla 1 reachability

interface vlan 20
 standby 20 track 1 decrement 20
 ! SW2 priority 110 - 20 = 90 < 100 (SW1) → se R1↔SW2 cade, failover verso SW1
```

---

## T3 — Sequenza failover live

Nessuna configurazione aggiuntiva. Sequenza di osservazione guidata:

```
! FASE 1 — Stato stabile iniziale
PC1> ping 1.1.1.1 repeat 9999        ! avvia ping continuo
SW1# show standby brief              ! Vl10: Active (110), Vl20: Standby (100)
SW2# show standby brief              ! Vl10: Standby (100), Vl20: Active (110)

! FASE 2 — Simula fault: shutdown link R1↔SW1
R1(config)# interface ethernet 0/1
R1(config-if)# shutdown

! FASE 3 — Osservare la propagazione (attendi 8-13 secondi)
! Syslog su SW1:
! %TRACKING-5-STATE: 1 ip sla 1 reachability Up->Down
! %HSRP-5-STATECHANGE: Vlan10 Grp 10 state Active -> Speak
! %HSRP-5-STATECHANGE: Vlan10 Grp 10 state Speak -> Standby
! Syslog su SW2:
! %HSRP-5-STATECHANGE: Vlan10 Grp 10 state Standby -> Active

! FASE 4 — Verifica post-failover
SW1# show standby brief
! Vl10: priority 90 (110-20), stato Standby
SW2# show standby brief
! Vl10: stato Active (100 > 90)
SW1# show track 1
! Reachability is Down | Change#: 1

! FASE 5 — Ripristino
R1(config)# interface ethernet 0/1
R1(config-if)# no shutdown
! Attendi ~8s: IP SLA riprende → Track Up → HSRP preempt → SW1 Active di nuovo
SW1# show standby brief
! Vl10: Active (priority 110, preempt eseguito)
```

---

## Output atteso dei comandi di verifica

### SW1# show standby brief

```
P indicates configured to preempt.
                     |
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Vl10         10  110 P Active   local           10.10.10.3      10.10.10.1
Vl20         20  100 P Standby  10.10.20.2      local           10.10.20.1
```

### SW1# show standby vlan 10

```
Vlan10 - Group 10 (version 2)
  State is Active
    4 state changes, last state change 00:02:15
  Virtual IP address is 10.10.10.1
  Active virtual MAC address is 0000.0c9f.f00a
    Local virtual MAC address is 0000.0c9f.f00a (v2 default)
  Hello time 1 sec, hold time 3 sec
    Next hello sent in 0.512 secs
  Preemption enabled
  Active router is local
  Standby router is 10.10.10.3, priority 100 (expires in 2.064 sec)
  Priority 110 (configured 110)
    Track object 1 state Up decrement 20
  IP redundancy name is "hsrp-Vl10-10" (default)
```

### SW1# show ip sla statistics 1

```
IPSLAs Latest Operation Statistics
IPSLA operation id: 1
        Latest RTT: 1 milliseconds
Latest operation start time: *00:05:32.000 UTC
Latest operation return code: OK
Number of successes: 66
Number of failures: 0
Operation time to live: Forever
```

### SW1# show track 1

```
Track 1
  IP SLA 1 reachability
  Reachability is Up
    2 changes, last change 00:05:12
  Delay up 0 secs, down 0 secs
  Latest operation return code: OK
  Tracked by:
    HSRP Vlan10 10
```

---

## Note Varianti & Alternative

### Calcolo del decrement

Formula generale: `decrement > (priority_attivo - priority_standby)`

Esempio: SW1 = 110, SW2 = 100 → decrement minimo = 11. Usare 20 per margine di sicurezza.

Errore comune: decrement troppo piccolo. Con decrement 5: 110 - 5 = 105 > 100 → SW1 resta Active nonostante il fault. Il failover non avviene.

### IP SLA con tracking del return code

Alternativa a `reachability` per monitorare non solo Up/Down ma anche la qualità:
```
track 1 ip sla 1 state
! Monitora il return code: OK, Timeout, Error — più granulare
! 'reachability' è binario e sufficiente per il caso d'uso HSRP
```

### Preempt delay

In ambienti di produzione si può aggiungere un delay al preempt per evitare oscillazioni:
```
standby 10 preempt delay minimum 60
! Attende 60s prima di riprendere il ruolo Active dopo il recovery
! Utile se i routing protocol (OSPF, BGP) hanno bisogno di tempo per convergere
```

### Errori frequenti degli studenti

1. **Versione HSRP mismatch**: un switch in v1, l'altro in v2 — non formano il gruppo. Syslog: "HSRP version mismatch". Aggiungere `standby version 2` su tutti.
2. **SVI VLAN down**: se Vlan10 SVI è down/down, HSRP non parte. Causa tipica: Po1 non configurato (MOD-13 prerequisito non soddisfatto).
3. **IP SLA non schedulato**: probe non parte → 0 successi → Track resta in stato "Not Tracked". Aggiungere `ip sla schedule 1 life forever start-time now`.
4. **Source-interface SLA errata**: SW1 usa `source-interface e0/0` (VRF LAB) invece di `vlan 10` — il probe non percorre il path che si vuole monitorare. Il Track resta Up anche se e0/1 è down.
5. **Preempt mancante**: dopo il ripristino di e0/1 su R1, SW1 resta in Standby anche con priority 110. Lo studente si aspetta che torni Active ma non succede. Aggiungere `standby 10 preempt`.
