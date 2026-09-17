# Règle systémique de traçabilité — s'applique à TOUS les agents, orchestrateur compris

Objectif : pouvoir toujours reconstituer après coup **quelle action a été faite, par quel agent, pourquoi, avec quel résultat**.

## Ce qui doit être journalisé

Toute action qui change l'état du projet :
créer / modifier / supprimer un fichier · exécuter une commande (tests, entraînement, script) · prendre ou proposer une décision · valider ou refuser un jalon · déléguer à un agent · escalader vers l'humain · échouer ou revenir en arrière.

Les simples lectures (Read, Grep, Glob) ne sont pas journalisées.

## Deux journaux complémentaires

| Journal | Écrit par | Répond à | Fichier |
|---|---|---|---|
| Automatique | hooks Claude Code (garanti) | quoi, quand, quel agent, quel outil, succès/échec | `logs/agents/actions.jsonl` |
| Sémantique | l'agent qui agit (obligatoire) | **pourquoi**, résultat vérifié, suite | `logs/agents/journal/AAAA-MM-JJ.md` |

- `logs/agents/actions.jsonl` est **interdit en écriture** aux agents : ne jamais le modifier.
- Ne pas confondre avec `logs/decisions.log`, qui est le journal **du produit** (moteur de décision du MVP).

## Format obligatoire d'une entrée sémantique

Fichier du jour : `logs/agents/journal/AAAA-MM-JJ.md` (le créer avec le titre `# Journal des agents — AAAA-MM-JJ` s'il n'existe pas). Ajouter l'entrée **à la fin** du fichier :

```markdown
### J-AAAAMMJJ-NNN · HH:MM · <agent> · <TYPE>
- **Action :** ce qui a été fait concrètement (verbe + objet)
- **Fichiers :** chemin (créé|modifié|supprimé), ... — ou « aucun »
- **Pourquoi :** justification + référence (Jalon N critère X · docs/02 §Y · ADR-XXX · RX · demande utilisateur)
- **Résultat :** ✅ succès | ❌ échec | ⚠️ partiel — avec preuve (sortie de test, métrique, chemin)
- **Suite :** prochaine étape, décision attendue ou « aucune »
```

- `NNN` = numéro séquentiel dans le fichier du jour (001, 002…).
- `<agent>` = `orchestrateur`, `data-engineer`, `ml-engineer`, `automation-engineer`, `dashboard-developer`, `qa-validator` ou `doc-keeper`.
- `<TYPE>` ∈ CRÉATION · MODIFICATION · SUPPRESSION · EXÉCUTION · DÉCISION · VALIDATION · DÉLÉGATION · ESCALADE · ÉCHEC.
- Heure locale au format 24 h, **lue sur l'horloge système au moment d'écrire l'entrée** (`date +%H:%M` ou `Get-Date -Format HH:mm`), jamais estimée ni reprise d'une entrée précédente. **Agent sans shell** (doc-keeper) : prendre l'heure de l'horodatage `ts` de la **dernière ligne** de `logs/agents/actions.jsonl`, juste après ta dernière écriture (compter les lignes avec Grep `output_mode: count`, puis lire la dernière avec Read `offset`).

## Règles

1. **Immédiat** : l'entrée est écrite juste après l'action, pas en fin de session.
2. **Pourquoi obligatoire** : toujours rattaché à une source (jalon, spec, ADR, risque, demande explicite). Une action sans justification traçable ne doit pas être faite.
3. **Résultat prouvé** : ne jamais annoncer un succès non vérifié ; citer la preuve.
4. **Les échecs et refus aussi** : un échec, un contournement, un retour arrière ou une **action refusée** (règle de permission, garde-fou de périmètre, refus humain) est journalisé comme le reste, en type ÉCHEC. Les refus dus aux règles `deny` des settings n'apparaissent pas dans le journal automatique : l'entrée sémantique est alors la seule trace.
5. **Append-only** : ne jamais modifier ni supprimer une entrée existante. Une correction = nouvelle entrée « Corrige J-… ».
6. **Granularité** : une entrée par action logique (ex. « implémentation de clean_data + tests »), pas une par frappe ni une seule pour toute la journée.
7. **Sobriété** : pas de secrets, pas de dumps de données ; résumer et pointer vers le fichier de preuve.
8. **Sous-agent** : avant de rendre la main, un sous-agent qui a modifié des fichiers ou exécuté des commandes **doit** avoir écrit son entrée — sinon le garde-fou `SubagentStop` le renvoie la compléter.
9. **Délégation** : l'orchestrateur journalise chaque délégation (type DÉLÉGATION : agent, brief, jalon) et son retour.
10. **Git** : chaque commit porte les trailers `Agent`, `Jalon`, `Journal` (et `Refs` si un ADR ou un risque est concerné) ; chaque push, PR, fusion ou tag fait l'objet d'une entrée citant hashes, numéro ou URL de PR. Conventions complètes : `.claude/rules/git-workflow.md`.

## Contrôle

- `/cloturer-session` et `qa-validator` croisent les deux journaux : tout fichier modifié dans `actions.jsonl` doit apparaître dans une entrée sémantique (`.claude/hooks/audit_trace.py`).
- Un écart non expliqué fait échouer le critère de traçabilité du jalon.
