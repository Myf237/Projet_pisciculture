# Validation — Jalon 2 : Exploration validée

- Date : 2026-09-18 23:49 · Itération : 1 · Validateur : qa-validator
- Branche : `feat/jalon-2-exploration-features` (4 commits au-dessus de `origin/main`, tag `jalon-1` en base)
- Livrables examinés : `notebooks/01_exploration.ipynb`, `reports/figures/jalon2_*.png` (7), `src/features.py`, `src/ingestion.py` (colonnes `_raw`), `src/config.py`, `tests/test_features.py`, `tests/test_ingestion.py`, `tests/test_config.py`, `reports/cleaning_report.json`, `reports/analyse-donnees-jalon1.md` (addendum daté), `data/processed/pond1_clean.csv` (régénéré)
- Références : `docs/04` (Jalon 2), `docs/02` §3 et §8, `docs/03`, `docs/01`, ADR-003, ADR-009, ADR-010, ADR-011, `reports/validations/jalon-1.md`, J-20260918-039 à 047
- Environnement : `venv/Scripts/python.exe` (pandas/numpy/matplotlib/jupyter). **Toutes les mesures ci-dessous ont été recalculées par le validateur** sur les fichiers eux-mêmes ou par exécution de scripts en mémoire ; aucun chiffre n'est repris du data-engineer sans recalcul. Aucun fichier suivi par git n'a été modifié (`git status` inchangé avant/après : seuls `logs/agents/actions.jsonl` et le journal du jour sont modifiés).
- **Verdict proposé : VALIDÉ AVEC RÉSERVES**

Les trois critères de `docs/04` sont satisfaits, et les six contrôles spécifiques du brief — dont l'absence de fuite temporelle, condition de validité du Jalon 3 — sont vérifiés **par construction de contre-exemples**, pas seulement par lecture du code. Les réserves sont toutes documentaires ou prospectives ; une seule a une portée technique réelle : **le signal brut restauré par l'ADR-011 n'est propagé par aucune des fonctions de features** (D1), ce qui vide l'ADR-011 de son effet en aval si rien n'est fait avant le Jalon 3.

---

## 1. Critères du Jalon 2 (`docs/04-JALONS_VALIDATION.md`)

| # | Critère (docs/04) | Méthode / commande | Observé | Verdict |
|---|---|---|---|---|
| 1 | Les distributions post-nettoyage sont cohérentes avec les seuils scientifiques du silure — et, pour les variables sans seuil applicable (ammoniac, nitrate, turbidité), l'interprétation ne prétend pas le contraire | Lecture de `reports/figures/jalon2_distributions_avant_apres.png` (8 panneaux) ; recalcul indépendant des parts hors seuils sur le livrable ; lecture des cellules markdown §1 et §6 du notebook exécuté | Figure : seuils tracés **uniquement** pour température (`critical_min=20`/`critical_max=35`), pH (`6`/`9`) et DO (`critical_min=3`) — issus de `config.get_applicable_thresholds()` ; **aucune ligne de seuil sur le panneau ammoniac**, ni panneau seuillé pour nitrate/turbidité. Recalcul : température **0,00 %** hors plage critique [20, 35] (min 23,00 / max 27,75) mais **95,79 %** sous l'optimum 26 °C — écart déjà chiffré et assumé par l'ADR-010 (l'alerte porte sur la plage critique, pas l'optimale) ; pH **0,46 %** hors [6, 9] sur 83 086 valeurs valides (les 145 relevés < 4 conservés par décision ADR-011) ; DO **22,23 %** sous le critique 3 sur 69 883 valeurs valides. Le notebook §1 accompagne chaque lecture de l'effectif réel (ammoniac 28,00 % manquant, DO 15,93 %) ; §6 traite explicitement la turbidité comme indicateur sans seuil absolu | ✅ |
| 2 | Une figure montre clairement au moins une période d'anomalie détectable à l'œil | Ouverture des 3 figures d'épisode ; vérification que le tracé correspond bien aux données (recalcul de la fenêtre) ; régénération complète du notebook et comparaison SHA-256 des PNG | `jalon2_anomalie_episode1_do_plateau.png` : bascule nette d'un régime 0-25 mg/L vers un plateau soutenu **36-41 mg/L** du 30/07 au 05/08, visible sans explication, avec bande orange de l'épisode et marques rouges `Dissolved Oxygen_missing` couvrant toute la largeur — la figure montre à la fois l'anomalie **et** le fait que le livrable nettoyé la perd. Deux autres figures pour l'épisode 2 (DO quasi nul, pH négatif). Les 7 PNG régénérés sont **bit à bit identiques** aux PNG commités (SHA-256 égaux un à un) : figures reproductibles, pas retouchées | ✅ |
| 3 | Les corrélations qualité d'eau ↔ croissance sont calculées **et interprétées**, même faibles (avec prise en compte des 81 paliers seulement et de la nature des capteurs) | Exécution du notebook ; recalcul indépendant du nombre de paliers via `ingestion.rebuild_growth_curve` ; lecture des cellules §3 | Table de 12 corrélations (6 variables × niveau/taux) avec, pour chacune, `n_paires` (55 à 81) **et** `part_paliers_avec_mesure_reelle` (0,691 pour l'ammoniac, 0,938 pour le DO, 1,000 ailleurs). Recalcul : `rebuild_growth_curve` → **81 paliers** (identique). Appariement par `merge_asof(direction="backward")`, explicitement justifié pour ne pas lire vers le futur. L'interprétation (§3 et Synthèse) énonce les trois limites attendues : effectif de 81 paliers insuffisant pour une significativité robuste ; confusion temporelle (croissance et nitrate croissent tous deux avec le cycle → r = 0,764 en niveau contre 0,483 en taux, lu comme un artefact et non un effet) ; ammoniac et nitrate = capteurs de gaz (ADR-009), valeur absolue non interprétable. Les corrélations de taux, présentées comme « la lecture la plus honnête », sont effectivement faibles à modérées (0,126 à 0,598) | ✅ |

**Definition of Done `docs/02` §8, point 1 (aucune valeur physiquement impossible)** — revérifiée sur le livrable régénéré à 23 colonnes : `Temperature` hors [0, 40] = **0** (23,00 / 27,75), `PH` hors [0, 14] = **0** (1,14327 / 8,55167), `DO` > 15 = **0** (0,007 / 14,994), `Ammonia` > 5 = **0** (max 4,98184). Les drapeaux `_imputed` et `_missing` ne sont jamais vrais simultanément (0 cas sur les 4 variables) et `<colonne nettoyée> is NaN ⇔ <label>_missing` sur les 83 126 lignes (0 divergence). ✅

---

## 2. Contrôles spécifiques demandés au brief

| # | Contrôle | Méthode / commande | Observé | Verdict |
|---|---|---|---|---|
| 4 | **Absence de fuite temporelle** dans `add_rolling_features` — contre-exemple construit, pas une lecture de code | Sur les 3 000 premières lignes réelles : perturbation massive de **toutes** les variables à partir des lignes 1 500, 2 000 et 2 999 (`v*1000 + 12345`), puis comparaison stricte des 12 colonnes `_rolling_mean`/`_rolling_std` sur **toutes** les lignes strictement antérieures. Plus : horodatages dupliqués, entrée non triée, recherche AST de `center=`/`closed=` | Écart maximal sur les lignes passées : **0,0** dans les 3 scénarios (et 0 divergence de `NaN`), alors que la ligne perturbée elle-même bouge de +292 à +312 — le test n'est donc pas trivialement satisfait. Aucun appel du code ne passe `center=` ni `closed=` (les deux occurrences textuelles de `center=True` sont dans la docstring et un commentaire, lignes 46 et 73). Aucun `shift(-…)`, `bfill` ni `interpolate` dans `src/features.py`. Réserve mineure, sans effet sur ce jeu : pour deux relevés **au même horodatage**, la feature dépend de l'ordre des lignes en entrée (le fichier n'en contient aucun — 0 doublon d'horodatage sur 83 126, confirmé par recomptage) | ✅ |
| 5 | **Agrégation horaire** : `n_measured + n_imputed + n_missing == n_readings`, aucune valeur inventée pour un créneau vide, une valeur interpolée jamais comptée comme mesurée | `features.resample_hourly` sur le livrable complet (2 789 créneaux × 6 variables) ; recalcul manuel d'un créneau tiré au sort ; totaux croisés avec les drapeaux du livrable | Invariant respecté sur **2 789 créneaux × 6 variables = 16 734 vérifications, 0 violation**, aucun `n_measured` négatif ; somme des `n_readings` = **83 126** = nombre de lignes source (aucun relevé perdu ni compté deux fois). **1 358 créneaux vides (48,69 %** — exactement la valeur annoncée par l'ADR-010) : 0 moyenne non-NaN et 0 compteur non nul sur ces créneaux (aucune valeur fabriquée, aucun report de la dernière valeur connue). Séparation mesuré/imputé exacte : DO 8 371 imputées et 61 512 mesurées dans le livrable = 8 371 et 61 512 dans les agrégats ; idem ammoniac (4 337 / 55 514), température (1 / 83 125), pH (0 / 83 086). Recalcul manuel du créneau 2021-07-25 01:00 : `n_readings` 42/42, moyennes et trois compteurs identiques au calcul indépendant pour DO, ammoniac et nitrate | ✅ |
| 6 | **Distance aux seuils** appliquée aux seules variables dont les seuils sont applicables ; quelques valeurs recalculées à la main | `add_threshold_distance` sur 8 lignes construites aux cas limites (juste sous, égal, juste au-dessus de chaque borne critique + NaN) ; recalcul manuel des 24 valeurs ; tentative de contournement par un dict `thresholds` forcé | Colonnes produites : `temperature_distance_critical`, `ph_distance_critical`, `dissolved_oxygen_distance_critical` — **et elles seules** (`config.get_applicable_thresholds()` = `{dissolved_oxygen, ph, temperature}`). Les 24 valeurs recalculées à la main coïncident exactement : température [-0,1 · 0,0 · 0,1 · 7,5 · 0,1 · 0,0 · -0,1 · NaN], pH [-0,1 · 0,0 · 0,5 · 1,5 · 0,5 · 0,0 · -0,1 · NaN], DO [-0,1 · 0,0 · 0,1 · 1,0 · 11,9 · 12,0 · 37,0 · NaN] — signe conforme à la convention (positif = marge, négatif = dépassement, 0 au seuil), NaN propagé sans valeur devinée. Un dict `thresholds` contenant volontairement `ammonia`/`nitrate`/`turbidity` avec des seuils numériques ne produit **aucune** colonne : le filtre porte bien sur le dict passé en paramètre | ✅ |
| 7 | **Taux de croissance** calculé entre paliers réels, pas ligne à ligne | `compute_growth_rate` sur la sortie de `rebuild_growth_curve` ; recalcul manuel de 4 paliers ; comparaison avec un calcul sur les 83 126 lignes brutes | 81 paliers (contre 83 126 lignes) ; premier taux = `NaN` (jamais extrapolé) ; recalculs manuels exacts : palier 1 `0,94 g / 24,0069 h = 0,039155` (code : 0,039155), palier 2 `0,039173`, palier 40 `0,016146`, palier 80 `0,103029`. 80 taux non nuls sur les paliers contre 79 seulement sur les 83 126 lignes brutes (le calcul ligne à ligne produirait ~83 000 zéros et des taux aberrants) : le calcul porte bien sur les paliers. Les 3 non-monotonies de `Fish_Length` se traduisent par 3 taux négatifs, conservés et non corrigés | ✅ |
| 8 | **ADR-011 appliqué** : colonne brute pour chaque variable bornée, jamais imputée, épisode 30/07-05/08 lisible dans le livrable régénéré (contrôlé par calcul) | Comparaison valeur par valeur `<label>_raw` ↔ CSV brut ; comptage sur la fenêtre exacte de l'épisode ; mutations injectées dans une copie hors dépôt pour vérifier que les tests détectent une régression | Livrable régénéré : **23 colonnes**, `_raw` présente pour les 4 variables bornées (température, pH, DO, ammoniac) et **absente** pour nitrate/turbidité (sans borne — conforme). Les 4 colonnes `_raw` sont **strictement identiques au CSV brut**, `NaN` compris (les 52 `NaN` d'ammoniac du brut sont préservés tels quels) : aucune imputation, aucune recopie depuis la colonne nettoyée. Épisode **2021-07-30 02:00 → 2021-08-05 09:00 = 13 422 lignes** : `Dissolved Oxygen(g/ml)` nettoyé → **368** valeurs non manquantes (dont 336 elles-mêmes imputées, soit **32 mesures réelles** seulement) et 13 054 `missing` ; `Dissolved Oxygen_raw` → **13 422/13 422**, moyenne **36,4668 mg/L**, **79,2 %** dans 35-41 mg/L, max 41,046. Les chiffres de l'ADR-011 (368 vs 13 422, moyenne 36,47) sont donc exacts et le signal est bien rétabli. Réserve : ce signal ne franchit pas la couche de features (défaut D1) | ✅ |
| 9 | **Notebook** : exécutable de bout en bout sans erreur, n'important que `src/`, sans logique réutilisable définie dedans | Ré-exécution complète d'une **copie** du notebook (`jupyter nbconvert --to notebook --execute`, `FIGURES_DIR` redirigé vers le répertoire de travail du validateur pour ne modifier aucun fichier suivi) ; analyse des imports et des définitions | Exécution : **code de sortie 0**, 28 cellules (13 code / 15 markdown), **aucune sortie d'erreur**, 7 figures écrites — toutes **bit à bit identiques** aux figures commitées. Imports : `sys`, `pathlib`, `numpy`, `pandas`, `matplotlib`, puis `from src import config, ingestion, features` — aucun autre module projet, aucune duplication de logique de nettoyage ou de features (le notebook appelle `ingestion.load_raw_data`/`clean_data`/`rebuild_growth_curve` et les 4 fonctions de `features`). **Une** fonction est toutefois définie dans le notebook : `plot_episode_raw_with_missing` (helper de tracé, 3 appels) — lecture stricte de `.claude/rules/conventions-code.md` (« aucune logique réutilisable n'y est définie ») | ⚠️ (défaut D6) |

---

## 3. Contrôles transverses

**Tests.** `venv/Scripts/python.exe -m pytest -q` → **89 réussis, 27 ignorés, 0 échec** (5,81 s). Les 27 `skip` sont tous rattachés aux Jalons 3 à 6 avec un motif explicite ; **aucun `skip` ne subsiste sur le Jalon 2** (`tests/test_features.py` : 19 tests réels). Répartition : `test_config.py` 29 · `test_ingestion.py` 30 · `test_features.py` 19 · `test_decision_engine.py` 14 · `test_models.py` 11 · `test_pipeline.py` 7 · `test_dashboard.py` 6. ✅

**Non-trivialité des tests (vérification par mutation).** Copie de `src/` et `tests/` hors du dépôt, mutation d'une seule ligne, exécution ciblée — **9 mutations sur 9 sont détectées, chacune par le test censé la couvrir** :

| Mutation injectée | Test qui échoue |
|---|---|
| `rolling(..., center=True)` (fuite future) | `test_add_rolling_features_uses_only_past_information` |
| `n_measured = n_present` (imputées comptées comme mesurées) | `test_resample_hourly_counts_are_consistent_with_total_readings` |
| Filtre `get_applicable_thresholds()` supprimé | `test_add_threshold_distance_omits_gas_sensors_and_undecided_turbidity` |
| Fréquence `"30min"` en dur au lieu de `config.RESAMPLING_FREQUENCY` | `test_resample_hourly_uses_configured_frequency` |
| Créneaux vides comblés par `ffill()` | `test_resample_hourly_does_not_invent_values_for_empty_slots` |
| Taux de croissance regardant la valeur suivante | `test_compute_growth_rate_is_causal_not_affected_by_future_measurement` |
| `_raw` recopiée depuis la colonne nettoyée | `test_clean_data_episode1_do_plateau_readable_again_in_raw_column…` |
| `NaN` brut remplacé par 0 dans `_raw` | `test_clean_data_raw_value_column_keeps_nan_when_raw_value_already_missing` |
| Suffixe `"_raw"` en dur au lieu de `config.RAW_VALUE_SUFFIX` | `test_clean_data_raw_value_suffix_comes_from_config_not_hard_coded` |

La suite de tests du Jalon 2 protège donc réellement les propriétés qu'elle annonce. ✅

**Valeurs en dur.** Recherche de littéraux numériques dans `src/` et `dashboard/` hors `src/config.py` : aucun seuil, aucune borne, aucun chemin, aucune fréquence en dur. Les seules occurrences sont des chiffres cités dans des docstrings (contexte R16, rappel des bornes) et la constante de conversion `3600.0` (secondes → heures), qui n'est pas un paramètre de configuration. ✅ — Réserve prospective : le notebook fixe en dur les bornes des deux épisodes (`"2021-07-30 02:00:00"`, etc.), acceptable dans un notebook d'exploration mais à déplacer dans `src/config.py` lorsque le scénario de démonstration du Jalon 5 s'en servira (`docs/02` §6).

**Cohérence code ↔ `docs/03` ↔ ADR.** Conformes : `RESAMPLING_FREQUENCY = "1h"` et `RAW_VALUE_SUFFIX = "_raw"` (ADR-010/011, `docs/03` L83) ; schéma 23 colonnes (`docs/03` L112-117) vérifié sur le livrable ; description des 4 fonctions (`docs/03` L139-142) conforme au comportement mesuré, invariant des compteurs inclus ; `THRESHOLDS` identique entre `src/config.py` et `docs/03` L73-80 ; bornes de nettoyage inchangées (ADR-010 : DO 21 614 relevés hors borne = **26,00 %** du fichier, recompté — valeur exacte de l'ADR). **Deux écarts** : la turbidité est décrite comme décision ouverte dans le code alors que l'ADR-011 l'a tranchée (D3), et `docs/03` L144 conserve la convention antérieure à l'ADR-009/010 (D4). ⚠️

**Traçabilité.** `venv/Scripts/python.exe .claude/hooks/audit_trace.py --date 2026-09-18` → **Verdict : ✅ CONFORME** — journal présent (47 entrées), 520 actions automatiques, **0 fichier modifié non cité dans le journal**, **0 entrée mal formée**. Les 7 échecs/refus enregistrés sont journalisés ou sans effet (refus de `git branch` pour un sous-agent, erreurs de heredoc, refus de périmètre). Les entrées J-20260918-039 à 047 couvrent bien la chaîne constat → correction → décision G1 → implémentation → documentation → délégation de vérification. Écart mineur : J-20260918-039 annonce « 6 figures produites » alors que 7 figures `jalon2_*` sont produites et commitées (D8). ✅ (avec réserve mineure)

**Périmètre (`cahier des charges` §3).** Rien hors périmètre : le travail livré couvre exactement le Module 2 de `docs/02` §3 (moyennes/écarts-types glissants, distance aux seuils, taux de croissance, agrégation temporelle, livrable d'exploration). Aucun modèle, moteur de décision ni dashboard n'a été anticipé. Observation de gouvernance : `reports/analyse-donnees-jalon1.md` (modifié par addendum daté) ne figure pas dans la liste « Tu écris » de `.claude/agents/data-engineer.md`, alors que ce fichier est de sa main depuis le Jalon 1 — c'est la liste qui est incomplète, pas l'action qui est abusive (addendum purement additif, aucune ligne existante réécrite, vérifié au diff).

**Git.** `git status` : seuls `logs/agents/actions.jsonl` et `logs/agents/journal/2026-09-18.md` sont modifiés (non commités — conforme à la règle 6 de `git-workflow.md`, les journaux rejoignent le commit de suivi de fin de session). `git log origin/main..HEAD` : **4 commits**, chacun avec un périmètre de fichiers cohérent avec le jalon (features+config+tests · ingestion+rapport+tests · notebook+figures+addendum · docs). Trailers `Agent`, `Jalon`, `Journal` présents sur les 4, `Refs` présent sur les 4, attribution `Co-Authored-By` présente. **Aucun fichier interdit** : pas de `data/raw/`, pas de `data/processed/`, pas de `venv/`, pas de `*.joblib`, plus gros fichier 152 Ko. `git check-ignore` confirme que `data/raw/IoTpond1.csv` et `data/processed/pond1_clean.csv` sont ignorés, et `git ls-files data` ne renvoie que `data/README.md` et `data/processed/.gitkeep`. Écarts mineurs de forme (D9). ✅

**Reproductibilité (contrôle ajouté par le validateur).** Deux exécutions de `ingestion.clean_data` sur le même brut produisent un CSV **identique au hash près**, lui-même identique au livrable présent sur disque : `data/processed/pond1_clean.csv` est bien l'artefact du code actuel, pas un fichier retouché. L'empreinte SHA-256 du brut citée dans `reports/cleaning_report.json` (`063ea4f0c9fc…`) est exacte (recalculée). ✅

---

## 4. Défauts à corriger

| # | Défaut | Preuve | Agent propriétaire | Bloquant ? |
|---|---|---|---|---|
| D1 | **Le signal brut restauré par l'ADR-011 ne franchit pas la couche de features.** Ni `add_rolling_features` (qui itère sur les clés de `config.SENSOR_TYPES`, donc sur les colonnes **nettoyées**) ni `resample_hourly` ne traitent les colonnes `<label>_raw` : l'objectif de l'ADR-011 (« le Jalon 3 dispose du signal brut pour la détection ») est satisfait dans le fichier nettoyé mais perdu dès la première transformation en aval | Colonnes de sortie de `resample_hourly` sur le livrable : 26 colonnes, **aucune contenant `_raw`** ; colonnes `*_rolling_mean` produites : les 6 variables nettoyées uniquement. Conséquence mesurable : sur l'épisode 1, l'agrégat horaire ne voit que 368 valeurs (dont 336 imputées) au lieu de 13 422 | data-engineer (cadrage à confirmer avec ml-engineer au Jalon 3) | Non bloquant pour le Jalon 2 · **à traiter avant le début du Jalon 3** |
| D2 | **Contradiction interne du notebook** : la cellule « Synthèse » affirme que les deux épisodes sont « reproduits ici depuis les données nettoyées + agrégation horaire causale (§2) », alors que §2 et §5 établissent et démontrent exactement l'inverse (figures construites sur `raw_df`, l'épisode 1 étant entièrement absent du livrable nettoyé). Énoncé trompeur dans un livrable destiné au mémoire | Cellule markdown finale du notebook vs cellules markdown §2 (« Les figures ci-dessous utilisent donc le signal **brut** ») et code de `plot_episode_raw_with_missing` (lit `raw_df`) | data-engineer | Non bloquant · à corriger avant la PR |
| D3 | **La turbidité est décrite comme décision ouverte alors que l'ADR-011 (Accepté) l'a tranchée** (indicateur relatif, sans seuil absolu) : `THRESHOLDS["turbidity"]` commenté « à définir après exploration — Jalon 2 (docs/11) », `SENSOR_TYPES["Turbidity(NTU)"]["bounds"]` commenté « seuil à définir », `absolute_thresholds_applicable = None` alors que l'en-tête de `src/config.py` documente `None` comme signifiant « décision ouverte, non tranchée » (les capteurs de gaz tranchés valent `False`), `note` « Seuil non tranché (décision ouverte, Jalon 2) » — recopiée telle quelle dans `reports/cleaning_report.json` —, docstrings de `src/features.py` et `src/ingestion.py`, notebook §5/§6, nom du test `…_excludes_gas_sensors_and_undecided_turbidity`, et `docs/03` L79. `docs/11` affirme pourtant « plus aucune décision en attente pour les Jalons 1 et 2 » : la référence pointe vers une ligne désormais supprimée | Lectures croisées citées ; comportement inchangé (`get_applicable_thresholds()` exclut la turbidité dans les deux cas) | data-engineer (code, config, notebook) · doc-keeper (`docs/03` L79 et formulation de la conséquence d'ADR-011, qui dit « traitement inchangé » sans lever l'étiquette « non tranché ») | Non bloquant (aucun effet sur le comportement) |
| D4 | **`docs/03` L144 conserve la convention antérieure à l'ADR-009/010** : « Colonne non produite … si le paramètre est `dissolved_oxygen`, `ammonia` ou `nitrate` tant que son unité n'est pas tranchée (décision A1) » — contredit la L140 du même document (restriction à `get_applicable_thresholds()`, DO inclus), le code, et la réserve D3 du rapport du Jalon 1 déjà traitée dans la docstring de `add_threshold_distance`. Mentionne aussi `ammonia`/`nitrate` comme exemples de « borne unique supérieure », alors que le code précise qu'aucun paramètre applicable n'est dans ce cas | `docs/03-ARCHITECTURE_CODE.md` L140 vs L144 ; sortie réelle : `dissolved_oxygen_distance_critical` est produite | doc-keeper | Non bloquant |
| D5 | **L'ADR-011 n'est cité ni dans `reports/cleaning_report.json` ni dans l'en-tête de `src/ingestion.py`**, alors que les colonnes `_raw` du livrable en découlent directement : `decisions_applied = ["ADR-003", "ADR-009", "ADR-010"]` | Lecture du rapport régénéré et du module | data-engineer | Non bloquant |
| D6 | **Le notebook définit une fonction** (`plot_episode_raw_with_missing`, 3 appels), là où `.claude/rules/conventions-code.md` demande qu'« aucune logique réutilisable » n'y soit définie. Il s'agit d'un helper de tracé, non de logique métier — mais la règle ne distingue pas | Cellule code 4 du notebook | data-engineer (lecture de la règle à confirmer — voir §5) | Non bloquant |
| D7 | **Étiquetage d'unité incohérent entre figures** : les axes de `jalon2_distributions_avant_apres.png` portent les noms bruts « Dissolved Oxygen(g/ml) » et « Ammonia(g/ml) », alors que l'ADR-009 établit que `g/ml` est une **erreur d'étiquetage** du CSV Kaggle et que l'unité réelle est mg/L — ce que la figure d'épisode affiche d'ailleurs correctement (« mg/L, brut »). Risque direct de citation erronée dans le mémoire | Comparaison des deux figures | data-engineer | Non bloquant · à corriger avant usage mémoire |
| D8 | **Écart de comptage dans le journal** : J-20260918-039 annonce « 6 figures produites dans `reports/figures/` », 7 figures `jalon2_*` ont été produites et commitées (c34c8c3) | `git show --stat c34c8c3` ; régénération : 7 PNG | data-engineer (journal append-only : correction par nouvelle entrée) | Non bloquant |
| D9 | **Écarts mineurs à `.claude/rules/git-workflow.md` §3** : portée `analyse` du commit `c34c8c3` absente de la liste de portées autorisées ; résumé du même commit non formulé à l'impératif ; une ligne de corps à 73 caractères (limite 72) dans `b8087c3` | `git log origin/main..HEAD` | orchestrateur (les sous-agents ne commitent pas) | Non bloquant |

**Observations sans caractère de défaut** (à conserver pour la suite, aucune action exigée au Jalon 2) :
- `add_rolling_features` dépend de l'ordre des lignes en entrée lorsque deux relevés portent **le même horodatage** (ce n'est pas une fuite : à horodatage égal, le « passé » n'est pas défini). Sans effet ici : 0 doublon d'horodatage sur 83 126 lignes. À garder en tête si un autre bassin (`IoTpond2.csv`…) en contient.
- Aucun test de `tests/test_config.py` ne couvre `RAW_VALUE_SUFFIX` ; la constante est couverte indirectement par `tests/test_ingestion.py` (monkeypatch).
- Dates des deux épisodes en dur dans le notebook : à déplacer en configuration quand le scénario de démonstration du Jalon 5 les réutilisera.
- La liste « Tu écris » de `.claude/agents/data-engineer.md` omet `reports/analyse-donnees-jalon1.md`, qu'il alimente depuis le Jalon 1.

---

## 5. Points à trancher par l'humain

1. **(G1 — conséquence directe de l'ADR-011, défaut D1)** Comment le signal brut doit-il être exploité en aval ? L'ADR-011 énonce que « le Jalon 3 doit choisir explicitement quelle colonne il utilise », mais aucune fonction de `src/features.py` n'expose aujourd'hui les colonnes `_raw` : en l'état, le modèle du Jalon 3 ne pourra détecter l'épisode 1 que par son **absence** (`_missing`), ce que l'ADR-011 voulait précisément éviter. Trois pistes à arbitrer, non tranchées ici : agréger aussi les colonnes `_raw` (moyenne + compteurs), produire un indicateur d'écart `raw` vs nettoyé, ou assumer la détection par l'absence. **Le validateur ne fixe pas la cible.**
2. **(G1 — défaut D6)** Lecture de la règle « aucune logique réutilisable n'est définie dans un notebook » : s'applique-t-elle à un helper de **tracé** sans logique métier ? Si oui, le helper doit être supprimé ou déplacé — mais `docs/03` ne prévoit aucun module de visualisation avant le dashboard du Jalon 5. Le validateur signale l'ambiguïté sans la lever.
3. **(G2)** Fusion de la pull request du Jalon 2 et passage au Jalon 3, au vu du présent verdict et du traitement retenu pour les réserves D1 à D9.

---

*Rapport produit par le `qa-validator` — aucune correction apportée au code, aucun fichier suivi par git modifié. Entrée de journal : J-20260918-048.*

---
---

# Validation — Jalon 2 : Exploration validée — **Itération 2**

- Date : 2026-09-19 07:53 · Itération : 2 · Validateur : qa-validator
- Branche : `feat/jalon-2-exploration-features`, **7 commits** au-dessus de `origin/main` ; base de comparaison de cette itération : `b8087c3..HEAD` (`09a6b7b`, `194db31`, `32c987b`)
- Correctifs examinés : data-engineer J-20260919-002 (D1, D2, D3 code/notebook, D5, D6, D7) · doc-keeper J-20260919-004 (D3 `docs/`, D4) · data-engineer J-20260919-003 (D8) · orchestrateur (D9, portée `analyse`)
- Références ajoutées : décision G1 J-20260919-001 (propagation du signal brut), J-20260919-006 (ré-exécution hors harnais mise de côté par `git stash`)
- **Toutes les mesures de cette itération ont été recalculées par le validateur.** Aucun chiffre n'est repris d'un agent sans recalcul indépendant. Aucun fichier suivi par git n'a été modifié : `git status --short` montre `logs/agents/actions.jsonl` et `logs/agents/journal/2026-09-19.md` avant **et** après mon passage. Le notebook a été ré-exécuté sur une **copie hors dépôt** avec `FIGURES_DIR` et `PROJECT_ROOT` redirigés.
- **Verdict proposé : VALIDÉ AVEC RÉSERVES**

Le défaut D1 — seul défaut à portée technique de l'itération 1 — est **entièrement levé et vérifié par recalcul indépendant**, ainsi que D2, D3, D4, D5, D6, D7 et D8. D9 n'est que partiellement levé. Trois défauts **nouveaux** apparaissent (D10, D11, D12), dont un — D12 — **contredit le diagnostic de J-20260919-006** et invalide la méthode de preuve du critère 2 utilisée en itération 1. Aucun n'est bloquant pour les trois critères de `docs/04`, qui restent satisfaits.

---

## 6. Défauts de l'itération 1 — levée défaut par défaut

| # | Défaut (itération 1) | Méthode de contre-vérification | Chiffre recalculé / observé | Verdict |
|---|---|---|---|---|
| **D1** | Le signal brut ne franchit pas la couche de features | 6 contrôles indépendants détaillés au §7 | `resample_hourly` produit **42 colonnes** (contre 26) et `add_rolling_features` **20 colonnes glissantes** (contre 12) ; recalcul totalement indépendant : **0 écart sur 55 780 comparaisons** | ✅ **levé** |
| **D2** | Cellule « Synthèse » du notebook contredisait §2/§5 | Lecture de la cellule 32 du notebook exécuté | La synthèse dit désormais « **reproduits ici depuis le signal brut** (`raw_df`, colonnes `<label>_raw`), pas depuis les données nettoyées », et cite le défaut corrigé. Plus aucune contradiction avec §2 et §5 | ✅ **levé** |
| **D3** | Turbidité décrite comme décision ouverte malgré l'ADR-011 | Relecture croisée des 8 emplacements listés en itération 1 | `src/config.py` : `absolute_thresholds_applicable` passé de `None` à **`False`** (et l'en-tête documente désormais `None` comme « réservé à une variable non tranchée — aucune entrée de `SENSOR_TYPES` n'est plus dans ce cas ») ; commentaires `THRESHOLDS["turbidity"]` et `SENSOR_TYPES[...]["bounds"]` réécrits ; `note` du rapport de nettoyage régénérée (« ADR-011 : indicateur relatif, aucun seuil absolu retenu ») ; docstrings de `src/ingestion.py` et `src/features.py` ; notebook §5 (cellule 27) et §6 (cellules 28/31) ; `docs/03` L79 ; `docs/11` L43. Test ajouté `test_sensor_types_turbidity_is_decided_indicator_not_open_decision_per_adr_011`. Comportement de `get_applicable_thresholds()` inchangé (vérifié) | ✅ **levé** |
| **D4** | `docs/03` L144 conservait la convention antérieure à l'ADR-009/010 | `git diff b8087c3..HEAD -- docs/03-ARCHITECTURE_CODE.md` | Le paragraphe est réécrit : exclusion fondée sur `config.get_applicable_thresholds()`, `ammonia`/`nitrate` exclus « capteurs de gaz, ADR-009 — **pas une question d'unité** », `turbidity` « ADR-011 — décision tranchée, pas ouverte », et la mention « borne unique supérieure (ex. `ammonia`, `nitrate`) » remplacée par « aucun paramètre actuellement applicable n'est dans ce cas ». Plus de contradiction avec la L140 | ✅ **levé** |
| **D5** | ADR-011 absent de `decisions_applied` et de l'en-tête de `src/ingestion.py` | Lecture du rapport régénéré et du module | `reports/cleaning_report.json` : `decisions_applied = ["ADR-003", "ADR-009", "ADR-010", "ADR-011"]` ; en-tête de `src/ingestion.py` : « ADR-011 (colonnes `<label>_raw` conservant le signal brut en parallèle, plage de pH inchangée, turbidité en indicateur relatif) » | ✅ **levé** |
| **D6** | Fonction définie dans le notebook | Recherche AST des `def` dans les 33 cellules | **1 seule** fonction définie (`plot_episode_raw_with_missing`, inchangée, non déplacée — conforme à la décision d'orchestrateur J-20260919-001). L'exception est signalée **deux fois** explicitement : cellule d'introduction (« Exception assumée : un helper de **tracé** […] toléré jusqu'au Jalon 5 en l'absence de tout module de visualisation avant le dashboard ») et §5 (« Décision d'orchestrateur (défaut D6) : tolérée jusqu'au Jalon 5, non déplacée dans `src/` ») | ✅ **levé** (dans les termes de la décision) |
| **D7** | Étiquetage d'unité incohérent entre figures | Lecture du code de la cellule 5 + régénération de la figure | Table `UNIT_DISPLAY = {"Temperature": "°C", "PH": "", "Dissolved Oxygen": "mg/L", "Ammonia": "mg/L"}`, appliquée via `ax.set_xlabel(axis_label)` — exactement la cible du brief (mg/L pour DO et ammoniac, °C pour la température, **aucune** unité pour le pH). Commentaire explicite : « purement présentationnel (axes de figure), jamais utilisé pour un calcul ni une borne ». La figure de démonstration `add_rolling_features`, qui n'avait aucun `ylabel`, en a un (« Dissolved Oxygen (mg/L) ») | ✅ **levé** |
| **D8** | J-20260918-039 annonçait 6 figures au lieu de 7 | `git diff b8087c3..HEAD -- logs/agents/journal/2026-09-18.md \| grep "^-"` | **Aucune ligne supprimée** : J-20260918-039 n'a pas été réécrite (append-only respecté, règle n°5). La correction est portée par la nouvelle entrée J-20260919-003, qui donne les deux chiffres exacts : **7** au moment de `c34c8c3`, **8** aujourd'hui. Recomptage : `ls reports/figures/jalon2_*` → **8** figures | ✅ **levé** |
| **D9** | Écarts de forme aux Conventional Commits | `git log b8087c3..HEAD` + mesure des longueurs | Portée `analyse` ajoutée à `.claude/rules/git-workflow.md` (choix assumé de ne pas réécrire un historique poussé). Sujets des 3 nouveaux commits : 65 / 67 / 70 caractères (≤ 72), impératif, minuscule, sans point. Trailers `Agent`/`Jalon`/`Refs`/`Journal` + `Co-Authored-By` présents sur les 3. **Mais** `194db31` contient une ligne de corps de **73 caractères** (« La turbidité n'est plus marquée comme décision ouverte, l'ADR-011 l'ayant »), limite 72 — le même écart exactement que celui signalé en itération 1 sur `b8087c3` | ⚠️ **partiellement levé** |

---

## 7. D1 en détail — six contrôles indépendants

Tous les contrôles portent sur le **livrable réel régénéré** (`ingestion.clean_data` sur `data/raw/IoTpond1.csv`, 83 126 lignes × 23 colonnes, forme identique au CSV présent sur disque), pas sur un jeu synthétique.

| # | Contrôle | Méthode | Observé | Verdict |
|---|---|---|---|---|
| 7.1 | **Colonnes produites** | Énumération des sorties de `add_rolling_features` et `resample_hourly` sur le livrable complet | `add_rolling_features` : **8 colonnes brutes** ajoutées (`Temperature_raw_rolling_mean/_std`, `PH_raw_…`, `Dissolved Oxygen_raw_…`, `Ammonia_raw_…`) en plus des 12 nettoyées → 20. `resample_hourly` : **42 colonnes** sur 2 789 créneaux, dont pour chacune des 4 variables bornées `<label>_raw_mean`, `<label>_raw_n_present`, `<label>_n_out_of_bounds`, `<label>_gap_mean`. Exactement les 4 colonnes exigées par la décision G1 | ✅ |
| 7.2 | **Recalcul totalement indépendant des agrégats** | Reconstruction par `groupby(index.floor("1h"))` — chemin de calcul différent du `resample` du code — pour `raw_mean`, `raw_n_present`, `n_out_of_bounds`, `gap_mean` et `mean` nettoyée, sur les 4 variables bornées × 2 789 créneaux | **0 écart sur 55 780 comparaisons** (NaN comparés comme NaN). Les agrégats du code sont exacts | ✅ |
| 7.3 | **Causalité de la colonne brute roulée** (contre-exemple construit, pas lecture de code) | Sur les 3 000 premières lignes réelles : perturbation de **toutes** les colonnes (nettoyées **et** `_raw`) à partir des lignes 1 500, 2 000 et 2 999 (`v*1000 + 12345`), comparaison stricte des 20 colonnes glissantes sur les lignes **strictement** antérieures (`iloc[:cut]`) | Écart maximal sur les lignes passées : **0,0** dans les 3 scénarios, dont **0,0** sur les seules colonnes brutes ; **0** divergence de `NaN`. Non-trivialité : la ligne perturbée elle-même bouge de **+161,7 / +195,2 / +396,3** sur `Dissolved Oxygen_raw_rolling_mean`. Entrée volontairement mélangée (`sample(frac=1)`) → résultat identique après tri interne (écart 0,0). Recherche AST : **aucun** appel avec `center=` ou `closed=` ; aucun `shift(`, `bfill`, `interpolate` ni `fillna` dans `src/features.py`. 0 doublon d'horodatage sur 83 126 lignes | ✅ |
| 7.4 | **Non-contamination brut ↔ nettoyé, dans les deux sens** | Quatre perturbations ciblées : (a) seules les colonnes `_raw` perturbées, (b) seules les colonnes nettoyées perturbées — appliquées à `add_rolling_features` **et** à `resample_hourly` | `add_rolling_features` : (a) écart max sur les glissantes **nettoyées = 0,0** (brutes : 2,96·10¹²) ; (b) écart max sur les glissantes **brutes = 0,0** (nettoyées : 2,38·10⁵). `resample_hourly` : (a) agrégats **nettoyés = 0,0** (bruts : 2,82·10¹¹) ; (b) agrégats **bruts = 0,0** (nettoyés : 2,36·10⁵). Séparation stricte des deux séries, vérifiée par l'effet et non par la docstring | ✅ |
| 7.5 | **`n_out_of_bounds` compté sur le signal brut, même découpage en créneaux** | (a) colonne **nettoyée** DO forcée à 999 → le compteur doit être inchangé ; (b) colonne **brute** DO forcée à 999 → le compteur doit exploser ; (c) recalcul **à la main** sur 3 créneaux tirés au sort (graine 20260919) ; (d) totaux croisés avec `reports/cleaning_report.json` | (a) compteur **strictement identique** (743 sur les 3 000 lignes) ; (b) 743 → **3 000** (non trivial). (c) créneaux 2021-07-15 03:00, 2021-07-13 05:00, 2021-08-27 17:00 : `n_readings`, `raw_n_present`, `raw_mean` et `n_out_of_bounds` **identiques au calcul manuel** pour les 4 variables bornées (ex. 2021-07-13 05:00 : DO 5/5, ammoniac 5/5, température 0/0, pH 0/0) — le découpage est bien celui des autres compteurs. (d) Totaux sur tout le fichier : Température **1**, pH **40**, DO **21 614**, ammoniac **27 560** — **exactement** les `n_out_of_bounds` de `reports/cleaning_report.json`, et le DO à 21 614 = **26,00 %**, valeur exacte de l'ADR-010 | ✅ |
| 7.6 | **`gap_mean` : `NaN` sans valeur inventée ; absence des colonnes pour nitrate/turbidité** | Comptage sur les 2 789 créneaux ; énumération des colonnes | `gap_mean` est `NaN` **partout** où la moyenne nettoyée est `NaN` : **0 violation** sur 1 358 (température) / 1 389 (pH) / 1 488 (DO) / 1 809 (ammoniac) créneaux concernés — aucune valeur fabriquée. Les créneaux les plus informatifs (moyenne brute présente, nettoyée absente) existent bien : 31 pour le pH, **130 pour le DO**, 451 pour l'ammoniac. Aucune des 4 colonnes `_raw_mean` / `_raw_n_present` / `_n_out_of_bounds` / `_gap_mean` n'est produite pour **Nitrate** ni **Turbidity** (sans borne — conforme) | ✅ |

### Chiffres du data-engineer (J-20260919-002) — **tous recalculés, tous confirmés**

| Affirmation J-20260919-002 | Recalcul du validateur | Verdict |
|---|---|---|
| 152 créneaux couvrent l'épisode 1 (30/07 02:00 → 05/08 09:00) | **152** | ✅ |
| 11/152 créneaux à moyenne nettoyée non-NaN | **11 / 152** | ✅ |
| 13 447 valeurs brutes présentes | **13 447** (somme des `raw_n_present` **et** comptage direct sur les relevés) | ✅ |
| moyenne des moyennes horaires brutes = 36,157 mg/L | **36,1569 mg/L** | ✅ |
| 109/140 créneaux à moyenne brute dans [35, 41] mg/L | **109 / 140** | ✅ |
| `Dissolved Oxygen_n_out_of_bounds` cumulé = 13 390 | **13 390** (et recomptage direct « brut > 15 » sur la fenêtre : 13 390) | ✅ |
| 57 valeurs mesurées côté nettoyé sur tout l'épisode | **57** mesurées, 336 imputées, 13 054 manquantes (somme = 13 447) | ✅ |

### Écart 13 422 (itération 1) vs 13 447 (itération 2) — **expliqué, ce n'est pas un défaut de calcul**

Les deux chiffres sont exacts, dans deux cadrages différents :

- **13 422** = relevés dont l'horodatage tombe dans l'intervalle **fermé** `[2021-07-30 02:00:00 , 2021-08-05 09:00:00]` (comptage ligne à ligne, itération 1) ;
- **13 447** = relevés couverts par les **152 créneaux horaires** `02:00 … 09:00`, le dernier créneau couvrant `09:00:00 → 09:59:59` (cadrage de l'agrégation horaire, itération 2).

Écart recalculé : **exactement 25 relevés**, tous situés dans le créneau `09:00` du 05/08 après `09:00:00`. Vérifié dans les deux sens : `raw_n_present` sur la fenêtre fermée = 13 422, sur la couverture horaire = 13 447. Le nombre de mesures nettoyées suit le même écart (32 → 57, soit +25). **Aucun chiffre n'est faux ; c'est la définition de la fenêtre qui change.** En revanche leur coexistence non expliquée dans la documentation constitue le défaut **D11** ci-dessous.

---

## 8. Non-régression des invariants validés en itération 1

| Invariant (itération 1) | Recalcul itération 2 | Verdict |
|---|---|---|
| `n_measured + n_imputed + n_missing == n_readings` | **0 violation** sur 2 789 créneaux × 6 variables = **16 734 vérifications** ; aucun `n_measured` négatif | ✅ |
| Somme des `n_readings` = 83 126 | **83 126** — aucun relevé perdu ni compté deux fois malgré les 16 colonnes ajoutées | ✅ |
| Créneaux vides non comblés | **1 358 créneaux vides (48,69 %** — valeur exacte de l'ADR-010) ; sur ces créneaux : **0** moyenne non-NaN (sur les 12 colonnes `_mean`, brutes incluses) et **0** compteur non nul (sur les 22 colonnes de comptage). Les colonnes ajoutées n'inventent rien | ✅ |
| Causalité de `compute_growth_rate` | 81 paliers ; premier taux `NaN` ; perturbation du **dernier** palier (→ 99 999 g) : écart max sur tous les paliers antérieurs = **0,0**, alors que le dernier taux passe de 0,103029 à 4 174,905 ; 3 taux négatifs conservés, non corrigés | ✅ |
| Filtre de `add_threshold_distance` | Colonnes produites : `temperature_`, `dissolved_oxygen_`, `ph_distance_critical` — **et elles seules** ; un dict forçant des seuils numériques sur `ammonia`/`nitrate`/`turbidity` ne produit **aucune** colonne supplémentaire. Les 24 valeurs aux cas limites sont **identiques à celles recalculées à la main en itération 1** (température `[-0.1, 0.0, 0.1, 7.5, 0.1, 0.0, -0.1, NaN]`, pH `[-0.1, 0.0, 0.5, 1.5, 0.5, 0.0, -0.1, NaN]`, DO `[-0.1, 0.0, 0.1, 1.0, 11.9, 12.0, 37.0, NaN]`) | ✅ |
| Schéma du livrable | 83 126 lignes × **23 colonnes**, inchangé (le correctif D1 ne touche que `src/features.py`, en aval du CSV nettoyé) | ✅ |

**Aucune régression.** Les 16 colonnes ajoutées à l'agrégat horaire n'ont cassé aucun contrôle de l'itération 1.

---

## 9. Tests et non-trivialité (mutations)

**Suite complète.** `venv/Scripts/python.exe -m pytest -q` → **99 réussis, 27 ignorés, 0 échec** (6,66 s), 126 tests collectés. Progression **89 → 99** : les **10 tests annoncés existent réellement** (9 dans `tests/test_features.py`, 1 dans `tests/test_config.py`).

**Aucun test affaibli.** `git diff b8087c3..HEAD -- tests/` ne contient **aucune suppression** de `def test_` ni d'`assert`, hors les 2 renommages. Les deux renommages `…undecided_turbidity` → `…turbidity_indicator` sont **cosmétiques** : seules la ligne `def` et la docstring changent, le corps et les assertions sont identiques au caractère près. Aucun `@pytest.mark.skip` ni `xfail` n'a été ajouté (les 2 occurrences de « skip » dans `tests/test_features.py` sont `pytest.importorskip("pandas")` et un **nom** de test). Aucun `skip` sur le Jalon 2 ; les 27 ignorés restent rattachés aux Jalons 3 à 6 avec motif explicite.

**Mutations sur les propriétés nouvelles.** Copie de `src/`, `tests/`, `dashboard/` et `pytest.ini` hors du dépôt, baseline vérifiée à **99 réussis**, puis mutation d'une seule ligne à la fois :

| # | Mutation injectée dans `src/features.py` | Détectée par |
|---|---|---|
| M1 | `center=True` sur la **seule** colonne `_raw` (fuite future ciblée sur le brut) | ✅ `test_add_rolling_features_raw_column_is_also_causal` |
| M2 | Glissante brute calculée sur la colonne **nettoyée** (contamination) | ✅ `…raw_and_cleaned_columns_do_not_contaminate_each_other` + `…also_rolls_raw_value_column_when_present` |
| M3 | `n_out_of_bounds` compté sur la colonne **nettoyée** | ✅ `…propagates_raw_mean_and_out_of_bounds_counter` + `…episode1_do_plateau_visible_in_raw_hourly_aggregates` |
| M4 | `gap_mean` : `NaN` remplacé par `0` (valeur inventée) | ✅ `…gap_mean_is_nan_when_cleaned_column_fully_missing` |
| M5 | `<label>_raw_mean` calculé sur la colonne **nettoyée** | ✅ 4 tests |
| M8 | `gap_mean` : signe inversé (nettoyé − brut) | ✅ `…gap_mean_is_computed_when_both_means_present` |
| M6 | `raw_n_present = n_readings` (valeurs brutes `NaN` comptées comme présentes) | ❌ **non détectée** |
| M7 | `raw_series > upper` → `>= upper` (**cas limite : valeur exactement égale à la borne**) | ❌ **non détectée** |
| M7b | `raw_series < lower` → `<= lower` (cas limite, borne basse) | ❌ **non détectée** |
| M9 | Suffixe `"_raw"` **en dur** au lieu de `config.RAW_VALUE_SUFFIX` dans `resample_hourly` | ❌ **non détectée** |
| M10 | Suffixe `"_raw"` **en dur** dans `add_rolling_features` | ❌ **non détectée** |
| M11 | Compteur hors borne comptant aussi les `NaN` bruts | ❌ **non détectée** |

**6 mutations sur 12 survivent** → défaut **D10**. Les 6 propriétés effectivement protégées sont les plus structurantes (causalité, non-contamination, brut ≠ nettoyé, pas de valeur inventée), mais les cas limites et la provenance du suffixe ne le sont pas. Note : `src/features.py` a été **restauré à l'identique** après chaque mutation (vérifié par comparaison de contenu).

---

## 10. Reproductibilité — méthode révisée, et une contradiction

### 10.1 Chiffres et sorties textuelles : **reproductibles** ✅

Ré-exécution complète d'une **copie hors dépôt** du notebook (`jupyter nbconvert --to notebook --execute`, `PROJECT_ROOT` et `FIGURES_DIR` redirigés) dans `venv/` : **code de sortie 0**, 33 cellules, **0 erreur**, 8 figures écrites, `git status` inchangé. Comparaison des sorties avec le notebook de HEAD : **24 sorties textuelles comparées, 23 identiques**. L'unique différence est la ligne `Répertoire des figures : …`, conséquence directe de ma propre redirection — donc **0 différence réelle**. Les chiffres du Jalon 2 sont reproductibles.

`ingestion.clean_data` : livrable régénéré de forme identique au CSV sur disque (83 126 × 23) ; `n_out_of_bounds` horaires cumulés = totaux du rapport de nettoyage ; `THRESHOLDS` de `src/config.py` **strictement égal** au bloc de `docs/03` L73-80 (comparaison structurelle, pas textuelle).

### 10.2 Figures PNG : **non reproductibles bit à bit — et le diagnostic de J-20260919-006 est contredit** ❌

Le brief m'invitait à ne plus fonder le contrôle sur le SHA-256 des PNG, la ré-exécution de 01:59 ayant été attribuée à « un environnement autre que `venv/` ». **Mesure faite :**

| Figure | HEAD (commitée) | stash 01:59 | Ma ré-exécution dans `venv/` |
|---|---|---|---|
| `jalon2_anomalie_episode1_do_plateau.png` | 1089×390 · `a1d6823c…` | 1090×390 · `41a12ba5…` | 1090×390 · `41a12ba5…` |
| `jalon2_anomalie_episode2a_do_crise.png` | 1087×390 · `1d04e081…` | 1087×390 · `d54fc549…` | 1087×390 · `d54fc549…` |
| `jalon2_anomalie_episode2b_ph_crise.png` | 1088×390 · `652db143…` | 1087×390 · `f803bda1…` | 1087×390 · `f803bda1…` |
| `jalon2_couverture_temporelle_journaliere.png` | 1189×340 · `15d86762…` | 1190×340 · `7e7588d7…` | 1190×340 · `7e7588d7…` |
| `jalon2_demo_rolling_features.png` | 1089×389 · `7a0fcc17…` | 1090×390 · `95dd99c9…` | 1090×390 · `95dd99c9…` |
| `jalon2_demo_rolling_features_raw_episode1.png` | 1089×390 · `0a70be61…` | 1090×390 · `e681d08b…` | 1090×390 · `e681d08b…` |
| `jalon2_distributions_avant_apres.png` | 1089×1286 · `081326ff…` | 1090×1286 · `a608ccbc…` | 1090×1286 · `a608ccbc…` |
| `jalon2_turbidite_distribution.png` | 790×340 · `a67cc868…` | 790×340 · `b1c438ec…` | 790×340 · `b1c438ec…` |

- Ma ré-exécution **dans le venv du projet** est **bit à bit identique au stash de 01:59 : 8/8**.
- Elle diffère des figures **commitées à HEAD : 0/8**.

Donc la ré-exécution de 01:59 n'a **pas** été produite dans un autre environnement : elle est exactement ce que produit l'environnement documenté. **Ce sont les figures commitées à HEAD qui ne sont pas régénérables.** J-20260919-006 conclut l'inverse, et le `git stash` a par conséquent mis de côté les artefacts **les plus** reproductibles pour conserver les moins reproductibles. → défaut **D12**.

**Ampleur réelle de l'écart** (et non « ±1 pixel ») : sur les figures de dimensions égales, **5,1 % à 9,0 % des pixels** diffèrent (`jalon2_anomalie_episode2a` 38 140/423 930 = 9,00 % ; `jalon2_turbidite_distribution` 13 613/268 600 = 5,07 % ; `jalon2_distributions_avant_apres`, zone commune, 7,15 %). Il s'agit d'un **décalage sous-pixel global du texte et des traits** (anti-crénelage), pas d'un changement de contenu : les 24 sorties textuelles sont identiques et toutes les valeurs tracées ont été recalculées comme exactes.

**Cause racine identifiée** : le notebook enregistre avec `bbox_inches="tight"`, dont la boîte englobante dépend des **métriques de police** du moteur de rendu ; seul `plt.rcParams["figure.dpi"] = 100` est fixé, ni police ni backend ne le sont, et `requirements.txt` ne borne pas matplotlib (`matplotlib>=3.7`, version installée 3.11.2).

**Limite de méthode à retenir pour le mémoire** (et conséquence sur l'itération 1) : *l'égalité SHA-256 d'un PNG n'est pas un critère de reproductibilité valide.* Le contrôle n°2 de l'itération 1 (« les 7 PNG régénérés sont bit à bit identiques ») **n'est plus vrai aujourd'hui** et ne devait pas être présenté comme une preuve de reproductibilité : il ne prouvait qu'une constance de rendu locale et transitoire. La preuve valide est celle du §10.1 : **sorties textuelles et chiffres identiques**. Point d'attention direct pour le **Jalon 6**, dont le critère « deux exécutions → sorties identiques (empreintes) » échouera si des images entrent dans le périmètre des empreintes.

---

## 11. Contrôles transverses

**Traçabilité.** `audit_trace.py --date 2026-09-19` → **✅ CONFORME** : journal présent (7 entrées), 110 actions automatiques, **0 fichier modifié non cité**, **0 entrée mal formée**. `--date 2026-09-18` → **✅ CONFORME** (0 fichier non cité, 0 entrée mal formée). Le trou du journal automatique entre 00:27:11 et 07:34:58 est expliqué par J-20260919-006 ; j'ai vérifié que l'explication **couvre exactement** les fichiers concernés : `git stash show --stat stash@{0}` liste `notebooks/01_exploration.ipynb` + les **8** PNG `jalon2_*`, ni plus ni moins. J'ai aussi vérifié par le calcul l'affirmation factuelle de cette entrée : 33 cellules, **0 source différente**, **24 sorties textuelles identiques**, `execution_count` identiques, 0 erreur, 8 images inline différentes — exact. Seule sa **conclusion** est erronée (D12). Deux refus d'outil sont enregistrés le 2026-09-19, dont le mien à 07:39 (`Write` hors périmètre vers le répertoire de travail) — journalisé en J-20260919-009.

**Valeurs en dur.** Recherche de littéraux (bornes 15/100/6.5/8.5/0.05, fréquence `"1h"`, suffixe `"_raw"`) dans `src/` et `dashboard/` hors `src/config.py` : **7 occurrences, toutes dans des docstrings** (`src/features.py` L14, 17, 31, 147, 260, 300 ; `src/ingestion.py` L192) — aucune dans du code exécuté. Le suffixe `_raw` est lu depuis `config.RAW_VALUE_SUFFIX` aux 3 emplacements du nouveau code, et les bornes depuis `config.SENSOR_TYPES[...]["bounds"]`. ✅ — mais cette conformité **n'est protégée par aucun test** côté `features.py` (mutations M9/M10, défaut D10), alors qu'elle l'est côté `ingestion.py`.

**Cohérence code ↔ docs ↔ ADR.** `config.THRESHOLDS` == bloc `docs/03` : **True**. `docs/03` L79 et L144 alignés sur le code (D3, D4 levés). `docs/11` L43 : « Plus aucune décision en attente pour les Jalons 1 et 2 » est désormais **justifié** (ADR-011 cité pour la turbidité et le pH). Totaux hors bornes du rapport de nettoyage == totaux des compteurs horaires. ⚠️ Un seul écart subsiste : les chiffres de l'épisode 1 (D11).

**Périmètre (`cahier des charges` §3).** Les 17 fichiers touchés depuis `b8087c3` relèvent tous du Jalon 2 : `src/features.py`, `src/config.py`, `src/ingestion.py`, `tests/`, `notebooks/`, `reports/`, `docs/`, `logs/`, `.claude/rules/git-workflow.md`. Les colonnes ajoutées relèvent du **Module 2** de `docs/02` §3 (agrégation temporelle et features dérivées) ; aucun modèle, moteur de décision ni dashboard n'est anticipé. Aucune fonctionnalité hors cahier §3. ✅

**Git.** `git status --short` : `logs/agents/actions.jsonl` et `logs/agents/journal/2026-09-19.md` seuls modifiés, avant **et** après mon passage. `git log origin/main..HEAD` : **7 commits**, tous avec trailers `Agent`/`Jalon`/`Journal`/`Refs` et `Co-Authored-By`. Aucun fichier interdit (pas de `data/raw/`, `data/processed/`, `venv/`, `*.joblib`). `git stash list` : 1 entrée conservée (rien de supprimé — conforme à G4). ✅ sauf l'écart de forme résiduel de D9.

**Definition of Done `docs/02` §8, point 1.** Revérifiée sur le livrable régénéré : `Temperature` hors [0, 40] = **0** ; `PH` hors [0, 14] = **0** ; `DO` > 15 = **0** ; `Ammonia` > 5 = **0**. Les colonnes `_raw` contiennent bien, elles, des valeurs physiquement impossibles (`Temperature_raw` min **−127,0 °C**, `PH_raw` min **−0,586**) — c'est **l'objet même** de l'ADR-011, et elles sont explicitement nommées et comptées (`n_out_of_bounds`), jamais confondues avec les colonnes nettoyées. ✅

---

## 12. Défauts — état après itération 2

| # | Défaut | Preuve | Agent propriétaire | Bloquant ? |
|---|---|---|---|---|
| D1-D8 | — | voir §6 | — | **Levés** |
| D9 | Ligne de corps de **73 caractères** dans `194db31` (limite 72, `git-workflow.md` §3) | `git log -1 --format=%b 194db31 \| awk 'length>72'` | orchestrateur | Non — **partiellement levé** |
| **D10** | **6 mutations survivent aux 10 nouveaux tests.** Ne sont couverts : ni le **cas limite « valeur exactement égale à la borne »** de `n_out_of_bounds` (M7/M7b) — exigence explicite de `.claude/rules/conventions-code.md` (« Toute règle métier […] a au moins un test de cas limite : juste sous, égal, juste au-dessus ») —, ni le traitement des `NaN` bruts par le compteur (M6/M11), ni la lecture du suffixe depuis `config` (M9/M10, alors qu'un test équivalent existe pour `ingestion.py`) | §9, tableau des mutations ; baseline 99 réussis vérifiée avant chaque mutation | data-engineer | Non bloquant pour le Jalon 2 · **à traiter avant le Jalon 3** (ces compteurs alimentent directement le modèle) |
| **D11** | **Chiffres de l'épisode 1 non réconciliés entre documents.** `docs/11` L66 et l'ADR-011 citent « 368 valeurs nettoyées contre **13 422** en `_raw`, moyenne **36,47** mg/L » ; le commit `194db31` et le notebook citent « **13 447** valeurs […] moyenne de **36,16** mg/L ». Les deux sont exacts mais dans des cadrages différents (fenêtre fermée ligne à ligne vs couverture de 152 créneaux horaires ; moyenne pondérée vs moyenne des moyennes horaires). Un lecteur du mémoire verra deux chiffres contradictoires sans explication. Trois valeurs de moyenne coexistent en réalité : **36,4668** (pondérée, fenêtre fermée), **36,4071** (pondérée, couverture horaire), **36,1569** (moyenne des moyennes horaires) | §7, « Écart 13 422 vs 13 447 » — écart recalculé à exactement 25 relevés. Le notebook, lui, qualifie correctement sa valeur (« moyenne des moyennes horaires ») ; le commit `194db31` omet ce qualificatif | doc-keeper (ADR-011, `docs/11`) | Non bloquant · **à corriger avant usage mémoire** |
| **D12** | **Les 8 figures commitées ne sont pas régénérables par l'environnement documenté**, et le diagnostic de J-20260919-006 est contredit : ma ré-exécution dans `venv/` est bit à bit identique au stash de 01:59 (**8/8**) et diffère de HEAD (**0/8**). L'écart n'est pas « ±1 pixel » mais **5,1 % à 9,0 % des pixels** (décalage sous-pixel, contenu inchangé). Contrevient à `.claude/rules/conventions-code.md` § Reproductibilité. Invalide rétroactivement la méthode de preuve du critère 2 de l'itération 1 | §10.2, tableau des 8 empreintes et dimensions ; comparaison pixel par pixel | orchestrateur (entrée corrective **append-only** de J-20260919-006 ; sort du `stash`) · data-engineer (régénération des figures) | Non bloquant pour les critères du Jalon 2 · **à trancher avant la PR** ; **risque direct sur le critère « deux exécutions → sorties identiques » du Jalon 6** |

**Observations sans caractère de défaut** (aucune action exigée au Jalon 2) :

- **`gap_mean` est une différence de deux moyennes calculées sur des supports différents** (`raw_n_present` relevés pour la brute, `n_present` pour la nettoyée), pas une moyenne de différences. Sur les créneaux à imputation partielle, elle mélange donc un effet de valeur et un effet d'effectif. La docstring ne prétend pas le contraire, mais le Jalon 3 ne doit pas la lire comme un « biais moyen du nettoyage ».
- **Amplitude des nouvelles colonnes brutes** : `Ammonia_raw_mean` va de 0,099 à **2,577·10¹⁰** et `Ammonia_gap_mean` jusqu'à **2,577·10¹⁰** ; `Dissolved Oxygen_raw_mean` monte à 40,86 contre 14,22 pour la nettoyée. Ces colonnes couvrent une dizaine d'ordres de grandeur : au Jalon 3, tout redimensionnement non robuste (`StandardScaler`, `MinMaxScaler`) sera entièrement dominé par ces valeurs. À cadrer explicitement avec le `ml-engineer`. Aucune valeur infinie (0 `inf`).
- `Temperature_raw` contient **un** relevé à **−127,0 °C** (2021-08-30 07:02:26, imputé à 24,5 — seule imputation de température du fichier) : c'est lui qui produit `Temperature_gap_mean = −7,575` sur son créneau et `n_out_of_bounds = 1`. Cohérent, vérifié, pas un défaut.
- La table `UNIT_DISPLAY` (D7) est définie **dans le notebook**. Acceptable en exploration, mais le dashboard du Jalon 5 aura besoin de la même correspondance : à déplacer dans `src/config.py` à ce moment-là, sans quoi l'étiquetage mg/L sera dupliqué.
- Rappel de l'itération 1, toujours valable : dates des deux épisodes en dur dans le notebook ; `add_rolling_features` dépend de l'ordre des lignes à horodatage strictement égal (0 cas sur 83 126).

---

## 13. Verdict proposé pour le Jalon 2 — itération 2

**VALIDÉ AVEC RÉSERVES.**

Les **trois critères de `docs/04`** restent satisfaits (voir §1, revérifiés : distributions et seuils applicables inchangés, figures d'épisode inchangées et valeurs tracées recalculées, 81 paliers et corrélations interprétées). Le seul défaut à portée technique de l'itération 1, **D1, est entièrement levé** et vérifié par recalcul indépendant, contre-exemples construits et recalcul manuel — non par lecture de code. **D2 à D8 sont levés.** Aucune régression.

Réserves, avec agent propriétaire et échéance :

| Réserve | Agent propriétaire | Échéance proposée |
|---|---|---|
| **D10** — cas limites et provenance du suffixe non testés (6 mutations survivantes) | data-engineer | **avant l'ouverture du Jalon 3** |
| **D12** — figures commitées non régénérables ; J-20260919-006 à corriger en append-only | orchestrateur, puis data-engineer | **avant la PR du Jalon 2** |
| **D11** — chiffres de l'épisode 1 à réconcilier (13 422/36,47 vs 13 447/36,16) | doc-keeper | avant usage mémoire |
| **D9** — ligne de corps à 73 caractères | orchestrateur | sans objet (historique poussé — par nouveau commit uniquement) |

Le critère 2 reste ✅, mais **sa preuve change de nature** : elle repose désormais sur l'identité des sorties textuelles et le recalcul des valeurs tracées, plus sur l'égalité SHA-256 des PNG (§10.2).

### Ce qui resterait à faire avant le Jalon 3

1. **D10** — ajouter les tests de cas limite sur `n_out_of_bounds` (valeur juste sous / égale / juste au-dessus de `bounds["min"]` et `bounds["max"]`), un test de `raw_n_present` en présence de `NaN` bruts, et deux tests de provenance du suffixe depuis `config.RAW_VALUE_SUFFIX` dans `features.py` (symétriques de celui qui existe pour `ingestion.py`).
2. **D12** — décider du sort du `stash@{0}` et de la régénération des figures, puis corriger J-20260919-006 par une entrée append-only. Fixer, pour le Jalon 6, ce qui entre dans le périmètre des empreintes de reproductibilité (les images ne peuvent pas en faire partie en l'état).
3. **D11** — réconcilier les chiffres de l'épisode 1 dans l'ADR-011 et `docs/11`, en nommant la fenêtre et le mode de moyenne.
4. **Cadrage ml-engineer (G1 ou brief)** — le Jalon 3 doit choisir explicitement, par variable, entre `<label>_mean` (nettoyée), `<label>_raw_mean`, `<label>_n_out_of_bounds` et `<label>_gap_mean`, et traiter l'amplitude extrême des colonnes brutes d'ammoniac. L'ADR-011 exige ce choix explicite ; il n'est pas encore fait.

---

## 14. Points à trancher par l'humain

1. **(G2)** Fusion de la pull request du Jalon 2 et passage au Jalon 3, au vu du présent verdict et du traitement retenu pour les réserves D9 à D12.
2. **(G4 / reproductibilité — défaut D12)** Que fait-on des 8 figures commitées, qui ne sont pas celles que produit l'environnement documenté ? Deux options, **le validateur ne tranche pas** : (a) régénérer et commiter les figures issues de `venv/` (le contenu scientifique est identique, seul le rendu change), en corrigeant J-20260919-006 par une entrée append-only ; (b) conserver les figures actuelles et documenter explicitement, dans le mémoire et dans `docs/`, que le rendu des images n'est pas reproductible bit à bit. Dans les deux cas, le `stash@{0}` ne doit pas être supprimé sans décision explicite (G4).
3. **(G3 / périmètre du Jalon 6)** Le critère « pipeline complet, deux exécutions → sorties identiques (empreintes) » doit-il exclure les images de son périmètre, ou faut-il fixer les versions de rendu (épingler `matplotlib` dans `requirements.txt`, fixer police et backend, renoncer à `bbox_inches="tight"`) ? À décider avant le Jalon 6, pas pendant.

---

*Rapport d'itération 2 produit par le `qa-validator` — aucune correction apportée au code, au notebook ni à `docs/` ; aucun fichier suivi par git modifié (`git status --short` identique avant et après). Notebook ré-exécuté sur copie hors dépôt, mutations appliquées sur copie hors dépôt et source restaurée à l'identique. Entrées de journal : J-20260919-008 (validation), J-20260919-009 (refus d'outil).*
