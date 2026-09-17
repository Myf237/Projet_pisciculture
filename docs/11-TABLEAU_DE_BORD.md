# Tableau de bord du projet

> État vivant du projet, lu en début de chaque session (`/demarrer-session`) et tenu à jour par l'agent `doc-keeper`.
> **Dernière mise à jour :** 2026-09-18 — doc-keeper (PR #1 fusionnée, réserves R1/R2/R5/R6 levées, J-20260918-006)

## Situation

- **Phase :** mise en place **fusionnée dans `main`** — pull request **#1** fusionnée par merge commit `22d029d` le 2026-09-17T23:13:11Z (décision humaine G2). `pytest -q` sur la branche `chore/reserves-verification` : **32 tests réussis, 38 prévus en `skip`, 0 échec**. Réserves du rapport de vérification (itération 2, `reports/validations/preparation-mise-en-place.md`) : **R1, R2, R5, R6 levées** ; **R3** traitée par cette mise à jour ; **R4** en surveillance ; **R7** confiée au `qa-validator` (voir « Réserves de validation en cours »). Travail de levée des réserves sur la branche `chore/reserves-verification`, pull request de suivi à vérifier et fusionner avant le Jalon 1.
- **Jour actuel :** 2026-09-18. Le Jalon 1 (prévu J1 = 2026-09-17 par l'ADR-006) n'a pas démarré à la date prévue — voir `08-REGISTRE_RISQUES.md`, R1 (délai) ; décision de replanification en cours (G3, humain).
- **Jalon actif :** aucun — le Jalon 1 démarre après la fusion de la pull request de levée des réserves.
- **Avancement :** réserves techniques levées le 2026-09-18 ; un jour de retard sur le planning de l'ADR-006 (Jalon 1 non démarré le 2026-09-17), replanification non tranchée.

## Jalons

Statuts : À faire · En cours · En vérification · Validé · Validé avec réserves · Bloqué

| # | Jalon | Jour prévu | Réalise | Statut | Validé le | Rapport |
|---|---|---|---|---|---|---|
| 1 | Données nettoyées et fiables | J1 — 17/09 | data-engineer | À faire | — | — |
| 2 | Exploration validée | J2 — 18/09 | data-engineer | À faire | — | — |
| 3 | Modèle de détection de risque opérationnel | J3-J4 — 19-20/09 | ml-engineer | À faire | — | — |
| 4 | Moteur de décision fonctionnel | J5 — 21/09 | automation-engineer | À faire | — | — |
| 5 | Dashboard démontrable | J6 — 22/09 | dashboard-developer | À faire | — | — |
| 6 | MVP intégré et démontrable | J7 — 23/09 | automation-engineer + dashboard-developer | À faire | — | — |

## Prérequis et blocages

| Élément | Bloque | Action | Statut |
|---|---|---|---|
| `data/raw/IoTpond1.csv` déposé par l'humain — SHA-256 `063ea4f0c9fcd24f016fbfc52e5422b655dfb4f3542d40476d99d899655dda76`, 6,8 Mo, 83 126 relevés, 11 colonnes conformes, suffixe « CET » confirmé ; 10 autres fichiers de bassins également présents (`IoTPond2.csv` à `IoTPond12.csv`, `IoTPond5.csv` absent du dépôt fourni), hors périmètre du MVP (ADR-001), tous ignorés par git | Jalon 1 | — | Levé (J-20260918-001, `docs/01`) |
| Environnement Python du projet | Jalon 1 | `python -m venv venv`, activation, `pip install -r requirements.txt` | Levé (J-20260917-001 : pandas 3.0.5, scikit-learn 1.9.1, streamlit 1.64.0, pytest 9.1.1) |
| Configuration des agents non encore chargée | Tous | Relancer Claude Code depuis la racine du projet, accepter la confiance du dossier, vérifier `/agents` et `/context` | Levé (agents opérationnels le 2026-09-16 au soir) |
| Pull request **#1** fusionnée dans `main` (merge commit `22d029d`, 2026-09-17T23:13:11Z) : https://github.com/Myf237/Projet_pisciculture/pull/1 | Jalon « préparation » | — | Levé (fusionnée, G2 obtenu, J-20260918-001) |
| Réserves techniques R2, R5, R6 levées sur la branche `chore/reserves-verification` ; pull request de suivi à vérifier (R7) et fusionner avant le Jalon 1 | Jalon 1 | Vérification `qa-validator` puis décision **G2** | En cours |
| GitHub CLI (`gh`) | Jalon « préparation » (ouverture de la PR) | Installation puis connexion interactive | Levé (installé et connecté — compte Myf237, dépôt public, droits admin — J-20260916-024, 027) |

## Décisions en attente

Constats de l'analyse de cadrage du 2026-09-16 (détail : `01-DATA_DICTIONARY.md` anomalies 7 à 11, `08-REGISTRE_RISQUES.md` R9 à R12).

| Réf. | Sujet | Bloque | Piste recommandée (à confirmer — G1) | ADR |
|---|---|---|---|---|
| A1 | Unité réelle de `Dissolved Oxygen`, `Ammonia`, `Nitrate` (en-têtes `g/ml` incohérents) | Jalon 1 | Vérifier dans l'article source ; hypothèse mg/L mal étiqueté à confirmer par les ordres de grandeur | à créer |
| A2 | Borne physique de l'oxygène dissous (max 41) et traitement du nitrate (45 → 1 936) | Jalon 1 | Analyse des distributions par le data-engineer avant décision | à créer |
| ADR-003 | Traitement de l'ammoniac (valeurs jusqu'à 4,27 × 10^11) | Jalon 1 | Exclusion documentée de la variable brute | ADR-003 (Proposé) |
| — | Hypothèse de fuseau horaire et limite maximale d'un trou interpolable | Jalon 1 | Horodatage local sans conversion ; limite à fixer après analyse des écarts entre relevés | à créer |
| — | Seuil de turbidité (« à définir » dans le cahier des charges) | Jalon 2 | Fixé à partir de l'exploration et d'une source citée | à créer |
| A4 | Stratégie de labels et d'évaluation (circularité) + cible de rappel de la classe critique (« à définir » au Jalon 3) | Jalon 3 | Baseline « seuils seuls » + anomalies non triviales ; cible de rappel fixée avant entraînement | à créer |
| A5 | Approche de prédiction de croissance (Random Forest non extrapolant) | Jalon 3 (priorité 2) | Régression simple sur le log du poids, comparée à une baseline naïve | à créer |
| A3 | Plage de température déclenchant l'alerte thermique (max observé 27,75 °C, optimal 26–32 °C) | Jalon 4 | Déclenchement sur la plage critique, vigilance sur la plage optimale | à créer |
| — | Mécanisme anti-oscillation des actions simulées | Jalon 4 | Hystérésis simple sur les règles à seuil | à créer |

## Décisions prises

| ADR | Décision | Date |
|---|---|---|
| ADR-001 | Dataset *Sensor Based Aquaponics Fish Pond Datasets*, fichier `IoTpond1.csv` | 2026-09-15 |
| ADR-002 | Modèles classiques interprétables (Isolation Forest / Random Forest) | 2026-09-15 |
| ADR-004 | Stack Python, pandas, scikit-learn, Streamlit, fichiers plats | 2026-09-15 |
| ADR-005 | Gouvernance par agents spécialisés et traçabilité systémique | 2026-09-16 |
| ADR-006 | `05-TIMELINE.md` fait foi ; J1 = 2026-09-17 → J7 = 2026-09-23 | 2026-09-16 |
| ADR-007 | Conventions Git et flux par pull requests (branches, Conventional Commits, fusion par merge commit après G2, tag `jalon-N`, garde-fou technique) ; contenu rédigé confirmé explicitement par l'humain le 2026-09-17 (J-20260917-014) | 2026-09-16 |

## Réserves de validation en cours

Rapport `reports/validations/preparation-mise-en-place.md`, itération 2 : verdict **VALIDÉ AVEC RÉSERVES** (R1 à R7), après lequel la PR #1 a été fusionnée dans `main` (merge commit `22d029d`, 2026-09-17T23:13:11Z, décision G2 humaine, J-20260918-001). État des réserves :

| # | Réserve | Statut | Preuve | Propriétaire |
|---|---|---|---|---|
| R1 | `data/raw/` et `IoTpond1.csv` absents | **Levée** | Fichier déposé par l'humain, SHA-256 `063ea4f0c9fcd24f016fbfc52e5422b655dfb4f3542d40476d99d899655dda76`, 6,8 Mo, 83 126 relevés, 11 colonnes conformes, suffixe CET confirmé (J-20260918-001, `docs/01-DATA_DICTIONARY.md`) | humain |
| R2 | Défaut littéral `log_path` (D6) | **Levée** | `log_decision(action: dict, log_path: str \| Path \| None = None) -> None` ; `None` résolu depuis `config.DECISIONS_LOG_PATH`, plus de littéral en dur (J-20260918-003, `docs/03`) | automation-engineer |
| R3 | `docs/11` et `README.md` : compteur de tests, statuts, prochaine action | Traitée par cette mise à jour | — | doc-keeper |
| R4 | Heure des entrées du doc-keeper (sans shell) lue légèrement avant sa dernière écriture | En surveillance | Règle rappelée en J-20260917-020 ; appliquée à cette entrée (heure lue après la dernière écriture, J-20260918-006) | doc-keeper |
| R5 | `RANDOM_STATE = 42` à confirmer par son propriétaire | **Levée** | Confirmée (valeur inchangée) et justifiée par un commentaire dans la section Modèles de `src/config.py` (J-20260918-004, `docs/03`) | ml-engineer |
| R6 | Choix d'un « écart signé » continu dans `add_threshold_distance` à préciser | **Levée** | Convention précisée dans la docstring (signe, unité, bornes, nommage `<clé>_distance_critical`), synchronisée dans `docs/03` (J-20260918-005) | data-engineer |
| R7 | Conformité des commits à contrôler | Confiée au `qa-validator` | Contrôle à faire sur la pull request de levée des réserves (branche `chore/reserves-verification`) | orchestrateur (contrôle qa-validator) |

## Prochaine action

1. Vérification par le `qa-validator` (réserve R7 : conformité des commits) puis décision **G2** de l'humain sur la pull request de levée des réserves (branche `chore/reserves-verification`).
2. **Jalon 1**, après cette fusion : `/demarrer-session`, création de la branche `feat/jalon-1-donnees-nettoyees` depuis `origin/main`, première délégation à `data-engineer` — analyse factuelle des colonnes concernées par A1, A2 et ADR-003 (empreinte déjà vérifiée, voir `docs/01`), pour trancher ces décisions (**G1**) avant d'écrire les règles de nettoyage.
3. **G3 — humain** : décision de replanification, le Jalon 1 n'ayant pas démarré le 2026-09-17 comme prévu par l'ADR-006 (voir `08-REGISTRE_RISQUES.md`, R1).

## Historique des mises à jour

| Date | Par | Changement | Journal |
|---|---|---|---|
| 2026-09-16 | orchestrateur | Création du tableau de bord (mise en place de la gouvernance) | J-20260916-010 |
| 2026-09-16 (soir) | doc-keeper | Règle git systémique et ADR-007 (Accepté) ; prérequis agents levé, installation Python en cours, ligne dépôt distant/branche/PR ajoutée | J-20260916-023 |
| 2026-09-17 | doc-keeper | Situation et prérequis actualisés (environnement Python levé, `data/raw/` G4, `gh` connecté) ; réserves de validation détaillées (rapport qa-validator, itération 1, D1-D11) ; décisions en attente D6, R13, ADR-007 ajoutées ; historique | J-20260917-012 |
| 2026-09-17 | doc-keeper | 3 décisions humaines tranchées (J-20260917-014) : R13 et confirmation ADR-007 retirées des décisions en attente et consignées dans les décisions prises ; prérequis `data/raw/` ajusté (pas de `.gitkeep`, `data/README.md` suffit) | J-20260917-015 |
| 2026-09-17 | doc-keeper | Itération 2 du qa-validator : verdict VALIDÉ AVEC RÉSERVES (R1-R7) ; PR #1 ouverte (lien, 10 commits) ; compteur de tests 29 → 31 ; réserves de validation remplacées par l'état final et le tableau R1-R7 ; « Prochaine action » alignée sur G2/G4/Jalon 1 | J-20260917-020 |
| 2026-09-18 | doc-keeper | PR #1 fusionnée dans `main` (merge commit `22d029d`) ; réserves R1, R2, R5, R6 levées avec preuve, R3 traitée, R4 en surveillance, R7 confiée au qa-validator ; compteur de tests 31 → 32 ; prérequis `data/raw/` Levé ; D6 retiré des décisions en attente (résolu par R2) ; prochaine action alignée sur la PR de levée des réserves, le Jalon 1 et la replanification (G3) | J-20260918-006 |
