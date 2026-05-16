# Workbook Studenti — MOD-15: FHRP — HSRP, VRRP & GLBP

**Area:** Layer 3 Technologies | **Ore:** 2h | **Codici syllabus:** 3.4.c

---

## 1. TOPOLOGIA

```
          [WAN / Upstream: 1.1.1.1 = R1 Lo0]
                    |
               R1 (IOU L3)
              /             \
        e0/1.100          e0/2.200
            |                  |
           SW1               SW2
      HSRP Gr.10 ACTIVE   HSRP Gr.20 ACTIVE
      HSRP Gr.20 Standby  HSRP Gr.10 Standby
      IP SLA → 1.1.1.1    IP SLA → 1.1.1.1
      Track 1 → HSRP 10   Track 1 → HSRP 20
            |                  |
      e0/2+e0/3 ←─ Po1 ─→ e0/2+e0/3
            |                  |
      e1/0: PC1           e1/0: PC2
      (VLAN 10)           (VLAN 20)
```

### Piano di indirizzamento HSRP

| VLAN | VIP (virtual) | SW1 SVI | SW2 SVI | HSRP Active | HSRP Standby |
|------|---------------|---------|---------|-------------|--------------|
| 10 | 10.10.10.1 | 10.10.10.2 | 10.10.10.3 | SW1 (priority 110) | SW2 (priority 100) |
| 20 | 10.10.20.1 | 10.10.20.3 | 10.10.20.2 | SW2 (priority 110) | SW1 (priority 100) |

| Device | IP SLA probe | Track | HSRP decrement | Effetto failover |
|--------|-------------|-------|----------------|------------------|
| SW1 | ICMP → 1.1.1.1 via Vlan10 | Track 1 | -20 su Gr.10 | priority 110 → 90 → SW2 diventa Active |
| SW2 | ICMP → 1.1.1.1 via Vlan20 | Track 1 | -20 su Gr.20 | priority 110 → 90 → SW1 diventa Active |

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sarà in grado di:

- [ ] Configurare HSRPv2 con load-balancing su due VLAN (dual-group)
- [ ] Configurare IP SLA ICMP e Object Tracking collegato ad HSRP
- [ ] Simulare e osservare un failover HSRP live
- [ ] Descrivere il funzionamento di VRRP e le differenze rispetto a HSRP
- [ ] Descrivere il funzionamento di GLBP e i suoi meccanismi di load-balancing

**Codici syllabus coperti:** 3.4.c — FHRP (HSRP, VRRP, GLBP)

**Prerequisiti:** MOD-13 (Po1 UP) + MOD-14 (STP configurato)

---

## 3. LAB SETUP

### File cfg da caricare via TFTP

```
! Su SW1
SW1# copy tftp://192.168.122.1/ENCOR/MOD-15/sw1-cfg running-config

! Su SW2
SW2# copy tftp://192.168.122.1/ENCOR/MOD-15/sw2-cfg running-config

! Su R1 (configurazione pre-lab già completa)
R1# copy tftp://192.168.122.1/ENCOR/MOD-15/r1-cfg running-config
```

### Prerequisiti

- Po1 tra SW1 e SW2 UP con flag SU (MOD-13)
- STP configurato con SW1 root VLAN 10, SW2 root VLAN 20 (MOD-14)
- SVI VLAN 10 e 20 UP su entrambi gli switch (IP già assegnati dalla cfg pre-lab)
- R1 raggiungibile da SW1 (ping 10.0.12.1) e da SW2 (ping 10.0.13.1)

### Verifica pre-lab

```
! Verifica SVI VLAN 10 e 20 su SW1
SW1# show interfaces vlan 10
SW1# show interfaces vlan 20

! Verifica raggiungibilità R1
SW1# ping 10.0.12.1
SW2# ping 10.0.13.1

! Verifica raggiungibilità R1 Loopback0 (target IP SLA)
SW1# ping 1.1.1.1
SW2# ping 1.1.1.1
```

---

## 4. TASK LIST

| # | Task | Codice syllabus | Tempo stimato |
|---|------|-----------------|---------------|
| T1 | HSRPv2 — Configurazione dual-group | 3.4.c | 20' |
| T2 | IP SLA + Object Tracking collegato a HSRP | 3.4.c + 4.4 | 25' |
| T3 | Failover HSRP Live | 3.4.c + 4.4 | 15' |
| T4 | VRRP — Teoria con configurazione di esempio | 3.4.c | (teoria) |
| T5 | GLBP — Teoria con configurazione di esempio | 3.4.c | (teoria) |

---

## 5. DETTAGLIO TASK

### T1 — HSRPv2 — Configurazione dual-group

#### TEORIA

**Come funziona HSRP**

HSRP (Hot Standby Router Protocol — RFC 2281, Cisco proprietario) fornisce un gateway virtuale ridondante per i client LAN. Il gateway virtuale ha un **IP virtuale** e un **MAC virtuale**. I client usano il VIP come default gateway — non sanno quale switch fisico sta gestendo effettivamente il traffico.

**Macchina a stati HSRP**

```
Init → Listen → Speak → Standby → Active
```

| Stato | Descrizione |
|-------|-------------|
| Init | Configurazione in corso o interfaccia down |
| Listen | Riceve messaggi HSRP degli altri peer |
| Speak | Partecipa all'elezione, invia hello |
| Standby | Backup pronto a subentrare (solo uno per gruppo) |
| Active | Risponde all'IP/MAC virtuale — forwarda il traffico |

**Parametri chiave**

| Parametro | Default | Note |
|-----------|---------|------|
| Priority | 100 | Chi ha il valore più alto diventa Active |
| Preempt | Disabilitato | Se abilitato, ripristina Active dopo recovery |
| Hello timer | 3s | Intervallo tra hello HSRP |
| Hold timer | 10s | Timeout prima di dichiarare il peer down |
| Versione | v1 | HSRPv2: gruppi 0-4095, multicast 224.0.0.102, IPv6 |

**Virtual MAC HSRPv2**

Il MAC virtuale generato da HSRPv2 è `0000.0C9F.FXXX` dove XXX è il numero di gruppo in hex. Esempio: gruppo 10 → `0000.0C9F.F00A`.

**Load-balancing con dual-group HSRP**

Non esiste load-balancing nativo in un singolo gruppo HSRP. Il bilanciamento si ottiene configurando **due gruppi distinti**:
- Gruppo 10: SW1 Active (priority 110), SW2 Standby (priority 100) → gateway VLAN 10
- Gruppo 20: SW2 Active (priority 110), SW1 Standby (priority 100) → gateway VLAN 20

I client su VLAN 10 usano VIP 10.10.10.1, i client su VLAN 20 usano VIP 10.10.20.1 — traffico bilanciato sui due switch.

#### TASK

**Step 1** — Configurare HSRPv2 su SW1:

```
! SW1: Active su VLAN 10 (priority 110), Standby su VLAN 20 (priority 100)

SW1(config)# interface vlan 10
SW1(config-if)# standby version 2
SW1(config-if)# standby 10 ip 10.10.10.1
SW1(config-if)# standby 10 priority 110
SW1(config-if)# standby 10 preempt
SW1(config-if)# standby 10 timers 1 3

SW1(config)# interface vlan 20
SW1(config-if)# standby version 2
SW1(config-if)# standby 20 ip 10.10.20.1
SW1(config-if)# standby 20 priority 100
SW1(config-if)# standby 20 preempt
SW1(config-if)# standby 20 timers 1 3
```

**Step 2** — Configurare HSRPv2 su SW2:

```
! SW2: Active su VLAN 20 (priority 110), Standby su VLAN 10 (priority 100)

SW2(config)# interface vlan 10
SW2(config-if)# standby version 2
SW2(config-if)# standby 10 ip 10.10.10.1
SW2(config-if)# standby 10 priority 100
SW2(config-if)# standby 10 preempt
SW2(config-if)# standby 10 timers 1 3

SW2(config)# interface vlan 20
SW2(config-if)# standby version 2
SW2(config-if)# standby 20 ip 10.10.20.1
SW2(config-if)# standby 20 priority 110
SW2(config-if)# standby 20 preempt
SW2(config-if)# standby 20 timers 1 3
```

> **Perché timers 1 3?** I timer hello/hold ridotti da default (3s/10s) accelerano la convergenza HSRP: ~3-5 secondi invece di ~10-13. In ambiente di test permettono di osservare il failover senza attese eccessive.

#### VERIFICA

```
SW1# show standby brief
```

Output atteso:
```
P indicates configured to preempt.
                     |
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Vl10         10  110 P Active   local           10.10.10.3      10.10.10.1
Vl20         20  100 P Standby  10.10.20.2      local           10.10.20.1
```

```
SW2# show standby brief
```

Output atteso:
```
Interface   Grp  Pri P State    Active          Standby         Virtual IP
Vl10         10  100 P Standby  10.10.10.2      local           10.10.10.1
Vl20         20  110 P Active   local           10.10.20.3      10.10.20.1
```

```
! Verifica da PC1 (VPCS)
PC1> ping 10.10.10.1
! Deve rispondere — VIP gestito da SW1 Active

PC1> ping 10.10.20.10
! Cross-VLAN: PC1 → VIP 10.10.10.1 (SW1) → R1 → VIP 10.10.20.1 (SW2) → PC2
```

---

### T2 — IP SLA + Object Tracking collegato a HSRP

#### TEORIA

**Cos'è IP SLA**

IP SLA (Service Level Agreement) genera probe attivi per misurare la raggiungibilità e le prestazioni della rete. In questo lab usiamo la probe `icmp-echo` per verificare se R1 Loopback0 (1.1.1.1) è raggiungibile.

**Tipi di probe IP SLA disponibili su IOS**

| Tipo | Uso tipico |
|------|-----------|
| `icmp-echo` | Verifica raggiungibilità IP (come ping) |
| `udp-jitter` | Misura jitter, latenza e packet loss (VoIP MOS) |
| `tcp-connect` | Verifica che una porta TCP sia aperta |
| `http` | Verifica disponibilità applicazione HTTP |
| `dns` | Verifica risoluzione DNS |

**La catena IP SLA → Track → HSRP**

```
IP SLA 1 (icmp-echo → 1.1.1.1, ogni 5s)
    |
    v
Track 1 (monitora IP SLA 1 reachability: Up/Down)
    |
    v
HSRP Gruppo 10 (standby 10 track 1 decrement 20)
    |
    v
Se Track 1 Down: priority 110 - 20 = 90 < 100 (SW2) → failover
```

#### TASK

**Step 1** — Configurare IP SLA e Tracking su SW1:

```
! IP SLA 1: ICMP echo verso R1 Loopback0 ogni 5 secondi
SW1(config)# ip sla 1
SW1(config-ip-sla)# icmp-echo 1.1.1.1 source-interface vlan 10
SW1(config-ip-sla-echo)# frequency 5
SW1(config-ip-sla-echo)# exit

! Avviare lo scheduling — probe parte immediatamente e non scade mai
SW1(config)# ip sla schedule 1 life forever start-time now

! Object Tracking: monitorare lo stato della probe IP SLA 1
SW1(config)# track 1 ip sla 1 reachability

! Collegare il tracking a HSRP gruppo 10 con decremento 20
SW1(config)# interface vlan 10
SW1(config-if)# standby 10 track 1 decrement 20
```

> **Perché decrement 20?** Calcolo: SW1 priority 110 - 20 = 90. SW2 priority = 100. Quando Track 1 va Down, SW1 scende a 90 < 100 → SW2 vince l'elezione e diventa Active. Il decremento deve essere abbastanza grande da invertire la gerarchia.

**Step 2** — Configurare IP SLA e Tracking su SW2:

```
! Simmetrico: SW2 monitora il proprio uplink verso R1 tramite VLAN 20
SW2(config)# ip sla 1
SW2(config-ip-sla)# icmp-echo 1.1.1.1 source-interface vlan 20
SW2(config-ip-sla-echo)# frequency 5
SW2(config-ip-sla-echo)# exit

SW2(config)# ip sla schedule 1 life forever start-time now
SW2(config)# track 1 ip sla 1 reachability

SW2(config)# interface vlan 20
SW2(config-if)# standby 20 track 1 decrement 20
```

#### VERIFICA

```
! Verifica IP SLA attivo e con successi
SW1# show ip sla statistics 1
```

Output atteso:
```
IPSLAs Latest Operation Statistics
IPSLA operation id: 1
        Latest RTT: 1 milliseconds
Latest operation start time: *now*
Latest operation return code: OK
Number of successes: 12
Number of failures: 0
Operation time to live: Forever
```

```
! Verifica stato del Track
SW1# show track 1
```

Output atteso:
```
Track 1
  IP SLA 1 reachability
  Reachability is Up
    2 changes, last change 00:01:05
  Delay up 0 secs, down 0 secs
  Latest operation return code: OK
  Tracked by:
    HSRP Vlan10 10
```

```
! Verifica HSRP con tracking attivo
SW1# show standby vlan 10
```

Output atteso (estratto):
```
  Priority 110 (configured 110)
    Track object 1 state Up decrement 20
  ...
  Active virtual MAC address is 0000.0c9f.f00a
```

---

### T3 — Failover HSRP Live

#### TEORIA

Questo task dimostra la cascata di eventi che porta al failover automatico:

```
1. R1 shutdown e0/1 → link R1↔SW1 cade
2. IP SLA su SW1: next probe (entro 5s) → timeout → Return code: Timeout
3. Track 1 su SW1 → Reachability: Up → Down
4. HSRP Gr.10 su SW1 → priority 110 - 20 = 90
5. SW2 (priority 100 > 90) → vince l'elezione → stato Active su VLAN 10
6. I client su VLAN 10 continuano a usare VIP 10.10.10.1, ora gestito da SW2
7. Packet loss atteso: 3-5 pacchetti (IP SLA frequency 5s + HSRP hold timer 3s)
```

#### TASK

**Step 1** — Avviare un ping continuo da PC1 prima del failover:

```
PC1> ping 1.1.1.1 repeat 9999
! Il ping parte e continua — osservare quando i pacchetti iniziano a fallire
```

**Step 2** — Simulare il fault spegnendo il link R1↔SW1:

```
R1(config)# interface ethernet 0/1
R1(config-if)# shutdown
```

**Step 3** — Osservare i syslog su SW1 (entro 8-13 secondi):

```
! Syslog attesi su SW1:
%TRACKING-5-STATE: 1 ip sla 1 reachability Up->Down
%HSRP-5-STATECHANGE: Vlan10 Grp 10 state Active -> Speak
%HSRP-5-STATECHANGE: Vlan10 Grp 10 state Speak -> Standby

! Syslog attesi su SW2:
%HSRP-5-STATECHANGE: Vlan10 Grp 10 state Standby -> Active
```

**Step 4** — Verificare lo stato post-failover:

```
SW1# show standby brief
! Vl10: priority 90, stato Standby (decrement attivo)

SW2# show standby brief
! Vl10: stato Active (ha vinto l'elezione)

SW1# show track 1
! Reachability is Down | Change#: 1
```

**Step 5** — Ripristinare il link e osservare il preempt:

```
R1(config)# interface ethernet 0/1
R1(config-if)# no shutdown

! Attendi ~8s (IP SLA + HSRP timers + preempt)
SW1# show standby brief
! Vl10: Active (priority 110 — preempt ha ripristinato lo stato originale)
```

#### VERIFICA

```
! Il ping da PC1 deve avere max 3-5 packet loss durante il failover
! poi riprendere correttamente

SW1# show ip sla statistics 1
! Number of failures: 1 (o più, a seconda della durata dello shutdown)

SW1# show track 1
! Reachability is Up (dopo il ripristino)
! Changes: 2 (Up→Down e Down→Up)
```

---

### T4 — VRRP — Teoria e configurazione di esempio

#### TEORIA

VRRP (Virtual Router Redundancy Protocol — RFC 5798) è lo standard aperto equivalente di HSRP. Funziona su qualsiasi vendor (Cisco, Juniper, Arista, ecc.).

**Differenze principali rispetto a HSRP**

| Caratteristica | HSRP | VRRP |
|---------------|------|------|
| Standard | Cisco proprietario | IEEE RFC 5798 |
| Terminologia | Active / Standby | Master / Backup |
| Priorità default | 100 | 100 |
| Preempt default | Disabilitato | **Abilitato** |
| Multicast hello | 224.0.0.2 (v1), 224.0.0.102 (v2) | 224.0.0.18 |
| Virtual MAC | `0000.0C07.ACXX` (v1) / `0000.0C9F.FXXX` (v2) | `0000.5E00.01XX` |
| IP virtuale può essere = IP reale | No | **Si** |

**Virtual MAC VRRP**: `0000.5E00.01XX` dove XX = numero di gruppo in hex (es. gruppo 10 → `0000.5E00.010A`).

**Configurazione di esempio (non applicabile su IOU L2 — solo riferimento)**

```
! Configurazione VRRP su SW1 — Active su VLAN 10
interface vlan 10
 vrrp 10 ip 10.10.10.1
 vrrp 10 priority 110
 ! Nota: in VRRP il preempt è abilitato per default — non serve specificarlo
 vrrp 10 timers advertise 1
 ! Hello ogni 1s (default 1s in VRRP, diverso da HSRP default 3s)
```

> Su IOU L2 la versione del protocollo VRRP non è supportata pienamente. La configurazione sopra è per studio e preparazione esame. Verificare su piattaforme IOS-XE (es. CSR1000v) o switch fisici.

---

### T5 — GLBP — Teoria e configurazione di esempio

#### TEORIA

GLBP (Gateway Load Balancing Protocol — Cisco proprietario) è l'unico protocollo FHRP che permette il **load-balancing reale**: più router/switch possono essere gateway attivi contemporaneamente per client diversi.

**Ruoli GLBP**

| Ruolo | Descrizione |
|-------|-------------|
| AVG (Active Virtual Gateway) | Gestisce il gruppo, risponde alle ARP request con MAC virtuali diversi per ogni client |
| AVF (Active Virtual Forwarder) | Inoltra il traffico destinato al MAC virtuale assegnato. Tutti i router nel gruppo possono essere AVF. |

**Meccanismi di load-balancing**

| Metodo | Comportamento |
|--------|---------------|
| `round-robin` (default) | Ogni ARP request riceve un MAC virtuale diverso in rotazione |
| `weighted` | Il MAC con peso maggiore viene assegnato più frequentemente |
| `host-dependent` | Stesso host riceve sempre lo stesso MAC virtuale (utile per applicazioni stateful) |

**Virtual MAC GLBP**: `0007.B400.XXYY` dove XX = numero di gruppo, YY = numero di AVF (01, 02, ecc.)

**Configurazione di esempio (teoria — Cisco IOS-XE)**

```
! Configurazione GLBP su SW1
interface vlan 10
 glbp 10 ip 10.10.10.1
 glbp 10 priority 110
 glbp 10 preempt
 glbp 10 load-balancing round-robin
 ! round-robin: il load-balancing è trasparente ai client
```

**Confronto FHRP per l'esame**

| Protocollo | Standard | Load-balancing nativo | Max router attivi | Use case |
|-----------|----------|----------------------|-------------------|---------|
| HSRP | Cisco | No (dual-group workaround) | 1 per gruppo | Semplice ridondanza |
| VRRP | RFC 5798 | No | 1 per gruppo | Ambienti multi-vendor |
| GLBP | Cisco | Si | Fino a 4 AVF | Load-balancing reale senza dual-group |

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa probabile | Diagnosi | Fix |
|---------|-----------------|----------|-----|
| HSRP non parte — SVI down/down | Nessuna porta attiva in quella VLAN (Po1 non configurato) | `show interfaces vlan 10` | Verificare MOD-13; Po1 deve essere UP |
| Versione mismatch HSRP | Un switch usa v1, l'altro v2 | `show standby vlan 10` — syslog "version mismatch" | Aggiungere `standby version 2` su tutti i dispositivi |
| SW1 non diventa Active (priority identica) | Entrambi hanno priority 100 — vince il MAC più basso | `show standby brief` — confrontare priority | Aumentare priority dello switch desiderato |
| IP SLA con 0 successi | `ip sla schedule` mancante | `show ip sla statistics 1` — "Operational state: Not Started" | Aggiungere `ip sla schedule 1 life forever start-time now` |
| Track rimane Up anche dopo fault | Source-interface IP SLA errata — probe esce da un'altra interfaccia | `show ip sla statistics 1` — confrontare source IP | Verificare `source-interface vlan 10` nella config SLA |
| Failover non avviene (Track Down ma HSRP non cambia) | Decrement insufficiente — priority non scende abbastanza | `show standby vlan 10` — priority effettiva post-decrement | Aumentare decrement o abbassare priority SW2 |
| Preempt non funziona al ripristino | `standby 10 preempt` mancante | `show standby vlan 10` — "Preemption disabled" | Aggiungere `standby 10 preempt` |
| Ping inter-VLAN fallisce (PC1 → PC2) | Rotte statiche R1 mancanti o SVI non UP | `R1# show ip route` + `SW1# show int vlan10` | Verificare rotte R1 e status SVI |

---

## 7. SOLUZIONI

Vedere il file `soluzione.md` nella stessa cartella per le configurazioni complete commentate.

---

## 8. RIEPILOGO & EXAM TIPS

**Punti chiave:**

- HSRP usa un IP virtuale e un MAC virtuale — i client non sanno quale switch fisico è attivo
- In HSRPv2 il preempt è disabilitato per default — senza preempt, il router recovered resta Standby anche con priority più alta
- Il load-balancing HSRP si ottiene con dual-group: gruppo 10 Active su SW1, gruppo 20 Active su SW2
- IP SLA + Object Tracking: la catena SLA → Track → HSRP decrement permette il failover automatico basato sulla raggiungibilità del gateway upstream
- VRRP (RFC 5798) è lo standard aperto: preempt abilitato per default, MAC virtuale `0000.5E00.01XX`
- GLBP è l'unico FHRP con load-balancing nativo: AVG assegna MAC virtuali diversi a client diversi

**Domande tipo CCNP:**

1. HSRP vs VRRP vs GLBP: quando sceglieresti GLBP invece di due gruppi HSRP?
2. Cosa succede se `standby 10 preempt` non è configurato su SW1 dopo il ripristino dell'uplink?
3. Qual è il virtual MAC generato da HSRPv2 per il gruppo 20?
4. Con IP SLA frequency 5s e HSRP hold timer 3s, qual è il worst-case di packet loss durante il failover?
5. In VRRP, se l'IP virtuale coincide con l'IP reale del Master, cosa cambia nel comportamento?
