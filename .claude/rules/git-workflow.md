# Règle systémique Git — branches, commits, push, pull requests (tous les agents)

Objectif : un historique propre, relisible et **relié à la traçabilité** (journal, jalons, ADR), où `main` ne contient que du travail validé par l'humain. Décision de référence : ADR-007.

Dépôt : `origin` = `https://github.com/Myf237/Projet_pisciculture.git` (public — ne jamais y pousser de secret). Identité locale : `Myf237 <yanellemogou@gmail.com>`.

## 1. Qui fait quoi

| Rôle | Opérations git autorisées |
|---|---|
| **Orchestrateur** | toutes les opérations ci-dessous, dans le respect de cette règle |
| **Sous-agents** | lecture seule : `status`, `diff`, `log`, `show`, `ls-files`, `ls-tree`, `blame`, `rev-parse`, `rev-list`, `merge-base`, `describe`, `shortlog`, `grep`, `check-ignore`, `cat-file`, `for-each-ref`, `show-ref` ; formes de consultation de `branch` (`--show-current`, `-a`, `-vv`, `--contains`…), `tag -l`, `remote -v`, `config --get/--list`, `stash list/show`, `reflog` — tout le reste est bloqué par hook |
| **Humain** | approuve la fusion d'une PR dans `main` (G2) et toute action irréversible (G4) |

Les sous-agents ne commitent pas : l'orchestrateur commite leur travail et les nomme dans le trailer `Agent:`.

## 2. Branches

- `main` = **état validé uniquement**. Jamais de commit, de merge ni de push direct sur `main` : il n'évolue que par pull request fusionnée après G2.
- Une branche par jalon ou par sujet, créée depuis `main` à jour (`git fetch origin` puis `git switch -c <branche> --no-track origin/main`). `--no-track` évite que la branche prenne `main` comme amont ; le premier `git push -u origin <branche>` fixe le bon amont.
- Nommage `<type>/<sujet-en-kebab-case>`, sans accent :
  - jalon : `feat/jalon-1-donnees-nettoyees`, `feat/jalon-3-modele-risque`
  - autre : `chore/mise-en-place-projet`, `docs/adr-008-unites`, `fix/ingestion-fuseau-horaire`
- Intégrer les nouveautés de `main` par `git merge origin/main` (jamais de rebase d'une branche déjà poussée).
- Après fusion : branche supprimée sur GitHub et en local avec `git branch -d` (suppression sûre, jamais `-D`).

## 3. Commits — Conventional Commits

```
<type>(<portée>): <résumé>

<corps : quoi et pourquoi>

Agent: <agent>[, <agent>]
Jalon: <1-6 | preparation>
Refs: <ADR-XXX, RX, docs/NN §X>
Journal: J-AAAAMMJJ-NNN[, J-…]
<lignes d'attribution fournies par l'environnement Claude Code, ex. Co-Authored-By>
```

- **Types** : `feat` (fonctionnalité) · `fix` (correction) · `docs` (documentation) · `test` (tests seuls) · `refactor` (sans changement de comportement) · `perf` · `build` (dépendances, `requirements.txt`) · `ci` · `chore` (structure, configuration, gouvernance) · `revert`. Changement incompatible (schéma de config, format de sortie) : `feat!` + ligne `BREAKING CHANGE: …` dans le corps.
- **Portées** alignées sur les modules : `ingestion`, `features`, `models`, `decision`, `pipeline`, `dashboard`, `config`, `tests`, `deps` ; documentation : `adr`, `risques`, `suivi`, `cadrage`, `readme` ; gouvernance : `gouvernance`, `git`, `tracabilite`, `structure`.
- **Résumé** : en français, à l'impératif, minuscule initiale, ≤ 72 caractères, sans point final (ex. `feat(ingestion): borner température et pH selon ADR-008`).
- **Corps** : lignes ≤ 72 caractères ; explique le pourquoi et les conséquences, pas le diff ligne à ligne.
- **Trailers** `Agent`, `Jalon`, `Journal` obligatoires ; `Refs` dès qu'un ADR, un risque ou une section de spec est concerné.
- Message écrit dans un fichier temporaire et passé par `git commit -F <fichier>` (évite les problèmes de guillemets et d'échappement).

### Règles de commit

1. **Atomique** : un commit = un changement logique cohérent (une tâche, idéalement un agent). Pas de commit fourre-tout, pas de « WIP », pas de « fix typo » enchaînés (les regrouper avant de pousser).
2. **Staging explicite** : `git add <chemins>` ; jamais `git add -A` ou `git add .` sans avoir lu `git status` ; relire `git diff --staged --stat` avant chaque commit.
3. **Vert avant de commiter** : `pytest -q` passe dès qu'il existe du code ; jamais `--no-verify`.
4. **Jamais dans un commit** : `data/raw/`, secret ou identifiant, `venv/`, fichier > 5 Mo, artefact régénérable (`data/processed/`, `*.joblib`) — le `.gitignore` est la première barrière, la relecture du staging la seconde.
5. **Historique publié immuable** : pas d'`--amend` ni de rebase sur un commit déjà poussé, pas de `push --force`, pas de `reset --hard` — une erreur se corrige par un nouveau commit ou `git revert` (G4 sinon).
6. **Journal automatique** : `logs/agents/actions.jsonl` s'allonge en continu ; il est commité avec le commit de suivi de fin de session, les lignes postérieures rejoignent le commit suivant.

## 4. Quand commiter et pousser

| Moment | Action | Autonome ? |
|---|---|---|
| Début de session | `git fetch origin` ; vérifier la branche courante et l'écart avec `origin/main` | oui |
| Unité logique terminée et testée | commit sur la branche de travail | oui |
| Fin de session (`/cloturer-session`) et avant toute PR | `git push -u origin <branche>` | oui |
| Jalon prêt à vérifier (`/valider-jalon`) | ouvrir la PR (ou la sortir du mode brouillon) | oui |
| Go humain G2 | fusionner la PR, taguer, mettre `main` à jour localement | **non — G2** |

## 5. Pull requests

- Une PR par jalon (ou par sujet hors jalon), de la branche de travail vers `main`, avec le modèle `.github/pull_request_template.md`.
- **Titre** au format Conventional Commits : `feat(ingestion): jalon 1 — données nettoyées et fiables`.
- **Description** : contexte et jalon, changements, critères du jalon (`docs/04`) cochés avec preuve, décisions (ADR), risques et limites, traçabilité (entrées de journal, rapport `reports/validations/`), checklist ; terminer par les lignes d'attribution fournies par l'environnement Claude Code.
- **Outil** : `gh pr create --base main --head <branche> --title "…" --body-file <fichier>`. Sans `gh` : pousser la branche, préparer titre et description dans un fichier, et donner à l'humain le lien `https://github.com/Myf237/Projet_pisciculture/compare/main...<branche>?expand=1`.
- **Fusion** : uniquement après verdict `qa-validator` et go humain (G2), par **merge commit** (`gh pr merge <n> --merge --delete-branch`) — conserve les commits atomiques et leurs trailers, et matérialise chaque jalon dans `main`.
- **Tag** annoté après fusion d'un jalon : `git tag -a jalon-N -m "Jalon N validé — <titre>"` puis `git push origin jalon-N` ; version de démonstration finale : `v1.0.0`.
- Toute opération GitHub (push, PR, fusion, tag) fait l'objet d'une entrée de journal citant hashes, numéro ou URL de PR.

## 6. Garanties techniques (hook `.claude/hooks/guard_git.py`)

Bloqué pour **tous** (G4 — l'humain peut exécuter lui-même la commande s'il la valide) :
`push --force` / `-f` / `--force-with-lease` / `--mirror` / `--delete` / `--all` / refspec `+…` ou `:…` · commit, merge ou push sur `main` (y compris `git push` sans refspec depuis `main`) · `pull` sur `main` sans `--ff-only` · `--no-verify` / `commit -n` · `commit --amend` d'un commit déjà poussé · `rebase` · `reset --hard|--merge|--keep` · `clean -f` · `branch -D|-f|-M|-C` · `checkout -B|-f`, `checkout -- <chemin>`, `checkout .` · `switch -C|-f` · `restore` sans `--staged` · `stash drop|clear` · `filter-branch` / `filter-repo` / `replace` / `update-ref` · `tag -d|-f` · `reflog expire|delete` · `gc --prune`.

Autorisé notamment : `git switch -c`, `git branch -d`, `git merge origin/main` sur une branche de travail, `git pull --ff-only` sur `main`, `git reset <commit>` (sans `--hard`), `git restore --staged`, `git stash`, `git tag -a`. Les textes cités (messages de commit, heredocs) ne sont pas analysés.

Bloqué pour les **sous-agents** : toute commande git hors de la liste en lecture seule du §1.

Chaque refus est tracé dans `logs/agents/actions.jsonl` (statut `refuse`) et doit être journalisé en ÉCHEC par l'agent concerné.
