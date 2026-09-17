---
name: demarrer-session
description: Ouvre une session de travail du projet Pisciculture IA — lit l'état du projet (tableau de bord, dernier journal, jalon actif, planning), audite la traçabilité de la veille, détecte retards, blocages et décisions ouvertes, propose le plan de session et journalise l'ouverture. À utiliser au début de chaque session.
---

# Démarrer une session

Exécuté par l'**orchestrateur** (session principale).

## 1. Situer la session

- Date du jour et jour du planning : J1 = 2026-09-17 … J7 = 2026-09-23 (`docs/05-TIMELINE.md`). Avant J1 : phase de préparation.
- Lire `docs/11-TABLEAU_DE_BORD.md` : jalon actif, statuts, décisions en attente, blocages, prochaine action.
- Lire le fichier le plus récent de `logs/agents/journal/` (fin de la session précédente).
- Lire les critères du jalon actif dans `docs/04-JALONS_VALIDATION.md` et le programme du jour dans `docs/05-TIMELINE.md`.
- Lire le dernier rapport de `reports/validations/` s'il existe (réserves en cours).

## 2. Contrôler

- Traçabilité de la dernière journée travaillée : `python .claude/hooks/audit_trace.py --date <AAAA-MM-JJ>`. Écarts → à régulariser en premier (nouvelles entrées, jamais de réécriture).
- Git : `git fetch origin` ; branche courante (jamais `main` pour travailler) ; travail non commité (`git status --short`) ; commits non poussés ; PR ouvertes en attente de G2. Si le jalon actif n'a pas de branche : `git switch -c feat/jalon-N-<sujet> --no-track origin/main` (`.claude/rules/git-workflow.md`).
- Retard : jalon actif comparé au jalon attendu ce jour-là.
- **Règle du Jour 4** : fin J4 (ou après) avec Jalon 3 non validé → préparer la proposition de coupe de la prédiction de croissance (G3).
- Décisions ouvertes (A1–A5, ADR « Proposé ») qui bloquent le jalon actif.

## 3. Présenter à l'humain

```
## Session du AAAA-MM-JJ — Jour N / Jalon actif : N
**État :** (à l'heure / en retard de … / en avance) — dernier résultat marquant
**À régulariser :** (écarts de traçabilité, réserves de validation, travail non commité)
**Décisions à trancher maintenant (G1/G3) :** option recommandée + impact pour chacune
**Plan de session :**
1. <agent> — <tâche> — critère visé (docs/04 Jalon N)
2. …
**Points de validation humaine prévus :**
```

## 4. Journaliser et lancer

- Entrée de journal `orchestrateur · DÉCISION` : « Ouverture de session — plan », avec le plan en résumé et la référence au jalon.
- S'il n'y a pas de décision bloquante, enchaîner directement sur la première délégation du plan (étape RÉALISER du workflow), en journalisant chaque délégation (type DÉLÉGATION).
- S'il y en a une, attendre la réponse de l'humain avant de déléguer les tâches qu'elle bloque ; les tâches non bloquées peuvent démarrer.
