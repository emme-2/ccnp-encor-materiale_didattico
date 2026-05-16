# Soluzione Commentata — MOD-32: EEM & Python Base

> **INSTRUCTOR COPY — Non distribuire agli studenti**
> Codici syllabus: 6.1 · 6.2 · 6.6

---

## SOLUZIONE EEM.1 — CONFIG-BACKUP-EEM

```
R1# configure terminal

! event manager applet <nome> — entra in modalità configurazione applet
R1(config)# event manager applet CONFIG-BACKUP-EEM

! SYS-5-CONFIG_I viene generato da: write memory, copy run start, conf t + end
! NON viene generato da: copy run flash: → nessun rischio di loop infinito
R1(config-applet)# event syslog pattern "SYS-5-CONFIG_I"

! action <numero> — le action vengono eseguite in ordine numerico
! Numeri decimali (1.0, 2.0, ...) permettono di inserire action intermedie in futuro
R1(config-applet)# action 1.0 syslog msg "EEM: backup config avviato"

! action cli command "enable" — necessario per eseguire comandi privilegiati
! Senza enable, il copy fallisce silenziosamente (applet parte da user mode)
R1(config-applet)# action 2.0 cli command "enable"

! copy running-config → copia la config attuale su flash
! Il nome "eem-backup.cfg" è fisso — ogni backup sovrascrive il precedente
! Per backup incrementali: flash:backup-$_cli_result (variabile EEM con data/ora)
R1(config-applet)# action 3.0 cli command "copy running-config flash:eem-backup.cfg"

R1(config-applet)# action 4.0 syslog msg "EEM: backup completato -> flash:eem-backup.cfg"
R1(config-applet)# end

! Verifica registrazione
R1# show event manager policy registered
! OUTPUT:
! No.  Class     Type    Event Type  Trap  Time Registered     Name
!   1  applet    system  syslog      Off   ...  CONFIG-BACKUP-EEM
```

**Nota docente:** L'applet viene salvata nella running-config. Per renderla persistente al reboot:
`R1# write memory` — questo triggera anche l'applet stessa (corretto: il backup viene eseguito).

---

## SOLUZIONE EEM.2 — Trigger e verifica CONFIG-BACKUP-EEM

```
R1# configure terminal
R1(config)# interface Loopback0
R1(config-if)# description EEM-TEST
R1(config-if)# end
R1# write memory
! ← genera SYS-5-CONFIG_I → applet parte in background

! Attendi 2-3 secondi, poi:
R1# dir flash: | include eem
! OUTPUT:
!    9  -rw-          1240  ...  eem-backup.cfg

R1# show logging | include EEM
! OUTPUT:
! %HA_EM-6-LOG: CONFIG-BACKUP-EEM: EEM: backup config avviato
! %HA_EM-6-LOG: CONFIG-BACKUP-EEM: EEM: backup completato -> flash:eem-backup.cfg

R1# show event manager history events
! OUTPUT:
! No.  Time    Event           Name                Status
!   1  ...     CONFIG-BACKUP-EEM                   success
```

---

## SOLUZIONE EEM.3 — OSPF-MONITOR-EEM

```
R1# configure terminal
R1(config)# event manager applet OSPF-MONITOR-EEM

! OSPF-5-ADJCHG: generato su qualsiasi cambio stato adjacency OSPF (up o down)
! Pattern case-sensitive — verificare con: show logging | include OSPF
R1(config-applet)# event syslog pattern "OSPF-5-ADJCHG"
R1(config-applet)# action 1.0 syslog msg "EEM: OSPF neighbor change rilevato!"
R1(config-applet)# action 2.0 cli command "enable"
R1(config-applet)# action 3.0 cli command "show ip ospf neighbor"
R1(config-applet)# action 4.0 syslog msg "EEM: stato neighbor OSPF loggato"
R1(config-applet)# end

R1# show event manager policy registered
! OUTPUT: 2 applet registrati
! 1  applet  system  syslog  Off  ...  CONFIG-BACKUP-EEM
! 2  applet  system  syslog  Off  ...  OSPF-MONITOR-EEM
```

---

## SOLUZIONE EEM.4 — Trigger e verifica OSPF-MONITOR-EEM

```
R1# terminal monitor
! Abilita visualizzazione syslog in sessione SSH corrente

R1# configure terminal
R1(config)# interface Ethernet0/0.12
R1(config-subif)# shutdown
! ← shutdown abbatte la sub-interface fisicamente
! IOS genera immediatamente OSPF-5-ADJCHG (Nbr 2.2.2.2 da FULL a DOWN)
! L'applet scatta entro 1-2 secondi

! Output visibile con terminal monitor:
! %OSPF-5-ADJCHG: Process 1, Nbr 2.2.2.2 on Ethernet0/0.12 from FULL to DOWN
! %HA_EM-6-LOG: OSPF-MONITOR-EEM: EEM: OSPF neighbor change rilevato!
! %HA_EM-6-LOG: OSPF-MONITOR-EEM: EEM: stato neighbor OSPF loggato

R1(config-subif)# no shutdown
! secondo trigger: neighbor torna FULL → OSPF-5-ADJCHG di nuovo

R1# show event manager history events
! OSPF-MONITOR-EEM   success   (almeno 2 occorrenze: down + up)

! PERCHE NON ASPETTIAMO IL DEAD TIMER (40s):
! shutdown abbatte fisicamente la sub-interface → ADJCHG istantaneo
! Dead timer scatta solo se interfaccia rimane UP ma hello cessano (es. ACL)
```

---

## SOLUZIONE P.3 — Script backup_config.py (completo)

```python
#!/usr/bin/env python3
"""
MOD-32 — Task P.3: Backup running-config con Paramiko
Raccoglie show running-config da R1-R4 e salva i file in backup/

Dipendenze: paramiko (pip install paramiko)
"""

import paramiko
import json
import os
import time

# Carica inventario
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

os.makedirs('backup', exist_ok=True)

for device in inventory['devices']:
    hostname = device['hostname']
    ip       = device['ip']

    client = paramiko.SSHClient()
    # AutoAddPolicy: accetta automaticamente la host key senza verificare fingerprint
    # In produzione: RejectPolicy + known_hosts verificato
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname      = ip,
        username      = device['username'],
        password      = device['password'],
        port          = 22,
        timeout       = 10,
        look_for_keys = False,
        allow_agent   = False,
    )

    # invoke_shell() crea una sessione interattiva (PTY) — necessario per IOS
    # exec_command() NON funziona bene con IOS (output incompleto senza PTY)
    shell = client.invoke_shell(width=250, height=50)
    time.sleep(1)
    shell.recv(65535)  # svuota banner di login

    shell.send('enable\n')
    time.sleep(0.5)
    shell.send(f"{device['enable']}\n")
    time.sleep(0.5)
    shell.recv(65535)

    shell.send('terminal length 0\n')
    time.sleep(0.5)
    shell.recv(65535)

    shell.send('show running-config\n')
    time.sleep(3)    # IOU è lento — attendere che l'output sia completo

    # 200000 byte = abbondante per qualsiasi running-config IOU
    output = shell.recv(200000).decode('utf-8', errors='replace')

    filename = f'backup/{hostname}-config.txt'
    with open(filename, 'w') as f:
        f.write(output)

    print(f"{hostname:4s} -> {filename} ({len(output)} bytes)")
    client.close()

print("\nBackup completato.")
```

---

## SOLUZIONE P.4 — Script b1_report.py (completo)

```python
#!/usr/bin/env python3
"""
MOD-32 — Task P.4: Parsing JSON e salvataggio report
Legge i file di backup, conta le interfacce configurate, produce report.json
"""

import json
import os

# json.load() accetta FILE OBJECT — NON json.load('inventory.json')
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

risultati = []

for device in inventory['devices']:
    hostname    = device['hostname']
    backup_file = f'backup/{hostname}-config.txt'

    with open(backup_file, 'r') as f:
        contenuto = f.read()

    interface_count = len([
        riga for riga in contenuto.splitlines()
        if riga.strip().startswith('interface')
    ])

    risultati.append({
        'hostname'       : hostname,
        'ip'             : device['ip'],
        'location'       : device.get('location', 'N/A'),
        'interface_count': interface_count,
    })
    print(f"{hostname}: {interface_count} interfacce trovate")

report = {
    'lab'        : 'ENCOR-MOD32',
    'modulo'     : 'MOD-32 — EEM & Python Base',
    'dispositivi': risultati,
}

# json.dump() scrive su FILE OBJECT — ritorna None
os.makedirs('backup', exist_ok=True)
with open('backup/report.json', 'w') as f:
    json.dump(report, f, indent=2)

# json.dumps() restituisce STRINGA — per visualizzare in console
print('\n--- REPORT ---')
print(json.dumps(report, indent=2))

with open('backup/report.json', 'r') as f:
    check = json.load(f)
assert len(check['dispositivi']) == 4, 'Errore: numero device errato'
print(f"\nVerifica OK: {len(check['dispositivi'])} dispositivi nel report")
```

---

## NOTE DIDATTICHE — Confronto EEM vs Python

| Aspetto | EEM (on-device) | Python + Paramiko (off-device) |
|---------|-----------------|-------------------------------|
| Infrastruttura | Zero — integrato in IOS | Script runner + Python + SSH |
| Reattività | Istantanea (evento IOS) | Polling o webhook |
| Scope | Un solo device | N device in loop o parallelo |
| Persistenza | In running-config | Solo se pushato esplicitamente |
| Caso d'uso | Reazione locale (backup, alert) | Automazione centralizzata su flotta |

### Errori comuni da correggere in aula

1. `json.load('percorso/file.json')` → `AttributeError: 'str' has no attribute 'read'`
   - Correzione: `with open('percorso/file.json') as f: json.load(f)`
2. EEM applet senza `action cli command "enable"` → il `copy run flash:` fallisce silenziosamente
3. Paramiko su IOU: `time.sleep(1)` insufficiente → output troncato. Usare almeno `sleep(3)` dopo `show run`
4. Trailing comma in JSON (`{"key": "val",}`) — valida in Python, **illegale** in JSON
