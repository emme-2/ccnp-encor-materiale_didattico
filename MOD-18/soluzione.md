# Soluzione Commentata — MOD-18: IPSec IKEv2 & VTI

> **Uso:** riservato al docente — non distribuire agli studenti
> **Prerequisito:** MOD-17 completato — VRF CUST-A, tunnel GRE, route statiche operative

---

## Configurazione completa — HUB

```
! ════════════════════════════════════════════════════════════════════════
! IKEv2 PROPOSAL — algoritmi per il canale di controllo IKE (Phase 1)
! ════════════════════════════════════════════════════════════════════════
crypto ikev2 proposal PROP-ENCOR
 encryption aes-cbc-256   ! AES 256-bit CBC — cifratura Phase 1
 integrity sha256          ! HMAC-SHA256 — integrita' Phase 1
 group 14                  ! Diffie-Hellman 2048-bit — scambio chiavi

! ════════════════════════════════════════════════════════════════════════
! IKEv2 POLICY — lega il proposal alla negoziazione IKE
! Piu' policy con priorita' diverse = meccanismo di fallback
! ════════════════════════════════════════════════════════════════════════
crypto ikev2 policy POL-ENCOR
 proposal PROP-ENCOR

! ════════════════════════════════════════════════════════════════════════
! IKEv2 KEYRING — PSK per ogni peer, identificato dal suo Lo0 (NBMA)
! IMPORTANTE: l'IP peer e' il Loopback0, non l'IP tunnel overlay
! ════════════════════════════════════════════════════════════════════════
crypto ikev2 keyring KR-ENCOR
 peer SP1
  address 198.51.100.254
  pre-shared-key cisco123
 !
 peer SP2
  address 203.0.113.254
  pre-shared-key cisco123

! ════════════════════════════════════════════════════════════════════════
! IKEv2 PROFILE — collega identita' peer, autenticazione e keyring
! match identity: l'IP sorgente dei messaggi IKE del peer remoto
! authentication: metodo di autenticazione bidirezionale
! ════════════════════════════════════════════════════════════════════════
crypto ikev2 profile PROF-ENCOR
 match identity remote address 198.51.100.254 255.255.255.255
 match identity remote address 203.0.113.254 255.255.255.255
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-ENCOR

! ════════════════════════════════════════════════════════════════════════
! TRANSFORM-SET — algoritmi per il canale dati ESP (Phase 2)
! esp-aes 256: cifratura ESP AES-256-CBC
! esp-sha256-hmac: integrita' ESP HMAC-SHA256
! mode tunnel: cifra l'intero pacchetto IP (header + payload)
! ════════════════════════════════════════════════════════════════════════
crypto ipsec transform-set TS-ENCOR esp-aes 256 esp-sha256-hmac
 mode tunnel

! ════════════════════════════════════════════════════════════════════════
! IPSEC PROFILE — lega transform-set e IKEv2 profile
! Questo oggetto viene applicato all'interfaccia tunnel (VTI)
! ════════════════════════════════════════════════════════════════════════
crypto ipsec profile IPSEC-PROF
 set transform-set TS-ENCOR
 set ikev2-profile PROF-ENCOR

! ════════════════════════════════════════════════════════════════════════
! TUNNEL PROTECTION — applicazione su tunnel GRE esistenti
! Aggiunta in fondo alla config del tunnel (non toccare altri parametri)
! ════════════════════════════════════════════════════════════════════════
interface Tunnel101
 tunnel protection ipsec profile IPSEC-PROF
!
interface Tunnel102
 tunnel protection ipsec profile IPSEC-PROF
```

---

## Configurazione completa — SP1

```
! SP1 e' uno spoke: nel keyring ha solo il peer HUB
! Nel profile: match identity solo per HUB

crypto ikev2 proposal PROP-ENCOR
 encryption aes-cbc-256
 integrity sha256
 group 14

crypto ikev2 policy POL-ENCOR
 proposal PROP-ENCOR

crypto ikev2 keyring KR-ENCOR
 peer HUB
  address 192.0.2.254      ! Lo0 di HUB
  pre-shared-key cisco123

crypto ikev2 profile PROF-ENCOR
 match identity remote address 192.0.2.254 255.255.255.255
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-ENCOR

crypto ipsec transform-set TS-ENCOR esp-aes 256 esp-sha256-hmac
 mode tunnel

crypto ipsec profile IPSEC-PROF
 set transform-set TS-ENCOR
 set ikev2-profile PROF-ENCOR

interface Tunnel101
 tunnel protection ipsec profile IPSEC-PROF
```

---

## Sequenza diagnostica — show commands con output atteso

```
! ── PRIMA del trigger (nessuna SA attiva) ────────────────────────────
HUB# show crypto ikev2 sa
! (output vuoto — nessuna SA negoziata)

HUB# show crypto isakmp sa
! (output vuoto)

! ── TRIGGER — forza negoziazione IKE ─────────────────────────────────
HUB# ping vrf CUST-A 10.1.2.1 source Loopback1 repeat 5

! ── DOPO Phase 1 completata ──────────────────────────────────────────
HUB# show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst             src             state     conn-id  status
198.51.100.254  192.0.2.254     QM_IDLE   1001     ACTIVE
203.0.113.254   192.0.2.254     QM_IDLE   1002     ACTIVE
! QM_IDLE = ISAKMP SA (Phase 1) attiva e pronta per Phase 2

HUB# show crypto ikev2 sa
IPv4 Crypto IKEv2 SA
Tunnel-id  Local                Remote               fvrf/ivrf   Status
1          192.0.2.254/4500     198.51.100.254/4500  none/CUST-A READY
2          192.0.2.254/4500     203.0.113.254/4500   none/CUST-A READY
! READY = IKEv2 SA (Phase 1) completata

! ── DOPO Phase 2 completata (trigger con traffico applicativo) ────────
HUB# show crypto ipsec sa | include encaps|decaps
    #pkts encaps: 5, #pkts encrypt: 5, #pkts digest: 5
    #pkts decaps: 5, #pkts decrypt: 5, #pkts verify: 5
! encaps/decaps > 0 = traffico ESP correttamente cifrato e verificato

HUB# show crypto engine connections active
  ID  Interface   IP-Address    State   Algorithm
  1   Tunnel101   192.0.2.254   set     AES+SHA256
  2   Tunnel102   192.0.2.254   set     AES+SHA256
```

---

## Note varianti e alternative

**PSK vs PKI in produzione**

In questo lab si usa Pre-Shared Key (`pre-shared-key cisco123`) per semplicita'. In ambienti di produzione si preferisce PKI con certificati X.509 perche':
- Non richiede la condivisione manuale del segreto tra tutti i peer
- Scalabile a N spoke senza modificare il keyring dell'HUB
- Revoca del certificato immediata senza riconfigurare tutti i router

**DH Group: 14 vs 19/20**

Group 14 (2048-bit MODP) e' il minimo raccomandato oggi. I Group 19 (256-bit ECC) e 20 (384-bit ECC) offrono sicurezza equivalente con minore carico computazionale — preferibili su piattaforme con hardware crypto (ASR, ISR 4000). IOU non ha hardware crypto, quindi la differenza di performance non e' misurabile in lab.

**SHA-256 vs SHA-384/512**

SHA-256 e' sufficiente per tutti i deployment attuali. SHA-384/512 sono usati in ambienti che richiedono conformita' NSA Suite B (governo USA) o in contesti di sicurezza elevata. All'esame ENCOR, il livello di dettaglio richiesto e' SHA-256 vs SHA-1 (quest'ultimo e' da evitare).

**Perche' l'IP peer nel keyring e' il Loopback0?**

IKEv2 negozia tra gli IP dell'outer header dei messaggi IKE. Questi messaggi vengono inviati dagli IP fisici dei router — cioe' i Loopback0 che sono anche i tunnel source/destination nell'underlay. L'IP tunnel overlay (172.16.x.x) non esiste ancora quando IKE negozia — viene creato solo dopo che la SA e' stabilita.
