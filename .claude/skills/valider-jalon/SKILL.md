---
name: valider-jalon
description: Fait vérifier un jalon du projet Pisciculture IA par le qa-validator (critères de docs/04 avec preuves), gère les boucles de correction (2 maximum), ouvre ou met à jour la pull request du jalon, soumet le go/no-go à l'humain et, sur accord, fusionne la PR, tague le jalon et met à jour la documentation. À utiliser quand l'agent réalisateur annonce un jalon terminé.
argument-hint: "<numéro du jalon, 1 à 6>"
---

# Valider le Jalon $ARGUMENTS

Exécuté par l'**orchestrateur**. Si `$ARGUMENTS` n'est pas un numéro de 1 à 6, demander lequel.

## 1. Préparer

- Déterminer l'itération : `reports/validations/jalon-$ARGUMENTS.md` absent → itération 1 ; présent avec verdict NON VALIDÉ → itération suivante.
- **Plus de 2 itérations échouées → ne pas relancer** : escalader à l'humain (options : corriger autrement, accepter avec réserves, replanifier).
- Rassembler : comptes rendus des agents réalisateurs, jours à auditer depuis la dernière validation, décisions tranchées pendant le jalon.
- Git (`.claude/rules/git-workflow.md`) : tout le travail du jalon est commité sur la branche `feat/jalon-$ARGUMENTS-<sujet>` (tests verts, trailers) et poussé ; la PR vers `main` est ouverte (`gh pr create`, modèle `.github/pull_request_template.md`) ou mise à jour. Journaliser le push et la PR (hashes, URL).

## 2. Déléguer la vérification

- Entrée de journal `orchestrateur · DÉLÉGATION` (agent qa-validator, jalon, itération).
- Déléguer à `qa-validator` avec le brief : numéro et titre du jalon, itération, liste des jours à auditer, ADR acceptés pertinents, livrables annoncés et leurs chemins.
- Lire le rapport produit `reports/validations/jalon-$ARGUMENTS.md`.

## 3. Traiter le verdict

**NON VALIDÉ**
- Pour chaque défaut bloquant : déléguer la correction à l'agent propriétaire indiqué dans le rapport (entrée DÉLÉGATION), puis relancer `/valider-jalon $ARGUMENTS`.
- Un défaut qui révèle une décision non tranchée → `/nouvel-adr` puis G1, pas de correction à l'aveugle.

**VALIDÉ ou VALIDÉ AVEC RÉSERVES → point de validation G2**

Présenter à l'humain :
```
## Jalon N — verdict proposé : …
- Critères : n ✅ · n ⚠️ · n ❌ (rapport : reports/validations/jalon-N.md)
- Preuves clés : …
- Réserves (agent, échéance) : …
- Recommandation : go / no-go, et pourquoi
- Pull request : #<numéro> <URL> — <n> commits, branche feat/jalon-N-<sujet>
Go pour fusionner dans main ?
```

## 4. Après la réponse de l'humain

**Go**
1. Entrée `orchestrateur · VALIDATION` : décision humaine, verdict, rapport, réserves.
2. Déléguer à `doc-keeper` : tableau de bord (jalon Validé + date, jalon suivant actif, réserves), révision du registre des risques, statuts d'ADR concernés.
3. Commiter et pousser la mise à jour documentaire sur la branche du jalon, puis cocher la checklist de la PR.
4. Fusionner : `gh pr merge <n> --merge --delete-branch` ; puis `git switch main && git pull --ff-only` ; tag `git tag -a jalon-N -m "Jalon N validé — <titre>"` et `git push origin jalon-N`. Entrée de journal citant le commit de fusion et le tag.
5. Annoncer le jalon suivant, créer sa branche depuis `origin/main` et rappeler ses critères.

**No-go**
- Entrée `orchestrateur · DÉCISION` avec la raison donnée par l'humain, puis plan de correction.
