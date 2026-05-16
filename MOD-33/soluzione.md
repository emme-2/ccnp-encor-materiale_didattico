# Soluzione Commentata — MOD-33: Netmiko & Nornir

> **INSTRUCTOR COPY — Non distribuire agli studenti**
> Codici syllabus: 6.2 · 6.3

---

## SOLUZIONE N.1 — ConnectHandler: connessione a R1

```python
from netmiko import ConnectHandler

r1 = {
    'device_type'        : 'cisco_ios',  # identifica il driver/parser Netmiko
    'host'               : '192.168.122.101',
    'username'           : 'admin',
    'password'           : 'cisco123',
    'secret'             : 'cisco123',   # enable password
    'global_delay_factor': 2,            # IOU è lento: moltiplica tutti i timeout
}

# ** unpacking del dizionario → ConnectHandler(device_type='cisco_ios', host=..., ...)
conn = ConnectHandler(**r1)
conn.enable()   # entra in modalità privilegiata (#)

output = conn.send_command('show ip ospf neighbor')
print(output)

conn.disconnect()
```

**Nota docente:** `global_delay_factor=2` è il parametro più critico su IOU.
Senza di esso, Netmiko legge l'output prima che IOU abbia finito di scriverlo
→ output troncato o vuoto. Su hardware reale: `global_delay_factor=1` (default).

---

## SOLUZIONE N.2 — send_config_set

```python
from netmiko import ConnectHandler

conn = ConnectHandler(
    device_type        = 'cisco_ios',
    host               = '192.168.122.101',
    username           = 'admin',
    password           = 'cisco123',
    secret             = 'cisco123',
    global_delay_factor= 2,
)
conn.enable()

config_cmds = [
    'interface Loopback99',
    'description NETMIKO-TEST',
    'ip address 99.99.99.99 255.255.255.255',
    'no shutdown',
]

# send_config_set() esegue automaticamente:
# conf t → [comandi] → end
# NON includere 'configure terminal' o 'end' nella lista
output = conn.send_config_set(config_cmds)
print(output)

verifica = conn.send_command('show interface Loopback99')
print(verifica)

conn.disconnect()
```

**Nota docente:** Chiedere agli studenti di confrontare `send_command` vs `send_config_set`.
L'errore comune è includere `configure terminal` nella lista — Netmiko lo aggiunge già.

---

## SOLUZIONE N.3 — Loop multi-device

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

    # Merge tramite ** unpacking: i campi specifici sovrascrivono i DEFAULTS
    params = {
        **NETMIKO_DEFAULTS,
        'host'    : device['ip'],
        'username': device['username'],
        'password': device['password'],
    }

    conn = ConnectHandler(**params)
    conn.enable()

    ospf_out = conn.send_command('show ip ospf neighbor')

    # Conta le righe che iniziano con indirizzo IP (neighbor attivi)
    neighbor_count = len([
        l for l in ospf_out.splitlines()
        if re.match(r'\s*\d+\.\d+\.\d+\.\d+', l)
    ])

    risultati[hostname] = {
        'hostname'      : hostname,
        'ip'            : device['ip'],
        'ospf_neighbors': neighbor_count,
    }

    print(f"{hostname} | OSPF neighbor count: {neighbor_count}")
    conn.disconnect()
```

**Nota docente:** Il pattern regex `r'\s*\d+\.\d+\.\d+\.\d+'` matcha le righe
che iniziano con un indirizzo IP — le righe di header (`Neighbor ID`, `Dead Time`, ecc.)
non matchano e vengono escluse automaticamente.

---

## SOLUZIONE N.4 — Exception handling

```python
from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

device_inesistente = {
    'device_type': 'cisco_ios',
    'host'       : '192.168.122.200',
    'username'   : 'admin',
    'password'   : 'cisco123',
    'secret'     : 'cisco123',
    'timeout'    : 5,
}

try:
    conn = ConnectHandler(**device_inesistente)
    conn.enable()
    print(conn.send_command('show version'))
    conn.disconnect()

except NetmikoTimeoutException as e:
    # TCP connection failed: device non raggiungibile
    print(f"TIMEOUT: {e}")

except NetmikoAuthenticationException as e:
    # SSH aperto ma credenziali errate
    print(f"AUTH FAIL: {e}")

except Exception as e:
    # Catch-all per altri errori (YAML malformato, import error, ecc.)
    print(f"Errore generico: {type(e).__name__}: {e}")
```

**Nota docente:** Per testare `AuthenticationException`, usare IP valido (es. 192.168.122.101)
con password sbagliata. Per testare `TimeoutException`, usare IP non raggiungibile con `timeout=5`.

---

## SOLUZIONE NR.1 — hosts.yaml completo

```yaml
# nornir/hosts.yaml
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

R3:
  hostname: 192.168.122.103
  groups:
    - ios_routers
  data:
    location: Distribution
    loopback: 3.3.3.3

R4:
  hostname: 192.168.122.104
  groups:
    - ios_routers
  data:
    location: Access
    loopback: 4.4.4.4
```

```yaml
# nornir/groups.yaml
ios_routers:
  platform: ios
  connection_options:
    netmiko:
      extras:
        secret: cisco123
        global_delay_factor: 2
```

```yaml
# nornir/defaults.yaml
username: admin
password: cisco123
```

```yaml
# nornir/config.yaml
runner:
  plugin: threaded
  options:
    num_workers: 4

inventory:
  plugin: SimpleInventory
  options:
    host_file: nornir/hosts.yaml
    group_file: nornir/groups.yaml
    defaults_file: nornir/defaults.yaml
```

```python
# Script di ispezione inventory
from nornir import InitNornir

nr = InitNornir(config_file='nornir/config.yaml')

print(f"Host nell'inventory: {len(nr.inventory.hosts)}")
for nome, host in nr.inventory.hosts.items():
    print(
        f"{nome} | {host.hostname} | "
        f"location={host.data.get('location', '?')} | "
        f"gruppi={[g.name for g in host.groups]}"
    )
print(f"Gruppi disponibili: {list(nr.inventory.groups.keys())}")
```

---

## SOLUZIONE NR.2 — Task parallelo: show ip ospf neighbor

```python
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file='nornir/config.yaml')

# nr.run() esegue il task su TUTTI gli host in parallelo (num_workers=4)
result = nr.run(
    task=netmiko_send_command,
    command_string='show ip ospf neighbor',
)

# print_result formatta l'output con header per host
print_result(result)

# Accesso programmatico
for host, task_result in result.items():
    if not task_result.failed:
        righe_neighbor = [
            l for l in task_result.result.splitlines()
            if l.strip().startswith(tuple('0123456789'))
        ]
        print(f"{host}: {len(righe_neighbor)} neighbor OSPF")

if result.failed_hosts:
    print(f"HOST FALLITI: {list(result.failed_hosts.keys())}")
else:
    print("Tutti gli host hanno risposto.")
```

**Nota docente:** `result.failed_hosts` è la proprietà chiave per capire se ci sono errori.
`print_result()` mostra anche gli errori in rosso — utile per debug rapido in aula.

---

## SOLUZIONE NR.3 — Filtro F()

```python
from nornir import InitNornir
from nornir.core.filter import F
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file='nornir/config.yaml')

# F(data__location='Distribution') filtra per host.data['location'] == 'Distribution'
# Doppio underscore (__) naviga dentro i dizionari annidati
nr_dist = nr.filter(F(data__location='Distribution'))

print("Host filtrati:", list(nr_dist.inventory.hosts.keys()))
# Output: ['R2', 'R3']

result = nr_dist.run(
    task=netmiko_send_command,
    command_string='show clock',
)
print_result(result)
```

**Varianti di filtri per la classe:**
```python
# OR: R1 oppure R4
nr.filter(F(name='R1') | F(name='R4'))

# AND: Distribution E hostname contiene '192.168.122'
nr.filter(F(data__location='Distribution') & F(hostname__contains='192.168'))

# NOT: tutti tranne R1
nr.filter(~F(name='R1'))
```

---

## SOLUZIONE NR.4 — send_configs: push NTP

```python
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file='nornir/config.yaml')

config_commands = [
    'ntp server 192.168.122.1',
    'ntp update-calendar',
]

# netmiko_send_config invia la lista di comandi in config mode su tutti gli host
result_cfg = nr.run(
    task=netmiko_send_config,
    config_commands=config_commands,
)
print_result(result_cfg)

# Verifica: show running-config | include ntp
result_verifica = nr.run(
    task=netmiko_send_command,
    command_string='show running-config | include ntp',
)
print_result(result_verifica)

for host, task_result in result_verifica.items():
    if not task_result.failed:
        print(f"{host}: {task_result.result.strip()}")
```

---

## NOTE DIDATTICHE — Confronto Netmiko vs Nornir

| Aspetto | Netmiko | Nornir 3.x |
|---------|---------|------------|
| Astrazione | Connessione SSH singola | Framework multi-host |
| Parallelismo | Manuale (threading) | Nativo (num_workers) |
| Inventory | Dict Python (manuale) | YAML strutturato |
| Curva apprendimento | Bassa | Media |
| Flessibilità | Alta (Python puro) | Molto alta (plugin system) |
| Caso d'uso ideale | Script semplici, backup | Automazione flotte larghe |

### Quando usare Netmiko invece di Nornir

Netmiko è preferibile quando:
- Lo script è semplice e riguarda 1-5 device
- Non c'è bisogno di inventory strutturato
- Il team non conosce Nornir
- Si vuole integrazione rapida in script esistenti

Nornir è preferibile quando:
- La flotta ha >10 device
- I task devono girare in parallelo (riduzione tempo)
- Serve filtraggio avanzato (per sito, ruolo, piattaforma)
- Il progetto crescerà nel tempo e la struttura inventory è importante
