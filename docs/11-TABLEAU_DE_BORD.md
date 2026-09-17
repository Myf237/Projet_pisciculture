# Tableau de bord du projet

> État vivant du projet, lu en début de chaque session (`/demarrer-session`) et tenu à jour par l'agent `doc-keeper`.
> **Dernière mise à jour :** 2026-09-17 — doc-keeper (itération 2 qa-validator : VALIDÉ AVEC RÉSERVES, PR #1 ouverte, J-20260917-020)

## Situation

- **Phase :** mise en place terminée côté agents — squelette créé et vérifié (`pytest -q` : 31 tests réussis, 38 prévus en `skip`, 0 échec) ; vérification indépendante `qa-validator`, itération 2 : **VALIDÉ AVEC RÉSERVES** (R1 à R7, voir « Réserves de validation en cours ») ; pull request **#1** ouverte vers `main`, fusionnable, en attente de la décision **G2** de l'humain (relecture puis fusion par merge commit).
- **Jour actuel :** Jour 1 — mercredi 2026-09-17. Le Jalon 1 démarre après la fusion de la pull request #1.
- **Jalon actif :** aucun.
- **Avancement :** à l'heure — Jour 1 consacré à la mise en place (structure, corrections, vérification, PR) ; Jalon 1 en attente de G2.

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
| `data/raw/` absent du dépôt (les agents n'ont pas le droit de le créer, permission `deny` — G4) ; `IoTpond1.csv` à y déposer | Jalon 1 | Créer `data/raw/` et y placer `IoTpond1.csv` (humain, avant le Jalon 1). Décidé le 2026-09-17 (J-20260917-014) : pas de `data/raw/.gitkeep` versionné, `data/README.md` suffit pour documenter l'obtention du dossier | Ouvert (G4) — action humaine attendue |
| Environnement Python du projet | Jalon 1 | `python -m venv venv`, activation, `pip install -r requirements.txt` | Levé (J-20260917-001 : pandas 3.0.5, scikit-learn 1.9.1, streamlit 1.64.0, pytest 9.1.1) |
| Configuration des agents non encore chargée | Tous | Relancer Claude Code depuis la racine du projet, accepter la confiance du dossier, vérifier `/agents` et `/context` | Levé (agents opérationnels le 2026-09-16 au soir) |
| Pull request **#1** ouverte, branche `chore/mise-en-place-projet` → `main` : https://github.com/Myf237/Projet_pisciculture/pull/1 (10 commits, fusionnable) | Jalon « préparation » | Décision **G2** de l'humain : relecture puis fusion par merge commit (tag optionnel) | En attente de G2 |
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
| D6 | Défaut littéral de `log_decision` (`log_path = "logs/decisions.log"`, `docs/03`) contraire à `conventions-code.md` (chemins construits depuis la racine) alors que `config.DECISIONS_LOG_PATH` existe (rapport qa-validator, préparation) | Jalon 4 | Arbitrage doc-keeper + automation-engineer avant l'implémentation du Jalon 4 | à créer |

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

Rapport `reports/validations/preparation-mise-en-place.md`. Itération 1 (2026-09-17, J-20260917-005) : NON VALIDÉ, 11 défauts (D1-D11). Itération 2 (2026-09-17, J-20260917-017) : plus qu'un défaut bloquant purement documentaire (N1), corrigé (J-20260917-018) → verdict **VALIDÉ AVEC RÉSERVES**. Tous les défauts D1 à D11 et N1 sont corrigés, expliqués ou reportés comme décision ouverte (D6, voir « Décisions en attente » ci-dessus) ; le détail de chaque correction et sa preuve figurent dans le rapport, section « Itération 2 ». Limite de 2 itérations atteinte : décision de fusion laissée à l'humain (G2) sous les réserves suivantes.

Réserves non bloquantes (R1 à R7) :

| # | Réserve | Propriétaire | Échéance |
|---|---|---|---|
| R1 | `data/raw/` et `IoTpond1.csv` absents ; décision humaine : pas de `.gitkeep` versionné, `data/README.md` suffit | humain (G4) | Avant l'ouverture du Jalon 1 |
| R2 | Défaut littéral `log_path = "logs/decisions.log"` (D6) : arbitrer entre `docs/03` et `conventions-code.md`, puis aligner code et doc | doc-keeper + automation-engineer (arbitrage orchestrateur, G1) | Avant l'implémentation du Jalon 4 |
| R3 | `docs/11` et `README.md` : compteur de tests, statuts D3/D10, « Prochaine action » et verdict à jour | doc-keeper | Cette mise à jour (J-20260917-020) |
| R4 | Heure des entrées du doc-keeper (sans shell) lue légèrement avant sa dernière écriture (2 min au plus) | doc-keeper | Prochaine entrée de journal — heure lue **après** la dernière écriture de document |
| R5 | `RANDOM_STATE = 42` (section ml-engineer de `config.py`, remplie par le data-engineer sur brief) à confirmer par son propriétaire | ml-engineer | Début du Jalon 3 |
| R6 | Choix d'un « écart signé » continu dans `add_threshold_distance`, alors que `docs/02` §3 laisse le choix binaire/continu | data-engineer | Début du Jalon 2 |
| R7 | Conformité des commits (Conventional Commits, trailers, aucun fichier interdit) à contrôler sur la PR #1 | orchestrateur (contrôle qa-validator) | Avant fusion |

## Prochaine action

1. **G2 — décision humaine sur la pull request #1** (https://github.com/Myf237/Projet_pisciculture/pull/1) : relecture, puis fusion par merge commit (tag optionnel), sous les réserves R1 à R7.
2. **G4 — humain** : créer `data/raw/` et y placer `IoTpond1.csv` (sans `.gitkeep` versionné, voir R1).
3. **Jalon 1**, après la fusion : `/demarrer-session`, création de la branche `feat/jalon-1-donnees-nettoyees` depuis `origin/main`, première délégation à `data-engineer` (chargement, empreinte SHA-256, analyse factuelle des colonnes concernées par A1, A2 et ADR-003, pour trancher ces décisions — G1 — avant d'écrire les règles de nettoyage).

## Historique des mises à jour

| Date | Par | Changement | Journal |
|---|---|---|---|
| 2026-09-16 | orchestrateur | Création du tableau de bord (mise en place de la gouvernance) | J-20260916-010 |
| 2026-09-16 (soir) | doc-keeper | Règle git systémique et ADR-007 (Accepté) ; prérequis agents levé, installation Python en cours, ligne dépôt distant/branche/PR ajoutée | J-20260916-023 |
| 2026-09-17 | doc-keeper | Situation et prérequis actualisés (environnement Python levé, `data/raw/` G4, `gh` connecté) ; réserves de validation détaillées (rapport qa-validator, itération 1, D1-D11) ; décisions en attente D6, R13, ADR-007 ajoutées ; historique | J-20260917-012 |
| 2026-09-17 | doc-keeper | 3 décisions humaines tranchées (J-20260917-014) : R13 et confirmation ADR-007 retirées des décisions en attente et consignées dans les décisions prises ; prérequis `data/raw/` ajusté (pas de `.gitkeep`, `data/README.md` suffit) | J-20260917-015 |
| 2026-09-17 | doc-keeper | Itération 2 du qa-validator : verdict VALIDÉ AVEC RÉSERVES (R1-R7) ; PR #1 ouverte (lien, 10 commits) ; compteur de tests 29 → 31 ; réserves de validation remplacées par l'état final et le tableau R1-R7 ; « Prochaine action » alignée sur G2/G4/Jalon 1 | J-20260917-020 |
