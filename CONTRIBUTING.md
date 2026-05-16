# Contributing — CCNP ENCOR Materiale Didattico

## Branch Strategy
- `main` — versione stabile, aggiornata solo a ogni release
- `develop` — branch di lavoro, tutti i commit vanno qui

## Workflow Standard
1. Lavora sempre su `develop`
2. Per ogni nuovo modulo o modifica significativa:
   ```
   git add MOD-xx/
   git commit -m "feat: MOD-xx descrizione breve"
   ```
3. Quando un milestone è completo, merge develop → main

## Convenzione Commit Messages
```
[tipo]: MOD-xx descrizione breve
```

Tipi:
| Tipo | Quando usarlo |
|------|---------------|
| feat | Nuovo modulo o contenuto |
| fix | Correzione errore tecnico o didattico |
| update | Aggiornamento modulo esistente |
| template | Modifiche a CLAUDE.md o template |
| docs | README, ROADMAP, MAPPATURA, WBS |
| chore | Git, CI, struttura repo |

Esempi:
```
feat: MOD-04 OSPF Troubleshooting completo
fix: MOD-11 corretto piano indirizzi PE1
update: MOD-17 aggiunta sezione Exam Tips
template: Mermaid sostituisce ASCII art in tutti i moduli
docs: WBS aggiornato Fase 1 completata
```

## Release
Le release sono taggate su main dopo merge da develop:
```
git checkout main
git merge develop
git tag -a v1.0 -m "Release v1.0 — 35 moduli completi"
git push origin main --tags
```
GitHub genera automaticamente il ZIP scaricabile dagli studenti.
