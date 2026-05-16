# Soluzione Commentata — MOD-13: EtherChannel LACP

**Uso:** riservato al docente | **Syllabus:** 3.1.b | **Verificata su:** GNS3 IOU L2

---

## T1 — EtherChannel LACP tra SW1 e SW2

### SW1 — configurazione completa

```
! Assegnare le porte fisiche al channel-group LACP active
interface range e0/2 - 3
 channel-group 1 mode active
 ! 'active': invia LACP PDU. È la modalità raccomandata.
 ! Non configurare trunk sulle porte fisiche — farlo sul Po1 logico.
exit

! Configurare il Port-Channel logico come trunk IEEE 802.1Q
interface port-channel 1
 switchport trunk encapsulation dot1q
 ! Su IOU L2 è obbligatorio specificare dot1q prima di 'mode trunk'.
 ! Senza questo comando IOS rifiuta il successivo switchport mode trunk.
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 ! Permettiamo solo VLAN 10 (DATA) e VLAN 20 (VOICE).
 ! VLAN 100/200 usano e0/1 — non devono attraversare Po1.
 no shutdown
```

### SW2 — configurazione completa

```
! Configurazione identica: entrambi i lati LACP active (active/active)
interface range e0/2 - 3
 channel-group 1 mode active
exit

interface port-channel 1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan 10,20
 no shutdown
```

> **Nota implementativa:** entrambi i lati in modalità `active` è la scelta corretta per massima disponibilità. La modalità `on` (bundle statico) non negozia e non rileva mismatch — evitare in produzione.

---

## Output atteso dei comandi di verifica

### show etherchannel summary (su SW1)

```
Flags: D-down P-bundled s-suspended I-stand-alone H-Hot-standby
       R-Layer3 S-Layer2 U-in-use N-not in use f-failed
Number of channel-groups in use: 1

Group Port-channel Protocol Ports
------+-------------+-----------+-------------------------------
1     Po1(SU)       LACP        Et0/2(P) Et0/3(P)
```

- `SU`: Layer**2** (**S**) + in-**U**se — il bundle è attivo
- `P`: porta correttamente **bundled** nel canale
- Se una porta mostrasse `I` (stand-alone) = mismatch di parametri

### show lacp neighbor (su SW1)

```
Channel group 1 neighbors
                LACP port     Admin     Oper    Port     Port
Port    Flags  Priority       Key       Key     Number   State
Et0/2   SA     32768          0x1       0x1     0x3      0x3D
Et0/3   SA     32768          0x1       0x1     0x4      0x3D
```

- `SA`: **S**hort timers + **A**ctive — negoziazione LACP attiva
- `Oper Key 0x1` identico su entrambe le porte: stesso bundle
- `State 0x3D`: porta in forwarding + bundled

### show interfaces port-channel 1 trunk (su SW1)

```
Port     Mode      Encapsulation  Status    Native vlan
Po1      on        802.1q         trunking  1

Port     Vlans allowed and active in management domain
Po1      10,20

Port     Vlans in spanning tree forwarding state and not pruned
Po1      10,20
```

### Ping inter-switch (conferma connettività)

```
SW1# ping 10.10.10.3 source vlan 10
!!!!!

SW1# ping 10.10.20.2 source vlan 20
!!!!!
```

---

## Note Varianti & Alternative

### LACP active/passive vs active/active

Entrambe le combinazioni formano il bundle. La differenza è chi inizia la negoziazione:
- `active/active`: entrambi inviano PDU — negoziazione più rapida, bundle si forma anche se un lato ha un breve ritardo
- `active/passive`: solo il lato active invia PDU — il lato passive aspetta; se il lato active non invia, il bundle non si forma

In produzione si usa tipicamente `active` su entrambi i lati.

### PAgP vs LACP

| Caratteristica | PAgP (Cisco) | LACP (IEEE 802.3ad) |
|---------------|-------------|---------------------|
| Standard | Proprietario Cisco | Aperto IEEE |
| Modalità | `desirable`/`auto` | `active`/`passive` |
| Interoperabilità | Solo switch Cisco | Qualsiasi vendor |
| Max porte | 8 | 16 (8 attive + 8 standby) |

Preferire sempre LACP in ambienti eterogenei o nuove installazioni.

### Pulizia configurazione errata

Se le porte fisiche hanno config residua che impedisce il channel-group:
```
SW1(config)# default interface range e0/2 - 3
! Ripristina tutti i default IOS sull'interfaccia
SW1(config)# interface range e0/2 - 3
SW1(config-if-range)# channel-group 1 mode active
```

### Errori frequenti degli studenti

1. **Trunk configurato sulle porte fisiche anziché su Po1**: IOS restituisce "Command rejected: Et0/2 is not compatible with the Po1". Soluzione: rimuovere la config dalle porte fisiche e configurare solo Po1.
2. **Encapsulamento mancante su IOU L2**: `switchport mode trunk` senza `encapsulation dot1q` prima — IOS rifiuta silenziosamente o restituisce errore. Sempre aggiungere `encapsulation dot1q` prima.
3. **Entrambi i lati `passive`**: Po1 non si forma. `show lacp neighbor` non mostra nessun neighbor. Cambiare almeno un lato in `active`.
4. **VLAN allowed mismatch**: Po1 appare `SU` ma il ping inter-VLAN fallisce. Verificare `show int po1 trunk` su entrambi i lati e allineare le VLAN allowed.
