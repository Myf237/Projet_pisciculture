# Pisciculture IA — Suivi, prédiction et automatisation pour un bac de silure

MVP académique (mémoire de Master 1) : pipeline **données → analyse → prédiction → décision → action** pour un bac d'élevage de silure (*Clarias gariepinus*), à partir de données IoT réelles (`IoTpond1.csv`, dataset *Sensor Based Aquaponics Fish Pond Datasets*, Udanor et al.). Les actionneurs sont **simulés** : ce dépôt ne pilote aucun matériel physique.

Détail du contexte et des objectifs : `docs/cahier-des-charges-pisciculture-ia.md` (document de référence, gelé) et `docs/README_PROJET.md`.

## Statut

Mise en place en revue (PR #1) — état au 2026-09-17 (Jour 1) : squelette du dépôt terminé et vérifié — structure de fichiers et signatures de fonctions en place, sans logique métier (`pytest -q` : 31 tests réussis, 38 prévus en `skip`). Vérification indépendante par `qa-validator` : **VALIDÉ AVEC RÉSERVES** (voir `docs/11-TABLEAU_DE_BORD.md`). Pull request **#1** ouverte vers `main`, en attente de la décision humaine (G2) : https://github.com/Myf237/Projet_pisciculture/pull/1. Le Jalon 1 démarre après la fusion. Décisions bloquantes sur les données (unités, bornes, ammoniac) à trancher au tout début du Jalon 1 (`docs/11-TABLEAU_DE_BORD.md`).

## Structure

```
data/          données brutes (non versionnées) et nettoyées — voir data/README.md
src/           code source : ingestion, features, modèles, moteur de décision
models/        modèles entraînés (.joblib) et fiches modèle (.json)
notebooks/     exploration (Jalon 2)
dashboard/     application Streamlit (Jalon 5)
reports/       rapports de nettoyage, expériences, figures, validations de jalon
logs/          journal du produit (logs/decisions.log) et journaux de traçabilité des agents
docs/          documentation du projet — voir docs/00-INDEX.md
tests/         tests unitaires (pytest)
```

## Installation (Windows)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

## Utilisation

Le pipeline n'est pas encore implémenté (squelette de fonctions, `NotImplementedError`). À terme (Jalon 6) :

```powershell
python src\main.py                 # pipeline complet : ingestion → modèle → décision
streamlit run dashboard\app.py     # dashboard de démonstration (rejeu historique)
```

**Non implémenté à ce stade** : nettoyage des données, features, modèles de détection de risque et de croissance, moteur de décision, dashboard. Voir `docs/11-TABLEAU_DE_BORD.md` pour l'état d'avancement réel par jalon.

## Données

Le fichier `IoTpond1.csv` n'est pas versionné (`data/raw/`, exclu par `.gitignore`). Provenance, empreinte et instructions d'obtention : `data/README.md`. Anomalies connues du jeu de données : `docs/01-DATA_DICTIONARY.md`.

## Documentation

Point d'entrée : `docs/00-INDEX.md`. Notamment : spécification technique (`docs/02`), architecture et signatures de fonctions (`docs/03`), critères de validation par jalon (`docs/04`), décisions techniques justifiées (`docs/07`), registre des risques (`docs/08`), tableau de bord vivant du projet (`docs/11`).

## Organisation du développement

Développement assisté par Claude Code, avec un orchestrateur (session principale) et six agents spécialisés propriétaires d'un périmètre (`data-engineer`, `ml-engineer`, `automation-engineer`, `dashboard-developer`, `qa-validator`, `doc-keeper`). Chaque session commence par `/demarrer-session` et chaque jalon est vérifié par `/valider-jalon N` avant validation humaine. Détail : `docs/10-GOUVERNANCE_AGENTS.md`.

Le versionnement suit une règle systémique : une branche par jalon, commits au format Conventional Commits, pull request vers `main` avec le modèle `.github/pull_request_template.md`, fusion par merge commit après validation humaine. Détail : `.claude/rules/git-workflow.md` (décision : ADR-007, `docs/07-JOURNAL_DECISIONS.md`).

## Licence

MIT — voir `LICENSE`.
