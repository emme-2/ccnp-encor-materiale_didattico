# Soluzione Commentata — MOD-34: Ansible & Git

> **INSTRUCTOR COPY — Non distribuire agli studenti**
> Codici syllabus: 6.7

---

## SOLUZIONE A.1 — Inventory Ansible (inventory.ini)

```ini
# ansible/inventory.ini

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

**Note docente:**

`ansible_become=yes` + `ansible_become_method=enable` → Ansible esegue automaticamente
`enable` per entrare in modalità privilegiata prima di eseguire comandi/configurazioni.

`ansible_network_os=cisco.ios.ios` → identifica il plugin di connessione network_cli per IOS.
Senza questo, Ansible userebbe connection=ssh standard che non funziona con IOS.

`StrictHostKeyChecking=no` → necessario in lab dove i router vengono distrutti e
ricreati frequentemente (la host key cambia). In produzione, usare known_hosts verificato.

---

## SOLUZIONE A.2 — gather_facts.yml

```yaml
---
# ansible/gather_facts.yml
# Raccoglie show version e show ip interface brief da tutti i router
# Salva show version in backup/Rx-version.txt

- name: Raccolta informazioni router IOS
  hosts: ios_routers
  gather_facts: no
  # gather_facts: no → disabilita il modulo 'setup'
  # su IOS via network_cli, 'setup' non è supportato e causerebbe errore

  tasks:

    - name: Esegui show version e show ip interface brief
      cisco.ios.ios_command:
        commands:
          - show version
          - show ip interface brief
      register: output
      # output.stdout → lista di stringhe (1 per comando)
      # output.stdout[0] = show version
      # output.stdout[1] = show ip interface brief
      # output.stdout_lines → lista di liste (righe)

    - name: Stampa prime 5 righe show version
      ansible.builtin.debug:
        msg: "{{ output.stdout[0].splitlines()[:5] }}"

    - name: Salva show version su file locale
      ansible.builtin.copy:
        content: "{{ output.stdout[0] }}"
        dest: "../backup/{{ inventory_hostname }}-version.txt"
      delegate_to: localhost
      # delegate_to: localhost → il task 'copy' gira sulla VM che esegue Ansible
      # Il router non ha un filesystem scrivibile da Ansible
      # inventory_hostname → nome dell'host nell'inventory (R1, R2, ...)
```

```bash
# Esecuzione
cd ~/ENCOR-MOD34/ansible
ansible-playbook -i inventory.ini gather_facts.yml

# Output atteso:
# PLAY RECAP:
# R1 : ok=3  changed=1  unreachable=0  failed=0
# (changed=1 perché il file viene creato la prima volta)

# Seconda esecuzione: changed=0 (file già esistente con lo stesso contenuto)
```

---

## SOLUZIONE A.3 — push_config.yml

```yaml
---
# ansible/push_config.yml
# Applica banner MOTD e logging host su tutti i router
# Idempotente: seconda esecuzione → changed=0

- name: Push configurazione banner e logging
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
      # ios_banner è idempotente per i banner
      # ios_config con banner non è affidabile (changed=1 ad ogni run)

    - name: Configura logging host e trap level
      cisco.ios.ios_config:
        lines:
          - logging host 192.168.122.1
          - logging trap informational
          - logging on
      # ios_config confronta i comandi con la running-config
      # Se già presenti → changed=0 (idempotency)

    - name: Verifica configurazione logging
      cisco.ios.ios_command:
        commands:
          - show running-config | include logging
      register: logging_check

    - name: Stampa risultato verifica
      ansible.builtin.debug:
        msg: "{{ logging_check.stdout[0] }}"
```

**Nota docente — ios_config vs ios_banner:**

Il task `logging host 192.168.122.1` in `ios_config` è idempotente perché Ansible
controlla se la stringa è presente nella running-config prima di reinviarla.

Il task banner NON sarebbe idempotente con `ios_config` perché IOS rappresenta il banner
in modo diverso (con delimitatori `^C` o altri caratteri) che Ansible non riesce a
confrontare correttamente. `ios_banner` risolve questo problema usando un'API specifica
per il confronto del testo del banner.

---

## SOLUZIONE A.4 — Idempotency

```bash
# PRIMA ESECUZIONE:
ansible-playbook -i inventory.ini push_config.yml
# RECAP: ok=4 changed=2 (banner + logging applicati)

# SECONDA ESECUZIONE (stessa configurazione):
ansible-playbook -i inventory.ini push_config.yml
# RECAP: ok=4 changed=0 ← IDEMPOTENCY CONFERMATA

# DRY-RUN con --check --diff:
ansible-playbook -i inventory.ini push_config.yml --check --diff
# Output: "no changes required" su tutti i router

# Limitare a un solo host:
ansible-playbook -i inventory.ini push_config.yml --limit R1
# Esegue il play solo su R1

# Verbosità aumentata (debug):
ansible-playbook -i inventory.ini push_config.yml -v    # 1 livello
ansible-playbook -i inventory.ini push_config.yml -vvv  # 3 livelli (molto dettagliato)
```

---

## SOLUZIONE A.5 — ios_facts.yml

```yaml
---
# ansible/ios_facts.yml

- name: Raccoglie e stampa facts strutturati
  hosts: ios_routers
  gather_facts: no

  tasks:

    - name: Raccoglie facts IOS
      cisco.ios.ios_facts:
        gather_subset:
          - all
      # Popola ansible_facts con:
      # net_hostname, net_version, net_model, net_serialnum
      # net_interfaces (dict), net_neighbors (LLDP/CDP)
      # net_config (running-config completa)

    - name: Stampa hostname e versione IOS
      ansible.builtin.debug:
        msg:
          - "Hostname : {{ ansible_facts['net_hostname'] }}"
          - "IOS Ver  : {{ ansible_facts['net_version'] }}"
          - "Modello  : {{ ansible_facts['net_model'] }}"

    - name: Stampa lista interfacce
      ansible.builtin.debug:
        msg: "Interfacce: {{ ansible_facts['net_interfaces'].keys() | list }}"

    - name: Salva facts su file JSON locale
      ansible.builtin.copy:
        content: "{{ ansible_facts | to_nice_json }}"
        dest: "../backup/{{ inventory_hostname }}-facts.json"
      delegate_to: localhost
```

---

## SOLUZIONE G.1 — git init, add, commit

```bash
cd ~/ENCOR-MOD34

# Inizializza repository
git init
# Crea la directory .git/ con tutta la struttura del repository

# Configura identità (salvata in .git/config per questo repo)
git config user.name "Student ENCOR"
git config user.email "student@encor.lab"

# Aggiungi file specifici (evitare git add -A che include .venv/)
git add ansible/inventory.ini
git add ansible/gather_facts.yml
git add ansible/push_config.yml
git add ansible/ios_facts.yml
git add scripts/

# Verifica staging
git status
# Changes to be committed:
#   new file:   ansible/gather_facts.yml
#   new file:   ansible/inventory.ini
#   ...

# Crea il commit
git commit -m "feat: aggiunge playbook Ansible MOD-34 e script Python"
# [main (root-commit) a1b2c3d] feat: aggiunge playbook ...

# Verifica
git log --oneline
# a1b2c3d feat: aggiunge playbook Ansible MOD-34 e script Python
```

**Nota docente — Buone pratiche commit message:**

Usare il prefisso convenzionale:
- `feat:` — nuova funzionalità
- `fix:` — correzione bug
- `docs:` — documentazione
- `refactor:` — refactoring senza cambio funzionale

---

## SOLUZIONE G.2 — git log, diff, status

```bash
# Aggiungi un commento al file
echo "# Aggiornato: $(date)" >> ansible/push_config.yml

# Stato del working tree
git status
# modified: ansible/push_config.yml

# Diff working tree vs ultimo commit
git diff ansible/push_config.yml
# + # Aggiornato: Thu May 14 12:34:56 UTC 2026

# Staging e diff staging vs commit
git add ansible/push_config.yml
git diff --staged

# Commit
git commit -m "docs: aggiunge commento data aggiornamento a push_config.yml"

# Storico formattato
git log --oneline
# b2c3d4e docs: aggiunge commento ...
# a1b2c3d feat: aggiunge playbook ...

# Dettaglio di un commit specifico
git show a1b2c3d     # sostituire con l'hash reale
```

---

## SOLUZIONE G.3 — git push su Gitea

```bash
# Prima: creare il repository "ENCOR-MOD34" su Gitea
# http://192.168.122.1 → + (New repository) → nome: ENCOR-MOD34 → Create

# Aggiungi il remote
git remote add origin http://192.168.122.1/git/ENCOR-MOD34.git

# Verifica
git remote -v
# origin  http://192.168.122.1/git/ENCOR-MOD34.git (fetch)
# origin  http://192.168.122.1/git/ENCOR-MOD34.git (push)

# Push (-u imposta il tracking del branch remoto)
git push -u origin main
# Username: student
# Password: student

# Verifica su Gitea: http://192.168.122.1/student/ENCOR-MOD34
```

---

## SOLUZIONE G.4 — Branch workflow

```bash
# Crea e spostati sul branch feature
git checkout -b feature/ntp-playbook
# Switched to a new branch 'feature/ntp-playbook'

git branch
# * feature/ntp-playbook
#   main

# Crea il nuovo playbook
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

# Torna su main e merge
git checkout main
git merge feature/ntp-playbook
# Fast-forward merge (nessun commit su main nel frattempo → nessun conflitto)

# Grafo dei branch
git log --oneline --graph
# *   c3d4e5f (HEAD -> main) Merge branch 'feature/ntp-playbook'
# |\
# | * d4e5f6g feat: aggiunge playbook configurazione NTP
# |/
# * b2c3d4e docs: aggiunge commento...
# * a1b2c3d feat: aggiunge playbook...

# Elimina il branch feature (già mergiato)
git branch -d feature/ntp-playbook

# Push
git push origin main
```

---

## NOTE DIDATTICHE

### Ansible vs Chef vs SaltStack — Tabella riepilogo esame

| Caratteristica | Ansible | Chef | SaltStack |
|----------------|---------|------|-----------|
| Architettura | Agentless | Agent-based (pull) | Agent o agentless |
| Linguaggio | YAML | Ruby | YAML/Jinja2 |
| Modello esecuzione | Push | Pull | Push o event-driven |
| Curva apprendimento | Bassa | Alta | Media |
| Uso in rete | ★★★★★ | ★★ | ★★★ |
| Idempotency | Si (moduli) | Si | Si |

### Errori comuni da correggere in aula

1. `gather_facts: yes` con `network_cli` → errore; impostare sempre `gather_facts: no`
2. Usare `ios_config` per banner → `changed=1` ad ogni run; usare `ios_banner`
3. `git add -A` o `git add .` nel root del progetto → include `.venv/` (gigabyte di file); specificare i file/directory esplicitamente
4. Dimenticare `ansible-become=yes` → i comandi vengono eseguiti in user mode, `ios_config` fallisce senza enable
5. Push senza aver creato il repository su Gitea → `remote: Repository not found`
