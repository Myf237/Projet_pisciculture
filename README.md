# Pisciculture IA — Suivi, prédiction et automatisation pour un bac de silure

MVP académique (mémoire de Master 1) : pipeline **données → analyse → prédiction → décision → action** pour un bac d'élevage de silure (*Clarias gariepinus*), à partir de données IoT réelles (`IoTpond1.csv`, dataset *Sensor Based Aquaponics Fish Pond Datasets*, Udanor et al.). Les actionneurs sont **simulés** : ce dépôt ne pilote aucun matériel physique.

Détail du contexte et des objectifs : `docs/cahier-des-charges-pisciculture-ia.md` (document de référence, gelé) et `docs/README_PROJET.md`.

## Statut

Mise en place fusionnée dans `main` — état au 2026-09-18 : squelette du dépôt terminé et vérifié — structure de fichiers et signatures de fonctions en place, sans logique métier (`pytest -q` : 32 tests réussis, 38 prévus en `skip`). Vérification indépendante par `qa-validator` : **VALIDÉ AVEC RÉSERVES**, pull request **#1** fusionnée par décision humaine (G2) le 2026-09-17 (merge commit `22d029d` — voir `docs/11-TABLEAU_DE_BORD.md`). Réserves techniques levées ; le Jalon 1 démarre après la fusion de la pull request de levée des réserves. Décisions bloquantes sur les données (unités, bornes, ammoniac) à trancher au tout début du Jalon 1 (`docs/11-TABLEAU_DE_BORD.md`).

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

### Aujourd'hui (Jalon 1 — nettoyage des données, implémenté et vérifié)

```powershell
python -m src.ingestion                        # régénère data/processed/pond1_clean.csv et reports/cleaning_report.json depuis data/raw/IoTpond1.csv
python -m src.ingestion --input <chemin.csv>   # même traitement sur un autre fichier brut (même schéma, docs/01)
```

Code de sortie 0 et message sur `stderr` en cas de succès ; code de sortie non nul et message d'erreur clair sur `stderr` en cas d'échec (ex. fichier brut introuvable). Cette commande ne couvre que le Module 1 (ingestion + nettoyage) — détail des artefacts produits : `docs/03-ARCHITECTURE_CODE.md`.

### À terme (Jalon 6 — pipeline complet, pas encore implémenté)

`python src\main.py` lève toujours `NotImplementedError` : le pipeline complet (ingestion → features → modèle → décision) arrive au Jalon 6.

```powershell
python src\main.py                 # pipeline complet : ingestion → modèle → décision (Jalon 6)
streamlit run dashboard\app.py     # dashboard de démonstration (rejeu historique, Jalon 5)
```

**Non implémenté à ce stade** : features, modèles de détection de risque et de croissance, moteur de décision, dashboard, pipeline complet (`src/main.py`). Le nettoyage des données (Jalon 1) est implémenté et vérifié (`reports/validations/jalon-1.md`). Voir `docs/11-TABLEAU_DE_BORD.md` pour l'état d'avancement réel par jalon.

## Données

Le fichier `IoTpond1.csv` n'est pas versionné (`data/raw/`, exclu par `.gitignore`). Provenance, empreinte et instructions d'obtention : `data/README.md`. Anomalies connues du jeu de données : `docs/01-DATA_DICTIONARY.md`.

## Documentation

Point d'entrée : `docs/00-INDEX.md`. Notamment : spécification technique (`docs/02`), architecture et signatures de fonctions (`docs/03`), critères de validation par jalon (`docs/04`), décisions techniques justifiées (`docs/07`), registre des risques (`docs/08`), tableau de bord vivant du projet (`docs/11`).

## Organisation du développement

Développement assisté par Claude Code, avec un orchestrateur (session principale) et six agents spécialisés propriétaires d'un périmètre (`data-engineer`, `ml-engineer`, `automation-engineer`, `dashboard-developer`, `qa-validator`, `doc-keeper`). Chaque session commence par `/demarrer-session` et chaque jalon est vérifié par `/valider-jalon N` avant validation humaine. Détail : `docs/10-GOUVERNANCE_AGENTS.md`.

Le versionnement suit une règle systémique : une branche par jalon, commits au format Conventional Commits, pull request vers `main` avec le modèle `.github/pull_request_template.md`, fusion par merge commit après validation humaine. Détail : `.claude/rules/git-workflow.md` (décision : ADR-007, `docs/07-JOURNAL_DECISIONS.md`).

## Licence

MIT — voir `LICENSE`.
