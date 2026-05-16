# Workbook Studenti — MOD-34: Ansible & Git

**Area:** AREA 13 — AUTOMATION & PROGRAMMABILITY
**Ore:** 2h | **Codici syllabus:** 6.7
**Prerequisito:** MOD-33 (Netmiko & Nornir) — venv attivo, router con SSH configurato

---

## 1. TOPOLOGIA

```
          VM GNS3 (192.168.122.1)
          Control Node Ansible + Git server
                  |
               SW1 (IOU L2)
           VLAN 10 — management
         /        |        \        \
       R1        R2        R3       R4
  .101/24     .102/24   .103/24  .104/24
  Lo0:1.1.1.1 2.2.2.2   3.3.3.3  4.4.4.4
```

### Tabella indirizzamento

| Device  | IP / Mask          | Ruolo        |
|---------|--------------------|--------------|
| VM GNS3 | 192.168.122.1/24   | Control Node Ansible · Gitea |
| R1      | 192.168.122.101/24 | Core router  |
| R2      | 192.168.122.102/24 | Distribution |
| R3      | 192.168.122.103/24 | Distribution |
| R4      | 192.168.122.104/24 | Access       |

> OSPF area 0 pre-configurato. SSH abilitato su tutti i router.

---

## 2. OBIETTIVI DELLA SESSIONE

Al termine di questo modulo lo studente sarà in grado di:

- [ ] Descrivere l'architettura Ansible (agentless, inventory, playbook, module)
- [ ] Creare un inventory Ansible in formato INI con variabili SSH per IOS
- [ ] Scrivere e eseguire playbook con i moduli `cisco.ios.ios_command`, `ios_config`, `ios_facts`
- [ ] Verificare l'idempotency di `ios_config` eseguendo il playbook due volte
- [ ] Utilizzare Git per versionare script Python e playbook Ansible (init, add, commit, log, diff)
- [ ] Fare push su un repository Gitea locale e gestire un branch workflow

**Codici syllabus coperti:** 6.7 (network automation tools — Ansible, Git)

---

## 3. LAB SETUP

### 3.1 Caricamento configurazioni router

```
R1# copy tftp://192.168.122.1/ENCOR/MOD-34/r1-cfg running-config
R2# copy tftp://192.168.122.1/ENCOR/MOD-34/r2-cfg running-config
R3# copy tftp://192.168.122.1/ENCOR/MOD-34/r3-cfg running-config
R4# copy tftp://192.168.122.1/ENCOR/MOD-34/r4-cfg running-config

Rx(config)# crypto key generate rsa modulus 1024
```

### 3.2 Setup ambiente

```bash
# Attiva il venv
cd ~/ENCOR-MOD34
source .venv/bin/activate

# Installa Ansible e la collection Cisco IOS
pip install ansible
ansible-galaxy collection install cisco.ios

# Verifica installazione
ansible --version
ansible-galaxy collection list | grep cisco

# Struttura del repo
ls ansible/
# inventory.ini  gather_facts.yml  push_config.yml  ansible.cfg
ls scripts/
# script Python da versionare con Git
```

### 3.3 Prerequisiti

- Ansible 2.9+ installato nel venv
- Collection `cisco.ios` installata (`ansible-galaxy collection install cisco.ios`)
- SSH abilitato su tutti i router (RSA key generata)
- Gitea accessibile su `http://192.168.122.1` (username: student, password: student)

### 3.4 Verifica pre-lab

```bash
# Test Ansible verso R1
cd ~/ENCOR-MOD34/ansible
ansible -i inventory.ini ios_routers -m ping

# Atteso:
# R1 | SUCCESS => {"ping": "pong"}
# R2 | SUCCESS => {"ping": "pong"}
# R3 | SUCCESS => {"ping": "pong"}
# R4 | SUCCESS => {"ping": "pong"}
```

---

## 4. TASK LIST

| #    | Task                                               | Codice | Tempo  |
|------|----------------------------------------------------|--------|--------|
| A.1  | Crea inventory Ansible con R1-R4                   | 6.7    | 10 min |
| A.2  | Playbook gather_facts.yml — raccolta show version  | 6.7    | 15 min |
| A.3  | Playbook push_config.yml — banner + logging        | 6.7    | 15 min |
| A.4  | Idempotency — seconda esecuzione + --check --diff  | 6.7    | 10 min |
| A.5  | Playbook ios_facts.yml — facts strutturati         | 6.7    | 10 min |
| G.1  | git init, add, commit degli script del lab         | 6.7    | 10 min |
| G.2  | git log, git diff, git status                      | 6.7    | 10 min |
| G.3  | git push su Gitea locale                           | 6.7    | 10 min |
| G.4  | git branch, checkout, merge workflow               | 6.7    | 10 min |

---

## 5. DETTAGLIO TASK

---

### TASK A.1 — Inventory Ansible

#### TEORIA — Ansible: architettura agentless

Ansible non richiede nulla installato sui router (agentless).
Si connette via SSH e invia i comandi direttamente, come farebbe un operatore umano.

**Componenti principali:**

| Componente | Descrizione |
|------------|-------------|
| **Inventory** | Lista di host e gruppi (INI o YAML) |
| **Playbook** | File YAML con la lista dei play e task |
| **Module** | Unità funzionale (es. `cisco.ios.ios_command`) |
| **Task** | Singola esecuzione di un module su un gruppo di host |
| **Role** | Raccolta strutturata di task, variabili, handler |

**Confronto Ansible vs Chef vs SaltStack:**

| Caratteristica | Ansible | Chef | SaltStack |
|----------------|---------|------|-----------|
| Architettura | Agentless (SSH) | Agent-based (pull) | Agent o agentless |
| Linguaggio config | YAML (Playbook) | Ruby (Cookbook) | YAML / Jinja2 |
| Modello esecuzione | Push | Pull dal server | Push o event-driven |
| Curva apprendimento | Bassa | Alta | Media |
| Uso in ambito rete | Molto comune | Raro | Nicchia |

#### TASK

Crea il file `ansible/inventory.ini`:

```ini
[ios_routers]
R1 ansible_host=192.168.122.101
R2 ansible_host=192.168.122.102
R3 ansible_host=192.168.122.103
R4 ansible_host=192.168.122.104

[ios_routers:vars]
ansible_user=admin
ansible_password=cisco123
ansible_become=yes
ansible_become_method=enable
ansible_become_password=cisco123
ansible_network_os=cisco.ios.ios
ansible_connection=network_cli
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

Testa la connettività:

```bash
cd ~/ENCOR-MOD34/ansible
ansible -i inventory.ini ios_routers -m ping
```

#### VERIFICA

```
R1 | SUCCESS => {
    "ping": "pong"
}
R2 | SUCCESS => {
    "ping": "pong"
}
R3 | SUCCESS => {
    "ping": "pong"
}
R4 | SUCCESS => {
    "ping": "pong"
}
```

---

### TASK A.2 — Playbook gather_facts.yml

#### TEORIA — Moduli ios_command e register

`ios_command`: esegue comandi show su IOS. Il risultato viene salvato con `register`.

```yaml
- name: Raccoglie show version
  cisco.ios.ios_command:
    commands:
      - show version
      - show ip interface brief
  register: output
# output.stdout → lista di stringhe (indice 0 = show version, indice 1 = show ip int brief)
# output.stdout_lines → lista di liste (ogni elemento = lista righe del comando)
```

`delegate_to: localhost`: i task di scrittura file girano sulla VM locale,
non sul router (che non ha filesystem accessibile da Ansible).

#### TASK

Crea il file `ansible/gather_facts.yml`:

```yaml
---
- name: Raccolta show version da tutti i router
  hosts: ios_routers
  gather_facts: no         # disabilita fact gathering automatico (non supportato su IOS via network_cli senza ios_facts)

  tasks:

    - name: Esegui show version e show ip interface brief
      cisco.ios.ios_command:
        commands:
          - show version
          - show ip interface brief
      register: output

    - name: Stampa le prime 5 righe di show version
      ansible.builtin.debug:
        msg: "{{ output.stdout[0].splitlines()[:5] }}"

    - name: Salva show version su file locale
      ansible.builtin.copy:
        content: "{{ output.stdout[0] }}"
        dest: "../backup/{{ inventory_hostname }}-version.txt"
      delegate_to: localhost
```

Esegui:

```bash
ansible-playbook -i inventory.ini gather_facts.yml
```

#### VERIFICA

```
PLAY RECAP **************************************************
R1   : ok=3  changed=1  unreachable=0  failed=0  skipped=0
R2   : ok=3  changed=1  unreachable=0  failed=0  skipped=0
R3   : ok=3  changed=1  unreachable=0  failed=0  skipped=0
R4   : ok=3  changed=1  unreachable=0  failed=0  skipped=0

# Verifica file salvati:
ls ../backup/*-version.txt
# backup/R1-version.txt  backup/R2-version.txt  ...
```

---

### TASK A.3 — Playbook push_config.yml

#### TEORIA — Modulo ios_config e idempotency

`ios_config`: applica linee di configurazione IOS.
Prima di inviare un comando, **verifica se è già presente** nella running-config.
Se il comando esiste identico → `changed=0` (idempotency).

```yaml
- name: Configura logging host
  cisco.ios.ios_config:
    lines:
      - logging host 192.168.122.1
      - logging trap informational
```

`ios_banner`: modulo dedicato per i banner IOS.
L'idempotency funziona correttamente solo con `ios_banner`
(con `ios_config` il banner viene sempre marcato come changed).

#### TASK

Crea il file `ansible/push_config.yml`:

```yaml
---
- name: Push configurazione banner e logging su tutti i router
  hosts: ios_routers
  gather_facts: no

  tasks:

    - name: Configura banner MOTD
      cisco.ios.ios_banner:
        banner: motd
        text: |
          ******************************************
          *  ENCOR Lab - Authorized Access Only    *
          *  Managed by Ansible - MOD-34           *
          ******************************************
        state: present

    - name: Configura logging host e trap level
      cisco.ios.ios_config:
        lines:
          - logging host 192.168.122.1
          - logging trap informational
          - logging on

    - name: Verifica configurazione logging applicata
      cisco.ios.ios_command:
        commands:
          - show running-config | include logging
      register: logging_check

    - name: Stampa risultato verifica
      ansible.builtin.debug:
        msg: "{{ logging_check.stdout[0] }}"
```

Esegui:

```bash
ansible-playbook -i inventory.ini push_config.yml
```

#### VERIFICA

```
PLAY RECAP **************************************************
R1   : ok=4  changed=2  unreachable=0  failed=0
R2   : ok=4  changed=2  unreachable=0  failed=0
R3   : ok=4  changed=2  unreachable=0  failed=0
R4   : ok=4  changed=2  unreachable=0  failed=0
! changed=2: banner MOTD + logging host applicati

! Su R1, verifica manuale:
R1# show running-config | include logging
! logging host 192.168.122.1
! logging trap informational
! logging on
```

---

### TASK A.4 — Idempotency

#### TEORIA — Idempotency: una proprietà fondamentale

Un'operazione è **idempotente** se eseguirla N volte produce lo stesso risultato
di eseguirla 1 volta.

In Ansible:
- **`changed=0`** nella seconda esecuzione = idempotency confermata
- **`changed=1`** ad ogni esecuzione = il modulo non è idempotente
  (tipico di `ios_config` con banner — usare `ios_banner`)

`--check`: dry-run — Ansible simula senza applicare modifiche.
`--diff`: mostra la differenza prima/dopo (utile con `ios_config`).

#### TASK

```bash
# Seconda esecuzione del playbook (stessa configurazione)
ansible-playbook -i inventory.ini push_config.yml

# Confronta il PLAY RECAP con la prima esecuzione
# Atteso: changed=0 per tutti i router

# Dry-run: cosa cambierebbe se modificassimo il banner?
ansible-playbook -i inventory.ini push_config.yml --check --diff

# Esegui solo su R1:
ansible-playbook -i inventory.ini push_config.yml --limit R1
```

#### VERIFICA

```
! Seconda esecuzione:
PLAY RECAP **************************************************
R1   : ok=4  changed=0  unreachable=0  failed=0
R2   : ok=4  changed=0  unreachable=0  failed=0
R3   : ok=4  changed=0  unreachable=0  failed=0
R4   : ok=4  changed=0  unreachable=0  failed=0
! changed=0 su tutti → IDEMPOTENCY CONFERMATA

! --check output:
R1   : ok=4  changed=0 (dry-run: nessuna modifica necessaria)
```

---

### TASK A.5 — Playbook ios_facts.yml

#### TEORIA — Facts: dati strutturati dal device

`ios_facts` raccoglie informazioni strutturate dal router e le mette nella variabile `ansible_facts`.
Utile per prendere decisioni basate sullo stato reale del device (versione OS, interfacce, ecc.).

```yaml
- name: Raccoglie facts IOS
  cisco.ios.ios_facts:
    gather_subset:
      - all
# Popola: ansible_facts['net_hostname'], net_version, net_interfaces, ...
```

#### TASK

Crea `ansible/ios_facts.yml`:

```yaml
---
- name: Raccoglie e stampa facts strutturati da tutti i router
  hosts: ios_routers
  gather_facts: no

  tasks:

    - name: Raccoglie facts IOS
      cisco.ios.ios_facts:
        gather_subset:
          - all

    - name: Stampa hostname e versione IOS
      ansible.builtin.debug:
        msg:
          - "Hostname : {{ ansible_facts['net_hostname'] }}"
          - "IOS Ver  : {{ ansible_facts['net_version'] }}"
          - "Modello  : {{ ansible_facts['net_model'] }}"

    - name: Stampa lista interfacce
      ansible.builtin.debug:
        msg: "Interfacce: {{ ansible_facts['net_interfaces'].keys() | list }}"
```

Esegui:

```bash
ansible-playbook -i inventory.ini ios_facts.yml
```

#### VERIFICA

```
TASK [Stampa hostname e versione IOS] ***
ok: [R1] => {
    "msg": [
        "Hostname : R1",
        "IOS Ver  : 15.x.x",
        "Modello  : IOSv"
    ]
}
```

---

### TASK G.1 — git init, add, commit

#### TEORIA — Git: distributed Version Control System

Git è un **sistema di controllo versione distribuito**.
Ogni clone del repository contiene l'intera storia dei commit.

**Concetti fondamentali:**

| Concetto | Descrizione |
|----------|-------------|
| **Working tree** | File nella directory di lavoro (modificati o nuovi) |
| **Staging area (Index)** | File pronti per il prossimo commit (`git add`) |
| **Commit** | Snapshot della staging area con messaggio e autore |
| **Branch** | Puntatore a un commit — permette sviluppo parallelo |
| **Remote** | Repository remoto (`origin`) — es. Gitea su 192.168.122.1 |

**Workflow di base:**
```
modifica file → git add → git commit → git push
```

#### TASK

```bash
# Dalla home del progetto
cd ~/ENCOR-MOD34

# Inizializza il repository Git
git init

# Configura identità (necessario per i commit)
git config user.name "Student ENCOR"
git config user.email "student@encor.lab"

# Aggiungi i file alla staging area
git add ansible/inventory.ini
git add ansible/gather_facts.yml
git add ansible/push_config.yml
git add ansible/ios_facts.yml
git add scripts/

# Verifica cosa è in staging
git status

# Crea il primo commit
git commit -m "feat: aggiunge playbook Ansible MOD-34 e script Python"

# Verifica il commit
git log --oneline
```

#### VERIFICA

```
$ git status
On branch main (or master)
nothing to commit, working tree clean

$ git log --oneline
a1b2c3d feat: aggiunge playbook Ansible MOD-34 e script Python
```

---

### TASK G.2 — git log, diff, status

#### TEORIA — Ispezione dello storico

```bash
git log --oneline           # lista compatta dei commit
git log --oneline --graph   # grafo dei branch
git diff                    # diff working tree vs staging
git diff --staged           # diff staging vs ultimo commit
git show <hash>             # dettaglio di un commit specifico
git status                  # stato del working tree
```

#### TASK

```bash
# Modifica un playbook (aggiungi un commento)
echo "# Aggiornato: $(date)" >> ansible/push_config.yml

# Verifica cosa è cambiato
git status
# Mostra: ansible/push_config.yml modified

git diff ansible/push_config.yml
# Mostra le righe aggiunte (in verde con +) e rimosse (in rosso con -)

# Aggiungi alla staging e crea un secondo commit
git add ansible/push_config.yml
git diff --staged ansible/push_config.yml

git commit -m "docs: aggiunge commento data aggiornamento a push_config.yml"

# Verifica lo storico
git log --oneline
# 2 commit visibili
```

#### VERIFICA

```
$ git log --oneline
b2c3d4e docs: aggiunge commento data aggiornamento a push_config.yml
a1b2c3d feat: aggiunge playbook Ansible MOD-34 e script Python
```

---

### TASK G.3 — git push su Gitea

#### TEORIA — Remote e push

`git remote add origin <URL>`: collega il repository locale a uno remoto.
`git push -u origin main`: invia i commit locali al remote (`-u` imposta il tracking).

Gitea è un'istanza self-hosted di Git (alternativa leggera a GitHub/GitLab).

#### TASK

```bash
# Aggiungi il remote Gitea
git remote add origin http://192.168.122.1/git/ENCOR-MOD34.git

# Verifica il remote
git remote -v

# Push del branch main
git push -u origin main
# Inserire credenziali: student / student

# Verifica su Gitea (browser):
# http://192.168.122.1 → repository ENCOR-MOD34 → commit visibili
```

#### VERIFICA

```
$ git remote -v
origin  http://192.168.122.1/git/ENCOR-MOD34.git (fetch)
origin  http://192.168.122.1/git/ENCOR-MOD34.git (push)

$ git push -u origin main
Enumerating objects: 10, done.
...
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

### TASK G.4 — Branch workflow

#### TEORIA — Branching strategy

Il workflow tipico in team:

```
main         ●────────────────────────●  (produzione stabile)
              \                      /
feature/ntp    ●──●──●──●           /    (sviluppo isolato)
                          \        /
                           merge --
```

```bash
git branch <nome>          # crea un branch
git checkout <nome>        # spostati sul branch
git checkout -b <nome>     # crea e spostati in un solo comando
git merge <branch>         # merge di un branch nel corrente
git branch -d <nome>       # elimina il branch (dopo il merge)
```

#### TASK

```bash
# Crea e spostati sul branch feature/ntp-playbook
git checkout -b feature/ntp-playbook

# Verifica su quale branch sei
git branch
# * feature/ntp-playbook
#   main

# Crea un nuovo playbook sul branch feature
cat > ansible/ntp_config.yml << 'EOF'
---
- name: Configura NTP su tutti i router
  hosts: ios_routers
  gather_facts: no
  tasks:
    - name: Push NTP server
      cisco.ios.ios_config:
        lines:
          - ntp server 192.168.122.1
          - ntp update-calendar
EOF

git add ansible/ntp_config.yml
git commit -m "feat: aggiunge playbook configurazione NTP"

# Torna su main e fai il merge
git checkout main
git merge feature/ntp-playbook
git log --oneline --graph

# Elimina il branch feature (già mergiato)
git branch -d feature/ntp-playbook

# Push finale
git push origin main
```

#### VERIFICA

```
$ git log --oneline --graph
*   c3d4e5f (HEAD -> main, origin/main) Merge branch 'feature/ntp-playbook'
|\
| * d4e5f6g feat: aggiunge playbook configurazione NTP
|/
* b2c3d4e docs: aggiunge commento data aggiornamento a push_config.yml
* a1b2c3d feat: aggiunge playbook Ansible MOD-34 e script Python

$ git branch
* main
! feature/ntp-playbook eliminato
```

---

## 6. TROUBLESHOOTING GUIDE

| Sintomo | Causa probabile | Diagnosi | Fix |
|---------|----------------|----------|-----|
| `ansible -m ping` → `UNREACHABLE` | SSH non abilitato / chiavi RSA mancanti | `ssh admin@IP` manuale | `crypto key generate rsa modulus 1024` sul router |
| `SSH key fingerprint warning` | `StrictHostKeyChecking` non disabilitato | Leggere il messaggio di errore | Aggiungere `ansible_ssh_common_args='-o StrictHostKeyChecking=no'` nell'inventory |
| `Module not found: cisco.ios` | Collection non installata | `ansible-galaxy collection list` | `ansible-galaxy collection install cisco.ios` |
| `ios_config: changed=1` ad ogni run | Comando non idempotente (es. banner con ios_config) | Confrontare RECAP prima/dopo | Usare `ios_banner` per i banner; `ios_config` per linee normali |
| `PLAY RECAP: failed=1` | Errore nel task | Rieseguire con `-v` o `-vvv` | `ansible-playbook ... -vvv` per debug verboso |
| `gather_facts: yes` causa errori | `setup` module non compatibile con network_cli | Messaggio di errore | Impostare `gather_facts: no` nei playbook per dispositivi IOS |
| `git push` → `403 Forbidden` | Credenziali errate o repository non esistente | Accedere a Gitea via browser | Creare il repo su Gitea prima del push; verificare credenziali |
| `git commit` → `Author identity unknown` | `user.name` e `user.email` non configurati | `git config --list` | `git config user.name "nome"` e `git config user.email "email"` |
| `git merge` → conflitti | Stesso file modificato su due branch | `git status` mostra i file in conflitto | Aprire il file, risolvere i marker `<<<<` `====` `>>>>`, poi `git add` + `git commit` |

---

## 7. SOLUZIONI

> Le soluzioni complete si trovano in `MOD-34/soluzione.md`.
> Non consultare prima di aver tentato i task autonomamente.

---

## 8. RIEPILOGO & EXAM TIPS

### Punti chiave

1. **Ansible è agentless**: usa SSH (network_cli per IOS) — non richiede nulla installato sui router
2. **Idempotency**: `ios_config` confronta i comandi con la running-config — seconda esecuzione `changed=0` se già configurato; usare `ios_banner` per i banner (idempotency garantita)
3. **`gather_facts: no`** è obbligatorio nei playbook per IOS via `network_cli` — il modulo `setup` non è compatibile
4. **Git workflow**: `git add` → staging → `git commit` → snapshot locale → `git push` → remote
5. **Branch strategy**: sviluppare su branch feature (`git checkout -b`), merge su main quando stabile, eliminare il branch feature dopo il merge

### Domande tipo CCNP

1. Qual è il vantaggio principale di Ansible rispetto a Chef per la gestione di dispositivi di rete?
   - Ansible è agentless (nessun agent sui dispositivi); Chef richiede un agent installato
2. Perché `ios_config` è idempotente e `ios_banner` è necessario per i banner?
   - `ios_config` verifica se la linea è già presente nella running-config; `ios_banner` gestisce correttamente il confronto del testo completo del banner (che `ios_config` non riesce a confrontare in modo affidabile)
3. In un playbook Ansible, a cosa serve `delegate_to: localhost`?
   - Esegue il task sulla macchina che lancia Ansible (la VM GNS3) invece che sul dispositivo remoto — utile per salvare file localmente
4. Qual è la differenza tra `git add` e `git commit`?
   - `git add` aggiunge i file alla staging area (area intermedia); `git commit` crea uno snapshot permanente di ciò che è in staging
5. Come si verifica se un playbook Ansible applicherebbe modifiche senza eseguirle davvero?
   - `ansible-playbook --check` (dry-run) — opzionalmente con `--diff` per vedere le differenze
