# Workbook Studenti — MOD-32: EEM & Python Base

**Area:** AREA 13 — AUTOMATION & PROGRAMMABILITY
**Ore:** 2h | **Codici syllabus:** 6.1 · 6.2 · 6.6
**Prerequisito:** MOD-31 (Python fondamenta) — o equivalente

---

## 1. TOPOLOGIA

```
          VM GNS3 (192.168.122.1)
          management + script runner
          TFTP · Git · RADIUS
                  |
               SW1 (IOU L2)
           VLAN 10 — management
         /        |        \        \
       R1        R2        R3       R4
  .101/24     .102/24   .103/24  .104/24
  Lo0:1.1.1.1 2.2.2.2   3.3.3.3  4.4.4.4

  R1-R2: e0/0.12  10.0.12.0/30  VLAN 12
  R1-R3: e0/0.13  10.0.13.0/30  VLAN 13
  R2-R4: e0/0.24  10.0.24.0/30  VLAN 24
  R3-R4: e0/0.34  10.0.34.0/30  VLAN 34
```

### Tabella indirizzamento

| Device | Interfaccia    | IP / Mask           | Ruolo        | Note                  |
|--------|----------------|---------------------|--------------|-----------------------|
| R1     | e0/0.10        | 192.168.122.101/24  | Management   | DHCP da VM GNS3       |
| R1     | Loopback0      | 1.1.1.1/32          | Router-ID    | OSPF advertised       |
| R1     | e0/0.12        | 10.0.12.1/30        | Link R1-R2   | OSPF area 0           |
| R1     | e0/0.13        | 10.0.13.1/30        | Link R1-R3   | OSPF area 0           |
| R2     | e0/0.10        | 192.168.122.102/24  | Management   |                       |
| R2     | Loopback0      | 2.2.2.2/32          | Router-ID    |                       |
| R2     | e0/0.12        | 10.0.12.2/30        | Link R2-R1   | OSPF area 0           |
| R2     | e0/0.24        | 10.0.24.1/30        | Link R2-R4   | OSPF area 0           |
| R3     | e0/0.10        | 192.168.122.103/24  | Management   |                       |
| R3     | Loopback0      | 3.3.3.3/32          | Router-ID    |                       |
| R3     | e0/0.13        | 10.0.13.2/30        | Link R3-R1   | OSPF area 0           |
| R3     | e0/0.34        | 10.0.34.1/30        | Link R3-R4   | OSPF area 0           |
| R4     | e0/0.10        | 192.168.122.104/24  | Management   |                       |
| R4     | Loopback0      | 4.4.4.4/32          | Router-ID    |                       |
| R4     | e0/0.24        | 10.0.24.2/30        | Link R4-R2   | OSPF area 0           |
| R4     | e0/0.34        | 10.0.34.2/30        | Link R4-R3   | OSPF area 0           |
| VM GNS3| virbr0         | 192.168.122.1/24    | TFTP · Git   | Script runner         |

> **Nota:** OSPF area 0 e-configurato su tutti i link P2P e le Loopback.
> Verifica iniziale: `show ip ospf neighbor` su R1 deve mostrare R2 e R3 in stato FULL.

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sarà in grado di:

- [ ] Configurare EEM Applet in IOS per reagire autonomamente a eventi di sistema (syslog, timer)
- [ ] Descrivere l'architettura EEM: Event Detector, EEM Server, Policy, Action
- [ ] Usare correttamente le 4 funzioni del modulo `json` (`load`, `loads`, `dump`, `dumps`)
- [ ] Creare e attivare un virtual environment Python (`venv`) e gestire dipendenze con `pip`
- [ ] Scrivere uno script Python con Paramiko per connettersi via SSH a un router IOS e raccogliere dati
- [ ] Salvare e leggere strutture dati in formato JSON da/su file

**Codici syllabus coperti:** 6.1 (on-device automation) · 6.2 (Python scripting) · 6.6 (JSON encoding/decoding)

---

## 3. LAB SETUP

### 3.1 Caricamento configurazioni router via TFTP

All'avvio del lab, caricare la configurazione iniziale su ogni router:

```
R1# copy tftp://192.168.122.1/ENCOR/MOD-32/r1-cfg running-config
R2# copy tftp://192.168.122.1/ENCOR/MOD-32/r2-cfg running-config
R3# copy tftp://192.168.122.1/ENCOR/MOD-32/r3-cfg running-config
R4# copy tftp://192.168.122.1/ENCOR/MOD-32/r4-cfg running-config
```

Dopo il caricamento, generare le chiavi RSA per SSH su ogni router:

```
Rx(config)# crypto key generate rsa modulus 1024
```

> **Attenzione — IOU:** Le chiavi RSA non vengono salvate nella running-config su IOU.
> Devono essere rigenerate ad ogni riavvio del router.

### 3.2 Clone del repository e setup venv

Dalla VM GNS3 (utente student):

```bash
# 1. Clone del repo del lab
cd ~
git clone http://192.168.122.1/git/ENCOR-MOD32.git
cd ENCOR-MOD32

# 2. Crea il virtual environment
python3 -m venv .venv

# 3. Attiva il venv (il prompt cambia: (.venv) student@gns3vm:~$)
source .venv/bin/activate

# 4. Installa le dipendenze
pip install -r requirements.txt
```

### 3.3 Prerequisiti

- Tutti i router raggiungibili via SSH dalla VM GNS3 (porta 22)
- OSPF area 0 attivo su tutti i link P2P
- Python 3.8+ disponibile sulla VM GNS3
- Accesso git a `http://192.168.122.1/git/`

### 3.4 Verifica pre-lab

```
! Su R1: verifica OSPF
R1# show ip ospf neighbor
! Atteso: R2 (2.2.2.2) e R3 (3.3.3.3) in stato FULL

! Su R1: verifica SSH
R1# show ip ssh
! Atteso: SSH Enabled - version 2.0

! Dalla VM GNS3: verifica connettività
student@gns3vm:~$ ssh admin@192.168.122.101
! Password: cisco123 | enable: cisco123
```

---

## 4. TASK LIST

| #    | Task                              | Codice syllabus | Tempo  |
|------|-----------------------------------|-----------------|--------|
| EEM.1 | CONFIG-BACKUP-EEM su R1          | 6.1             | 15 min |
| EEM.2 | Trigger e verifica CONFIG-BACKUP  | 6.1             | 10 min |
| EEM.3 | OSPF-MONITOR-EEM su R1            | 6.1             | 10 min |
| EEM.4 | Trigger e verifica OSPF-MONITOR   | 6.1             | 10 min |
| P.1  | Setup venv, clone repo, pip install | 6.2           | 10 min |
| P.2  | Teoria json — le 4 funzioni       | 6.6             | 10 min |
| P.3  | Script backup_config.py (Paramiko)| 6.2 · 6.6       | 20 min |
| P.4  | Parsing JSON e salvataggio report | 6.6             | 15 min |

---

## 5. DETTAGLIO TASK

---

### TASK EEM.1 — CONFIG-BACKUP-EEM

#### TEORIA — EEM: Architettura

**Embedded Event Manager (EEM)** è un framework di automazione integrato in IOS.
Permette al router di reagire autonomamente a eventi di sistema senza strumenti esterni.

**Architettura:**
```
[Event Detector] --> [EEM Server] --> [Policy (Applet / TCL)] --> [Action]
```

| Componente | Esempi | Funzione |
|------------|--------|----------|
| `event syslog pattern "..."` | `"SYS-5-CONFIG_I"` | Monitora syslog per pattern |
| `event timer watchdog time N` | ogni 60 secondi | Timer periodico |
| `event track N state down` | track IP SLA | Reagisce a cambio stato tracking |
| `event interface name X parameter operstate` | e0/0.12 up/down | Cambio stato interfaccia |
| `action cli command "..."` | `copy run flash:` | Esegue comandi IOS |
| `action syslog msg "..."` | messaggio custom | Scrive nel syslog del router |

> **Nota:** In questo modulo usiamo solo **EEM Applet** — configurazione CLI nativa IOS.
> Non richiedono TCL né Python on-device.

#### TASK — Configurazione CONFIG-BACKUP-EEM

Configura su R1 un applet che esegue il backup automatico della running-config su flash
ogni volta che qualcuno salva la configurazione con `write memory`.

Il pattern `SYS-5-CONFIG_I` viene generato da: `write memory`, `copy run start`, `conf t` + `end`.
Non viene generato da: `copy run flash:` — nessun rischio di loop.

Completa lo schema (inserisci i comandi nei punti `! TODO`):

```
R1# configure terminal
R1(config)# event manager applet CONFIG-BACKUP-EEM
R1(config-applet)# event syslog pattern "___________"   ! TODO: pattern CONFIG_I
R1(config-applet)# action 1.0 syslog msg "___________"  ! TODO: messaggio avvio
R1(config-applet)# action 2.0 cli command "enable"
R1(config-applet)# action 3.0 cli command "___________" ! TODO: copy run flash:eem-backup.cfg
R1(config-applet)# action 4.0 syslog msg "___________"  ! TODO: messaggio completamento
R1(config-applet)# end
```

#### VERIFICA

```
R1# show event manager policy registered
! Atteso: CONFIG-BACKUP-EEM  applet  system  ...  registered

R1# show running-config | section event manager
! Atteso: l'intero blocco applet CONFIG-BACKUP-EEM
```

---

### TASK EEM.2 — Trigger e verifica CONFIG-BACKUP-EEM

#### TEORIA — Come testare un'applet EEM

Un'applet che reagisce a `SYS-5-CONFIG_I` si attiva ogni volta che IOS salva la configurazione.
Il modo più semplice per triggherarla è: modificare la config e poi eseguire `write memory`.

#### TASK

```
R1# configure terminal
R1(config)# interface Loopback0
R1(config-if)# description EEM-TEST
R1(config-if)# end
R1# write memory
! ← questo genera SYS-5-CONFIG_I e attiva l'applet

! Verifica file backup su flash:
R1# dir flash: | include eem

! Verifica messaggi EEM nel syslog:
R1# show logging | include EEM

! Verifica storico eventi EEM:
R1# show event manager history events
```

#### VERIFICA

```
! dir flash:
!   eem-backup.cfg   [dimensione > 0 byte]

! show logging | include EEM
!   %HA_EM-6-LOG: CONFIG-BACKUP-EEM: EEM: backup config avviato
!   %HA_EM-6-LOG: CONFIG-BACKUP-EEM: EEM: backup completato -> flash:eem-backup.cfg

! show event manager history events
!   CONFIG-BACKUP-EEM   Status: success
```

---

### TASK EEM.3 — OSPF-MONITOR-EEM

#### TEORIA — Event syslog pattern su messaggi OSPF

Il pattern `OSPF-5-ADJCHG` viene generato ogni volta che cambia lo stato di un neighbor OSPF
(sia quando cade che quando torna su). Permette di loggare automaticamente lo stato della topologia.

#### TASK

Configura su R1 un secondo applet che intercetta i cambiamenti di stato OSPF e logga
lo stato attuale dei neighbor.

```
R1# configure terminal
R1(config)# event manager applet OSPF-MONITOR-EEM
R1(config-applet)# event syslog pattern "___________"        ! TODO: pattern ADJCHG
R1(config-applet)# action 1.0 syslog msg "EEM: OSPF neighbor change rilevato!"
R1(config-applet)# action 2.0 cli command "enable"
R1(config-applet)# action 3.0 cli command "___________"      ! TODO: show ip ospf neighbor
R1(config-applet)# action 4.0 syslog msg "EEM: stato neighbor OSPF loggato"
R1(config-applet)# end
```

#### VERIFICA

```
R1# show event manager policy registered
! Atteso: 2 applet registrati
!   CONFIG-BACKUP-EEM
!   OSPF-MONITOR-EEM
```

---

### TASK EEM.4 — Trigger e verifica OSPF-MONITOR-EEM

#### TEORIA — Shutdown su sub-interface vs dead timer

Quando si spegne una sub-interface con `shutdown`, IOS abbatte il layer fisico della sub-interface.
Il router peer perde immediatamente l'adiacenza OSPF (evento `ADJCHG` immediato).
Il **dead timer** di default (40 secondi) scatta solo se l'interfaccia rimane UP ma gli hello cessano.

#### TASK

```
! Abilita visualizzazione syslog in sessione SSH:
R1# terminal monitor

R1# configure terminal
R1(config)# interface Ethernet0/0.12
R1(config-subif)# shutdown
! ← l'adiacenza OSPF verso R2 cade -> OSPF-5-ADJCHG -> applet scatta

R1(config-subif)# end

! Attendi 2-3 secondi, poi osserva:
R1# show logging | include EEM
R1# show event manager history events

! Ripristina e osserva il secondo trigger:
R1# configure terminal
R1(config)# interface Ethernet0/0.12
R1(config-subif)# no shutdown
```

#### VERIFICA

```
! show logging | include EEM
!   EEM: OSPF neighbor change rilevato! (x2: down + up)
!   EEM: stato neighbor OSPF loggato (x2)

! show event manager history events
!   OSPF-MONITOR-EEM   Status: success (almeno 2 occorrenze)

! show ip ospf neighbor
!   Dopo no shutdown: R2 torna in stato FULL/DR o FULL/BDR
```

---

### TASK P.1 — Setup Ambiente Python

#### TEORIA — Perché usare un virtual environment

| Problema senza venv | Soluzione con venv |
|---------------------|--------------------|
| Conflitti di versione tra pacchetti | Ogni progetto ha il suo interprete isolato |
| `pip` installa globalmente (root) | Pacchetti in `.venv/`, non toccano il sistema |
| Non riproducibile su altra macchina | `requirements.txt` con versioni pinnate |
| Difficile da pulire | `rm -rf .venv/` lascia il sistema intatto |

> **Regola pratica:** un progetto = un venv. Mai installare pacchetti con `pip` fuori da un venv attivo.

#### TASK

```bash
# Dalla home della VM GNS3 (venv già attivato dal Lab Setup)
# Verifica che il venv sia attivo (deve comparire (.venv) nel prompt)
which python3
# Atteso: /home/student/ENCOR-MOD32/.venv/bin/python3

# Verifica pacchetti installati
pip list
# Deve comparire: paramiko, cryptography

# Verifica la struttura del repo
ls -la ~/ENCOR-MOD32/scripts/
# Atteso: b1_json_scheletro.py  inventory.json  backup/ (directory)
```

#### VERIFICA

```
(.venv) student@gns3vm:~/ENCOR-MOD32$ python3 --version
Python 3.x.x

(.venv) student@gns3vm:~/ENCOR-MOD32$ pip show paramiko
Name: paramiko
Version: 3.x.x
```

---

### TASK P.2 — Le 4 funzioni del modulo json

#### TEORIA — Tabella mnemonico

| Funzione         | La "s" | Sorgente / Destinazione | Ritorna  |
|------------------|--------|-------------------------|----------|
| `json.load(f)`   | NO     | Legge da FILE object    | `dict` / `list` |
| `json.loads(s)`  | SI     | Legge da STRINGA JSON   | `dict` / `list` |
| `json.dump(obj, f)` | NO  | Scrive su FILE object   | `None`   |
| `json.dumps(obj)` | SI    | Scrive su STRINGA       | `str`    |

> **Mnemonico:** La `s` finale sta per **S**tring. Senza `s` si lavora sempre con un file object (`open()`).

#### TASK — Esercizi interattivi nel REPL Python

```bash
# Avvia Python interattivo
python3
```

```python
import json

# Esercizio 1: json.loads() — leggi una stringa JSON
stringa = '{"hostname": "R1", "ip": "192.168.122.101"}'
dati = json.loads(stringa)
print(type(dati))          # <class 'dict'>
print(dati['hostname'])    # R1

# Esercizio 2: json.dumps() — serializza in stringa
router = {"hostname": "R2", "ip": "192.168.122.102", "ospf": True}
output = json.dumps(router, indent=2)
print(output)

# Esercizio 3: errore comune — trailing comma
json_errato = '{"hostname": "R3", "ip": "192.168.122.103",}'
try:
    json.loads(json_errato)
except json.JSONDecodeError as e:
    print(f"Errore: {e.msg} — riga {e.lineno}")

exit()
```

#### VERIFICA

```
<class 'dict'>
R1
{
  "hostname": "R2",
  "ip": "192.168.122.102",
  "ospf": true
}
Errore: Expecting property name enclosed in double quotes — riga 1
```

---

### TASK P.3 — Script backup_config.py con Paramiko

#### TEORIA — Paramiko: SSH client per Python

Paramiko implementa il protocollo SSH in Python puro. Permette di aprire sessioni SSH,
inviare comandi e leggere l'output — esattamente come un operatore umano farebbe manualmente.

Flusso tipico Paramiko:
```
SSHClient() → connect() → exec_command() → read stdout → close()
```

> **Nota IOU:** IOU è più lento di hardware reale. Aggiungere `time.sleep(2)` dopo ogni
> `exec_command()` per garantire che l'output sia completo prima di leggerlo.

#### TASK

Apri il file `scripts/b1_backup.py` e completa i punti marcati `# TODO`:

```python
import paramiko
import json
import os
import time

# Carica l'inventario dei router
with open('inventory.json', 'r') as f:
    inventory = json.load(f)

os.makedirs('backup', exist_ok=True)

for device in inventory['devices']:
    hostname = device['hostname']
    ip       = device['ip']

    # TODO: crea un SSHClient e configura auto-add della host key
    client = paramiko.___________()
    client.set_missing_host_key_policy(paramiko.___________)

    # TODO: connetti al router con username, password e port=22
    client.connect(
        hostname = ___,
        username = ___,
        password = ___,
        port     = 22,
        timeout  = 10,
    )

    # Apri una sessione interattiva (invoke_shell per IOS)
    shell = client.invoke_shell()
    time.sleep(1)
    shell.recv(65535)   # svuota il banner di login

    # Entra in enable mode
    shell.send('enable\n')
    time.sleep(0.5)
    shell.send('cisco123\n')
    time.sleep(0.5)
    shell.recv(65535)

    # Disabilita paginazione e raccogli show running-config
    shell.send('terminal length 0\n')
    time.sleep(0.5)
    shell.send('show running-config\n')
    time.sleep(3)   # IOU è lento: attendi 3 secondi

    # TODO: leggi l'output dal buffer (max 200000 byte) e decodifica in stringa
    output = shell.recv(___________).decode('utf-8', errors='replace')

    # Salva su file
    filename = f'backup/{hostname}-config.txt'
    with open(filename, 'w') as f:
        f.write(output)

    print(f"{hostname:4s} -> {filename} ({len(output)} bytes)")
    client.close()

print("\nBackup completato.")
```

Esegui lo script:

```bash
cd ~/ENCOR-MOD32
python3 scripts/b1_backup.py
```

#### VERIFICA

```
R1   -> backup/R1-config.txt (1240 bytes)
R2   -> backup/R2-config.txt (1195 bytes)
R3   -> backup/R3-config.txt (1210 bytes)
R4   -> backup/R4-config.txt (1188 bytes)

Backup completato.

# Verifica file:
ls -lh backup/*.txt
# Tutti i file devono essere > 1000 byte
```

---

### TASK P.4 — Parsing JSON e salvataggio report

#### TEORIA — json.load() e json.dump() su file

```python
# Leggere da file:
with open('dati.json', 'r') as f:
    dati = json.load(f)      # f = file object, NON stringa path

# Scrivere su file:
with open('dati.json', 'w') as f:
    json.dump(dati, f, indent=2)   # ritorna None

# ERRORE COMUNE:
dati = json.load('dati.json')    # AttributeError: 'str' has no attribute 'read'
```

#### TASK

Apri `scripts/b1_report.py` e completalo:

```python
import json
import os

# 1. Leggi inventory.json
with open('_____________', 'r') as f:    # TODO: path corretto
    inventory = json.load(f)

# 2. Per ogni device in inventory['devices'], leggi il file di backup
#    e conta le righe che contengono "interface"
risultati = []
for device in inventory['devices']:
    hostname = device['hostname']
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

# 3. Costruisci il dizionario report
report = {
    'lab'        : 'ENCOR-MOD32',
    'modulo'     : 'MOD-32 — EEM & Python Base',
    'dispositivi': risultati,
}

# 4. Salva su file con json.dump (indent=2)
os.makedirs('backup', exist_ok=True)
with open('backup/report.json', 'w') as f:
    json._____(report, f, indent=___)    # TODO: completa

# 5. Preview in console con json.dumps
print('\n--- REPORT ---')
print(json._____(report, indent=2))      # TODO: completa
```

Esegui:

```bash
python3 scripts/b1_report.py
```

#### VERIFICA

```
R1: 7 interfacce trovate
R2: 6 interfacce trovate
R3: 6 interfacce trovate
R4: 6 interfacce trovate

--- REPORT ---
{
  "lab": "ENCOR-MOD32",
  "modulo": "MOD-32 — EEM & Python Base",
  "dispositivi": [
    {
      "hostname": "R1",
      ...
    },
    ...
  ]
}

# Verifica file JSON:
python3 -c "import json; d=json.load(open('backup/report.json')); print(len(d['dispositivi']))"
# Atteso: 4
```

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa probabile | Diagnosi | Fix |
|---------|----------------|----------|-----|
| `show event manager policy registered` vuoto | Applet non salvata / errore di sintassi | `show run | section event manager` | Rientrare in config applet e correggere la sintassi |
| EEM non scatta dopo `write mem` | Pattern errato nel syslog | `debug event manager action cli` | Verificare il pattern esatto con `show logging | include CONFIG` |
| `show event manager history events` vuoto | Il trigger non è ancora avvenuto | Eseguire `write memory` | Normale — l'applet è registrata ma non ancora scattata |
| `eem-backup.cfg` non compare in `dir flash:` | `action cli command` senza `enable` prima | `show event manager history` → Status: fail | Aggiungere `action 2.0 cli command "enable"` PRIMA del copy |
| SSH: `Connection refused` da Python | SSH non abilitato / chiavi RSA assenti | `show ip ssh` sul router | `crypto key generate rsa modulus 1024` + `transport input ssh` su VTY |
| Paramiko: `AuthenticationException` | Credenziali errate | Testare SSH manuale: `ssh admin@192.168.122.101` | Verificare username/password in `inventory.json` |
| Output Paramiko troncato | Buffer piccolo o sleep insufficiente | Aggiungere print del len(output) | Aumentare `time.sleep()` e dimensione buffer `recv()` |
| `json.load('percorso')` → `AttributeError` | Passato string invece di file object | Leggere il traceback | Usare `with open(...) as f: json.load(f)` |
| `json.JSONDecodeError: Trailing comma` | Virgola dopo ultimo campo JSON | `e.lineno` indica la riga | Rimuovere la virgola finale — non valida in JSON |
| Venv non attivo: `pip install` installa globalmente | Manca `source .venv/bin/activate` | `which python3` → percorso di sistema | Attivare venv: `source .venv/bin/activate` |

---

## 7. SOLUZIONI

> Le soluzioni complete si trovano in `MOD-32/soluzione.md`.
> Non consultare prima di aver tentato i task autonomamente.

---

## 8. RIEPILOGO & EXAM TIPS

### Punti chiave

1. **EEM Applet** = automazione on-device integrata in IOS: nessun tool esterno, reazione istantanea a eventi di sistema (`syslog`, `timer`, `track`, `interface`)
2. **Il modulo `json`** ha 4 funzioni: la `s` finale indica operazione su **S**tring; senza `s` si usa un file object
3. **`json.load` vs `json.loads`**: `load` vuole un file object aperto — l'errore più comune è passare il path come stringa
4. **`venv`**: un progetto = un venv. Sempre attivare prima di usare `pip` o eseguire script
5. **Paramiko su IOU**: IOU è lento — usare `time.sleep()` generosi e buffer `recv()` grandi (200000+ byte)

### Domande tipo CCNP

1. Quale comando EEM reagisce ad un pattern nel syslog del router?
   - `event syslog pattern "<stringa>"` (risposta: `event syslog pattern`)
2. Un EEM Applet che usa `action cli command "copy run flash:backup.cfg"` può causare un loop
   se l'evento trigger è `SYS-5-CONFIG_I`? Perché no?
   - No: `copy run flash:` NON genera `SYS-5-CONFIG_I` (solo `write mem` e `copy run start` lo fanno)
3. Qual è la differenza tra `json.dump()` e `json.dumps()`?
   - `dump()` scrive su file object; `dumps()` restituisce una stringa
4. Come si isola l'ambiente Python per un singolo progetto?
   - `python3 -m venv .venv` + `source .venv/bin/activate`
5. Quale parametro Paramiko è necessario aumentare quando si lavora con IOU invece di hardware reale?
   - `global_delay_factor` (Netmiko) o `time.sleep()` (Paramiko) — IOU è più lento dell'hardware reale
