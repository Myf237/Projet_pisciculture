---
name: cloturer-session
description: Clôture une session de travail du projet Pisciculture IA — bilan réalisé contre plan, audit croisé des journaux de traçabilité et régularisation des écarts, mise à jour du tableau de bord et des risques, prochaine action. À utiliser en fin de chaque session.
---

# Clôturer la session

Exécuté par l'**orchestrateur**.

## 1. Bilan

- Retrouver le plan dans l'entrée « Ouverture de session » du journal du jour.
- Lister les entrées du jour (`logs/agents/journal/AAAA-MM-JJ.md`) : fait, non fait, échecs.
- Situer l'avancement par rapport à `docs/05-TIMELINE.md` (à l'heure / retard / avance).

## 2. Audit de traçabilité

- `python .claude/hooks/audit_trace.py` (jour courant).
- Pour chaque écart : l'agent concerné (ou l'orchestrateur pour ses propres actions) ajoute l'entrée manquante — **nouvelle entrée**, jamais de réécriture — puis relancer l'audit.
- Écart impossible à expliquer → le consigner tel quel (entrée ÉCHEC) et le signaler à l'humain.

## 3. Mise à jour du suivi

Déléguer à `doc-keeper` (entrée DÉLÉGATION) :
- `docs/11-TABLEAU_DE_BORD.md` : statuts, décisions en attente, blocages, **prochaine action** précise ;
- `docs/08-REGISTRE_RISQUES.md` : si un risque est apparu, a évolué ou est survenu pendant la session.

## 4. État git

- `git status --short` : commiter le travail terminé et testé restant (commits atomiques, trailers — `.claude/rules/git-workflow.md`), dont le commit de suivi `docs(suivi)` (journal, tableau de bord, `actions.jsonl`).
- `git push -u origin <branche>` : la branche de travail est toujours poussée en fin de session. Jamais de push sur `main`.
- Signaler une PR en attente de fusion (G2).

## 5. Journaliser et rendre compte

- Entrée `orchestrateur · DÉCISION` : « Clôture de session », bilan en une ligne, verdict d'audit, prochaine action.
- Présenter à l'humain :

```
## Clôture — AAAA-MM-JJ (Jour N)
- Réalisé : … (preuves)
- Non réalisé / reporté : … (raison)
- Traçabilité : ✅ conforme | ❌ écarts : …
- Décisions en attente : …
- Avancement : … par rapport au planning
- Prochaine session commence par : …
```
