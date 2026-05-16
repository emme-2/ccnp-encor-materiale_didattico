# Soluzione Commentata — MOD-16: IP SLA & SPAN

**Uso:** riservato al docente | **Syllabus:** 4.3 · 4.4 | **Verificata su:** GNS3 IOU L2
**Prerequisiti:** MOD-13 + MOD-14 + MOD-15

---

## T1 — IP SLA ICMP Monitoring

### SW1 — probe di monitoring con threshold

```
! IP SLA 2: ICMP echo verso R1 Loopback0, fonte SVI VLAN 10
! (IP SLA 1 è usata in MOD-15 per il tracking HSRP — non sovrascrivere)
ip sla 2
 icmp-echo 1.1.1.1 source-interface vlan 10
 ! source-interface garantisce che il probe esca dalla stessa interfaccia
 ! del traffico reale — monitoraggio path-specific
 frequency 10
 ! Probe ogni 10s: meno aggressivo dell'SLA 1 (5s) — solo monitoring
 threshold 100
 ! Alert se RTT supera 100ms — soglia tipica per voce interattiva
 timeout 5000
 ! Timeout di 5000ms prima di dichiarare la probe fallita
exit

ip sla schedule 2 life forever start-time now
! 'start-time now': la probe parte immediatamente
! 'life forever': non scade — monitoring continuo
```

### SW2 — probe di monitoring simmetrica

```
ip sla 2
 icmp-echo 1.1.1.1 source-interface vlan 20
 frequency 10
 threshold 100
 timeout 5000
exit
ip sla schedule 2 life forever start-time now
```

---

## T2 — Local SPAN

### SW1 — Session 1: sorgente e1/0, destinazione e1/1

```
! Configura Local SPAN — sorgente e1/0 (PC1), destinazione e1/1 (SPAN-dst)
monitor session 1 source interface ethernet 1/0 both
! 'both' = cattura Rx (traffico da PC1 verso la rete) e Tx (verso PC1)
! Alternativa 'rx': solo traffico ingress — utile per vedere cosa PC1 invia
! Alternativa 'tx': solo traffico egress — utile per vedere cosa riceve PC1

monitor session 1 destination interface ethernet 1/1
! e1/1 diventa porta SPAN destination:
! - Riceve una copia di tutto il traffico di e1/0
! - Non fa più parte del normale processo di forwarding
! - Il VPCS su e1/1 non risponde a ping (non può inviare)
```

> **Nota:** Non è necessario configurare alcuna VLAN su e1/1 per la sessione SPAN. Se e1/1 aveva una VLAN access configurata, questa viene ignorata mentre la sessione è attiva.

---

## T3 — RSPAN Cross-Switch

### Pulizia preventiva (rimuovere Local SPAN)

```
! Su SW1 — rimuovere session 1 prima di configurare RSPAN session 2
no monitor session 1
```

### VLAN 999 RSPAN su entrambi gli switch

```
! Su SW1
vlan 999
 name RSPAN
 remote-span
 ! Il flag 'remote-span' è critico:
 ! - Impedisce che la VLAN 999 venga usata per traffico normale
 ! - BUM (Broadcast/Unknown/Multicast) non viene flooded normalmente
 ! - Lo switch tratta questa VLAN in modo speciale per il trasporto SPAN
exit

! Su SW2 — stessa configurazione obbligatoria
vlan 999
 name RSPAN
 remote-span
exit
```

### RSPAN Source Session su SW1

```
! SW1: clona il traffico di e1/0 (PC1) e lo inietta nella VLAN 999
monitor session 2 source interface ethernet 1/0 both
monitor session 2 destination remote vlan 999
! 'remote vlan 999': il traffico clonato viene taggato con VLAN 999
! e trasportato via Po1 fino a SW2
```

### RSPAN Destination Session su SW2

```
! SW2: estrae il traffico dalla VLAN 999 e lo consegna a e1/1
monitor session 2 source remote vlan 999
! 'remote vlan 999': SW2 ascolta sulla VLAN 999 per traffico RSPAN

monitor session 2 destination interface ethernet 1/1
! e1/1 riceve il traffico clonato da PC1 su SW1
! Il VPCS SPAN-dst su e1/1 vede il traffico di PC1 come se fosse locale
```

### VLAN 999 nel trunk Po1

```
! Su SW1
interface port-channel 1
 switchport trunk allowed vlan add 999
 ! Aggiungere VLAN 999 al trunk — senza questo passo il RSPAN non funziona
 ! Errore più comune: RSPAN configurato correttamente ma VLAN non nel trunk

! Su SW2
interface port-channel 1
 switchport trunk allowed vlan add 999
```

---

## Output atteso dei comandi di verifica

### SW1# show monitor session 2

```
Session 2
----------
Type              : Remote Source Session
Source Ports      :
    Both          : Et1/0
Dest RSPAN VLAN   : 999
Operational Status: Up
```

### SW2# show monitor session 2

```
Session 2
----------
Type              : Remote Destination Session
Source RSPAN VLAN : 999
Destination Ports : Et1/1
    Encapsulation : Native
        Ingress   : Disabled
Operational Status: Up
```

### SW1# show vlan id 999

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- ----
999  RSPAN                            active

VLAN Type  SAID       MTU
---- ----- ---------- -----
999  enet  100999     1500

Remote SPAN VLAN    ← questo flag conferma la corretta configurazione
```

### SW1# show interfaces port-channel 1 trunk

```
Port     Mode      Encapsulation  Status    Native vlan
Po1      on        802.1q         trunking  1

Port     Vlans allowed and active in management domain
Po1      10,20,999    ← VLAN 999 deve apparire qui
```

### IP SLA Statistics

```
SW1# show ip sla statistics 2
IPSLAs Latest Operation Statistics
IPSLA operation id: 2
        Latest RTT: 1 milliseconds
Latest operation start time: *00:03:20
Latest operation return code: OK
Number of successes: 18
Number of failures: 0
Operation time to live: Forever

SW1# show ip sla summary
IPSLAs Latest Operation Summary
Codes: * active, ^ inactive, ~ pending
ID     Type        Destination       Stats       Return    Last
                                     (ms)        Code      Run
------+------------+-----------------+-----------+---------+----------
*1     echo        1.1.1.1           RTT=1       OK        2 seconds ago
*2     echo        1.1.1.1           RTT=1       OK        8 seconds ago
```

---

## Note Varianti & Alternative

### SPAN su VLAN anziché su porta

È possibile usare una VLAN come sorgente SPAN invece di una porta fisica:
```
monitor session 1 source vlan 10 both
! Cattura tutto il traffico VLAN 10 sullo switch — più ampia della porta singola
! Utile per analizzare tutto il traffico inter-VLAN
```

### Più porte sorgente nella stessa sessione

```
monitor session 1 source interface range e1/0 - 1 both
! Cattura traffico di e1/0 E e1/1 contemporaneamente — consegnato su e1/2
```

### RSPAN su più switch intermedi

In topologie più complesse con switch intermedi:
- Ogni switch intermedio deve avere la VLAN 999 nel trunk
- Non serve configurare nessuna sessione SPAN sugli switch intermedi
- Solo source e destination switch hanno la configurazione `monitor session`

### Errori frequenti degli studenti

1. **RSPAN VLAN senza flag `remote-span`**: la sessione resta in stato Down o non funziona correttamente. `show vlan id 999` non mostra "Remote SPAN VLAN". Fix: aggiungere `remote-span` nella config VLAN.

2. **VLAN 999 non nel trunk**: errore più frequente di RSPAN non funzionante. SW1 può iniettare il traffico nella VLAN 999 ma non arriva a SW2. `show int po1 trunk` mostra "allowed and active" senza 999. Fix: `switchport trunk allowed vlan add 999`.

3. **Sessioni SPAN in conflitto**: se la session 1 di Local SPAN non è rimossa prima di creare la session 2 RSPAN, IOS potrebbe comportarsi in modo imprevedibile o rifiutare la configurazione. Usare sempre `no monitor session 1` prima.

4. **Porta destinazione SPAN con VLAN attiva**: se e1/1 ha una VLAN access e un host connesso che genera traffico, può interferire con la sessione SPAN. Mantenere e1/1 come porta plain senza VLAN attiva durante il lab.

5. **IP SLA senza schedule**: la probe è configurata ma non schedulata — 0 successi, "Operational state: Not Started". Aggiungere `ip sla schedule X life forever start-time now`.
