# Soluzione Commentata — MOD-31: ACL & CoPP

> **Uso:** riservato al docente — non distribuire agli studenti

---

## T1 — Standard ACL

### R1

```
R1# configure terminal

! ACL standard: identifica solo il source IP.
! "permit 10.0.12.2 0.0.0.0" = host specifico R2 (wildcard /32).
! Alternativa: "permit host 10.0.12.2"
R1(config)# ip access-list standard ACL-PERMIT-R2
R1(config-std-nacl)# permit 10.0.12.2 0.0.0.0
! "deny any log" esplicito: equivalente all'implicit deny ma mostra i contatori in log.
R1(config-std-nacl)# deny any log
R1(config-std-nacl)# exit

! Applica INBOUND: filtra il traffico che arriva da R2 verso R1.
! Posizionamento vicino alla DESTINAZIONE (R1) — regola per Standard ACL.
R1(config)# interface Ethernet0/0.12
R1(config-if)# ip access-group ACL-PERMIT-R2 in
R1(config-if)# exit

R1(config)# end
```

### Verifica T1

```
R1# show ip interface Ethernet0/0.12 | include access
! Inbound access list is ACL-PERMIT-R2

R2# ping 1.1.1.1 source 10.0.12.2   → !!!!!  (permesso)
R2# ping 1.1.1.1 source 2.2.2.2     → UUUUU  (bloccato)

R1# show ip access-lists ACL-PERMIT-R2
! Mostra match count per ogni riga
```

### Cleanup T1

```
R1(config)# interface Ethernet0/0.12
R1(config-if)# no ip access-group ACL-PERMIT-R2 in
R1(config)# no ip access-list standard ACL-PERMIT-R2
```

---

## T2 — Extended ACL

### R1

```
R1# configure terminal

R1(config)# ip access-list extended ACL-PROTECT-R1

! Permette SSH (TCP 22) — accesso management autorizzato:
R1(config-ext-nacl)# permit tcp any any eq 22

! Permette ICMP — necessario per ping/traceroute e diagnostica:
R1(config-ext-nacl)# permit icmp any any

! CRITICO: permette OSPF (proto 89) — senza questa riga, OSPF cade dopo 40s (dead interval).
! È l'errore più comune quando si applica una Extended ACL su un'interfaccia con OSPF.
R1(config-ext-nacl)# permit ospf any any

! Blocca tutto il resto, incluso Telnet (TCP 23):
R1(config-ext-nacl)# deny ip any any log
R1(config-ext-nacl)# exit

! Applica INBOUND vicino alla SORGENTE — regola per Extended ACL.
! Così blocchiamo Telnet prima che entri nella rete, risparmiando banda.
R1(config)# interface Ethernet0/0.12
R1(config-if)# ip access-group ACL-PROTECT-R1 in
R1(config-if)# exit

R1(config)# end
```

### Verifica T2

```
R2# ssh -v 2 -l admin 10.0.12.1     → accesso OK (TCP 22 permesso)
R2# telnet 10.0.12.1                 → bloccato (TCP 23 → deny ip)
R2# ping 1.1.1.1                     → !!!!! (ICMP permesso)
R1# show ip ospf neighbor            → R2 FULL (OSPF permesso)

R1# show ip access-lists ACL-PROTECT-R1
! permit tcp ... eq 22: N matches
! permit icmp: N matches
! permit ospf: N matches (OSPF hello ogni 10s)
! deny ip: N matches (Telnet bloccato)
```

---

## T3 — Reflexive ACL e IPv6 ACL

### R1 — Reflexive

```
R1# configure terminal

! Prima rimuovere ACL-PROTECT-R1:
R1(config)# interface Ethernet0/0.12
R1(config-if)# no ip access-group ACL-PROTECT-R1 in
R1(config)# no ip access-list extended ACL-PROTECT-R1

! ACL outbound: classifica il traffico in uscita da R1 e crea entry reflect.
! "reflect SESS-TCP" → ogni sessione TCP outbound crea una entry temporanea.
R1(config)# ip access-list extended OUT-REFLEXIVE
R1(config-ext-nacl)# permit tcp any any reflect SESS-TCP
R1(config-ext-nacl)# permit icmp any any reflect SESS-ICMP
R1(config-ext-nacl)# permit ospf any any
R1(config-ext-nacl)# exit

! ACL inbound: "evaluate SESS-TCP" ammette solo il traffico di risposta delle sessioni aperte.
! Se una sessione TCP verso R2 è stata aperta da R1, il traffico di ritorno è permesso.
! Nessuna sessione inbound non richiesta può entrare.
R1(config)# ip access-list extended IN-REFLEXIVE
R1(config-ext-nacl)# evaluate SESS-TCP
R1(config-ext-nacl)# evaluate SESS-ICMP
R1(config-ext-nacl)# permit ospf any any
R1(config-ext-nacl)# deny ip any any log
R1(config-ext-nacl)# exit

! Applica:
R1(config)# interface Ethernet0/0.12
R1(config-if)# ip access-group OUT-REFLEXIVE out
R1(config-if)# ip access-group IN-REFLEXIVE in
R1(config-if)# exit

R1(config)# end
```

### R1 — IPv6 ACL

```
R1# configure terminal

! IPv6 ACL (sempre named, sempre extended):
! Nota: "permit 89" = permette il protocollo OSPFv3 per IPv6 (stessa sintassi di ACL IPv4).
R1(config)# ipv6 access-list ACL-V6-INBOUND
R1(config-ipv6-acl)# permit tcp any any eq 22
R1(config-ipv6-acl)# permit icmp any any
R1(config-ipv6-acl)# permit 89 any any
R1(config-ipv6-acl)# deny ipv6 any any log
R1(config-ipv6-acl)# exit

! Applica — diverso da IPv4: usa "ipv6 traffic-filter" invece di "ip access-group":
R1(config)# interface Ethernet0/0.12
R1(config-if)# ipv6 traffic-filter ACL-V6-INBOUND in
R1(config-if)# exit

R1(config)# end
```

### Verifica T3

```
! Reflexive: da R1 apri una sessione verso R2
R1# telnet 2.2.2.2  (o ssh -v 2 -l admin 2.2.2.2)
! Lascia la sessione aperta e verifica le entry dinamiche:
R1# show ip access-lists IN-REFLEXIVE
! "Dynamic reflect entry" per SESS-TCP apparirà

! IPv6:
R2# ping 2001:db8:12::1              → !!!!!  (ICMP v6 permesso)
R1# show ipv6 access-list ACL-V6-INBOUND
```

---

## T4 — CoPP

### R1

```
R1# configure terminal

! ACL per classificazione:
R1(config)# ip access-list extended ACL-OSPF
R1(config-ext-nacl)# permit ospf any any
R1(config-ext-nacl)# exit

R1(config)# ip access-list extended ACL-SSH
R1(config-ext-nacl)# permit tcp any any eq 22
R1(config-ext-nacl)# exit

R1(config)# ip access-list extended ACL-SNMP
R1(config-ext-nacl)# permit udp any any eq 161
R1(config-ext-nacl)# exit

R1(config)# ip access-list extended ACL-ICMP
R1(config-ext-nacl)# permit icmp any any
R1(config-ext-nacl)# exit

! Class-map CRITICAL: routing protocols — massima priorità:
R1(config)# class-map match-any CM-CRITICAL
R1(config-cmap)# match access-group name ACL-OSPF
R1(config-cmap)# exit

! Class-map MANAGEMENT: traffico di gestione:
R1(config)# class-map match-any CM-MANAGEMENT
R1(config-cmap)# match access-group name ACL-SSH
R1(config-cmap)# match access-group name ACL-SNMP
R1(config-cmap)# exit

! Class-map ICMP: diagnostica — bassa priorità:
R1(config)# class-map match-any CM-ICMP
R1(config-cmap)# match access-group name ACL-ICMP
R1(config-cmap)# exit

! Policy-map CoPP:
R1(config)# policy-map PM-COPP
R1(config-pmap)# class CM-CRITICAL
! OSPF: 512 kbps è ampio per traffico di routing reale.
! Police conform-action transmit / exceed-action drop sono i default.
R1(config-pmap-c)# police rate 512000 bps burst 64000
R1(config-pmap-c)# exit
R1(config-pmap)# class CM-MANAGEMENT
! SSH: 256 kbps. Una sessione SSH usa molto meno; il burst gestisce picchi.
R1(config-pmap-c)# police rate 256000 bps burst 32000
R1(config-pmap-c)# exit
R1(config-pmap)# class CM-ICMP
! ICMP flood limitato a 64 kbps:
R1(config-pmap-c)# police rate 64000 bps burst 8000
R1(config-pmap-c)# exit
R1(config-pmap)# class class-default
! Tutto il non classificato: drop.
! ATTENZIONE: verificare che tutti i protocolli necessari siano nelle classi sopra.
R1(config-pmap-c)# drop
R1(config-pmap-c)# exit
R1(config-pmap)# exit

! Applica al control plane (non su un'interfaccia — questo è il punto chiave di CoPP):
R1(config)# control-plane
R1(config-cp)# service-policy input PM-COPP
R1(config-cp)# exit

R1(config)# end
```

### Verifica T4

```
R1# show policy-map control-plane
! Mostra PM-COPP applicata al control plane con contatori per ogni classe

R1# show ip ospf neighbor
! R2 deve essere ancora FULL (OSPF permesso da CM-CRITICAL)

R2# ping 1.1.1.1 repeat 100
R1# show policy-map control-plane
! CM-ICMP: conformed/exceeded packets aggiornati
```

---

## Note Varianti & Alternative

### CoPP con BGP

In ambienti BGP, aggiungere TCP 179 alla classe CRITICAL:
```
R1(config)# ip access-list extended ACL-BGP
R1(config-ext-nacl)# permit tcp any any eq 179
R1(config-ext-nacl)# permit tcp any eq 179 any
R1(config-ext-nacl)# exit

R1(config)# class-map match-any CM-CRITICAL
R1(config-cmap)# match access-group name ACL-OSPF
R1(config-cmap)# match access-group name ACL-BGP
```

### Named vs Numbered ACL

Le Extended ACL numbered (100-199) sono equivalenti alle named. Le named sono preferite perché:
- Più leggibili (nome descrittivo)
- Permettono di modificare singole righe con sequencing (no delete+recreate)
- Supportano `no seq-number` per rimuovere una riga specifica
