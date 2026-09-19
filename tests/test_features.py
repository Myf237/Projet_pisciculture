"""Tests du module de features (`src/features.py`) — Module 2, Jalon 2.

Décisions appliquées et vérifiées ici : ADR-009/010 (`config.get_applicable_
thresholds()`, `config.RESAMPLING_FREQUENCY = "1h"`), règle data-engineer
n°8 (fenêtres causales, jamais `center=True`), règle n°7 (non-monotonie de
la croissance jamais corrigée), R16 (`docs/08-REGISTRE_RISQUES.md` —
distinction mesuré/imputé/manquant à propager dans les agrégats). Jeux de
données synthétiques uniquement (règle data-engineer n°12), cas limites
inclus (valeur égale au seuil critique, créneau horaire vide, trou plus
long que la fenêtre, valeurs 100 % imputées dans un créneau).
"""

from __future__ import annotations

import pytest

pytest.importorskip("pandas")

import pandas as pd

from src import config, features

# --- Aides de construction de jeux synthétiques -----------------------------


def _rolling_input(rows: list[dict]) -> pd.DataFrame:
    """DataFrame minimal pour add_rolling_features : created_at + colonnes de config.SENSOR_TYPES."""
    df = pd.DataFrame(rows)
    df[config.TIMESTAMP_COLUMN] = pd.to_datetime(df[config.TIMESTAMP_COLUMN])
    return df


def _growth_curve_input(rows: list[dict]) -> pd.DataFrame:
    """DataFrame minimal imitant la sortie de ingestion.rebuild_growth_curve."""
    df = pd.DataFrame(rows)
    df[config.TIMESTAMP_COLUMN] = pd.to_datetime(df[config.TIMESTAMP_COLUMN])
    return df


def _resample_input(rows: list[dict]) -> pd.DataFrame:
    """DataFrame minimal imitant la sortie de ingestion.clean_data (colonnes brutes + drapeaux)."""
    df = pd.DataFrame(rows)
    df[config.TIMESTAMP_COLUMN] = pd.to_datetime(df[config.TIMESTAMP_COLUMN])
    return df


# --- Contrat du module -------------------------------------------------------


def test_module_exposes_expected_callable_functions() -> None:
    """Le module expose les 4 fonctions de feature engineering, appelables et documentées."""
    for name in ("add_rolling_features", "add_threshold_distance", "compute_growth_rate", "resample_hourly"):
        func = getattr(features, name, None)
        assert callable(func), f"{name} doit être une fonction appelable"
        assert func.__doc__, f"{name} doit avoir une docstring (entrée -> sortie)"


# --- add_rolling_features : absence de fuite temporelle ---------------------


def test_add_rolling_features_uses_only_past_information() -> None:
    """Une valeur future n'entre jamais dans la feature glissante calculée à un temps passé (règle n°8)."""
    base_rows = [
        {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 24.0},
        {"created_at": "2021-06-19 00:20:00", "Temperature (C)": 25.0},
        {"created_at": "2021-06-19 00:40:00", "Temperature (C)": 26.0},
    ]
    df_past_only = _rolling_input(base_rows)
    df_with_future = _rolling_input(
        base_rows + [{"created_at": "2021-06-19 00:41:00", "Temperature (C)": 999.0}]
    )

    out_past_only = features.add_rolling_features(df_past_only, window="1h")
    out_with_future = features.add_rolling_features(df_with_future, window="1h")

    # Les 3 premières lignes (passées) sont strictement identiques, que la
    # ligne future extrême existe ou non — aucune information future ne fuite.
    pd.testing.assert_series_equal(
        out_past_only["Temperature_rolling_mean"],
        out_with_future["Temperature_rolling_mean"].iloc[:3],
        check_names=False,
    )
    pd.testing.assert_series_equal(
        out_past_only["Temperature_rolling_std"],
        out_with_future["Temperature_rolling_std"].iloc[:3],
        check_names=False,
    )
    # La ligne future, elle, est bien affectée par la nouvelle valeur extrême
    # (sinon le test serait trivial) : la moyenne du créneau [00:00-01:00]
    # englobant les 4 points est tirée vers le haut par 999.0.
    assert out_with_future.loc[3, "Temperature_rolling_mean"] > 100


def test_add_rolling_features_first_point_has_no_std_and_equals_its_own_value() -> None:
    """Le premier point d'une série n'a aucun voisin passé : moyenne = sa propre valeur, écart-type = NaN (pas de valeur inventée)."""
    df = _rolling_input([{"created_at": "2021-06-19 00:00:00", "Temperature (C)": 24.0}])
    out = features.add_rolling_features(df, window="1h")
    assert out.loc[0, "Temperature_rolling_mean"] == 24.0
    assert pd.isna(out.loc[0, "Temperature_rolling_std"])


def test_add_rolling_features_excludes_points_beyond_window() -> None:
    """Un point situé au-delà de la fenêtre glissante n'entre pas dans la moyenne courante (fenêtre causale bornée, pas un cumul infini)."""
    df = _rolling_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 0.0},
            {"created_at": "2021-06-19 02:00:00", "Temperature (C)": 10.0},  # 2h plus tard : hors fenêtre 1h
        ]
    )
    out = features.add_rolling_features(df, window="1h")
    # Le 2e point est seul dans sa fenêtre d'1h (le 1er point est trop ancien) :
    # moyenne = sa propre valeur, pas la moyenne des deux points.
    assert out.loc[1, "Temperature_rolling_mean"] == 10.0


def test_add_rolling_features_produces_columns_for_all_sensor_variables() -> None:
    """add_rolling_features couvre toutes les variables de qualité d'eau de config.SENSOR_TYPES, pas seulement la température."""
    df = _rolling_input(
        [
            {
                "created_at": "2021-06-19 00:00:00",
                "Temperature (C)": 24.0,
                "PH": 7.2,
                "Dissolved Oxygen(g/ml)": 5.0,
                "Ammonia(g/ml)": 0.4,
                "Nitrate(g/ml)": 150,
                "Turbidity(NTU)": 50,
            }
        ]
    )
    out = features.add_rolling_features(df, window="1h")
    for meta in config.SENSOR_TYPES.values():
        assert f"{meta['label']}_rolling_mean" in out.columns
        assert f"{meta['label']}_rolling_std" in out.columns


def test_add_rolling_features_default_window_is_config_value() -> None:
    """Le paramètre par défaut de window est bien config.ROLLING_WINDOW_DEFAULT (docs/03), pas une valeur en dur."""
    import inspect

    sig = inspect.signature(features.add_rolling_features)
    assert sig.parameters["window"].default == config.ROLLING_WINDOW_DEFAULT


# --- add_rolling_features : propagation du signal brut (ADR-011, G1 --------
# --- du 2026-09-19, J-20260919-002, défaut D1 reports/validations/jalon-2.md)


def test_add_rolling_features_also_rolls_raw_value_column_when_present() -> None:
    """<label>_raw produit aussi <label>_raw_rolling_mean/_rolling_std (le signal brut ne s'arrête pas au nettoyage, D1)."""
    df = _rolling_input(
        [
            {"created_at": "2021-07-30 02:00:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 38.6},
            {"created_at": "2021-07-30 02:20:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 39.1},
        ]
    )
    out = features.add_rolling_features(df, window="1h")

    assert "Dissolved Oxygen_raw_rolling_mean" in out.columns
    assert "Dissolved Oxygen_raw_rolling_std" in out.columns
    assert out.loc[1, "Dissolved Oxygen_raw_rolling_mean"] == pytest.approx((38.6 + 39.1) / 2)
    # La colonne nettoyée (entièrement NaN ici) donne une moyenne glissante NaN
    # elle aussi : pas de fuite depuis la colonne brute vers la colonne nettoyée.
    assert pd.isna(out.loc[1, "Dissolved Oxygen_rolling_mean"])


def test_add_rolling_features_raw_and_cleaned_columns_do_not_contaminate_each_other() -> None:
    """Les moyennes glissantes nettoyée et brute restent calculées indépendamment, même quand les deux colonnes divergent fortement."""
    df = _rolling_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Dissolved Oxygen(g/ml)": 5.0, "Dissolved Oxygen_raw": 38.6},
            {"created_at": "2021-06-19 00:20:00", "Dissolved Oxygen(g/ml)": 5.2, "Dissolved Oxygen_raw": 39.1},
        ]
    )
    out = features.add_rolling_features(df, window="1h")

    assert out.loc[1, "Dissolved Oxygen_rolling_mean"] == pytest.approx((5.0 + 5.2) / 2)
    assert out.loc[1, "Dissolved Oxygen_raw_rolling_mean"] == pytest.approx((38.6 + 39.1) / 2)


def test_add_rolling_features_raw_column_is_also_causal() -> None:
    """La colonne brute suit la même règle de causalité que la colonne nettoyée : aucune valeur future n'y entre."""
    base_rows = [
        {"created_at": "2021-07-30 02:00:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 38.6},
        {"created_at": "2021-07-30 02:20:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 39.1},
    ]
    out_past_only = features.add_rolling_features(_rolling_input(base_rows), window="1h")
    out_with_future = features.add_rolling_features(
        _rolling_input(base_rows + [{"created_at": "2021-07-30 02:21:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 999.0}]),
        window="1h",
    )
    pd.testing.assert_series_equal(
        out_past_only["Dissolved Oxygen_raw_rolling_mean"],
        out_with_future["Dissolved Oxygen_raw_rolling_mean"].iloc[:2],
        check_names=False,
    )


def test_add_rolling_features_raw_value_suffix_comes_from_config_not_hard_coded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le suffixe de colonne brute utilisé par add_rolling_features suit config.RAW_VALUE_SUFFIX,
    jamais un littéral "_raw" en dur (règle data-engineer n°2 ; même modèle que
    tests/test_ingestion.py::test_clean_data_raw_value_suffix_comes_from_config_not_hard_coded ;
    D10, reports/validations/jalon-2.md itération 2, mutation M10)."""
    monkeypatch.setattr(config, "RAW_VALUE_SUFFIX", "_original")
    df = _rolling_input(
        [
            {"created_at": "2021-07-30 02:00:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_original": 38.6},
            {"created_at": "2021-07-30 02:20:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_original": 39.1},
        ]
    )
    out = features.add_rolling_features(df, window="1h")

    assert "Dissolved Oxygen_original_rolling_mean" in out.columns
    assert "Dissolved Oxygen_original_rolling_std" in out.columns
    # Un suffixe "_raw" en dur chercherait "Dissolved Oxygen_raw", absent ici :
    # aucune colonne glissante brute ne doit apparaître sous ce nom.
    assert "Dissolved Oxygen_raw_rolling_mean" not in out.columns


# --- add_threshold_distance : convention de signe ---------------------------


def test_add_threshold_distance_double_bound_positive_inside_negative_outside() -> None:
    """Température (double borne critique) : positif dans la zone critique, négatif hors zone, 0 pile au seuil."""
    df = pd.DataFrame({"temperature": [15.0, 20.0, 27.5, 35.0, 40.0]})
    out = features.add_threshold_distance(df, config.THRESHOLDS)

    critical_min = config.THRESHOLDS["temperature"]["critical_min"]
    critical_max = config.THRESHOLDS["temperature"]["critical_max"]
    assert critical_min == 20 and critical_max == 35  # hypothèse du test, cohérente avec docs/03

    assert out.loc[0, "temperature_distance_critical"] == pytest.approx(15.0 - 20)  # < critical_min : négatif
    assert out.loc[1, "temperature_distance_critical"] == pytest.approx(0.0)        # == critical_min : pile au seuil
    assert out.loc[2, "temperature_distance_critical"] == pytest.approx(7.5)        # dans la zone : positif
    assert out.loc[3, "temperature_distance_critical"] == pytest.approx(0.0)        # == critical_max : pile au seuil
    assert out.loc[4, "temperature_distance_critical"] == pytest.approx(35 - 40)    # > critical_max : négatif


def test_add_threshold_distance_single_lower_bound_dissolved_oxygen() -> None:
    """DO (borne critique unique inférieure) : distance = valeur - critical_min, y compris exactement au seuil."""
    critical_min = config.THRESHOLDS["dissolved_oxygen"]["critical_min"]
    df = pd.DataFrame({"dissolved_oxygen": [critical_min - 1, critical_min, critical_min + 2]})
    out = features.add_threshold_distance(df, config.THRESHOLDS)

    assert out.loc[0, "dissolved_oxygen_distance_critical"] == pytest.approx(-1.0)
    assert out.loc[1, "dissolved_oxygen_distance_critical"] == pytest.approx(0.0)
    assert out.loc[2, "dissolved_oxygen_distance_critical"] == pytest.approx(2.0)


def test_add_threshold_distance_omits_gas_sensors_and_turbidity_indicator() -> None:
    """Ammonia/Nitrate (capteurs de gaz, ADR-009) et Turbidity (indicateur relatif, ADR-011 — décision durable, pas ouverte) n'ont jamais de colonne produite, même présents dans thresholds."""
    df = pd.DataFrame({
        "temperature": [27.0],
        "ph": [7.5],
        "dissolved_oxygen": [5.0],
        "ammonia": [0.2],
        "nitrate": [150],
        "turbidity": [50],
    })
    out = features.add_threshold_distance(df, config.THRESHOLDS)

    assert "temperature_distance_critical" in out.columns
    assert "ph_distance_critical" in out.columns
    assert "dissolved_oxygen_distance_critical" in out.columns
    assert "ammonia_distance_critical" not in out.columns
    assert "nitrate_distance_critical" not in out.columns
    assert "turbidity_distance_critical" not in out.columns


def test_add_threshold_distance_missing_value_stays_missing_not_guessed() -> None:
    """Une valeur NaN en entrée donne une distance NaN, jamais une valeur inventée."""
    df = pd.DataFrame({"temperature": [27.0, None]})
    out = features.add_threshold_distance(df, config.THRESHOLDS)
    assert pd.isna(out.loc[1, "temperature_distance_critical"])


def test_add_threshold_distance_column_not_present_is_silently_skipped() -> None:
    """Si la colonne correspondante n'est pas dans df, aucune colonne n'est produite pour cette clé (pas d'erreur, pas de valeur devinée)."""
    df = pd.DataFrame({"ph": [7.5]})  # pas de colonne "temperature" ni "dissolved_oxygen"
    out = features.add_threshold_distance(df, config.THRESHOLDS)
    assert "ph_distance_critical" in out.columns
    assert "temperature_distance_critical" not in out.columns
    assert "dissolved_oxygen_distance_critical" not in out.columns


# --- compute_growth_rate -----------------------------------------------------


def test_compute_growth_rate_between_consecutive_weight_measurements() -> None:
    """Taux = delta_poids / delta_temps (en heures) entre deux paliers consécutifs de la courbe reconstruite."""
    df = _growth_curve_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-20 00:00:00", "Fish_Weight(g)": 3.85, "Fish_Length(cm)": 18.08},  # +24h
        ]
    )
    out = features.compute_growth_rate(df)

    assert pd.isna(out.loc[0, "Fish_Weight_growth_rate"])  # premier palier : rien avant, jamais extrapolé
    expected_rate = (3.85 - 2.91) / 24.0
    assert out.loc[1, "Fish_Weight_growth_rate"] == pytest.approx(expected_rate)


def test_compute_growth_rate_preserves_non_monotonic_drop_as_negative_rate() -> None:
    """Une non-monotonie héritée de la courbe de croissance donne un taux négatif, jamais corrigée ni masquée (règle n°7)."""
    df = _growth_curve_input(
        [
            {"created_at": "2021-09-04 00:02:11", "Fish_Weight(g)": 300.0, "Fish_Length(cm)": 25.85, "Fish_Length_non_monotonic": False},
            {"created_at": "2021-09-05 00:07:20", "Fish_Weight(g)": 305.0, "Fish_Length(cm)": 12.09, "Fish_Length_non_monotonic": True},
        ]
    )
    out = features.compute_growth_rate(df)

    assert out.loc[1, "Fish_Length_growth_rate"] < 0
    # La colonne de signalement déjà présente en entrée est conservée telle quelle.
    assert out.loc[1, "Fish_Length_non_monotonic"] == True  # noqa: E712
    # La valeur brute n'est jamais corrigée par cette fonction.
    assert out.loc[1, "Fish_Length(cm)"] == 12.09


def test_compute_growth_rate_is_causal_not_affected_by_future_measurement() -> None:
    """Le taux au palier i ne dépend que des paliers i et i-1 : un 3e palier futur ne modifie pas le taux déjà calculé au 2e."""
    rows = [
        {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91},
        {"created_at": "2021-06-20 00:00:00", "Fish_Weight(g)": 3.85},
    ]
    out_two = features.compute_growth_rate(_growth_curve_input(rows))
    out_three = features.compute_growth_rate(
        _growth_curve_input(rows + [{"created_at": "2021-06-21 00:00:00", "Fish_Weight(g)": 400.0}])
    )
    assert out_two.loc[1, "Fish_Weight_growth_rate"] == pytest.approx(out_three.loc[1, "Fish_Weight_growth_rate"])


# --- resample_hourly ---------------------------------------------------------


def test_resample_hourly_aggregates_without_looking_ahead() -> None:
    """Un créneau horaire n'agrège que ses propres relevés : les valeurs d'un créneau voisin ne le contaminent jamais."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:10:00", "Temperature (C)": 10.0,
             "Temperature_imputed": False, "Temperature_missing": False},
            {"created_at": "2021-06-19 00:40:00", "Temperature (C)": 20.0,
             "Temperature_imputed": False, "Temperature_missing": False},
            {"created_at": "2021-06-19 01:10:00", "Temperature (C)": 1000.0,  # créneau suivant, valeur extrême
             "Temperature_imputed": False, "Temperature_missing": False},
        ]
    )
    out = features.resample_hourly(df)

    first_slot = out.loc[out["created_at"] == pd.Timestamp("2021-06-19 00:00:00")].iloc[0]
    assert first_slot["Temperature_mean"] == pytest.approx((10.0 + 20.0) / 2)
    assert first_slot["n_readings"] == 2


def test_resample_hourly_does_not_invent_values_for_empty_slots() -> None:
    """Un créneau horaire sans aucun relevé reste NaN/0, jamais une valeur fabriquée (ex. report du dernier point connu)."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:10:00", "Temperature (C)": 24.0,
             "Temperature_imputed": False, "Temperature_missing": False},
            # Trou : rien entre 00:10 et 02:10 -> le créneau 01:00-02:00 est vide.
            {"created_at": "2021-06-19 02:10:00", "Temperature (C)": 25.0,
             "Temperature_imputed": False, "Temperature_missing": False},
        ]
    )
    out = features.resample_hourly(df)

    empty_slot = out.loc[out["created_at"] == pd.Timestamp("2021-06-19 01:00:00")].iloc[0]
    assert empty_slot["n_readings"] == 0
    assert pd.isna(empty_slot["Temperature_mean"])
    assert empty_slot["Temperature_n_measured"] == 0
    assert empty_slot["Temperature_n_imputed"] == 0
    assert empty_slot["Temperature_n_missing"] == 0


def test_resample_hourly_distinguishes_measured_from_imputed_values() -> None:
    """R16 : un créneau où toutes les valeurs présentes sont interpolées a n_measured=0 malgré une moyenne non-NaN — pas de contamination silencieuse."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Dissolved Oxygen(g/ml)": 12.0,
             "Dissolved Oxygen_imputed": True, "Dissolved Oxygen_missing": False},
            {"created_at": "2021-06-19 00:35:00", "Dissolved Oxygen(g/ml)": 14.0,
             "Dissolved Oxygen_imputed": True, "Dissolved Oxygen_missing": False},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    # La moyenne existe (13.0) : si on ne consultait que Dissolved Oxygen_mean,
    # on croirait à une mesure réelle. Le compteur dédié révèle que non.
    assert slot["Dissolved Oxygen_mean"] == pytest.approx(13.0)
    assert slot["Dissolved Oxygen_n_measured"] == 0
    assert slot["Dissolved Oxygen_n_imputed"] == 2
    assert slot["Dissolved Oxygen_n_missing"] == 0


def test_resample_hourly_counts_are_consistent_with_total_readings() -> None:
    """Pour chaque variable et chaque créneau : n_measured + n_imputed + n_missing == n_readings (aucune valeur perdue ni double-comptée)."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Ammonia(g/ml)": 0.4,
             "Ammonia_imputed": False, "Ammonia_missing": False, "Nitrate(g/ml)": 120},
            {"created_at": "2021-06-19 00:20:00", "Ammonia(g/ml)": None,
             "Ammonia_imputed": False, "Ammonia_missing": True, "Nitrate(g/ml)": None},
            {"created_at": "2021-06-19 00:40:00", "Ammonia(g/ml)": 0.6,
             "Ammonia_imputed": True, "Ammonia_missing": False, "Nitrate(g/ml)": 130},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    for label in ("Ammonia", "Nitrate"):
        total = slot[f"{label}_n_measured"] + slot[f"{label}_n_imputed"] + slot[f"{label}_n_missing"]
        assert total == slot["n_readings"] == 3


def test_resample_hourly_uses_configured_frequency() -> None:
    """La fréquence appliquée est bien config.RESAMPLING_FREQUENCY (ADR-010), pas une valeur en dur dans le code."""
    assert config.RESAMPLING_FREQUENCY == "1h"
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 24.0,
             "Temperature_imputed": False, "Temperature_missing": False},
            {"created_at": "2021-06-19 03:00:00", "Temperature (C)": 25.0,
             "Temperature_imputed": False, "Temperature_missing": False},
        ]
    )
    out = features.resample_hourly(df)
    # 4 créneaux horaires couverts (00:00 à 03:00 inclus) : la fréquence horaire est bien appliquée.
    assert len(out) == 4


# --- resample_hourly : propagation du signal brut (ADR-011, G1 du 2026-09-19,
# --- J-20260919-002, défaut D1 reports/validations/jalon-2.md) --------------


def test_resample_hourly_propagates_raw_mean_and_out_of_bounds_counter() -> None:
    """<label>_raw_mean, <label>_raw_n_present et <label>_n_out_of_bounds sont produits à partir du seul signal brut."""
    df = _resample_input(
        [
            {"created_at": "2021-07-30 02:05:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 38.6,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
            {"created_at": "2021-07-30 02:35:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 39.1,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    assert slot["Dissolved Oxygen_raw_mean"] == pytest.approx((38.6 + 39.1) / 2)
    assert slot["Dissolved Oxygen_raw_n_present"] == 2
    # Les deux valeurs brutes dépassent DISSOLVED_OXYGEN_BOUNDS["max"] = 15 :
    # le compteur "hors borne" les voit, alors que la colonne nettoyée est
    # entièrement manquante (n_measured = 0) sur ce créneau.
    assert slot["Dissolved Oxygen_n_out_of_bounds"] == 2
    assert slot["Dissolved Oxygen_n_measured"] == 0
    assert pd.isna(slot["Dissolved Oxygen_mean"])


def test_resample_hourly_gap_mean_is_nan_when_cleaned_column_fully_missing() -> None:
    """<label>_gap_mean est NaN quand la colonne nettoyée n'a aucune valeur dans le créneau (pas de valeur inventée)."""
    df = _resample_input(
        [
            {"created_at": "2021-07-30 02:05:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 38.6,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
        ]
    )
    out = features.resample_hourly(df)
    assert pd.isna(out.iloc[0]["Dissolved Oxygen_gap_mean"])


def test_resample_hourly_gap_mean_is_computed_when_both_means_present() -> None:
    """<label>_gap_mean = moyenne brute - moyenne nettoyée quand les deux existent dans le créneau."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Dissolved Oxygen(g/ml)": 5.0, "Dissolved Oxygen_raw": 5.0,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},
            {"created_at": "2021-06-19 00:35:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": 38.6,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]
    expected_raw_mean = (5.0 + 38.6) / 2
    expected_clean_mean = 5.0
    assert slot["Dissolved Oxygen_gap_mean"] == pytest.approx(expected_raw_mean - expected_clean_mean)


def test_resample_hourly_raw_and_cleaned_aggregates_do_not_contaminate_each_other() -> None:
    """Non-contamination : <label>_mean ne reflète jamais le signal brut, <label>_raw_mean ne reflète jamais la colonne nettoyée."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Dissolved Oxygen(g/ml)": 5.0, "Dissolved Oxygen_raw": 38.6,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},
            {"created_at": "2021-06-19 00:35:00", "Dissolved Oxygen(g/ml)": 5.4, "Dissolved Oxygen_raw": 39.1,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    assert slot["Dissolved Oxygen_mean"] == pytest.approx((5.0 + 5.4) / 2)
    assert slot["Dissolved Oxygen_raw_mean"] == pytest.approx((38.6 + 39.1) / 2)
    # Les deux moyennes restent nettement distinctes : aucun mélange des deux séries.
    assert abs(slot["Dissolved Oxygen_mean"] - slot["Dissolved Oxygen_raw_mean"]) > 30


def test_resample_hourly_no_out_of_bounds_column_for_unbounded_variables() -> None:
    """Nitrate/Turbidity (sans borne, sans colonne _raw) n'ont pas de <label>_n_out_of_bounds — rien à compter."""
    df = _resample_input(
        [{"created_at": "2021-06-19 00:05:00", "Nitrate(g/ml)": 150, "Turbidity(NTU)": 60}]
    )
    out = features.resample_hourly(df)
    assert "Nitrate_n_out_of_bounds" not in out.columns
    assert "Turbidity_n_out_of_bounds" not in out.columns
    assert "Nitrate_raw_mean" not in out.columns


def test_resample_hourly_episode1_do_plateau_visible_in_raw_hourly_aggregates() -> None:
    """Vérification par le calcul (jeu synthétique représentatif de l'épisode 1) : le plateau DO 36-41 mg/L ressort
    dans les agrégats horaires issus du brut, alors que la colonne nettoyée y est quasi vide (défaut D1, jalon-2.md)."""
    rows = [
        {"created_at": "2021-07-29 23:00:00", "Dissolved Oxygen(g/ml)": 4.0, "Dissolved Oxygen_raw": 4.0,
         "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},
    ]
    # Plateau hors bornes sur plusieurs créneaux horaires consécutifs (30/07, 02h-05h) :
    # aucun voisin valide proche, donc entièrement `missing` côté colonne nettoyée.
    plateau_values = [38.6, 39.1, 40.2, 37.8]
    for hour, value in zip(range(2, 6), plateau_values):
        rows.append({
            "created_at": f"2021-07-30 0{hour}:15:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": value,
            "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True,
        })
    df = _resample_input(rows)
    out = features.resample_hourly(df)

    plateau_slots = out[out[config.TIMESTAMP_COLUMN].between("2021-07-30 02:00:00", "2021-07-30 05:00:00")]
    assert len(plateau_slots) == 4
    # Côté nettoyé : rien d'exploitable.
    assert plateau_slots["Dissolved Oxygen_n_measured"].sum() == 0
    assert plateau_slots["Dissolved Oxygen_mean"].isna().all()
    # Côté brut : le plateau est intégralement visible et dans la plage attendue.
    assert plateau_slots["Dissolved Oxygen_raw_n_present"].sum() == 4
    assert plateau_slots["Dissolved Oxygen_raw_mean"].between(35, 41).all()
    assert plateau_slots["Dissolved Oxygen_n_out_of_bounds"].sum() == 4


# --- resample_hourly : suffixe brut lu depuis config, cas limites et NaN de --
# --- n_out_of_bounds (D10, reports/validations/jalon-2.md itération 2, ------
# --- mutations M6, M7, M7b, M9, M11) -----------------------------------------


def test_resample_hourly_raw_value_suffix_comes_from_config_not_hard_coded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Le suffixe de colonne brute utilisé par resample_hourly suit config.RAW_VALUE_SUFFIX,
    jamais un littéral "_raw" en dur (règle data-engineer n°2 ; même modèle que
    tests/test_ingestion.py::test_clean_data_raw_value_suffix_comes_from_config_not_hard_coded ;
    mutation M9)."""
    monkeypatch.setattr(config, "RAW_VALUE_SUFFIX", "_original")
    df = _resample_input(
        [
            {"created_at": "2021-07-30 02:05:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_original": 38.6,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
        ]
    )
    out = features.resample_hourly(df)

    assert "Dissolved Oxygen_original_mean" in out.columns
    assert "Dissolved Oxygen_original_n_present" in out.columns
    # Un suffixe "_raw" en dur chercherait "Dissolved Oxygen_raw", absent ici.
    assert "Dissolved Oxygen_raw_mean" not in out.columns


def test_resample_hourly_n_out_of_bounds_excludes_value_exactly_at_lower_bound() -> None:
    """Une valeur brute exactement égale à bounds["min"] n'est PAS comptée hors bornes ; juste
    en-dessous, elle l'est (cas limite exigé par .claude/rules/conventions-code.md § Tests :
    juste sous / égal / juste au-dessus). Même convention que ingestion.clean_data, cf.
    tests/test_ingestion.py::test_clean_data_enforces_temperature_and_ph_bounds_at_edges
    (mutation M7b, `<` -> `<=`). Température choisie pour isoler la borne basse (valeurs très
    inférieures à critical_max/bounds['max'] = 40, donc aucune interférence avec la borne haute)."""
    lower = config.TEMPERATURE_BOUNDS["min"]
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Temperature (C)": None, "Temperature_raw": lower - 0.1,
             "Temperature_imputed": False, "Temperature_missing": True},  # juste sous la borne : hors bornes
            {"created_at": "2021-06-19 00:15:00", "Temperature (C)": lower, "Temperature_raw": lower,
             "Temperature_imputed": False, "Temperature_missing": False},  # exactement à la borne : pas hors bornes
            {"created_at": "2021-06-19 00:25:00", "Temperature (C)": lower + 0.1, "Temperature_raw": lower + 0.1,
             "Temperature_imputed": False, "Temperature_missing": False},  # juste au-dessus : pas hors bornes
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    assert slot["Temperature_n_out_of_bounds"] == 1


def test_resample_hourly_n_out_of_bounds_excludes_value_exactly_at_upper_bound() -> None:
    """Une valeur brute exactement égale à bounds["max"] n'est PAS comptée hors bornes ; juste
    au-dessus, elle l'est (cas limite exigé par .claude/rules/conventions-code.md § Tests :
    juste sous / égal / juste au-dessus). Même convention que ingestion.clean_data, cf.
    tests/test_ingestion.py::test_clean_data_applies_dissolved_oxygen_bound_per_adr_010
    (mutation M7, `>` -> `>=`). Oxygène dissous choisi pour isoler la borne haute
    (DISSOLVED_OXYGEN_BOUNDS n'a pas de borne basse : bounds.get("min") est None)."""
    upper = config.DISSOLVED_OXYGEN_BOUNDS["max"]
    assert config.DISSOLVED_OXYGEN_BOUNDS.get("min") is None  # hypothèse du test : isole la borne haute
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Dissolved Oxygen(g/ml)": upper - 0.1, "Dissolved Oxygen_raw": upper - 0.1,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},  # juste sous : pas hors bornes
            {"created_at": "2021-06-19 00:15:00", "Dissolved Oxygen(g/ml)": upper, "Dissolved Oxygen_raw": upper,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},  # exactement à la borne : pas hors bornes
            {"created_at": "2021-06-19 00:25:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": upper + 0.1,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},  # juste au-dessus : hors bornes
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    assert slot["Dissolved Oxygen_n_out_of_bounds"] == 1


def test_resample_hourly_raw_n_present_excludes_nan_raw_values() -> None:
    """<label>_raw_n_present compte les valeurs brutes réellement présentes, jamais le nombre
    total de relevés du créneau (`n_readings`) : une valeur brute NaN n'est jamais comptée comme
    présente (mutation M6 : `raw_n_present = n_readings`)."""
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Dissolved Oxygen(g/ml)": 5.0, "Dissolved Oxygen_raw": 5.0,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},
            {"created_at": "2021-06-19 00:15:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": None,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
            {"created_at": "2021-06-19 00:25:00", "Dissolved Oxygen(g/ml)": 5.4, "Dissolved Oxygen_raw": 5.4,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": False},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    assert slot["n_readings"] == 3
    # Une seule valeur brute NaN sur les 3 relevés du créneau : n_present = 2, jamais 3.
    assert slot["Dissolved Oxygen_raw_n_present"] == 2


def test_resample_hourly_n_out_of_bounds_never_counts_missing_raw_value() -> None:
    """Une valeur brute manquante (NaN) n'est jamais comptée dans <label>_n_out_of_bounds, même
    au sein d'un créneau contenant par ailleurs une vraie valeur hors bornes (mutation M11 :
    compteur hors borne comptant aussi les NaN bruts)."""
    upper = config.DISSOLVED_OXYGEN_BOUNDS["max"]
    df = _resample_input(
        [
            {"created_at": "2021-06-19 00:05:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": upper + 5,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
            {"created_at": "2021-06-19 00:15:00", "Dissolved Oxygen(g/ml)": None, "Dissolved Oxygen_raw": None,
             "Dissolved Oxygen_imputed": False, "Dissolved Oxygen_missing": True},
        ]
    )
    out = features.resample_hourly(df)
    slot = out.iloc[0]

    # Une seule valeur brute réellement hors bornes dans le créneau ; le NaN
    # de la seconde ligne n'est jamais compté, quelle que soit sa position.
    assert slot["Dissolved Oxygen_n_out_of_bounds"] == 1
