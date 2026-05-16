# Soluzione Commentata — MOD-14: Spanning Tree

**Uso:** riservato al docente | **Syllabus:** 3.1.c | **Verificata su:** GNS3 IOU L2
**Prerequisito:** MOD-13 — Po1 tra SW1 e SW2 deve essere UP prima di iniziare.

---

## T1 — Root Bridge Election per VLAN

### SW1 — root primario VLAN 10, secondario VLAN 20

```
! Priority 4096 su VLAN 10: Bridge ID = 4096 + 10 = 4106
! È il valore più basso possibile non-zero — garantisce SW1 come root VLAN 10
spanning-tree vlan 10 priority 4096

! Priority 8192 su VLAN 20: SW1 sarà secondario VLAN 20 (fallback se SW2 va down)
! Bridge ID = 8192 + 20 = 8212
spanning-tree vlan 20 priority 8192
```

### SW2 — root primario VLAN 20, secondario VLAN 10

```
spanning-tree vlan 20 priority 4096
! Bridge ID VLAN 20 = 4096 + 20 = 4116 → SW2 è root VLAN 20

spanning-tree vlan 10 priority 8192
! Bridge ID VLAN 10 = 8192 + 10 = 8202 → SW2 è secondario VLAN 10
```

> **Nota progettuale:** la simmetria STP/HSRP è intenzionale. SW1 è root STP e HSRP Active per VLAN 10; SW2 è root STP e HSRP Active per VLAN 20. Il traffico non attraversa percorsi asimmetrici — prestazioni ottimali e troubleshooting semplificato.

---

## T2 — PortFast e BPDU Guard

### SW1 — porta host e1/0 (PC1)

```
interface ethernet 1/0
 spanning-tree portfast
 ! Bypassa Discarding→Learning→Forwarding: la porta va subito in Forwarding.
 ! Riduce il tempo di attivazione del PC da ~30s a <1s.
 ! IMPORTANTE: configurare SOLO su porte host, mai su trunk o Port-Channel.
 spanning-tree bpduguard enable
 ! Se la porta riceve una BPDU → err-disabled immediatamente.
 ! Protegge contro switch non autorizzati collegati su porte host.
```

### SW2 — porta host e1/0 (PC2)

```
interface ethernet 1/0
 spanning-tree portfast
 spanning-tree bpduguard enable
```

---

## T3 — Root Guard sul Port-Channel Po1

### SW1

```
interface port-channel 1
 spanning-tree guard root
 ! Root Guard: se Po1 riceve BPDU con Bridge ID inferiore al root attuale,
 ! la porta entra in stato 'root-inconsistent' (Discarding).
 ! Al contrario di BPDU Guard, il recovery è automatico quando le BPDU
 ! superiori smettono di arrivare — no intervento manuale necessario.
```

### SW2

```
interface port-channel 1
 spanning-tree guard root
```

---

## Output atteso dei comandi di verifica

### SW1# show spanning-tree vlan 10

```
VLAN0010
  Spanning tree enabled protocol rstp
  Root ID    Priority    4106
             Address     aabb.cc00.0100
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    4106   (priority 4096 sys-id-ext 10)
             Address     aabb.cc00.0100

Interface        Role  Sts  Cost      Prio.Nbr  Type
-----------      ----  ---  ------    --------  ----
Et0/1            Desg  FWD  100       128.2     Shr
Po1              Desg  FWD  4         128.65    Shr P2p
Et1/0            Desg  FWD  100       128.193   Shr Edge P2p
```

### SW2# show spanning-tree vlan 10

```
VLAN0010
  Root ID    Priority    4106
             Address     aabb.cc00.0100
             Cost        4
             Port        Port-channel1 (Po1)
             ! SW2 raggiunge il root VLAN 10 (SW1) tramite Po1

  Bridge ID  Priority    8202   (priority 8192 sys-id-ext 10)

Interface        Role  Sts  Cost      Prio.Nbr  Type
-----------      ----  ---  ------    --------  ----
Et0/1            Desg  FWD  100       128.2     Shr
Po1              Root  FWD  4         128.65    Shr P2p
Et1/0            Desg  FWD  100       128.193   Shr Edge P2p
```

### SW1# show spanning-tree interface ethernet 1/0 detail

```
Port 193 (Ethernet1/0) of VLAN0010 is designated forwarding
   Port path cost 100, Port priority 128, Port Identifier 128.193
   ...
   The port is in the portfast mode
   Bpdu guard is enabled
```

### SW1# show spanning-tree interface port-channel 1 detail

```
Port 65 (Port-channel1) of VLAN0010 is designated forwarding
   ...
   Root guard is enabled on the port
```

---

## Note Varianti & Alternative

### Alternativa: spanning-tree vlan X root primary/secondary

IOS offre una macro che calcola automaticamente la priority ottimale:
```
SW1(config)# spanning-tree vlan 10 root primary
! IOS imposta la priority a 24576 se il root attuale ha priority >= 24576,
! altrimenti usa 4096. Non deterministico — preferire il valore esplicito in ambienti didattici.

SW1(config)# spanning-tree vlan 20 root secondary
! IOS imposta priority a 28672.
```

Per corsi CCNP si raccomanda la configurazione esplicita (`priority 4096`) per trasparenza e controllo.

### Configurazione BPDU Guard globale

Alternativa alla configurazione per-porta: attivare BPDU Guard su tutte le porte PortFast globalmente:
```
SW1(config)# spanning-tree portfast bpduguard default
! Attiva BPDU Guard su TUTTE le porte con PortFast abilitato
```

La configurazione per-porta (`spanning-tree bpduguard enable`) sovrascrive quella globale. Preferire la configurazione globale in produzione per non dimenticare porte.

### Errdisable recovery automatico

Per il ripristino automatico dopo BPDU Guard (utile in ambienti didattici per non bloccare il lab):
```
SW1(config)# errdisable recovery cause bpduguard
SW1(config)# errdisable recovery interval 30
! La porta si riattiva automaticamente dopo 30 secondi
```

In produzione non configurare il recovery automatico per BPDU Guard — richiede sempre intervento consapevole del network team.

### Errori frequenti degli studenti

1. **Priority non in multipli di 4096**: IOS arrotonda silenziosamente. Verificare sempre con `show spanning-tree vlan X` il valore effettivo.
2. **PortFast su porte trunk**: IOS emette un warning (`TOPOTRAP`) ma non blocca il trunk. Spiegare perché è pericoloso (un loop potrebbe propagarsi senza che STP intervenga immediatamente).
3. **Confusione BPDU Guard vs Root Guard**: BPDU Guard = qualsiasi BPDU → err-disabled; Root Guard = solo BPDU superiore → root-inconsistent.
4. **Root Guard su e1/0 (porta host)**: non ha senso pratico — non ci sarà mai un root bridge connesso su una porta PC. Mettere Root Guard su porte trunk, BPDU Guard su porte host.
