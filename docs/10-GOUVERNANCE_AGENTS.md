# Gouvernance du projet par agents — organisation, workflow et traçabilité

Ce document décrit comment le développement du MVP est piloté avec Claude Code. Il est la version lisible de la configuration opérationnelle située dans `.claude/` et peut être repris dans le chapitre « méthodologie » du mémoire. Décision de référence : ADR-005 (`07-JOURNAL_DECISIONS.md`).

En cas de divergence, **les fichiers de `.claude/` font foi** pour le comportement des agents ; ce document doit alors être mis à jour.

## 1. Principes

1. **Un pilote, des spécialistes** : la session principale de Claude Code orchestre ; chaque sous-agent est propriétaire d'un périmètre (modules, fichiers) aligné sur le découpage de `02-SPEC_TECHNIQUE.md`.
2. **Séparer réaliser et vérifier** : aucun agent ne valide son propre travail ; un agent indépendant (`qa-validator`) vérifie chaque jalon avec preuves.
3. **L'humain décide** : les choix scientifiques, de périmètre et les validations de jalon restent sous le contrôle du porteur du projet (points de validation G1 à G4).
4. **Garantir plutôt que recommander** : ce qui doit être certain est imposé techniquement (hooks, permissions) ; le reste est porté par des règles écrites.
5. **Tout est traçable** : chaque action est journalisée automatiquement, et son auteur en écrit la justification.

## 2. Organisation

```
                         Porteur du projet (humain)
                     décide aux points G1 · G2 · G3 · G4
                                     │
                     ┌───────────────┴───────────────┐
                     │  ORCHESTRATEUR (session princ.)│
                     │  planifie · délègue · pilote   │
                     └───────────────┬───────────────┘
        ┌───────────────┬────────────┼─────────────┬───────────────┬──────────────┐
        ▼               ▼            ▼             ▼               ▼              ▼
  data-engineer    ml-engineer  automation-   dashboard-      qa-validator    doc-keeper
  Modules 1-2      Module 3     engineer      developer       vérification    documentation
  Jalons 1-2       Jalon 3      Module 4      Module 5        tous jalons     en continu
                                Jalons 4, 6   Jalons 5, 6     (indépendant)
```

| Agent | Mission | Écrit dans | Outils | Modèle |
|---|---|---|---|---|
| **orchestrateur** | Planifier, déléguer, tenir le rythme et les points de validation | aucun module (délègue) | tous | session |
| **data-engineer** | Ingestion, validation du schéma, nettoyage, courbe de croissance, EDA, features | `src/ingestion.py`, `src/features.py`, `notebooks/`, `data/processed/`, `reports/cleaning_report.json`, `reports/figures/` | lecture, écriture, shell | sonnet |
| **ml-engineer** | Baseline, anomalies synthétiques, modèle de risque, évaluation, explicabilité, croissance (P2) | `src/models/`, `models/`, `reports/experiments.md` | lecture, écriture, shell | opus |
| **automation-engineer** | Moteur de décision, journal des décisions, pipeline de bout en bout | `src/decision_engine.py`, `src/main.py`, `logs/decisions.log` | lecture, écriture, shell | sonnet |
| **dashboard-developer** | Dashboard Streamlit, mode rejeu, scénario de démonstration | `dashboard/` | lecture, écriture, shell | sonnet |
| **qa-validator** | Vérification indépendante des jalons, tests, audit de traçabilité | `reports/validations/` **uniquement** (imposé par hook) | lecture, shell, écriture limitée | opus |
| **doc-keeper** | ADR, risques, tableau de bord, dictionnaire, glossaire, README | `docs/`, `README.md` **uniquement** (imposé par hook) | lecture, écriture limitée | sonnet |

Fichiers partagés : `src/config.py` (chaque agent édite sa section ; tout seuil modifié exige un ADR), `tests/` (chaque agent possède les tests de son module), `requirements.txt` (ajout justifié). Tous les agents écrivent dans le journal sémantique. Les sous-agents ne peuvent pas déléguer à leur tour : toute délégation passe par l'orchestrateur, ce qui garde la chaîne de responsabilité lisible.

## 3. Matrice des responsabilités (RACI)

R = réalise · A = approuve · C = consulté · I = informé

| Activité | Orchestrateur | data | ml | automation | dashboard | qa | doc | Humain |
|---|---|---|---|---|---|---|---|---|
| Jalon 1 — Données nettoyées | C | R | I | I | I | C | C | A |
| Jalon 2 — Exploration | C | R | C | I | I | C | C | A |
| Jalon 3 — Modèle de risque | C | C | R | I | I | C | C | A |
| Jalon 4 — Moteur de décision | C | I | C | R | I | C | C | A |
| Jalon 5 — Dashboard | C | I | I | C | R | C | C | A |
| Jalon 6 — MVP intégré | R (coordination) | I | C | R (pipeline) | R (démo) | C | R (README) | A |
| Vérification d'un jalon | R (déclenche) | I | I | I | I | R | I | I |
| Commits, push, pull request | R | I | I | I | I | I | I | A |
| ADR (proposition) | C | C | C | C | C | I | R | A |
| Registre des risques, tableau de bord | C | I | I | I | I | I | R | I |

Commits et push sur la branche de travail sont autonomes (ADR-007) ; le « A » de la ligne « Commits, push, pull request » ne porte que sur la fusion de la pull request dans `main` (G2).

## 4. Workflow d'un jalon

```
/demarrer-session
  1. CADRER       orchestrateur : tableau de bord, journal précédent, critères du jalon actif
        │
        ├── décision bloquante ? ──► 2. DÉCIDER : doc-keeper rédige un ADR « Proposé » ──► [G1 humain]
        ▼
  3. RÉALISER     agent propriétaire : code + tests + entrée de journal
        ▼
  4. VÉRIFIER     /valider-jalon N → qa-validator : rapport critère par critère avec preuves
        │           NON VALIDÉ → retour à 3 (2 itérations maximum, puis escalade)
        ▼
  5. DOCUMENTER   doc-keeper : ADR, risques, dictionnaire, tableau de bord
        ▼
  6. VALIDER      [G2 humain] go / no-go → commit git → jalon suivant
/cloturer-session
```

Règles de pilotage : un seul jalon actif à la fois ; délégations parallèles seulement sur des fichiers disjoints ; **règle du Jour 4** — si le Jalon 3 n'est pas validé fin J4, proposition de couper la prédiction de croissance (G3).

## 5. Points de validation humaine

| Point | Déclencheur | Exemples |
|---|---|---|
| **G1** Décision structurante | Tout choix scientifique ou méthodologique, tout ADR | unité réelle d'une colonne, borne de nettoyage, exclusion de l'ammoniac, stratégie de labels, seuil de rappel |
| **G2** Validation de jalon | Rapport de vérification disponible | go / no-go, puis commit |
| **G3** Périmètre et planning | Écart au cahier des charges §3 ou au planning | fonctionnalité de dashboard supplémentaire, coupe de la croissance, report d'un jalon |
| **G4** Action irréversible | Perte possible d'information | suppression de fichier, modification de `data/raw/`, réécriture de l'historique git ou d'un journal |

En dehors de ces points, les agents travaillent en autonomie. À chaque point, l'orchestrateur présente les options, sa recommandation et l'impact, puis attend la réponse.

## 6. Traçabilité

Objectif : pouvoir toujours établir **quelle action a été faite, par quel agent, pourquoi et avec quel résultat**. Règle complète : `.claude/rules/tracabilite.md`, chargée automatiquement par tous les agents.

| Couche | Mécanisme | Contenu | Emplacement |
|---|---|---|---|
| 1. Journal automatique | Hooks Claude Code après chaque écriture, commande, délégation, skill ; début/fin de session et de sous-agent ; refus du mode auto et du garde-fou de périmètre | horodatage, session, agent, outil, cible, succès/échec/refus | `logs/agents/actions.jsonl` (protégé en écriture) |
| 2. Journal sémantique | Écrit par l'agent juste après chaque action | action, fichiers, **pourquoi** (référence), **résultat avec preuve**, suite | `logs/agents/journal/AAAA-MM-JJ.md` |
| 3. Contrôle | Garde-fou de fin de sous-agent (renvoi unique s'il a agi sans journaliser) ; audit croisé (`.claude/hooks/audit_trace.py`) en fin de session et à chaque validation ; commits sur la branche du jalon, fusion dans `main` à G2 (ADR-007, précise la conséquence « commit git par jalon validé » de l'ADR-005) | écarts entre les deux journaux, entrées mal formées | sortie de l'audit, `reports/validations/` |

Exemple d'entrée sémantique :

```markdown
### J-20260917-004 · 14:32 · data-engineer · MODIFICATION
- **Action :** bornes physiques température/pH + interpolation temporelle dans clean_data()
- **Fichiers :** src/ingestion.py (modifié), tests/test_ingestion.py (créé)
- **Pourquoi :** Jalon 1, critère « aucune température hors [0, 40] » ; 01-DATA_DICTIONARY anomalies 1-2
- **Résultat :** ✅ pytest 8/8 ; 1 243 valeurs imputées (preuve : reports/cleaning_report.json)
- **Suite :** ADR-003 (ammoniac) à trancher → G1
```

*(Exemple illustratif du format, pas un résultat réel.)*

Principes : entrée immédiate ; justification obligatoire et référencée ; résultat prouvé ; échecs journalisés ; ajout seulement (une correction est une nouvelle entrée) ; distinct de `logs/decisions.log`, qui est le journal du produit.

Précision (2026-09-16, J-20260916-016) : un événement de fin de sous-agent sans `agent_type` (sous-agent lancé par Claude Code lui-même, pas par l'orchestrateur) est étiqueté `sous-agent-interne` dans le journal automatique, et non `orchestrateur`.

## 7. Garanties techniques et règles

| Exigence | Garantie technique | Porté par une règle |
|---|---|---|
| Toute écriture, commande, délégation est tracée avec l'agent | ✅ hooks `PostToolUse`, `SubagentStart/Stop`, `SessionStart` | — |
| Le journal automatique n'est pas modifié par les outils d'édition, ni par les commandes shell de fichiers qu'elle reconnaît (copie, redirection…) | ⚠️ permission `deny` (`Edit(...)`) — ne couvre pas un sous-processus qui écrit lui-même dans le fichier (ex. script Python), voir §11 | règle + audit croisé |
| `data/raw/` protégé des mêmes outils et commandes (ex. `mkdir data/raw` refusé au data-engineer, J-20260916-019) | ⚠️ permission `deny` (`Edit(...)`) — même limite, voir §11 | règle + audit croisé |
| Un sous-agent qui agit écrit son entrée de journal | ✅ garde-fou `SubagentStop` (renvoi unique) | contenu de l'entrée |
| `qa-validator` ne modifie pas le code ; `doc-keeper` n'écrit que la doc | ✅ hook `PreToolUse` de périmètre | écritures par shell de `qa-validator` |
| Ownership des fichiers par les agents développeurs | — | ✅ règles des agents + contrôle `qa-validator` |
| Qualité du « pourquoi », honnêteté des résultats | — | ✅ règles + audit + revue humaine |
| Journal sémantique en ajout seulement | — | ✅ règle + historique git |
| Aucun commit, merge ni push direct sur `main` ; opérations git irréversibles bloquées (force push, rebase, reset --hard, amend d'un commit poussé…) | ✅ hook `PreToolUse` `guard_git.py` | — |
| Git en lecture seule pour les sous-agents (`status`, `diff`, `log`… uniquement) | ✅ hook `PreToolUse` `guard_git.py` | — |
| Conventions de branche, de commit (Conventional Commits, trailers) et de pull request | — | ✅ règle `.claude/rules/git-workflow.md` (ADR-007) |

## 8. Commandes de pilotage (skills)

| Commande | Rôle |
|---|---|
| `/demarrer-session` | Lit l'état, audite la veille, détecte retards et décisions ouvertes, propose le plan, journalise l'ouverture |
| `/valider-jalon N` | Fait vérifier le jalon N par `qa-validator`, gère les corrections (2 itérations max), soumet le go/no-go, met à jour la doc, puis, sur accord humain (G2), fusionne la pull request par merge commit et tague `jalon-N` |
| `/nouvel-adr <titre>` | Crée un ADR « Proposé » ; `/nouvel-adr accepter ADR-XXX` enregistre la validation humaine |
| `/cloturer-session` | Bilan, audit croisé, mise à jour du suivi, prochaine action |

## 9. Déroulé d'une journée type

1. Lancer Claude Code **depuis la racine du projet** (et accepter la confiance du dossier au premier lancement, nécessaire aux hooks).
2. `/demarrer-session` → valider le plan et trancher les décisions bloquantes présentées.
3. Laisser l'orchestrateur déléguer ; répondre aux points de validation quand ils apparaissent.
4. Quand le jalon est annoncé terminé : `/valider-jalon N` → go / no-go.
5. `/cloturer-session`.

Consulter à tout moment : `11-TABLEAU_DE_BORD.md` (état), `logs/agents/journal/` (ce qui a été fait et pourquoi), `python .claude/hooks/audit_trace.py` (conformité de la traçabilité).

## 10. Emplacement de la configuration

```
.claude/
├── CLAUDE.md                 instructions projet + rôle de l'orchestrateur
├── settings.json             hooks de journalisation + permissions
├── rules/                    règles chargées pour tous les agents
│   ├── tracabilite.md
│   ├── conventions-code.md
│   ├── integrite-academique.md
│   └── git-workflow.md       branches, commits, push, pull requests (ADR-007)
├── agents/                   6 sous-agents (mission, périmètre, règles, compte rendu)
├── skills/                   4 procédures de pilotage
└── hooks/
    ├── log_action.py         journal automatique
    ├── check_journal.py      garde-fou de fin de sous-agent
    ├── guard_paths.py        garde-fou de périmètre d'écriture
    ├── guard_git.py          garde-fou git (opérations irréversibles, git lecture seule pour les sous-agents)
    └── audit_trace.py        audit croisé des journaux

.github/
└── pull_request_template.md  modèle de pull request (contexte, critères, décisions, traçabilité, checklist)
```

## 11. Limites connues du dispositif

- Les fichiers écrits **indirectement** par un script lancé en shell (ex. `python src/main.py` qui produit `data/processed/`) apparaissent dans le journal automatique comme une commande, pas fichier par fichier : l'entrée sémantique doit citer les sorties produites.
- Le garde-fou de périmètre porte sur les outils d'écriture de Claude Code ; une écriture par commande shell de `qa-validator` n'est pas bloquée techniquement (règle + audit).
- La permission `deny` sur `data/raw/` et sur `logs/agents/actions.jsonl` (`.claude/settings.json`, `Edit(...)`) couvre les outils d'édition de Claude Code et les commandes shell de fichiers qu'elle reconnaît (copie, redirection…) — exemple réel : `mkdir data/raw` refusé au data-engineer (J-20260916-019). Elle **ne couvre pas un sous-processus arbitraire** qui écrirait lui-même dans ces chemins (ex. un script Python lancé en shell), et ce pour **tous les agents**, pas seulement `qa-validator` : la protection dépend alors de la règle et de l'audit, pas d'un blocage technique.
- L'ownership des fichiers par les agents développeurs est une règle vérifiée par `qa-validator`, pas un blocage technique (choix délibéré pour éviter des blocages sur les fichiers partagés).
- Le caractère « ajout seulement » du journal sémantique repose sur la règle et sur l'historique git, pas sur une protection technique.
- Une action refusée par une règle `deny` des settings (ex. écriture dans `data/raw/`) ne déclenche aucun hook et n'apparaît donc pas dans le journal automatique ; seule l'entrée sémantique de type ÉCHEC, exigée par la règle, la trace. Les refus du mode auto et du garde-fou de périmètre, eux, sont tracés automatiquement.
- L'identification de l'agent repose sur l'information fournie par Claude Code aux hooks (`agent_type`) ; les actions de la session principale sont attribuées à `orchestrateur`.
- Les hooks nécessitent Python accessible dans le `PATH` ; en cas d'échec interne, la journalisation automatique échoue silencieusement (sans bloquer le travail) — l'audit croisé révèle alors les trous.
- Le garde-fou git (`guard_git.py`) analyse les commandes de façon **heuristique** (motifs textuels) ; les textes cités (messages de commit, heredocs) sont retirés avant analyse pour éviter les faux positifs, mais une commande git lancée depuis un **script** exécuté en shell (et non tapée directement) peut ne pas être détectée.
- Le garde-fou est **local** : tant que la protection de branche `main` n'est pas configurée côté GitHub par l'humain, rien n'empêche techniquement un push direct effectué en dehors de Claude Code (voir R14, `08-REGISTRE_RISQUES.md`).

## 12. Gestion de version (git)

Décision de référence : ADR-007 (`07-JOURNAL_DECISIONS.md`). Règle complète, y compris la liste exhaustive des commandes bloquées et autorisées : `.claude/rules/git-workflow.md`.

Résumé : seul l'orchestrateur écrit dans l'historique (commit, push, merge, tag) ; les sous-agents sont en lecture seule sur git. `main` ne reçoit que du travail validé par l'humain, via pull request fusionnée à G2. Une branche par jalon (`feat/jalon-N-sujet`), Conventional Commits avec trailers `Agent`/`Jalon`/`Journal` (et `Refs` si ADR/risque concerné), fusion par merge commit, tag annoté `jalon-N`.

| Moment | Qui | Action |
|---|---|---|
| Début de session | Orchestrateur | `git fetch origin` ; vérifie la branche courante et l'écart avec `origin/main` |
| Ouverture d'un jalon | Orchestrateur | Crée la branche depuis `origin/main` à jour |
| Unité de travail terminée et testée | Orchestrateur | Commit atomique (Conventional Commits + trailers) |
| Fin de session, avant toute pull request | Orchestrateur | `git push -u origin <branche>` |
| Jalon prêt à vérifier (`/valider-jalon`) | Orchestrateur | Ouvre ou met à jour la pull request (modèle `.github/pull_request_template.md`) |
| Vérification du jalon | qa-validator | Vérifie critère par critère (git en lecture seule) |
| Go humain (G2) | Humain → orchestrateur | Fusion par merge commit, tag `jalon-N`, mise à jour locale de `main` |

Garanties techniques et limites : voir §7 et §11.
