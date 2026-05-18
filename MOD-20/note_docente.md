# Note Docente — MOD-20: LISP & VXLAN (Teoria)

> **Tipo:** Modulo teoria pura — nessun lab pratico su IOU
> **Ore:** 1.5h | **Codici syllabus:** 4.9 (LISP), 4.10 (VXLAN)
> **Formato:** Lezione frontale con slide + discussione

---

## Premessa didattica

LISP e VXLAN **non sono configurabili su IOU L3** (piattaforma GNS3 del corso). Le domande CCNP ENCOR su questi argomenti richiedono:

- Identificare i componenti e i loro ruoli (EID, RLOC, MS/MR per LISP; VNI, VTEP per VXLAN)
- Descrivere il flusso di una Map-Request/Reply LISP
- Confrontare VXLAN con 802.1Q (spazio di segmentazione, incapsulamento)
- Riconoscere il ruolo di LISP + VXLAN in SD-Access

**Non e' richiesta** la memorizzazione dei comandi di configurazione. L'esame usa domande di tipo "quale componente svolge il ruolo X?" o "quale protocollo risolve il problema Y?".

---

## Outline Slide

| # | Slide | Layout | Contenuto |
|---|-------|--------|-----------|
| 1 | Cover | 01 Cover Module | MOD-20: LISP & VXLAN — Architettura e Caso d'Uso SD-Access |
| 2 | Agenda | 02 Agenda | 1. Il problema della mobilita' IP / 2. LISP — componenti e flusso / 3. VXLAN — segmentazione estesa / 4. LISP+VXLAN in SD-Access / 5. Exam Tips |
| 3 | Section Header | 03 Section Header | PARTE 1 — LISP: Locator/ID Separation Protocol |
| 4 | Teoria: il problema | 04 Teoria Concetto | In IP tradizionale l'indirizzo ha due significati: identita' (chi sei) e locazione (dove sei). La mobilita' e' costosa: ogni spostamento richiede cambio IP o aggiornamenti di routing massivi. |
| 5 | Diagramma: EID vs RLOC | 05 Diagramma | Schema con due piani separati: piano identita' (EID — fisso) e piano locazione (RLOC — variabile). Frecce che mostrano come EID rimane stabile mentre RLOC cambia con lo spostamento. |
| 6 | Teoria: componenti LISP | 04 Teoria Concetto | Tabella: EID / RLOC / Map-Server (MS) / Map-Resolver (MR) / ITR / ETR / xTR. Analogia con sistema telefonico. |
| 7 | Diagramma: flusso Map-Request | 05 Diagramma | Sequenza numerata: Host A (EID) → ITR → Map-Request al MR → Map-Reply con RLOC → ITR incapsula in UDP/4341 → ETR decapsula → Host B |
| 8 | Config/Comando (reference) | 06 Config/Comando | Pseudo-config LISP per mostrare la struttura — annotato "TEORIA ONLY / non su IOU" |
| 9 | Section Header | 03 Section Header | PARTE 2 — VXLAN: Virtual eXtensible LAN |
| 10 | Teoria: il problema | 04 Teoria Concetto | 802.1Q: tag 12-bit = max 4096 VLAN. Insufficiente per datacenter multi-tenant o campus enterprise su larga scala. VXLAN estende a 24 bit (VNI) = ~16 milioni di segmenti. |
| 11 | Diagramma: struttura pacchetto VXLAN | 05 Diagramma | Struttura a stack: Outer IP \| UDP (dport 4789) \| VXLAN Header (VNI 24-bit) \| Inner Ethernet Frame. Confronto visivo con 802.1Q tag. |
| 12 | Teoria: componenti VXLAN | 04 Teoria Concetto | VNI / VTEP / Underlay / Overlay / BUM traffic (multicast underlay vs ingress replication) |
| 13 | Tabella confronto VXLAN vs 802.1Q | 04 Teoria Concetto | Tabella 4 colonne: caratteristica / 802.1Q / VXLAN / EVPN+VXLAN |
| 14 | Section Header | 03 Section Header | PARTE 3 — LISP + VXLAN in SD-Access (Cisco Campus Fabric) |
| 15 | Diagramma: SD-Access fabric | 05 Diagramma | Schema campus fabric: Fabric Edge (xTR+VTEP) / Fabric Border / Fabric Control-Plane (MS/MR) / Catalyst Center. Piano control: LISP. Piano dati: VXLAN. Piano policy: SGT. |
| 16 | Teoria: separazione dei piani | 04 Teoria Concetto | Control Plane = LISP (mobilita' endpoint, EID→RLOC mapping). Data Plane = VXLAN (trasporto L2 su L3, segmentazione VNI). Policy Plane = SGT (Cisco TrustSec — policy per gruppo). |
| 17 | Exam Tips | 09 Exam Tips | 5 bullet: EID/RLOC, MS/MR vs ITR/ETR, VNI 24-bit, VTEP funzione, LISP+VXLAN in SD-Access. |
| 18 | Summary | 10 Summary | 5 concetti: 1. LISP separa identita' da locazione. 2. EID fisso, RLOC variabile. 3. VXLAN 24-bit VNI vs 12-bit VLAN. 4. VTEP incapsula/decapsula. 5. SD-Access: LISP control + VXLAN data + SGT policy. |

---

## Contenuto dettagliato — LISP

### Componenti e ruoli

| Componente | Ruolo | Analogia |
|-----------|-------|---------|
| EID (Endpoint Identifier) | Indirizzo logico del dispositivo — non cambia con lo spostamento | Numero di telefono |
| RLOC (Routing Locator) | Indirizzo del router di bordo — cambia con la posizione nella rete | Cella GSM corrente |
| Map-Server (MS) | Riceve registrazioni EID→RLOC dagli xTR, popola il database | Registro delle SIM |
| Map-Resolver (MR) | Risponde alle Map-Request degli ITR con il RLOC corretto | Directory telefonica |
| ITR (Ingress Tunnel Router) | Riceve traffico verso EID, invia Map-Request, incapsula in UDP/4341 verso RLOC | Instradatore chiamata |
| ETR (Egress Tunnel Router) | Riceve pacchetti LISP, decapsula, consegna all'EID locale | Destinazione chiamata |
| xTR | Router che svolge sia ITR che ETR — ruolo tipico in SD-Access | Nodo completo |

### Flusso Map-Request (da descrivere sulla slide 7)

```
1. Host A (EID: 10.1.1.10) vuole raggiungere Host B (EID: 10.2.1.10)
2. ITR non ha mappatura EID→RLOC in cache
3. ITR invia Map-Request al MR: "Dove trovo EID 10.2.1.10?"
4. MR risponde con Map-Reply: "RLOC = 203.0.113.254 (xTR di Host B)"
5. ITR incapsula il pacchetto:
   [outer IP: ITR→203.0.113.254][UDP port 4341][EID payload]
6. ETR (203.0.113.254) riceve, decapsula, consegna a Host B
7. ITR salva mappatura in cache (TTL configurabile — evita Map-Request ripetute)
8. Pacchetti successivi vanno direttamente ITR→RLOC senza nuova Map-Request
```

### Domande alla classe (suggerimenti per discussione)

- "Se un host si sposta da un edificio all'altro, cosa cambia in LISP?" (solo il RLOC — l'EID rimane uguale, non serve riconfigurare nulla sull'host)
- "Perche' non basta usare il routing IP tradizionale?" (ogni spostamento richiederebbe aggiornamento di routing in tutta la rete — non scalabile)
- "LISP e' un sostituto di BGP o un complemento?" (complemento — LISP gestisce la mobilita' degli endpoint, non il routing tra AS)

---

## Contenuto dettagliato — VXLAN

### Confronto VXLAN vs 802.1Q

| Caratteristica | 802.1Q | VXLAN |
|---------------|--------|-------|
| Spazio segmentazione | 12 bit = 4.096 segmenti | 24 bit = 16.777.216 segmenti |
| Incapsulamento | Tag 4 byte nell'header Ethernet | Outer IP + UDP (dport 4789) + VXLAN header (8 byte) + inner Ethernet frame completo |
| Requisito rete | L2 contigua (stesso broadcast domain) | Qualsiasi rete IP routable (L3 tra i VTEP) |
| Overhead | 4 byte per frame | ~50 byte per frame (outer IP+UDP+VXLAN) |
| Endpoint | Host con porta 802.1Q trunk | VTEP (switch, hypervisor, router) |
| Mobilita' host | Richiede L2 stretch (STP su larga scala) | Nativa — host si sposta, solo LISP/EVPN aggiorna la mappatura |

### Struttura pacchetto VXLAN (da mostrare sulla slide 11)

```
┌──────────────────┬──────────────┬──────────────────┬───────────────────────────┐
│  Outer IP Header │   UDP Header │  VXLAN Header    │   Inner Ethernet Frame     │
│  VTEP-A → VTEP-B │  dport: 4789 │  VNI: 24 bit     │   (frame L2 originale      │
│  (underlay)      │              │  (identifica      │    dell'host — completo    │
│                  │              │   il segmento)    │    con MAC src/dst)        │
└──────────────────┴──────────────┴──────────────────┴───────────────────────────┘

! Confronto: 802.1Q aggiunge solo 4 byte all'header Ethernet originale
! VXLAN incapsula l'intero frame L2 (incluso il MAC dell'host) in UDP/IP
```

### BUM traffic (Broadcast/Unknown unicast/Multicast)

Problema: in una rete VXLAN, quando un host vuole inviare un frame broadcast (es. ARP), come viene distribuito a tutti i VTEP dello stesso VNI?

Opzione 1 — **Multicast underlay:** ogni VNI e' mappato a un gruppo multicast. I VTEP si uniscono al gruppo per il VNI che gestiscono. Scalabile ma richiede multicast routing nell'underlay.

Opzione 2 — **Ingress Replication (unicast flood):** il VTEP mittente invia una copia unicast a ciascun VTEP della lista. Piu' semplice (no multicast) ma genera traffico proporzionale a N VTEP.

In Cisco SD-Access (Catalyst Center), si usa ingress replication per semplicita' di deployment.

---

## SD-Access — Separazione dei piani

### Architettura fabric (per la slide 15)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Catalyst Center                               │
│             (orchestrazione e provisioning automatico)           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ management plane
        ┌───────────────────┴───────────────────────┐
        │           Fabric Control Plane             │
        │      LISP Map-Server + Map-Resolver        │
        │  (Fabric Border Node — nodo di bordo)      │
        └──────┬──────────────────────────┬──────────┘
               │ Map-Request/Reply (LISP)  │
     ┌─────────┴─────┐               ┌────┴──────────┐
     │ Fabric Edge 1 │               │ Fabric Edge 2 │
     │   (xTR+VTEP)  │               │   (xTR+VTEP)  │
     │  Edificio A   │               │   Edificio B  │
     └───────┬───────┘               └───────┬────────┘
             │                               │
          Host A                           Host B
         (EID fisso)                     (EID fisso)

Control Plane: LISP → EID→RLOC mapping, mobilita' host
Data Plane:    VXLAN → trasporto frame L2 su L3 con VNI
Policy Plane:  SGT (Security Group Tag) → policy per gruppo, indip. dall'IP
```

### Transizione da SD-Access a SD-WAN

- **SD-Access** (campus): LISP + VXLAN gestiti da Catalyst Center (ex DNA Center). I Fabric Edge node sono switch Catalyst.
- **SD-WAN** (WAN): vEdge/cEdge con Cisco vManage. Usa TLOC (analogo al RLOC) e OMP (Overlay Management Protocol, analogo a LISP).

La domanda ENCOR tipica e' "quale componente in SD-Access svolge il ruolo di control plane?" (LISP, gestito dal Fabric Control Plane node).

---

## Suggerimenti demo dCloud

Se il tempo lo permette (30 min aggiuntivi), mostrare la demo Catalyst Center su dCloud:

1. **dCloud — Cisco DNA Center (SD-Access) demo**
   - URL: dcloud.cisco.com → ricercare "DNA Center" o "Catalyst Center"
   - Mostrare: provisioning automatico di un Fabric Edge, aggiunta di un host, visualizzazione della mappa fabric

2. **Punti da enfatizzare nella demo:**
   - Come Catalyst Center traduce la policy "gruppo X puo' parlare con gruppo Y" in SGT
   - Come la mobilita' host e' trasparente all'utente (l'host mantiene lo stesso IP)
   - L'assenza di configurazione manuale LISP/VXLAN sui singoli switch

3. **Alternativa senza dCloud:** video Cisco Live (DevNet) disponibili su ciscolive.com — cercare "SD-Access LISP VXLAN architecture" per sessioni BRKARC-3378 o simili.

---

## Exam Tips — da includere nella slide 17

1. **EID = chi sei (fisso), RLOC = dove sei (variabile)** — il punto centrale di LISP
2. **MS riceve registrazioni, MR risponde alle Map-Request** — due ruoli distinti anche se spesso sullo stesso nodo
3. **VNI = 24 bit = ~16 milioni di segmenti** (vs 4096 delle VLAN 802.1Q) — domanda frequente
4. **VTEP = dispositivo che incapsula/decapsula frame Ethernet in UDP/4789** — puo' essere switch, hypervisor o router
5. **SD-Access: LISP = control plane, VXLAN = data plane, SGT = policy plane** — tripletta da memorizzare

---

## Domande tipo ENCOR (da usare in chiusura sessione)

1. In LISP, quale componente riceve le registrazioni EID→RLOC dagli xTR?
   - **A) Map-Server (MS)** ← corretto

2. Quale porta UDP usa VXLAN per il trasporto?
   - **A) 4789** ← corretto

3. Qual e' il limite dello spazio di segmentazione 802.1Q?
   - **A) 4.096 VLAN (12-bit tag)** ← corretto. VXLAN usa VNI 24-bit = ~16 milioni

4. In un'architettura SD-Access, quale protocollo gestisce il control plane per la mobilita' degli endpoint?
   - **A) LISP** ← corretto. VXLAN e' il data plane.

5. Cosa succede all'EID di un host quando si sposta da Fabric Edge 1 a Fabric Edge 2 in SD-Access?
   - **A) L'EID rimane lo stesso — solo il RLOC (xTR di destinazione) cambia nel database LISP** ← corretto

---

## Note operative per il docente

- Allocare 35-40 min a LISP, 25-30 min a VXLAN, 10-15 min a SD-Access e domande
- La sessione e' puramente teorica — nessun terminale aperto
- Se gli studenti chiedono perche' non si fa lab: IOU non implementa LISP Data Plane ne' il processo ETR/ITR completo; VXLAN richiede hardware specifico (ASR/Catalyst) o containerlab con immagini supportate
- Per containerlab (futura migrazione): le immagini Cisco CSR1000v o Cat8000v supportano LISP e VXLAN — annotare come potenziale upgrade futuro del corso


---

> © 2026 Matteo Mirenda — Tutti i diritti riservati.
> Materiale ad uso esclusivo degli studenti iscritti al corso.
> Vietata la riproduzione, distribuzione o condivisione
> senza autorizzazione scritta dell'autore.
> CCNP ENCOR 350-401 

---
