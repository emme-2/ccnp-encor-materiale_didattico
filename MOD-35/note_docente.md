# Note Docente — MOD-35: API & RESTCONF (TEORIA)

> **Tipo:** Modulo teoria — nessun lab pratico su IOU
> **Ore:** 1.5h | **Codici syllabus:** 6.4 · 6.5
> **Nota:** RESTCONF e NETCONF non disponibili su IOU L3. Richiedono IOS-XE o Catalyst Center.
> Questo modulo è erogato come lezione frontale con esempi curl/Postman sulla VM GNS3.

---

## OUTLINE SLIDE DETTAGLIATO

---

### SLIDE 1 — Cover Module
**Layout:** 01 Cover Module (sfondo nero, titolo arancio, codici avorio)

**Contenuto:**
- Titolo: `MOD-35 — API & RESTCONF`
- Sottotitolo: `REST API · YANG · RESTCONF · DNA Center · NETCONF`
- Codici syllabus: `6.4 · 6.5`
- Ore: `1.5h — Modulo Teoria`

---

### SLIDE 2 — Agenda
**Layout:** 02 Agenda (sfondo avorio, numerazione arancio)

**Contenuto:**
1. REST API: fondamenta (HTTP methods, status codes, JSON/XML)
2. Autenticazione API: Basic Auth, Token, OAuth 2.0
3. Cisco DNA Center API: autenticazione + endpoint dispositivi
4. YANG Data Modeling Language
5. RESTCONF (RFC 8040)
6. NETCONF vs RESTCONF vs SNMP — tabella comparativa
7. Exam Tips & Summary

**Note docente:** Avvisare subito che questo è un modulo di sola teoria.
Il lab pratico su RESTCONF richiede IOS-XE — non disponibile su IOU.
Demo opzionale con curl verso la sandbox dCloud di Cisco.

---

### SLIDE 3 — Section Header
**Layout:** 03 Section Header (sfondo arancio pieno, titolo bianco)

**Testo:** `REST API — Fondamenta`

**Domanda alla classe:** "Chi ha già usato una REST API? In quale contesto?"

---

### SLIDE 4 — HTTP Methods e Status Codes
**Layout:** 04 Teoria Concetto (sfondo avorio, max 5-6 righe)

**Titolo:** `HTTP Methods — Il vocabolario REST`

**Contenuto:**

| Method | Azione su risorsa | Idempotente? | Body richiesta? |
|--------|-------------------|-------------|----------------|
| GET    | Leggi/recupera    | Si          | No             |
| POST   | Crea nuova risorsa | No         | Si             |
| PUT    | Sostituisci intera risorsa | Si | Si            |
| PATCH  | Modifica parziale | Si          | Si             |
| DELETE | Elimina           | Si          | No             |

**Note docente:** Enfatizzare idempotency — GET ripetuto N volte → stesso risultato.
POST ripetuto → potrebbe creare N risorse duplicate.
In RESTCONF: GET = leggi config, PUT = sostituisci, PATCH = modifica parziale.

---

### SLIDE 5 — HTTP Status Codes
**Layout:** 04 Teoria Concetto

**Titolo:** `Status Codes — Risposta del server`

**Contenuto:**

| Codice | Categoria | Esempio |
|--------|-----------|---------|
| 200 OK | Successo | GET riuscito |
| 201 Created | Risorsa creata | POST riuscito |
| 204 No Content | Successo senza body | DELETE riuscito |
| 400 Bad Request | Client error | JSON malformato |
| 401 Unauthorized | Auth mancante | Token assente o scaduto |
| 403 Forbidden | Auth OK ma permesso negato | Ruolo insufficiente |
| 404 Not Found | Risorsa non esiste | Endpoint errato |
| 500 Internal Server Error | Server error | Bug nel server |

**Note docente:** Sottolineare 401 vs 403: entrambi relativi all'autorizzazione
ma significato diverso. Errore comune: usare 403 quando si intende 401.

---

### SLIDE 6 — Diagramma REST API Flow
**Layout:** 05 Diagramma (sfondo bianco/avorio, didascalia sotto)

**Diagramma:**
```
Client (Python / curl / Postman)
        |
        |  HTTP Request
        |  Method: GET
        |  URL: https://api.cisco.com/resource
        |  Headers: Authorization: Bearer <token>
        |           Content-Type: application/json
        |
        v
   [REST API Server]  (DNA Center / IOS-XE / cloud service)
        |
        |  HTTP Response
        |  Status: 200 OK
        |  Body: {"data": [...]}
        |
        v
Client riceve JSON/XML e lo processa
```

**Didascalia:** `Flusso richiesta-risposta REST API — stateless: ogni richiesta contiene tutte le informazioni necessarie`

**Note docente:** Enfatizzare "stateless": il server non mantiene sessione tra le richieste.
Ogni richiesta deve includere le credenziali/token. Contrasto con SNMP che è polling-based.

---

### SLIDE 7 — Section Header
**Layout:** 03 Section Header

**Testo:** `Autenticazione API`

---

### SLIDE 8 — Basic Auth vs Token vs OAuth 2.0
**Layout:** 04 Teoria Concetto

**Titolo:** `Tre metodi di autenticazione REST`

**Contenuto:**

**Basic Auth:**
- Username:password in Base64 nell'header `Authorization`
- `Authorization: Basic YWRtaW46Y2lzY28xMjM=`
- Semplice ma password viaggia (encoded, non encrypted) in ogni richiesta
- Usare solo su HTTPS

**Token-based:**
- Il client ottiene un token con una prima richiesta POST (login)
- Il token viene incluso in tutte le richieste successive
- `Authorization: Bearer <token>`
- Token ha scadenza (es. 60 minuti) — più sicuro di Basic Auth

**OAuth 2.0:**
- Standard industriale per delegare l'accesso
- Il client ottiene un `access_token` tramite Authorization Code o Client Credentials flow
- Usato da Cisco DNA Center, piattaforme cloud, API di terze parti

**Note docente:** DNA Center usa Token-based (POST su `/auth/token` con Basic Auth iniziale,
poi tutte le chiamate successive usano il token ottenuto).

---

### SLIDE 9 — Config/Comando: esempio curl Basic Auth
**Layout:** 06 Config/Comando (sfondo nero, monospace bianco, highlight giallo)

**Titolo:** `Esempio: Token DNA Center con curl`

```bash
# Passo 1: ottieni il token (Basic Auth: admin:cisco123 in Base64)
curl -X POST https://dnac.company.com/dna/system/api/v1/auth/token \
     -H "Content-Type: application/json" \
     -u admin:cisco123 \
     --insecure

# Risposta:
# {"Token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."}

# Passo 2: usa il token per le chiamate successive
curl -X GET https://dnac.company.com/dna/intent/api/v1/network-device \
     -H "x-auth-token: eyJhbGciOiJSUzI1NiIs..." \
     -H "Content-Type: application/json" \
     --insecure
```

**Highlight giallo:** `x-auth-token: <valore_token>`

**Note docente:** DNA Center usa l'header `x-auth-token` (non `Authorization: Bearer`).
Questo è un dettaglio che compare spesso nelle domande d'esame.
`--insecure` = skip verifica certificato SSL (solo per lab).

---

### SLIDE 10 — Section Header
**Layout:** 03 Section Header

**Testo:** `YANG — Data Modeling Language`

---

### SLIDE 11 — YANG: cos'è e a cosa serve
**Layout:** 04 Teoria Concetto

**Titolo:** `YANG — Yet Another Next Generation`

**Contenuto:**

YANG (RFC 6020, RFC 7950) è un **linguaggio di modellazione dati** per dispositivi di rete.
Definisce la struttura, i tipi e i vincoli dei dati di configurazione e stato.

**Componenti YANG:**

| Costrutto | Descrizione | Esempio |
|-----------|-------------|---------|
| `module` | Unità di modello (file .yang) | `ietf-interfaces`, `cisco-ios-xe-native` |
| `container` | Raggruppamento di nodi (non lista) | `interface { ... }` |
| `list` | Lista di elementi con chiave | `interface[name='GigabitEthernet1']` |
| `leaf` | Valore singolo (stringa, int, bool) | `description "uplink"` |
| `leaf-list` | Lista di valori scalari | `ip address [...]` |

**Relazione YANG → RESTCONF:**
- YANG definisce **il modello** (struttura dati)
- RESTCONF fornisce **il trasporto** (HTTP) per leggere/modificare quei dati
- NETCONF fornisce **il trasporto alternativo** (SSH/XML)

**Note docente:** Analogia utile: YANG è lo schema di un database,
RESTCONF/NETCONF sono le API per leggere e scrivere su quel database.

---

### SLIDE 12 — Diagramma YANG tree
**Layout:** 05 Diagramma

**Titolo:** `Struttura dati YANG — esempio interfaccia`

```
module: ietf-interfaces
  +--rw interfaces
     +--rw interface* [name]              ← list (chiave: name)
        +--rw name                string  ← leaf
        +--rw description?        string  ← leaf (opzionale)
        +--rw type                identityref
        +--rw enabled?            boolean
        +--ro oper-status         enumeration ← read-only (stato)
        +--rw ipv4
           +--rw address* [ip]
              +--rw ip             inet:ipv4-address
              +--rw prefix-length  uint8
```

**Didascalia:** `Albero YANG — +--rw = read-write (config) · +--ro = read-only (stato operativo)`

**Note docente:** Far notare la distinzione `rw` (config) vs `ro` (stato).
RESTCONF rispetta questa distinzione con path `/data/` (config) vs `/data/...?content=all`.

---

### SLIDE 13 — Section Header
**Layout:** 03 Section Header

**Testo:** `RESTCONF — RFC 8040`

---

### SLIDE 14 — RESTCONF: architettura e URL
**Layout:** 04 Teoria Concetto

**Titolo:** `RESTCONF — REST su YANG`

**Contenuto:**

RESTCONF (RFC 8040) espone i dati YANG tramite HTTP/HTTPS.

**Struttura URL RESTCONF:**
```
https://<device>/restconf/data/<yang-module>:<container>/<list>[key=value]
```

**Esempi:**
```
# Leggi tutte le interfacce
GET /restconf/data/ietf-interfaces:interfaces

# Leggi una singola interfaccia
GET /restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1

# Modifica la descrizione (PATCH = modifica parziale)
PATCH /restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1
Body: {"ietf-interfaces:interface": [{"name": "GigabitEthernet1", "description": "UPLINK"}]}

# Leggi running-config Cisco IOS-XE nativa
GET /restconf/data/Cisco-IOS-XE-native:native
```

**Header richiesti:**
- `Accept: application/yang-data+json` (risposta in JSON)
- `Content-Type: application/yang-data+json` (body in JSON)
- `Authorization: Basic <base64>` o `X-Auth-Token: <token>`

**Note docente — Vincolo IOU:** RESTCONF richiede IOS-XE (GigabitEthernet, non Ethernet0/0).
Su IOU non è disponibile. Per demo: usare DevNet Sandbox o Always-On IOS-XE su DevNet.

---

### SLIDE 15 — Config/Comando: RESTCONF con Python
**Layout:** 06 Config/Comando (sfondo nero, monospace bianco)

**Titolo:** `RESTCONF con Python — esempio IOS-XE`

```python
import requests
import json

# IOS-XE sandbox (DevNet Always-On)
HOST     = "sandbox-iosxe-latest-1.cisco.com"
USER     = "admin"
PASSWORD = "C1sco12345"

# Headers per RESTCONF JSON
HEADERS = {
    "Accept"       : "application/yang-data+json",
    "Content-Type" : "application/yang-data+json",
}

# GET: leggi tutte le interfacce
url = f"https://{HOST}/restconf/data/ietf-interfaces:interfaces"
response = requests.get(url, auth=(USER, PASSWORD),
                        headers=HEADERS, verify=False)

print(f"Status: {response.status_code}")
data = response.json()
interfacce = data["ietf-interfaces:interfaces"]["interface"]
for intf in interfacce:
    print(f"  {intf['name']}: {intf.get('description', 'N/A')}")
```

**Highlight giallo:** `"Accept": "application/yang-data+json"`

**Note docente:** Mostrare l'output reale se si ha accesso alla DevNet sandbox.
Alternativa: mostrare uno screenshot pre-catturato dell'output JSON.

---

### SLIDE 16 — Section Header
**Layout:** 03 Section Header

**Testo:** `NETCONF vs RESTCONF vs SNMP`

---

### SLIDE 17 — Tabella comparativa
**Layout:** 08 Troubleshooting (tabella 2 col adattata a 6 col)

**Titolo:** `Confronto protocolli di gestione di rete`

| Caratteristica | SNMP | NETCONF | RESTCONF |
|----------------|------|---------|----------|
| RFC | RFC 1157/3411 | RFC 6241 | RFC 8040 |
| Trasporto | UDP/161 | SSH/TCP 830 | HTTPS/443 |
| Modello dati | MIB (OID) | YANG | YANG |
| Encoding | ASN.1/BER | XML | JSON o XML |
| Operazioni | Get, Set, Trap | `<get>`, `<edit-config>`, `<commit>` | GET/PUT/PATCH/DELETE |
| Transazioni | No | Si (commit/rollback) | No (parziale) |
| Read/Write | Limitato | Completo | Completo |
| Supporto IOU | Si (SNMPv2c) | No | No |
| Supporto IOS-XE | Si | Si | Si |

**Note docente:** SNMP è "il passato" — ancora usato per monitoring legacy.
NETCONF è "il presente" enterprise — transazioni atomiche, rollback.
RESTCONF è "il futuro API-first" — più semplice da usare con Python/curl.

---

### SLIDE 18 — Cisco DNA Center API
**Layout:** 04 Teoria Concetto

**Titolo:** `Cisco DNA Center (Catalyst Center) API`

**Contenuto:**

DNA Center espone REST API per:
- Scoperta e inventory dispositivi
- Provisioning automatizzato
- Assurance e telemetria
- Intento di rete (Intent API)

**Endpoint principali:**

| Endpoint | Method | Descrizione |
|----------|--------|-------------|
| `/dna/system/api/v1/auth/token` | POST | Ottieni token di autenticazione |
| `/dna/intent/api/v1/network-device` | GET | Lista tutti i dispositivi |
| `/dna/intent/api/v1/network-device/{id}` | GET | Dettagli singolo dispositivo |
| `/dna/intent/api/v1/topology/physical-topology` | GET | Topologia fisica |
| `/dna/intent/api/v1/site` | GET | Struttura siti |

**Autenticazione DNA Center:**
1. POST su `/auth/token` con `Authorization: Basic <base64(user:pass)>`
2. Server risponde con `{"Token": "<jwt_token>"}`
3. Tutte le chiamate successive: header `x-auth-token: <jwt_token>`

**Note docente:** Sottolineare che DNA Center usa `x-auth-token` (non `Authorization: Bearer`).
I token JWT hanno scadenza — in produzione gestire il refresh automatico.

---

### SLIDE 19 — Config/Comando: DNA Center API con Python
**Layout:** 06 Config/Comando (sfondo nero, monospace bianco, highlight giallo)

**Titolo:** `DNA Center API — Script Python completo`

```python
import requests, json

DNAC_HOST = "sandboxdnac.cisco.com"
USERNAME  = "devnetuser"
PASSWORD  = "Cisco123!"

# Step 1: Autenticazione — ottieni token
auth_url = f"https://{DNAC_HOST}/dna/system/api/v1/auth/token"
resp = requests.post(auth_url, auth=(USERNAME, PASSWORD), verify=False)
token = resp.json()["Token"]
print(f"Token: {token[:30]}...")

# Step 2: Lista dispositivi
headers  = {"x-auth-token": token, "Content-Type": "application/json"}
dev_url  = f"https://{DNAC_HOST}/dna/intent/api/v1/network-device"
devices  = requests.get(dev_url, headers=headers, verify=False)

for device in devices.json()["response"]:
    print(f"{device['hostname']:20s} {device['platformId']:15s} {device['softwareVersion']}")
```

**Highlight giallo:** `"x-auth-token": token`

**Note docente:** DevNet Sandbox DNA Center: `sandboxdnac.cisco.com`.
Credenziali: `devnetuser` / `Cisco123!`. Verificare disponibilità prima della lezione.

---

### SLIDE 20 — Exam Tips
**Layout:** 09 Exam Tips (sfondo giallo, bullet nero)

**Titolo:** `Exam Tips — API & RESTCONF`

**Bullet:**
- **RESTCONF usa HTTP methods**: GET = leggi, PUT = sostituisci, PATCH = modifica parziale, DELETE = cancella
- **YANG** definisce la struttura dati; RESTCONF/NETCONF sono il trasporto
- **DNA Center**: autenticazione con POST `/auth/token` → token in `x-auth-token` (NON `Authorization: Bearer`)
- **NETCONF usa XML su SSH porta 830**; RESTCONF usa JSON/XML su HTTPS porta 443
- **NETCONF supporta transazioni** (commit/rollback atomico); RESTCONF no
- **SNMP**: ancora rilevante per monitoring legacy; usa MIB/OID, non YANG
- **Su IOU**: RESTCONF/NETCONF non disponibili — richiedono IOS-XE reale o DevNet Sandbox

**Note docente:** Le domande d'esame ENCOR su questa sezione sono principalmente
a risposta multipla concettuale — non richiedono di scrivere codice.
Enfatizzare le differenze NETCONF vs RESTCONF vs SNMP (tabella slide precedente).

---

### SLIDE 21 — Summary
**Layout:** 10 Summary (sfondo arancio, 5 concetti in bianco bold)

**Titolo:** `Riepilogo MOD-35`

**Bullet (bianco bold):**
- REST API: GET/POST/PUT/PATCH/DELETE su risorse HTTP — stateless
- YANG: schema dati per config e stato dei dispositivi (module, container, list, leaf)
- RESTCONF: HTTP + YANG — URL `/restconf/data/<modulo>:<path>`
- NETCONF: XML + SSH — transazioni atomiche con commit/rollback
- DNA Center: token via POST `/auth/token`, usato con `x-auth-token` in ogni chiamata

---

## SCRIPT DOCENTE — NOTE PER OGNI SEZIONE

### Apertura (2 min)
"Nelle ultime sessioni abbiamo automatizzato con EEM, Python, Netmiko, Nornir, Ansible.
Tutti questi strumenti usano SSH — il vecchio paradigma. Le API REST rappresentano il
paradigma moderno: ogni risorsa di rete è accessibile tramite URL, con HTTP, in JSON.
Oggi capiamo perché questa è la direzione dell'industria e come funziona in Cisco."

### Transizione REST → YANG (dopo slide 6)
"Le API REST lavorano bene su applicazioni web. Ma la rete ha bisogno di un modello
dati strutturato. Che cos'è un'interfaccia? Che attributi ha? Quali valori sono validi?
YANG risponde a queste domande. È lo schema che dice: un'interfaccia ha un nome, una
descrizione, un indirizzo IP, uno stato operativo..."

### Transizione YANG → RESTCONF (dopo slide 12)
"Ora abbiamo il modello (YANG) e il trasporto (REST). RESTCONF li combina:
il path URL rispecchia esattamente l'albero YANG. Se l'albero dice
`interfaces/interface[name]`, l'URL sarà `.../interfaces/interface=GigabitEthernet1`."

### Vincolo IOU — momento didattico
"So già la domanda: perché non lo facciamo sul lab? IOU non supporta RESTCONF.
È una limitazione della piattaforma di virtualizzazione — IOU emula solo la parte
di routing, non l'infrastruttura di gestione. In un ambiente reale con IOS-XE o
Catalyst Center, tutti questi comandi funzionano. Per oggi, usiamo la sandbox DevNet."

### Chiusura (3 min)
"Ricapitolando: SNMP è il passato (ancora vivo). NETCONF è il presente enterprise
(transazioni, rollback). RESTCONF e le Intent API di DNA Center sono il futuro.
Per l'esame ENCOR, concentratevi sulle differenze tra questi tre protocolli,
sulla struttura URL RESTCONF, e sull'autenticazione DNA Center."

---

## DOMANDE TIPICHE DA PORRE ALLA CLASSE

1. "Qual è la differenza tra PUT e PATCH in RESTCONF?" — PUT sostituisce l'intera risorsa, PATCH modifica solo i campi specificati
2. "Perché NETCONF è preferito in ambienti enterprise per le configurazioni critiche?" — Supporta transazioni atomiche con commit/rollback
3. "Cosa succede se il token DNA Center scade durante uno script Python?" — La chiamata riceve 401 Unauthorized — bisogna gestire il refresh
4. "YANG è un linguaggio di programmazione?" — No, è un linguaggio di modellazione dati (come XML Schema o JSON Schema, ma specifico per la rete)
5. "Perché non usiamo RESTCONF nel lab?" — Non disponibile su IOU — richiede IOS-XE reale o DevNet Sandbox

---

## RISORSE & RIFERIMENTI

- RFC 8040: RESTCONF Protocol — https://datatracker.ietf.org/doc/html/rfc8040
- RFC 6241: NETCONF Protocol — https://datatracker.ietf.org/doc/html/rfc6241
- RFC 7950: YANG 1.1 — https://datatracker.ietf.org/doc/html/rfc7950
- Cisco DevNet Learning Labs — https://developer.cisco.com/learning/
- DNA Center Always-On Sandbox — https://sandboxdnac.cisco.com (credenziali DevNet)
- IOS-XE RESTCONF Lab DevNet — https://devnetsandbox.cisco.com/
- Cisco DNA Center API Reference — https://developer.cisco.com/docs/dna-center/

### dCloud Demo (opzionale)
Se disponibile un ambiente dCloud con Catalyst Center:
- Demo "Cisco DNA Center 2.x API" disponibile su dCloud
- Mostrare live la GUI Catalyst Center + chiamate API via Postman
- Durata consigliata demo: 15 min (dentro questo modulo da 1.5h)


---

> © 2026 Matteo Mirenda — Tutti i diritti riservati.
> Materiale ad uso esclusivo degli studenti iscritti al corso.
> Vietata la riproduzione, distribuzione o condivisione
> senza autorizzazione scritta dell'autore.
> CCNP ENCOR 350-401 

---
