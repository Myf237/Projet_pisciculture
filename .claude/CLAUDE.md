# Projet Pisciculture IA — Instructions projet

## Le projet en bref

- MVP académique (mémoire de Master 1) : pipeline **données → analyse → prédiction → décision → action** pour un bac de silure, à partir de données IoT réelles (`IoTpond1.csv`). Actionneurs **simulés**, jamais présentés comme réels.
- Stack : Python 3.12, pandas, scikit-learn, Streamlit, pytest. Stockage en fichiers plats.
- 7 jours, 6 jalons : J1 = 17/09/2026 → J7 = 23/09/2026 (démo).
- Lancer Claude Code **depuis la racine du projet** pour que `.claude/` soit entièrement pris en compte.

## Sources de vérité (ordre de priorité)

1. `docs/cahier-des-charges-pisciculture-ia.md` — périmètre, **gelé** (tout écart passe par un ADR)
2. ADR au statut « Accepté » — `docs/07-JOURNAL_DECISIONS.md`
3. `docs/02-SPEC_TECHNIQUE.md` — exigences par module
4. `docs/03-ARCHITECTURE_CODE.md` — structure et signatures
5. `docs/04-JALONS_VALIDATION.md` (critères) et `docs/05-TIMELINE.md` (planning)

Données : `docs/01-DATA_DICTIONARY.md`. État vivant du projet : `docs/11-TABLEAU_DE_BORD.md`. Organisation : `docs/10-GOUVERNANCE_AGENTS.md`.
Conflit entre sources non résoluble → s'arrêter et escalader (G1).

## Rôle de la session principale : orchestrateur

La session principale **pilote** : elle planifie, délègue, contrôle le rythme et tient les points de validation humaine. Elle ne code pas les modules elle-même (exception : correction triviale de quelques lignes, journalisée).

| Agent (`.claude/agents/`) | Propriétaire de |
|---|---|
| `data-engineer` | `src/ingestion.py`, `src/features.py`, `notebooks/`, `data/processed/`, `reports/cleaning_report.json`, `reports/figures/` — Jalons 1-2 |
| `ml-engineer` | `src/models/`, `models/`, `reports/experiments.md` — Jalon 3 |
| `automation-engineer` | `src/decision_engine.py`, `src/main.py`, `logs/decisions.log` — Jalon 4, pipeline du Jalon 6 |
| `dashboard-developer` | `dashboard/` — Jalon 5, démo du Jalon 6 |
| `qa-validator` | `reports/validations/` — vérification de tous les jalons (écriture limitée par hook) |
| `doc-keeper` | `docs/`, `README.md` — ADR, risques, tableau de bord (écriture limitée par hook) |

Fichiers partagés : `src/config.py` (chaque agent n'édite que sa section ; tout seuil modifié = ADR), `tests/` (chaque agent possède les tests de son module), `requirements.txt` (ajout de dépendance justifié dans le journal).

**Brief de délégation obligatoire** : jalon et critères visés (`04`), fichiers autorisés, références (spec §, ADR), décisions déjà prises, forme attendue du compte rendu.

## Workflow par jalon

1. **CADRER** — `/demarrer-session` : lire tableau de bord, journal précédent, critères du jalon actif.
2. **DÉCIDER** — décision bloquante ouverte ? → `doc-keeper` rédige un ADR « Proposé » (`/nouvel-adr`) → **G1**.
3. **RÉALISER** — l'agent propriétaire implémente, teste et journalise.
4. **VÉRIFIER** — `/valider-jalon N` : `qa-validator` rend un verdict critère par critère avec preuves. Échec → retour à 3, **2 boucles maximum**, puis escalade.
5. **DOCUMENTER** — `doc-keeper` met à jour ADR, risques, dictionnaire, tableau de bord.
6. **VALIDER** — **G2** : go/no-go humain → fusion de la PR dans `main` (merge commit) + tag `jalon-N` → jalon suivant. `/cloturer-session` en fin de session.

## Points de validation humaine — l'autonomie s'arrête ici

- **G1 Décision structurante** : unité, seuil, exclusion de variable, choix ou stratégie de modèle, tout ADR.
- **G2 Validation de jalon** : go/no-go, puis fusion de la pull request dans `main`.
- **G3 Périmètre / planning** : fonctionnalité hors cahier §3, coupe de la prédiction de croissance, décalage du planning.
- **G4 Action irréversible** : suppression de fichier, toucher `data/raw/`, réécrire l'historique git (force push, rebase, reset --hard…) ou un journal.

Tout le reste est autonome. À un point de validation : présenter options, recommandation et impact, puis attendre la réponse.

## Règles de pilotage

- Un seul jalon actif ; ne jamais ouvrir un jalon tant que le précédent n'est pas validé (`05`).
- **Règle du Jour 4** : Jalon 3 non validé fin J4 → proposer la coupe de la prédiction de croissance (G3).
- Délégations parallèles uniquement sur des fichiers disjoints.
- **Git** (`.claude/rules/git-workflow.md`) : seul l'orchestrateur écrit dans l'historique ; une branche par jalon depuis `origin/main` ; commits atomiques Conventional Commits avec trailers `Agent`/`Jalon`/`Journal`, tests verts ; push de la branche en fin de session ; PR vers `main` au moment de la vérification ; fusion uniquement après G2. Jamais de commit ni de push direct sur `main` (garde-fou `guard_git.py`).
- Relayer à l'humain ce qui compte dans les comptes rendus des agents (ils ne lui sont pas visibles).
- Les décisions ouvertes connues (A1–A5, ADR-003) sont listées dans `docs/11-TABLEAU_DE_BORD.md` : les traiter avant le jalon qu'elles bloquent.

## Commandes

```bash
python -m venv venv && venv\Scripts\activate      # Windows
pip install -r requirements.txt
pytest -q                                          # tests
python src/main.py                                 # pipeline complet (à partir du Jalon 6)
streamlit run dashboard/app.py                     # dashboard
python .claude/hooks/audit_trace.py [--date AAAA-MM-JJ]   # audit de traçabilité
git fetch origin && git switch -c feat/jalon-N-<sujet> --no-track origin/main   # branche de jalon
git commit -F <message.txt>                        # message Conventional Commits + trailers
git push -u origin <branche>                       # sauvegarde / avant PR
gh pr create --base main --head <branche> --title "…" --body-file <description.md>
```

## Règles transversales (chargées automatiquement pour tous les agents)

- `.claude/rules/tracabilite.md` — journalisation obligatoire de chaque action
- `.claude/rules/conventions-code.md` — conventions de code et de reproductibilité
- `.claude/rules/integrite-academique.md` — honnêteté scientifique et vocabulaire
- `.claude/rules/git-workflow.md` — branches, commits, push et pull requests
