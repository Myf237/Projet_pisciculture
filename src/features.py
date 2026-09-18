"""Module 2 — Exploration et feature engineering (docs/02 §3, docs/03 `src/features.py`).

Rôle : enrichir les données nettoyées (sortie de `src/ingestion.py`) de
features dérivées causales (fenêtres glissantes tournées vers le passé,
écarts aux seuils, taux de croissance) et produire une agrégation horaire
pour réduire le bruit avant modélisation.

Jalon de rattachement : Jalon 2 — Exploration validée (docs/04).
Propriétaire : data-engineer (`.claude/agents/data-engineer.md`).

Toutes les fenêtres et seuils utilisés ici viennent de `src/config.py`
(`ROLLING_WINDOW_DEFAULT`, `THRESHOLDS`, `RESAMPLING_FREQUENCY`) — aucune
valeur en dur. `RESAMPLING_FREQUENCY` est désormais tranchée et appliquée
(ADR-010, "1h") : voir `resample_hourly`.

Point de vigilance (R16, `docs/08-REGISTRE_RISQUES.md`) : après nettoyage,
28,00 % de l'ammoniac et 15,93 % de l'oxygène dissous sont manquants, et
11,98 % / 7,25 % des valeurs présentes de DO / ammoniac sont interpolées, pas
mesurées (`<label>_imputed`). Aucune fonction de ce module ne doit faire
passer une valeur interpolée pour une mesure : `resample_hourly` propage donc
des compteurs de valeurs réellement mesurées, imputées et manquantes par
créneau, en plus de la moyenne agrégée.
"""

from __future__ import annotations

import pandas as pd

from src import config


def add_rolling_features(df: pd.DataFrame, window: str = config.ROLLING_WINDOW_DEFAULT) -> pd.DataFrame:
    """Ajoute moyennes/écarts-types glissants par variable de qualité d'eau.

    Entrée : DataFrame nettoyé (sortie de `ingestion.clean_data`, colonnes
    brutes de `config.SENSOR_TYPES` attendues, pas nécessairement triées) ;
    `window`, fenêtre temporelle (par défaut `config.ROLLING_WINDOW_DEFAULT`),
    chaîne compatible `pandas.Timedelta`.
    Sortie : copie du DataFrame d'entrée (trié chronologiquement), enrichie
    pour chaque colonne de `config.SENSOR_TYPES` présente d'une colonne
    `<label>_rolling_mean` et `<label>_rolling_std` (`label` =
    `config.SENSOR_TYPES[...]["label"]`, même convention que
    `<label>_imputed`/`<label>_missing` de `src/ingestion.py`).

    Règles à respecter : fenêtre **causale uniquement** (tournée vers le
    passé, jamais `center=True`) — implémentée via un `rolling` temporel
    indexé sur `config.TIMESTAMP_COLUMN`, dont la convention pandas par
    défaut (`closed="right"`) inclut la valeur au temps t et les valeurs des
    `window` précédentes, jamais une valeur future : aucune information
    future n'entre dans la valeur au temps t (règle data-engineer n°8), ce
    qui reste valide en rejeu temps réel. Implémentation vectorisée
    (`Series.rolling`), pas de boucle ligne à ligne sur les ~83 000 relevés
    (règle data-engineer n°9). Les valeurs manquantes (`NaN`, y compris
    celles marquées `<label>_missing`) sont ignorées dans le calcul de la
    moyenne/écart-type de leur fenêtre (comportement par défaut de
    `Series.rolling`, cohérent avec l'absence de valeur inventée) ; les
    colonnes `<label>_imputed`/`<label>_missing` déjà présentes en entrée
    sont conservées telles quelles dans la sortie, sans être elles-mêmes
    lissées.
    """
    ts_col = config.TIMESTAMP_COLUMN
    if ts_col not in df.columns:
        raise ValueError(f"Colonne d'horodatage '{ts_col}' absente du DataFrame passé à add_rolling_features.")

    working = df.sort_values(ts_col, kind="mergesort").reset_index(drop=True).copy()
    indexed = working.set_index(ts_col)

    for raw_col, meta in config.SENSOR_TYPES.items():
        if raw_col not in indexed.columns:
            continue
        label = meta["label"]
        # `closed` non précisé = défaut pandas "right" pour un rolling temporel :
        # intervalle (t - window, t], jamais center=True (règle n°8).
        rolling = indexed[raw_col].rolling(window, min_periods=1)
        working[f"{label}_rolling_mean"] = rolling.mean().to_numpy()
        working[f"{label}_rolling_std"] = rolling.std().to_numpy()

    return working


def add_threshold_distance(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Ajoute une variable d'écart signé au seuil critique, par paramètre.

    Entrée : DataFrame nettoyé, dont les colonnes de qualité d'eau portent le
    nom des clés de `thresholds` (ex. `temperature`, `ph` — la correspondance
    avec les noms bruts de `config.RAW_COLUMNS` est assurée en amont, ce
    n'est pas la responsabilité de cette fonction) ; `thresholds`, dict de
    seuils (typiquement `config.THRESHOLDS`).
    Sortie : DataFrame enrichi d'une colonne `<clé>_distance_critical` par
    paramètre dont le seuil critique est exploitable (voir ci-dessous).

    Convention de signe, d'unité et de nommage (lève l'ambiguïté de la
    réserve R6, `reports/validations/preparation-mise-en-place.md`) :
    - **Unité** : identique à la colonne d'entrée, sans conversion — la
      distance est une simple différence entre deux valeurs de même unité,
      jamais un pourcentage ni une valeur normalisée.
    - **Signe** : **positif** = marge de sécurité restante avant d'atteindre
      le seuil critique (valeur encore dans la zone critique/acceptable) ;
      **négatif** = seuil critique déjà dépassé, la valeur absolue donnant
      l'ampleur du dépassement (valeur hors de la zone critique) ; **zéro** =
      valeur exactement égale au seuil critique.
    - **Paramètre à borne critique unique inférieure** (seul `critical_min`
      défini, ex. `dissolved_oxygen`) : `distance = valeur - critical_min`.
    - **Paramètre à borne critique unique supérieure** (seul `critical_max`
      défini) : `distance = critical_max - valeur`. Aucun paramètre
      actuellement applicable n'est dans ce cas (voir ci-dessous) ; la
      formule reste documentée pour un futur paramètre immergé de ce type.
    - **Paramètre à double borne critique** (`critical_min` et
      `critical_max` définis, ex. `temperature`, `ph`) : distance signée à la
      borne critique la plus proche — si `critical_min <= valeur <=
      critical_max`, `distance = min(valeur - critical_min, critical_max -
      valeur)` (>= 0) ; si `valeur < critical_min`, `distance = valeur -
      critical_min` (< 0) ; si `valeur > critical_max`, `distance =
      critical_max - valeur` (< 0).
    - **Seuil non exploitable → colonne non produite** (pas de valeur
      devinée). Reformulé le 2026-09-18 (D3, `reports/validations/jalon-1.md`) :
      ce n'était plus exact de fonder l'exclusion de `dissolved_oxygen` sur
      une unité non tranchée — l'ADR-009/010 a tranché l'unité (mg/L) *et*
      la borne (`config.DISSOLVED_OXYGEN_BOUNDS = {"max": 15}`) : ce
      paramètre est désormais **inclus**, pas exclu. La règle réelle,
      indépendante de tout indicateur `None` : `<clé>_distance_critical`
      n'est calculée que pour les clés présentes dans
      `config.get_applicable_thresholds()` (sondes immergées à seuils
      aquacoles applicables — température, pH, oxygène dissous). Sont donc
      exclus : `turbidity` (`critical_min`/`critical_max` valent tous deux
      `None`, seuil encore à définir — Jalon 2, docs/11) et `ammonia` /
      `nitrate`, non plus pour une question d'unité mais parce que ce sont
      des capteurs de gaz suspendus au-dessus de l'eau, pas des sondes
      immergées (ADR-009) — `THRESHOLDS["ammonia"]`/`["nitrate"]` contiennent
      des valeurs numériques héritées du cahier §5 qui ne doivent jamais être
      lues comme des seuils absolus (règle data-engineer n°3). Ce filtre est
      appliqué à `thresholds` (le dict passé en paramètre), pas seulement à
      `config.THRESHOLDS` : même un `thresholds` custom contenant `ammonia`
      ou `nitrate` ne produit jamais de colonne pour ces clés.
    - **Nommage** : `<clé>_distance_critical`, où `<clé>` est la clé du
      paramètre dans `thresholds` (ex. `temperature_distance_critical`,
      `ph_distance_critical`), jamais le nom de colonne brut.

    Règles à respecter : ne jamais appliquer un seuil absolu à un paramètre
    hors de `config.get_applicable_thresholds()` (règle data-engineer n°3) ;
    implémentation vectorisée (pandas/numpy), pas de boucle ligne à ligne
    (règle data-engineer n°9).
    """
    applicable_keys = set(config.get_applicable_thresholds().keys())
    working = df.copy()

    for key, bounds in thresholds.items():
        if key not in applicable_keys or key not in working.columns:
            continue

        critical_min = bounds.get("critical_min")
        critical_max = bounds.get("critical_max")
        if critical_min is None and critical_max is None:
            continue

        value = working[key]
        if critical_min is not None and critical_max is not None:
            # Distance à la borne critique la plus proche, signée (formule
            # centrale) puis corrigée sur les deux queues (hors zone). Les
            # deux membres du `min` valent NaN simultanément quand `value`
            # est NaN (propagation arithmétique), donc `skipna=True` (défaut
            # de `DataFrame.min`) ne masque jamais un NaN par une valeur
            # réelle ici — pas de valeur inventée pour une entrée manquante.
            margins = pd.concat([value - critical_min, critical_max - value], axis=1)
            distance = margins.min(axis=1)
            distance = distance.mask(value < critical_min, value - critical_min)
            distance = distance.mask(value > critical_max, critical_max - value)
        elif critical_min is not None:
            distance = value - critical_min
        else:
            distance = critical_max - value

        working[f"{key}_distance_critical"] = distance

    return working


def compute_growth_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le taux de croissance instantané entre deux mesures de poids.

    Entrée : DataFrame issu de `ingestion.rebuild_growth_curve` (un point par
    changement réel de `Fish_Weight`/`Fish_Length`, colonnes brutes de
    `config.GROWTH_COLUMNS` + `config.TIMESTAMP_COLUMN`).
    Sortie : copie du DataFrame d'entrée (trié chronologiquement), enrichie
    pour chaque colonne de `config.GROWTH_COLUMNS` présente d'une colonne
    `<label>_growth_rate` = delta de la valeur / delta de temps (en heures)
    entre ce palier et le précédent (même unité que la colonne d'entrée, par
    heure — ex. g/h pour `Fish_Weight`, cm/h pour `Fish_Length`). `NaN` pour
    le premier palier (aucun point précédent, jamais extrapolé).

    Règles à respecter : causal (le taux au palier i ne dépend que des
    paliers i et i-1, jamais d'un palier futur) ; implémentation vectorisée
    (`Series.diff`), pas de boucle ligne à ligne (règle data-engineer n°9) ;
    toute non-monotonie héritée de la courbe de croissance (colonnes
    `<label>_non_monotonic` de `rebuild_growth_curve`, si présentes) se
    traduit simplement par un taux négatif, jamais corrigée ni masquée
    silencieusement (règle data-engineer n°7) — ces colonnes, si présentes en
    entrée, sont conservées telles quelles dans la sortie.
    """
    ts_col = config.TIMESTAMP_COLUMN
    if ts_col not in df.columns:
        raise ValueError(f"Colonne d'horodatage '{ts_col}' absente du DataFrame passé à compute_growth_rate.")

    growth_raw_columns = [c for c in config.GROWTH_COLUMNS if c in df.columns]
    if not growth_raw_columns:
        raise ValueError(
            f"Aucune colonne de croissance (config.GROWTH_COLUMNS={list(config.GROWTH_COLUMNS)!r}) "
            "trouvée dans le DataFrame passé à compute_growth_rate."
        )

    working = df.sort_values(ts_col, kind="mergesort").reset_index(drop=True).copy()
    delta_hours = working[ts_col].diff().dt.total_seconds() / 3600.0

    for raw_col in growth_raw_columns:
        label = config.GROWTH_COLUMNS[raw_col]
        delta_value = working[raw_col].diff()
        working[f"{label}_growth_rate"] = delta_value / delta_hours

    return working


def resample_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Agrège les données à la fréquence horaire pour réduire le bruit.

    Entrée : DataFrame nettoyé (sortie de `ingestion.clean_data`, colonnes
    brutes de `config.SENSOR_TYPES` et, quand applicable, `<label>_imputed`/
    `<label>_missing` — docs/03), indexable par `config.TIMESTAMP_COLUMN`.
    Sortie : DataFrame ré-échantillonné à la fréquence `config.RESAMPLING_
    FREQUENCY` (ADR-010, "1h"), une ligne par créneau horaire de l'étendue
    temporelle couverte par `df` (créneaux vides inclus, jamais omis). Pour
    chaque créneau :
    - `n_readings` : nombre total de relevés bruts tombés dans ce créneau
      (0 pour un créneau sans aucun relevé — pas de valeur inventée).
    - `<label>_mean` : moyenne du créneau (ignore les `NaN` ; `NaN` si aucune
      valeur présente dans le créneau — jamais de valeur fabriquée pour un
      créneau vide).
    - `<label>_n_measured` : nombre de valeurs **réellement mesurées** dans
      le créneau (présentes et non `<label>_imputed`) — pour les colonnes
      sans borne de nettoyage (Nitrate, Turbidity, ADR-009), toute valeur
      brute présente est une mesure réelle (aucune imputation possible).
    - `<label>_n_imputed` : nombre de valeurs comblées par interpolation
      dans le créneau (`<label>_imputed` = True).
    - `<label>_n_missing` : nombre de valeurs manquantes dans le créneau —
      pour les colonnes bornées, `<label>_missing` = True (hors bornes non
      comblé) ; pour les colonnes sans borne de nettoyage (Nitrate,
      Turbidity), `n_readings - n_present` (valeur brute `NaN` dans le CSV
      d'origine, aucune borne ni imputation ne s'y applique). Par
      construction, `n_measured + n_imputed + n_missing == n_readings` pour
      chaque créneau et chaque variable.
    Ces compteurs (R16, `docs/08-REGISTRE_RISQUES.md`) permettent au Jalon 3
    de ne jamais traiter `<label>_mean` comme une moyenne de mesures quand
    `<label>_n_measured` est nul ou faible pour ce créneau : la moyenne peut
    exister (valeurs imputées) sans qu'aucune mesure réelle n'existe.

    Règles à respecter : `config.RESAMPLING_FREQUENCY` (jamais une fréquence
    en dur) ; agrégation strictement intra-créneau — un créneau horaire
    n'agrège que ses propres relevés, jamais ceux d'un créneau voisin
    (causalité au sens de l'absence de fuite entre créneaux, règle
    data-engineer n°8) ; pas de valeur inventée pour un créneau vide (mean =
    NaN, compteurs = 0) ; vectorisé (`DataFrame.resample`), pas de boucle
    ligne à ligne sur les ~83 000 relevés (règle data-engineer n°9).
    """
    ts_col = config.TIMESTAMP_COLUMN
    if ts_col not in df.columns:
        raise ValueError(f"Colonne d'horodatage '{ts_col}' absente du DataFrame passé à resample_hourly.")

    freq = config.RESAMPLING_FREQUENCY
    if freq is None:
        raise ValueError(
            "config.RESAMPLING_FREQUENCY n'est pas tranchée (décision ouverte) — "
            "resample_hourly ne devine jamais une fréquence."
        )

    working = df.sort_values(ts_col, kind="mergesort").reset_index(drop=True)
    indexed = working.set_index(ts_col)
    resampler = indexed.resample(freq)

    n_readings = resampler.size()
    aggregated = pd.DataFrame(index=n_readings.index)
    aggregated.index.name = ts_col
    aggregated["n_readings"] = n_readings.astype("int64")

    for raw_col, meta in config.SENSOR_TYPES.items():
        if raw_col not in indexed.columns:
            continue
        label = meta["label"]

        aggregated[f"{label}_mean"] = resampler[raw_col].mean()

        imputed_col = f"{label}_imputed"
        missing_col = f"{label}_missing"
        n_present = resampler[raw_col].count()
        if imputed_col in indexed.columns and missing_col in indexed.columns:
            n_imputed = resampler[imputed_col].sum()
            n_missing = resampler[missing_col].sum()
            n_measured = n_present - n_imputed
        else:
            # Colonne sans borne de nettoyage (Nitrate, Turbidity — ADR-009 /
            # décision ouverte) : aucune imputation possible, toute valeur
            # présente est une mesure réelle ; une valeur brute manquante
            # (NaN dans le CSV d'origine) reste "manquante", jamais imputée.
            n_measured = n_present
            n_imputed = pd.Series(0, index=n_present.index)
            n_missing = n_readings - n_present

        aggregated[f"{label}_n_measured"] = n_measured.astype("int64")
        aggregated[f"{label}_n_imputed"] = n_imputed.astype("int64")
        aggregated[f"{label}_n_missing"] = n_missing.astype("int64")

    return aggregated.reset_index()
