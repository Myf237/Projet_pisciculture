# Tableau de bord du projet

> État vivant du projet, lu en début de chaque session (`/demarrer-session`) et tenu à jour par l'agent `doc-keeper`.
> **Dernière mise à jour :** 2026-09-18 — doc-keeper (borne DO définitive à 15 mg/L, article source versionné et attribué, J-20260918-022)

## Situation

- **Phase :** mise en place terminée — pull requests **#1** (merge commit `22d029d`, 2026-09-17T23:13:11Z) et **#2** de levée des réserves (merge commit `f7a123a`, 2026-09-17T23:50:18Z) fusionnées dans `main` par décision humaine (G2). Replanification décidée le 2026-09-18 (**G3**, ADR-008) : démonstration maintenue au **2026-09-23**, Jalons 1 et 2 regroupés au 2026-09-18 (voir `05-TIMELINE.md`).
- **Jour actuel :** Jour 1 du planning révisé — vendredi 2026-09-18. Branche de travail `feat/jalon-1-donnees-nettoyees`, créée depuis `origin/main`.
- **Jalon actif :** **Jalon 1** (Données nettoyées et fiables) — décisions G1 tranchées le 2026-09-18 (ADR-009, ADR-010, ADR-003 accepté) après lecture de l'article source du dataset ; implémentation du nettoyage (`src/ingestion.py`, `src/config.py`) par le data-engineer en cours ; seule la borne haute de l'oxygène dissous reste ouverte (A2). Jalon 2 (Exploration) à mener le même jour, juste après.
- **Avancement :** replanifié (ADR-008) après un jour de retard sur l'ADR-006 (mise en place non comptée comme jalon le 2026-09-17) ; plus aucune marge de planning avant la démonstration du 2026-09-23 (voir `08-REGISTRE_RISQUES.md`, R1).

## Jalons

Statuts : À faire · En cours · En vérification · Validé · Validé avec réserves · Bloqué

| # | Jalon | Jour prévu | Réalise | Statut | Validé le | Rapport |
|---|---|---|---|---|---|---|
| 1 | Données nettoyées et fiables | J1 — 18/09 | data-engineer | En cours | — | — |
| 2 | Exploration validée | J1 — 18/09 | data-engineer | À faire | — | — |
| 3 | Modèle de détection de risque opérationnel | J2-J3 — 19-20/09 | ml-engineer | À faire | — | — |
| 4 | Moteur de décision fonctionnel | J4 — 21/09 | automation-engineer | À faire | — | — |
| 5 | Dashboard démontrable | J5 — 22/09 | dashboard-developer | À faire | — | — |
| 6 | MVP intégré et démontrable | J6 — 23/09 | automation-engineer + dashboard-developer | À faire | — | — |

*Planning révisé le 2026-09-18 (ADR-008, remplace ADR-006) : Jalons 1 et 2 regroupés au Jour 1 (18/09) ; démonstration maintenue au 23/09.*

## Prérequis et blocages

| Élément | Bloque | Action | Statut |
|---|---|---|---|
| `data/raw/IoTpond1.csv` déposé par l'humain — SHA-256 `063ea4f0c9fcd24f016fbfc52e5422b655dfb4f3542d40476d99d899655dda76`, 6,8 Mo, 83 126 relevés, 11 colonnes conformes, suffixe « CET » confirmé ; 10 autres fichiers de bassins également présents (`IoTPond2.csv` à `IoTPond12.csv`, `IoTPond5.csv` absent du dépôt fourni), hors périmètre du MVP (ADR-001), tous ignorés par git | Jalon 1 | — | Levé (J-20260918-001, `docs/01`) |
| Environnement Python du projet | Jalon 1 | `python -m venv venv`, activation, `pip install -r requirements.txt` | Levé (J-20260917-001 : pandas 3.0.5, scikit-learn 1.9.1, streamlit 1.64.0, pytest 9.1.1) |
| Configuration des agents non encore chargée | Tous | Relancer Claude Code depuis la racine du projet, accepter la confiance du dossier, vérifier `/agents` et `/context` | Levé (agents opérationnels le 2026-09-16 au soir) |
| Pull request **#1** fusionnée dans `main` (merge commit `22d029d`, 2026-09-17T23:13:11Z) : https://github.com/Myf237/Projet_pisciculture/pull/1 | Jalon « préparation » | — | Levé (fusionnée, G2 obtenu, J-20260918-001) |
| Pull request **#2** (levée des réserves R1-R7) fusionnée dans `main` (merge commit `f7a123a`, 2026-09-17T23:50:18Z) : https://github.com/Myf237/Projet_pisciculture/pull/2 | Jalon 1 | — | Levé (fusionnée, G2 obtenu, J-20260918-012) |
| Replanification (Jalon 1 non démarré le 2026-09-17 comme prévu par l'ADR-006) | Jalon 1 | Décision **G3** de l'humain | Levé (ADR-008, démonstration maintenue au 23/09, Jalons 1-2 regroupés au 18/09, J-20260918-012) |
| GitHub CLI (`gh`) | Jalon « préparation » (ouverture de la PR) | Installation puis connexion interactive | Levé (installé et connecté — compte Myf237, dépôt public, droits admin — J-20260916-024, 027) |

## Décisions en attente

Constats de l'analyse de cadrage du 2026-09-16, tranchés le 2026-09-18 par ADR-009 et ADR-010 (détail : `01-DATA_DICTIONARY.md` anomalies 7 à 11, `08-REGISTRE_RISQUES.md` R9, R10, R12, R15). **Plus aucune décision en attente pour le Jalon 1** — la dernière, la borne haute d'oxygène dissous, a été confirmée à 15 mg/L le 2026-09-18 (voir « Décisions prises », ADR-010).

| Réf. | Sujet | Bloque | Piste recommandée (à confirmer — G1) | ADR |
|---|---|---|---|---|
| — | Seuil de turbidité (« à définir » dans le cahier des charges) | Jalon 2 | Fixé à partir de l'exploration et d'une source citée | à créer |
| A4 | Stratégie de labels et d'évaluation (circularité) + cible de rappel de la classe critique (« à définir » au Jalon 3) | Jalon 3 | Baseline « seuils seuls » + anomalies non triviales ; cible de rappel fixée avant entraînement | à créer |
| A5 | Approche de prédiction de croissance (Random Forest non extrapolant) | Jalon 3 (priorité 2) | Régression simple sur le log du poids, comparée à une baseline naïve | à créer |
| — | Mécanisme anti-oscillation des actions simulées | Jalon 4 | Hystérésis simple sur les règles à seuil | à créer |

## Décisions prises

| ADR | Décision | Date |
|---|---|---|
| ADR-001 | Dataset *Sensor Based Aquaponics Fish Pond Datasets*, fichier `IoTpond1.csv` | 2026-09-15 |
| ADR-002 | Modèles classiques interprétables (Isolation Forest / Random Forest) | 2026-09-15 |
| ADR-003 | Ammoniac seuillé à 5 (33,18 % marqué artefact), 66,82 % conservés | 2026-09-18 |
| ADR-004 | Stack Python, pandas, scikit-learn, Streamlit, fichiers plats | 2026-09-15 |
| ADR-005 | Gouvernance par agents spécialisés et traçabilité systémique | 2026-09-16 |
| ADR-006 | `05-TIMELINE.md` fait foi ; J1 = 2026-09-17 → J7 = 2026-09-23 — **remplacé par ADR-008** | 2026-09-16 |
| ADR-007 | Conventions Git et flux par pull requests (branches, Conventional Commits, fusion par merge commit après G2, tag `jalon-N`, garde-fou technique) ; contenu rédigé confirmé explicitement par l'humain le 2026-09-17 (J-20260917-014) | 2026-09-16 |
| ADR-008 | Replanification : démonstration maintenue au 2026-09-23 ; Jalons 1 et 2 regroupés au 2026-09-18 (remplace ADR-006) | 2026-09-18 |
| ADR-009 | Unités réelles mg/L (A1) ; ammoniac et nitrate = capteurs de gaz, indicateurs relatifs sans seuil absolu ; température/pH/DO = sondes immergées, seuils du cahier applicables | 2026-09-18 |
| ADR-010 | Bornes de nettoyage (température, pH, ammoniac, **DO = 15 mg/L définitif**), alerte thermique sur la plage critique (A3), fuseau horaire sans conversion, interpolation max 1 h, ré-échantillonnage horaire | 2026-09-18 |

## Réserves de validation en cours

Clos le 2026-09-18 : les 7 réserves ont toutes été levées (rapport `reports/validations/reserves-mise-en-place.md`, J-20260918-008) et la pull request #2 qui les portait est fusionnée (J-20260918-012). Section conservée ci-dessous comme trace de leur traitement.

Rapport `reports/validations/preparation-mise-en-place.md`, itération 2 : verdict **VALIDÉ AVEC RÉSERVES** (R1 à R7), après lequel la PR #1 a été fusionnée dans `main` (merge commit `22d029d`, 2026-09-17T23:13:11Z, décision G2 humaine, J-20260918-001). État des réserves :

| # | Réserve | Statut | Preuve | Propriétaire |
|---|---|---|---|---|
| R1 | `data/raw/` et `IoTpond1.csv` absents | **Levée** | Fichier déposé par l'humain, SHA-256 `063ea4f0c9fcd24f016fbfc52e5422b655dfb4f3542d40476d99d899655dda76`, 6,8 Mo, 83 126 relevés, 11 colonnes conformes, suffixe CET confirmé (J-20260918-001, `docs/01-DATA_DICTIONARY.md`) | humain |
| R2 | Défaut littéral `log_path` (D6) | **Levée** | `log_decision(action: dict, log_path: str \| Path \| None = None) -> None` ; `None` résolu depuis `config.DECISIONS_LOG_PATH`, plus de littéral en dur (J-20260918-003, `docs/03`) | automation-engineer |
| R3 | `docs/11` et `README.md` : compteur de tests, statuts, prochaine action | Traitée par cette mise à jour | — | doc-keeper |
| R4 | Heure des entrées du doc-keeper (sans shell) lue légèrement avant sa dernière écriture | En surveillance | Règle rappelée en J-20260917-020 ; appliquée à cette entrée (heure lue après la dernière écriture, J-20260918-006) | doc-keeper |
| R5 | `RANDOM_STATE = 42` à confirmer par son propriétaire | **Levée** | Confirmée (valeur inchangée) et justifiée par un commentaire dans la section Modèles de `src/config.py` (J-20260918-004, `docs/03`) | ml-engineer |
| R6 | Choix d'un « écart signé » continu dans `add_threshold_distance` à préciser | **Levée** | Convention précisée dans la docstring (signe, unité, bornes, nommage `<clé>_distance_critical`), synchronisée dans `docs/03` (J-20260918-005) | data-engineer |
| R7 | Conformité des commits à contrôler | **Levée** | 11 commits conformes aux Conventional Commits, trailers `Agent`/`Jalon`/`Journal` présents, 68 fichiers commités sans fichier interdit, fusion par merge commit `f7a123a` (J-20260918-008, rapport `reserves-mise-en-place.md`) | orchestrateur (contrôle qa-validator) |

## Prochaine action

1. **Jalon 1, en cours** : toutes les décisions G1 sont tranchées (ADR-003, ADR-009, ADR-010) — le data-engineer termine l'implémentation du nettoyage (`src/ingestion.py`, `src/config.py`, dont le retrait du commentaire « provisoire » sur `DISSOLVED_OXYGEN_BOUNDS`), puis vérification du Jalon 1 par le `qa-validator`.
2. **Jalon 2** le même jour (2026-09-18) : exploration et `features.py`, avec sa propre vérification par le `qa-validator` (rapport distinct de celui du Jalon 1).
3. Suite du planning révisé (ADR-008, `05-TIMELINE.md`) : Jalon 3 les 19-20/09 (point de bascule le 20/09 pour la prédiction de croissance), Jalon 4 le 21/09, Jalon 5 le 22/09, Jalon 6 le 23/09 (démonstration).

## Historique des mises à jour

| Date | Par | Changement | Journal |
|---|---|---|---|
| 2026-09-16 | orchestrateur | Création du tableau de bord (mise en place de la gouvernance) | J-20260916-010 |
| 2026-09-16 (soir) | doc-keeper | Règle git systémique et ADR-007 (Accepté) ; prérequis agents levé, installation Python en cours, ligne dépôt distant/branche/PR ajoutée | J-20260916-023 |
| 2026-09-17 | doc-keeper | Situation et prérequis actualisés (environnement Python levé, `data/raw/` G4, `gh` connecté) ; réserves de validation détaillées (rapport qa-validator, itération 1, D1-D11) ; décisions en attente D6, R13, ADR-007 ajoutées ; historique | J-20260917-012 |
| 2026-09-17 | doc-keeper | 3 décisions humaines tranchées (J-20260917-014) : R13 et confirmation ADR-007 retirées des décisions en attente et consignées dans les décisions prises ; prérequis `data/raw/` ajusté (pas de `.gitkeep`, `data/README.md` suffit) | J-20260917-015 |
| 2026-09-17 | doc-keeper | Itération 2 du qa-validator : verdict VALIDÉ AVEC RÉSERVES (R1-R7) ; PR #1 ouverte (lien, 10 commits) ; compteur de tests 29 → 31 ; réserves de validation remplacées par l'état final et le tableau R1-R7 ; « Prochaine action » alignée sur G2/G4/Jalon 1 | J-20260917-020 |
| 2026-09-18 | doc-keeper | PR #1 fusionnée dans `main` (merge commit `22d029d`) ; réserves R1, R2, R5, R6 levées avec preuve, R3 traitée, R4 en surveillance, R7 confiée au qa-validator ; compteur de tests 31 → 32 ; prérequis `data/raw/` Levé ; D6 retiré des décisions en attente (résolu par R2) ; prochaine action alignée sur la PR de levée des réserves, le Jalon 1 et la replanification (G3) | J-20260918-006 |
| 2026-09-18 | doc-keeper | Correction N2 (10 autres bassins, pas 11 ; `IoTPond5` absent) dans `docs/01` et `docs/11` | J-20260918-010 |
| 2026-09-18 | doc-keeper | G2 : PR #2 fusionnée (merge commit `f7a123a`) ; G3 : replanification ADR-008 (démo maintenue au 23/09, Jalons 1-2 regroupés au 18/09) ; jours prévus des jalons mis à jour, Jalon 1 En cours, ADR-006 marqué remplacé, ADR-008 ajouté aux décisions prises, prochaine action alignée sur le nouveau planning | J-20260918-013 |
| 2026-09-18 | doc-keeper | Décisions G1 du Jalon 1 après lecture de l'article source : ADR-009 (unités mg/L, ammoniac/nitrate = capteurs de gaz) et ADR-010 (bornes, alerte thermique sur la plage critique, fuseau sans conversion, interpolation 1 h, ré-échantillonnage horaire) ajoutés aux décisions prises avec ADR-003 ; décisions en attente réduites à la seule borne haute d'oxygène dissous (A2, ADR-010 Proposé) | J-20260918-020 |
| 2026-09-18 | doc-keeper | Borne haute d'oxygène dissous confirmée à 15 mg/L (ADR-010 entièrement Accepté) ; article source versionné et attribué (`docs/00-INDEX.md`, `docs/01`) ; plus aucune décision en attente pour le Jalon 1 ; prochaine action alignée sur la fin de l'implémentation du nettoyage | J-20260918-022 |
