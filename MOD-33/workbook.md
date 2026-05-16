# Workbook Studenti — MOD-33: Netmiko & Nornir

**Area:** AREA 13 — AUTOMATION & PROGRAMMABILITY
**Ore:** 2h | **Codici syllabus:** 6.2 · 6.3
**Prerequisito:** MOD-32 (EEM & Python Base) — venv attivo, inventory.json disponibile

---

## 1. TOPOLOGIA

```
          VM GNS3 (192.168.122.1)
          management + script runner
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

| Device | Interfaccia | IP / Mask          | Ruolo        | Note            |
|--------|-------------|--------------------|--------------|-----------------|
| R1     | e0/0.10     | 192.168.122.101/24 | Management   | Core router     |
| R2     | e0/0.10     | 192.168.122.102/24 | Management   | Distribution    |
| R3     | e0/0.10     | 192.168.122.103/24 | Management   | Distribution    |
| R4     | e0/0.10     | 192.168.122.104/24 | Management   | Access          |
| VM GNS3| virbr0      | 192.168.122.1/24   | Script runner| Netmiko/Nornir  |

> OSPF area 0 pre-configurato su tutti i link P2P e Loopback.

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sarà in grado di:

- [ ] Usare Netmiko `ConnectHandler` per aprire sessioni SSH su dispositivi IOS
- [ ] Inviare comandi (`send_command`) e configurazioni (`send_config_set`) con Netmiko
- [ ] Gestire eccezioni Netmiko (`NetmikoTimeoutException`, `AuthenticationException`)
- [ ] Inizializzare Nornir con un inventory YAML e ispezionare hosts e gruppi
- [ ] Eseguire task paralleli su tutti gli host con `nr.run()` e `netmiko_send_command`
- [ ] Filtrare host con `F()` e applicare task su sottoinsiemi dell'inventory
- [ ] Descrivere le differenze tra Netmiko (connessione singola) e Nornir (framework multi-host)

**Codici syllabus coperti:** 6.2 (Python scripting) · 6.3 (network automation tools)

---

## 3. LAB SETUP

### 3.1 Caricamento configurazioni router

```
R1# copy tftp://192.168.122.1/ENCOR/MOD-33/r1-cfg running-config
R2# copy tftp://192.168.122.1/ENCOR/MOD-33/r2-cfg running-config
R3# copy tftp://192.168.122.1/ENCOR/MOD-33/r3-cfg running-config
R4# copy tftp://192.168.122.1/ENCOR/MOD-33/r4-cfg running-config

! Su ogni router, rigenera le chiavi RSA per SSH:
Rx(config)# crypto key generate rsa modulus 1024
```

### 3.2 Setup ambiente

```bash
# Attiva il venv (se non già attivo dal MOD-32)
cd ~/ENCOR-MOD33
source .venv/bin/activate

# Installa le dipendenze aggiuntive
pip install netmiko nornir nornir-netmiko nornir-utils

# Verifica struttura repo
ls scripts/
# b2_netmiko_scheletro.py  b3_nornir_scheletro.py
ls nornir/
# config.yaml  hosts.yaml  groups.yaml  defaults.yaml
```

### 3.3 Prerequisiti

- SSH abilitato su tutti i router (RSA key generata)
- `inventory.json` dalla sessione MOD-32 disponibile in `~/ENCOR-MOD33/`
- Python 3.8+ con venv attivo

### 3.4 Verifica pre-lab

```bash
# Test SSH manuale verso R1
ssh admin@192.168.122.101
# Password: cisco123 — deve funzionare senza errori

# Test Netmiko installato
python3 -c "from netmiko import ConnectHandler; print('Netmiko OK')"

# Test Nornir installato
python3 -c "from nornir import InitNornir; print('Nornir OK')"
```

---

## 4. TASK LIST

| #    | Task                                        | Codice | Tempo  |
|------|---------------------------------------------|--------|--------|
| N.1  | ConnectHandler — connessione a R1           | 6.2    | 15 min |
| N.2  | send_config_set — push configurazione R1    | 6.2    | 10 min |
| N.3  | Loop multi-device — raccolta dati R1-R4     | 6.2    | 15 min |
| N.4  | Exception handling Netmiko                  | 6.2    | 10 min |
| NR.1 | InitNornir — inventory YAML R1-R4           | 6.3    | 15 min |
| NR.2 | Task parallelo — show ip ospf neighbor      | 6.3    | 10 min |
| NR.3 | Filtro F() — task su sottoinsieme           | 6.3    | 10 min |
| NR.4 | send_configs — push NTP + verifica          | 6.3    | 15 min |

---

## 5. DETTAGLIO TASK

---

### TASK N.1 — ConnectHandler: connessione a R1

#### TEORIA — Netmiko: architettura

Netmiko è una libreria Python che **astrae SSH verso dispositivi di rete**.
Il driver `cisco_ios` gestisce automaticamente:
- Il banner di login
- La paginazione dell'output (`--More--` disabilitato con `terminal length 0`)
- Il timing di risposta
- La modalità enable (tramite `secret`)

```
ConnectHandler(**params)
    |
    +-- connect() SSH
    |
    +-- send_command('show ...')   → output come stringa
    |
    +-- send_config_set([...])     → invia lista comandi in config mode
    |
    +-- disconnect()
```

**Parametro `global_delay_factor`:** moltiplica tutti i timeout interni.
Su IOU (più lento dell'hardware reale) impostare a `2` o `3`.

#### TASK

Apri `scripts/b2_netmiko_scheletro.py` e completa i punti `# TODO`:

```python
from netmiko import ConnectHandler

r1 = {
    'device_type': '___________',    # TODO: cisco_ios
    'host'       : '192.168.122.101',
    'username'   : 'admin',
    'password'   : 'cisco123',
    'secret'     : 'cisco123',
    'global_delay_factor': 2,
}

conn = ConnectHandler(**r1)
conn._______()                       # TODO: entra in enable mode

output = conn.send_command('_____________')  # TODO: show ip ospf neighbor
print(output)

conn.disconnect()
```

Esegui:

```bash
python3 scripts/b2_netmiko_scheletro.py
```

#### VERIFICA

```
Neighbor ID     Pri  State   Dead Time   Address         Interface
2.2.2.2           1  FULL/DR   00:00:38  10.0.12.2      Ethernet0/0.12
3.3.3.3           1  FULL/DR   00:00:38  10.0.13.2      Ethernet0/0.13
```

---

### TASK N.2 — send_config_set: push configurazione

#### TEORIA — send_command vs send_config_set

| Metodo | Modalità | Uso |
|--------|----------|-----|
| `send_command('show ...')` | Enable (`#`) | Comandi show, ping, trace |
| `send_config_set([...])` | Config (`(config)#`) | Lista di comandi di configurazione |

`send_config_set()` esegue automaticamente `configure terminal` prima dei comandi
e `end` dopo — non serve specificarli nella lista.

#### TASK

Connettiti a R1 e applica la configurazione seguente via `send_config_set`:

```python
from netmiko import ConnectHandler

r1 = {
    'device_type': 'cisco_ios',
    'host': '192.168.122.101',
    'username': 'admin',
    'password': 'cisco123',
    'secret': 'cisco123',
    'global_delay_factor': 2,
}

conn = ConnectHandler(**r1)
conn.enable()

# Lista dei comandi da inviare in config mode
config_cmds = [
    'interface Loopback99',
    'description NETMIKO-TEST',
    'ip address 99.99.99.99 255.255.255.255',
    'no shutdown',
]

output = conn.send_config_set(_________)    # TODO: passa la lista
print(output)

# Verifica: leggi la running-config dell'interfaccia appena creata
verifica = conn.send_command('show interface Loopback99')
print(verifica)

conn.disconnect()
```

#### VERIFICA

```
configure terminal
Enter configuration commands, one per line.  End with CNTL/Z.
R1(config)#interface Loopback99
R1(config-if)#description NETMIKO-TEST
...
R1(config-if)#end

! show interface Loopback99
Loopback99 is up, line protocol is up
  Description: NETMIKO-TEST
  Internet address is 99.99.99.99/32
```

---

### TASK N.3 — Loop multi-device

#### TEORIA — Pattern dizionario DEFAULTS + unpacking

Per evitare ripetizioni, si usa un dizionario con i parametri comuni e si unisce
con quelli specifici del device tramite `**` (dict unpacking):

```python
DEFAULTS = {
    'device_type'        : 'cisco_ios',
    'secret'             : 'cisco123',
    'global_delay_factor': 2,
}

for device in inventory['devices']:
    params = {
        **DEFAULTS,          # espande il dizionario DEFAULTS
        'host'    : device['ip'],
        'username': device['username'],
        'password': device['password'],
    }
    conn = ConnectHandler(**params)
```

#### TASK

Completa `scripts/b2_netmiko_loop.py`:

```python
import json, re
from netmiko import ConnectHandler

with open('inventory.json', 'r') as f:
    inventory = json.load(f)

NETMIKO_DEFAULTS = {
    'device_type'        : 'cisco_ios',
    'secret'             : 'cisco123',
    'global_delay_factor': 2,
}

risultati = {}

for device in inventory['devices']:
    hostname = device['hostname']
    params = {
        **NETMIKO_DEFAULTS,
        'host'    : device['___'],      # TODO: IP del device
        'username': device['___'],      # TODO: username
        'password': device['___'],      # TODO: password
    }

    conn = ConnectHandler(**params)
    conn.enable()

    ospf_out = conn.send_command('show ip ospf neighbor')

    # Conta le righe che iniziano con un indirizzo IP (neighbor attivi)
    neighbor_count = len([
        l for l in ospf_out.splitlines()
        if re.match(r'\s*\d+\.\d+\.\d+\.\d+', l)
    ])

    risultati[hostname] = {
        'hostname'       : hostname,
        'ip'             : device['ip'],
        'ospf_neighbors' : neighbor_count,
    }

    print(f"{hostname} | OSPF neighbor count: {neighbor_count}")
    conn.disconnect()
```

#### VERIFICA

```
R1 | OSPF neighbor count: 2
R2 | OSPF neighbor count: 2
R3 | OSPF neighbor count: 2
R4 | OSPF neighbor count: 2
```

---

### TASK N.4 — Exception handling

#### TEORIA — Eccezioni Netmiko

| Eccezione | Causa | Quando si presenta |
|-----------|-------|--------------------|
| `NetmikoTimeoutException` | SSH irraggiungibile o timeout | Device spento, IP errato, firewall |
| `NetmikoAuthenticationException` | Credenziali errate | Username/password/secret errati |
| `NetmikoPatternNotFoundException` | Pattern atteso non trovato | Timeout IOU, delay_factor troppo basso |

#### TASK

```python
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

# Device con IP non esistente — per testare il timeout
device_inesistente = {
    'device_type': 'cisco_ios',
    'host'       : '192.168.122.200',   # IP non raggiungibile
    'username'   : 'admin',
    'password'   : 'cisco123',
    'secret'     : 'cisco123',
    'timeout'    : 5,                    # 5 secondi di timeout
}

try:
    conn = ConnectHandler(**device_inesistente)
    conn.enable()
    print(conn.send_command('show version'))
    conn.disconnect()

except _____________________________ as e:    # TODO: eccezione timeout
    print(f"TIMEOUT: {e}")

except _____________________________ as e:    # TODO: eccezione autenticazione
    print(f"AUTH FAIL: {e}")

except Exception as e:
    print(f"Errore generico: {type(e).__name__}: {e}")
```

#### VERIFICA

```
TIMEOUT: TCP connection to device failed. ...
! Atteso: NetmikoTimeoutException dopo 5 secondi

! Per testare AuthenticationException: usare IP valido ma password sbagliata
```

---

### TASK NR.1 — InitNornir e inventory YAML

#### TEORIA — Architettura Nornir

Nornir è un **framework Python di automazione di rete** con esecuzione parallela nativa.
A differenza di Ansible, tutto rimane in Python: nessun YAML di playbook,
piena libertà di logica condizionale, cicli, gestione errori.

**Struttura inventory Nornir:**

```
nornir/
├── config.yaml        ← punta ai file dell'inventory
├── hosts.yaml         ← definizione dei singoli host
├── groups.yaml        ← attributi condivisi per gruppo
└── defaults.yaml      ← valori di default (username, password, ecc.)
```

Esempio `hosts.yaml`:

```yaml
R1:
  hostname: 192.168.122.101
  groups:
    - ios_routers
  data:
    location: Core
    loopback: 1.1.1.1

R2:
  hostname: 192.168.122.102
  groups:
    - ios_routers
  data:
    location: Distribution
    loopback: 2.2.2.2
```

Esempio `groups.yaml`:

```yaml
ios_routers:
  platform: ios
  connection_options:
    netmiko:
      extras:
        secret: cisco123
        global_delay_factor: 2
```

Esempio `defaults.yaml`:

```yaml
username: admin
password: cisco123
```

#### TASK

Completa `nornir/hosts.yaml` con R3 e R4 (R1 e R2 sono già presenti come esempio).
Poi esegui:

```python
from nornir import InitNornir

nr = InitNornir(config_file='nornir/config.yaml')

# Ispeziona inventory
print(f"Host nell'inventory: {len(nr.inventory.hosts)}")

for nome, host in nr.inventory.hosts.items():
    print(
        f"{nome} | {host.hostname} | "
        f"location={host.data.get('location', '?')} | "
        f"gruppi={[g.name for g in host.groups]}"
    )

print(f"Gruppi disponibili: {list(nr.inventory.groups.keys())}")
```

#### VERIFICA

```
Host nell'inventory: 4
R1 | 192.168.122.101 | location=Core         | gruppi=['ios_routers']
R2 | 192.168.122.102 | location=Distribution | gruppi=['ios_routers']
R3 | 192.168.122.103 | location=Distribution | gruppi=['ios_routers']
R4 | 192.168.122.104 | location=Access       | gruppi=['ios_routers']
Gruppi disponibili: ['ios_routers']
```

---

### TASK NR.2 — Task parallelo: show ip ospf neighbor

#### TEORIA — nr.run() e AggregatedResult

`nr.run(task=funzione, **kwargs)` esegue il task su **tutti gli host in parallelo**
(numero di worker configurato in `config.yaml`, default 20).

Ritorna un oggetto `AggregatedResult`:
- Comportamento dict: `result['R1']` → `MultiResult` (lista di `Result`)
- `result['R1'].result` → output del task
- `result.failed_hosts` → dict degli host falliti

```python
result = nr.run(task=netmiko_send_command, command_string='show clock')
for host, task_result in result.items():
    if not task_result.failed:
        print(f"[{host}] {task_result.result.strip()}")
```

#### TASK

```python
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file='nornir/config.yaml')

# Esegui show ip ospf neighbor su tutti gli host in parallelo
result = nr.run(
    task=_______________,               # TODO: funzione netmiko_send_command
    command_string='_______________',   # TODO: show ip ospf neighbor
)

# Stampa l'output formattato
print_result(result)

# Accesso programmatico: stampa solo il numero di righe per host
for host, task_result in result.items():
    if not task_result.failed:
        righe = [
            l for l in task_result.result.splitlines()
            if l.strip().startswith(tuple('0123456789'))
        ]
        print(f"{host}: {len(righe)} neighbor OSPF")

# Verifica errori
if result.failed_hosts:
    print(f"HOST FALLITI: {list(result.failed_hosts.keys())}")
else:
    print("Tutti gli host hanno risposto.")
```

#### VERIFICA

```
vvvv show ip ospf neighbor ** changed : False vvvvvvvvvvvvv
---- R1 ** changed : False -------------------------
Neighbor ID     Pri  State ...
2.2.2.2           1  FULL/DR ...
3.3.3.3           1  FULL/DR ...
---- R2 ...
...

R1: 2 neighbor OSPF
R2: 2 neighbor OSPF
R3: 2 neighbor OSPF
R4: 2 neighbor OSPF
Tutti gli host hanno risposto.
```

---

### TASK NR.3 — Filtro F(): task su sottoinsieme

#### TEORIA — F() e attributi host.data

`F()` permette di filtrare l'inventory per attributi degli host.
Si usa **doppio underscore** (`__`) per navigare all'interno di `host.data`:

```python
from nornir.core.filter import F

# Filtra per host.data['location'] == 'Distribution'
nr_dist = nr.filter(F(data__location='Distribution'))

# Altri esempi:
nr.filter(F(name='R1') | F(name='R4'))          # R1 OR R4
nr.filter(F(hostname__contains='192.168.122'))   # hostname contiene stringa
nr.filter(F(groups__contains='ios_routers'))     # appartenenza a gruppo
```

> **Attenzione:** `F()` è **case-sensitive**. `'distribution'` != `'Distribution'`.

#### TASK

```python
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file='nornir/config.yaml')

# Filtra solo i router con location='Distribution' (R2 e R3)
nr_dist = nr.filter(F(data__location='___________'))    # TODO

# Stampa la lista degli host filtrati
print("Host filtrati:", list(nr_dist.inventory.hosts.keys()))

# Esegui show clock solo su R2 e R3
result = nr_dist.run(
    task=netmiko_send_command,
    command_string='show clock',
)
print_result(result)
```

#### VERIFICA

```
Host filtrati: ['R2', 'R3']

vvvv show clock ** changed : False vvvvvvvvvvvvv
---- R2 ** changed : False -------------------------
*12:34:56.789 UTC Thu May 14 2026
---- R3 ** changed : False -------------------------
*12:34:56.801 UTC Thu May 14 2026
```

---

### TASK NR.4 — send_configs: push NTP su tutti i router

#### TEORIA — Idempotency con Nornir

Nornir non è intrinsecamente idempotente: se invii due volte `ntp server 192.168.122.1`,
IOS accetta il secondo comando senza errore (la config è già presente).
Per idempotency vera è necessario verificare lo stato attuale prima di applicare
(pattern check-before-push — implementabile con `nr.run()` di `show` + logica condizionale).

#### TASK

```python
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file='nornir/config.yaml')

# 1. Push configurazione NTP su tutti i router
config_commands = [
    'ntp server 192.168.122.1',
    'ntp update-calendar',
]

result_cfg = nr.run(
    task=netmiko_send_config,
    config_commands=config_commands,
)
print_result(result_cfg)

# 2. Verifica: show running-config | include ntp
result_verifica = nr.run(
    task=netmiko_send_command,
    command_string='show running-config | include ntp',
)
print_result(result_verifica)

# 3. Stampa riepilogo
for host, task_result in result_verifica.items():
    if not task_result.failed:
        print(f"{host}: {task_result.result.strip()}")
```

#### VERIFICA

```
! result_cfg: nessun errore su tutti gli host

! result_verifica — per ogni host:
R1: ntp server 192.168.122.1
    ntp update-calendar
R2: ntp server 192.168.122.1
    ntp update-calendar
R3: ntp server 192.168.122.1
    ntp update-calendar
R4: ntp server 192.168.122.1
    ntp update-calendar
```

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa probabile | Diagnosi | Fix |
|---------|----------------|----------|-----|
| `NetmikoTimeoutException` | SSH irraggiungibile | `ssh admin@IP` manuale | Verificare IP, `transport input ssh`, chiavi RSA generate |
| `NetmikoAuthenticationException` | Credenziali errate | Test manuale SSH | Controllare `username`/`password`/`secret` in inventory.json |
| Output troncato (paging) | `--More--` interrompe | Aumentare `global_delay_factor` | Impostare a 2-3; Netmiko chiama `terminal length 0` automaticamente |
| `Pattern error` su IOU | IOU è più lento | `global_delay_factor=1` | Aumentare a `global_delay_factor=2` o `3` |
| Nornir: `F()` non filtra | Campo non in `host.data` | Stampare `host.data` di ogni host | Verificare che il campo sia definito in `hosts.yaml` sotto `data:` |
| Nornir: `result.failed_hosts` non vuoto | Timeout o autenticazione | `print_result(result)` | Correggere il device nell'inventory o verificare connettività |
| `InitNornir` errore YAML | Indentazione errata in hosts.yaml | `python3 -c "import yaml; yaml.safe_load(open('nornir/hosts.yaml'))"` | Correggere l'indentazione (YAML è case-sensitive e indentation-sensitive) |
| Nornir: task blocca tutto | Un host non risponde | Usare `raise_on_error=False` in `nr.run()` | `nr.run(..., raise_on_error=False)` — processa tutti gli host |
| `send_config_set` non applica | Non sei in enable mode | Il prompt non è `(config)#` | Verificare `conn.enable()` prima di `send_config_set()` |

---

## 7. SOLUZIONI

> Le soluzioni complete si trovano in `MOD-33/soluzione.md`.
> Non consultare prima di aver tentato i task autonomamente.

---

## 8. RIEPILOGO & EXAM TIPS

### Punti chiave

1. **Netmiko** = libreria Python per SSH verso dispositivi di rete; `device_type='cisco_ios'` identifica il driver; `global_delay_factor` gestisce la lentezza di IOU
2. **`send_command`** esegue comandi show in enable mode; **`send_config_set`** invia una lista di comandi in config mode (gestisce automaticamente `conf t` e `end`)
3. **Nornir** = framework Python multi-host con esecuzione parallela nativa; l'inventory è in YAML (`hosts.yaml`, `groups.yaml`, `defaults.yaml`)
4. **`nr.run()`** ritorna un `AggregatedResult`: dict-like con un `Result` per host; `result.failed_hosts` contiene gli host che hanno fallito
5. **`F()`** filtra l'inventory per attributi: `F(data__location='X')` usa `data__` per navigare in `host.data`

### Domande tipo CCNP

1. Quale parametro Netmiko si usa per gestire la lentezza di dispositivi virtuali come IOU?
   - `global_delay_factor` (valore consigliato: 2 su IOU)
2. Qual è la differenza tra `send_command()` e `send_config_set()` in Netmiko?
   - `send_command()` esegue un comando in enable mode; `send_config_set()` invia una lista di comandi in config mode
3. In Nornir, come si accede al risultato di un task per un singolo host?
   - `result['R1'].result` (dove `result` è l'`AggregatedResult` ritornato da `nr.run()`)
4. Come si filtrano gli host Nornir per un attributo custom definito in `hosts.yaml`?
   - `nr.filter(F(data__nome_campo='valore'))` — doppio underscore per navigare in `host.data`
5. Netmiko e Nornir: quale dei due è più adatto per automazione su una flotta di 100 router?
   - Nornir — esecuzione parallela nativa, inventory strutturato, gestione errori centralizzata
