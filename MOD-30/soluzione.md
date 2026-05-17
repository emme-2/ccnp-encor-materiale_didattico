# Soluzione Commentata — MOD-30: Device Security & AAA

> **Uso:** riservato al docente — non distribuire agli studenti

---

## T1 — Hardening Accesso Locale

### R1

```
R1# configure terminal

! Enable secret: hash MD5 (più sicuro di "enable password" che usa reversible encryption)
R1(config)# enable secret Cisco@123

! Domain name necessario per la generazione delle chiavi RSA:
R1(config)# ip domain-name lab.encor

! Genera chiavi RSA 2048 bit — SSHv2 richiede minimo 768 bit, 2048 raccomandato:
R1(config)# crypto key generate rsa modulus 2048

! Forza SSHv2 — SSHv1 è vulnerabile a MITM e deprecato:
R1(config)# ip ssh version 2

! Timeout authentication SSH: disconnette se il client non completa il login in 60s:
R1(config)# ip ssh time-out 60

! Banner di accesso (avviso legale — comparirà prima del login):
! Il delimitatore ^ può essere qualsiasi carattere non presente nel testo.
R1(config)# banner motd ^
*** ACCESSO AUTORIZZATO SOLO A PERSONALE ABILITATO ***
Ogni attività è registrata. Disconnettersi se non autorizzati.
^

! Console: timeout 5 minuti, logging synchronous evita che i log interrompano l'input:
R1(config)# line console 0
R1(config-line)# exec-timeout 5 0
R1(config-line)# logging synchronous
R1(config-line)# exit

! VTY: timeout 10 min, blocca Telnet (solo SSH accettato):
! "transport input ssh" su IOS < 15.x si scrive "transport input ssh" (senza v2 — gestito da ip ssh version 2)
R1(config)# line vty 0 4
R1(config-line)# exec-timeout 10 0
R1(config-line)# transport input ssh
R1(config-line)# exit

R1(config)# end
```

### Verifica T1

```
! Verifica SSHv2 attivo:
R1# show ip ssh
! SSH Enabled - version 2.0

! Da R2 — test Telnet bloccato:
R2# telnet 10.12.0.1
! Connection refused

! Da R2 — test SSH (ancora senza utente → fallisce con auth error, non con connection refused):
R2# ssh -v 2 -l test 10.12.0.1
! Chiave RSA scambiata correttamente, poi "Authentication failed" (ok — SSH funziona)
```

---

## T2 — AAA Locale

### R1

```
R1# configure terminal

! Abilita il framework AAA — ATTENZIONE: cambia immediatamente il comportamento di autenticazione.
! Dopo questo comando, "login local" non è più sufficiente senza le liste AAA.
R1(config)# aaa new-model

! Utente amministratore (privilege 15 = accesso completo):
R1(config)# username admin privilege 15 secret Cisco@123

! Utente viewer (privilege 1 = base):
R1(config)# username viewer privilege 1 secret Viewer@456

! Lista di autenticazione "LOGIN-LOCAL":
! "local" = usa il database locale degli username.
! "none" = se "local" fallisce (database vuoto), consenti comunque l'accesso (ATTENZIONE in prod!).
! In produzione usare "local none" con cautela; meglio "local" senza fallback none.
R1(config)# aaa authentication login LOGIN-LOCAL local

! Autorizzazione exec: determina se l'utente può entrare nella modalità EXEC.
! "local" = usa le info del database locale (privilege level dell'username).
R1(config)# aaa authorization exec DEFAULT local

! Applica la lista di autenticazione alle linee VTY:
R1(config)# line vty 0 4
R1(config-line)# login authentication LOGIN-LOCAL
R1(config-line)# exit

! La console NON usa AAA (backdoor di emergenza):
R1(config)# line console 0
R1(config-line)# login local
R1(config-line)# exit

R1(config)# end
```

### Verifica T2

```
! SSH con admin (privilege 15):
R2# ssh -v 2 -l admin 10.12.0.1
! Password: Cisco@123 → accesso con prompt R1#

R1# show privilege
! Current privilege level is 15

! SSH con viewer (privilege 1):
R2# ssh -v 2 -l viewer 10.12.0.1
! Password: Viewer@456 → accesso con prompt R1>

R1# show privilege
! Current privilege level is 1
```

---

## T3 — RADIUS con FreeRADIUS

### R1

```
R1# configure terminal

! Definisci il server RADIUS (nuovo metodo IOS 15+):
! ! RADIUS server: 192.168.122.100
! ! Modifica questo IP se l'ambiente e' diverso
R1(config)# radius server FREERADIUS
R1(config-radius-server)# address ipv4 192.168.122.100 auth-port 1812 acct-port 1813
! Shared secret: deve corrispondere a clients.conf su FreeRADIUS
R1(config-radius-server)# key RadiusSecret123
R1(config-radius-server)# exit

! Server group: raggruppa uno o più server RADIUS:
R1(config)# aaa group server radius RADIUS-SERVERS
R1(config-sg-radius)# server name FREERADIUS
R1(config-sg-radius)# exit

! Aggiorna la lista di autenticazione: RADIUS prima, poi locale come fallback.
! Se RADIUS non risponde (timeout), il router prova il database locale.
R1(config)# aaa authentication login LOGIN-LOCAL group RADIUS-SERVERS local

! Autorizzazione exec: usa RADIUS per recuperare privilege level (cisco-avpair).
! "if-authenticated" = se l'auth ha avuto successo, permettere exec senza ulteriore check.
R1(config)# aaa authorization exec DEFAULT group RADIUS-SERVERS local if-authenticated

R1(config)# end
```

### FreeRADIUS — configurazione di riferimento

> Non eseguire su IOS — sono i file di configurazione del container FreeRADIUS.

```
# /etc/freeradius/3.0/clients.conf
client R1-NAS {
    ipaddr = 192.168.122.10
    secret = RadiusSecret123
    shortname = R1
}

# /etc/freeradius/3.0/users
radiususer Cleartext-Password := "Radius@789"
    cisco-avpair = "shell:priv-lvl=15",
    Service-Type = NAS-Prompt-User
```

### Verifica T3

```
! Verifica connettività:
R1# ping 192.168.122.100

! SSH con utente RADIUS:
R2# ssh -v 2 -l radiususer 10.12.0.1
! Password: Radius@789

! Verifica accounting e contatori RADIUS:
R1# show aaa servers
! Atteso: counters auth requests/accepts per 192.168.122.100

! Test fallback: con RADIUS irraggiungibile, login con admin (locale) deve funzionare
```

---

## T4 — RBAC con Privilege Levels

### R1

```
R1# configure terminal

! Livello 5 — Read-Only (monitoring):
! "privilege exec level 5 show" assegna il comando "show" al livello 5.
! Tutti i sub-comandi di "show" sono disponibili di conseguenza.
R1(config)# privilege exec level 5 show
R1(config)# privilege exec level 5 ping
R1(config)# privilege exec level 5 traceroute

! Livello 10 — Operativo (aggiunge clear e configure terminal):
R1(config)# privilege exec level 10 show
R1(config)# privilege exec level 10 ping
R1(config)# privilege exec level 10 traceroute
R1(config)# privilege exec level 10 clear
R1(config)# privilege exec level 10 configure terminal

! Crea gli utenti con i rispettivi livelli:
R1(config)# username readonly privilege 5 secret ReadOnly@5
R1(config)# username operator privilege 10 secret Operator@10

R1(config)# end
```

### Verifica T4

```
! SSH come readonly (privilege 5):
R2# ssh -v 2 -l readonly 10.12.0.1
R1# show privilege
! Current privilege level is 5

R1> show ip route      ! OK
R1> configure terminal ! Errore: % Invalid input detected

! SSH come operator (privilege 10):
R2# ssh -v 2 -l operator 10.12.0.1
R1# show privilege
! Current privilege level is 10

R1# configure terminal ! OK
```

---

## Note Varianti & Alternative

### Parser View (alternativa ai privilege levels)

Per un controllo più granulare dei comandi (es. permettere `show ip route` ma non `show running-config`):

```
! Abilita parser view con AAA attivo:
R1(config)# aaa authorization commands 15 DEFAULT local

! Crea una view "READONLY":
R1# enable view
R1# configure terminal
R1(config)# parser view READONLY
R1(config-view)# secret ReadView@123
R1(config-view)# commands exec include show
R1(config-view)# commands exec include ping
R1(config-view)# exit
```

### TACACS+ invece di RADIUS

Se l'ambiente usa TACACS+ (Cisco ISE):
```
R1(config)# tacacs server ISE
R1(config-server-tacacs)# address ipv4 192.168.122.200
R1(config-server-tacacs)# key TacacsSecret
R1(config-server-tacacs)# exit

R1(config)# aaa group server tacacs+ TACACS-SERVERS
R1(config-sg-tacacs+)# server name ISE
R1(config-sg-tacacs+)# exit

R1(config)# aaa authentication login LOGIN-LOCAL group TACACS-SERVERS local
```
