"""Tests du module d'ingestion (`src/ingestion.py`) — Module 1, Jalon 1.

Décisions appliquées et vérifiées ici : ADR-003 (ammoniac), ADR-009 (unités
mg/L, nature des capteurs), ADR-010 (bornes température/pH/DO/nitrate,
fuseau horaire, limite d'interpolation) — `docs/07-JOURNAL_DECISIONS.md`.
Jeux de données synthétiques uniquement (règle data-engineer n°12, jamais le
CSV complet), cas limites inclus (valeur égale à la borne, -127 °C, pH
négatif, trou plus long que la limite).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("pandas")

import pandas as pd

from src import config, ingestion

# --- Aides de construction de jeux synthétiques ----------------------------

# Valeurs par défaut plausibles (dans les bornes) pour les colonnes non
# testées explicitement par un cas donné — évite de répéter 11 colonnes à
# chaque test tout en gardant des lignes valides par défaut.
_DEFAULTS = {
    "Temperature (C)": 25.0,
    "Turbidity(NTU)": 50,
    "Dissolved Oxygen(g/ml)": 5.0,
    "PH": 7.2,
    "Ammonia(g/ml)": 0.5,
    "Nitrate(g/ml)": 150,
    "Population": 50,
    "Fish_Length(cm)": 7.11,
    "Fish_Weight(g)": 2.91,
}


def _write_raw_csv(tmp_path: Path, rows: list[dict]) -> Path:
    """Écrit un CSV brut conforme à `config.RAW_COLUMNS` dans `tmp_path`.

    Chaque `row` de `rows` doit contenir au moins `created_at` (str, sans le
    suffixe — ajouté ici) ; les colonnes non précisées prennent une valeur
    par défaut plausible (`_DEFAULTS`) ; `entry_id` est auto-incrémenté si
    absent.
    """
    records = []
    for i, row in enumerate(rows, start=1):
        record = dict(_DEFAULTS)
        record.update(row)
        record["created_at"] = f"{row['created_at']}{config.TIMESTAMP_SUFFIX}"
        record.setdefault("entry_id", i)
        records.append({col: record[col] for col in config.RAW_COLUMNS})

    df = pd.DataFrame.from_records(records, columns=config.RAW_COLUMNS)
    path = tmp_path / "synthetic_raw.csv"
    df.to_csv(path, index=False)
    return path


def _synthetic_clean_input(rows: list[dict]) -> pd.DataFrame:
    """Construit directement un DataFrame « post-`load_raw_data` » (timestamps
    déjà parsés en datetime, pas de suffixe) pour tester `clean_data` sans
    passer par un fichier CSV.
    """
    records = []
    for i, row in enumerate(rows, start=1):
        record = dict(_DEFAULTS)
        record.update(row)
        record.setdefault("entry_id", i)
        records.append({col: record[col] for col in config.RAW_COLUMNS})
    df = pd.DataFrame.from_records(records, columns=config.RAW_COLUMNS)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


# --- Contrat du module ------------------------------------------------------


def test_module_exposes_expected_callable_functions() -> None:
    """Le module expose load_raw_data, clean_data et rebuild_growth_curve, appelables et documentées."""
    for name in ("load_raw_data", "clean_data", "rebuild_growth_curve"):
        func = getattr(ingestion, name, None)
        assert callable(func), f"{name} doit être une fonction appelable"
        assert func.__doc__, f"{name} doit avoir une docstring (entrée -> sortie)"


# --- load_raw_data -----------------------------------------------------------


def test_load_raw_data_raises_on_invalid_schema(tmp_path: Path) -> None:
    """load_raw_data lève une exception claire si les colonnes ne correspondent pas à config.RAW_COLUMNS."""
    bad_columns = [c for c in config.RAW_COLUMNS if c != "PH"]  # colonne manquante
    df = pd.DataFrame(columns=bad_columns)
    path = tmp_path / "invalid_schema.csv"
    df.to_csv(path, index=False)

    with pytest.raises(ValueError, match="Schéma brut invalide"):
        ingestion.load_raw_data(str(path))


def test_load_raw_data_raises_on_missing_file(tmp_path: Path) -> None:
    """load_raw_data lève une exception explicite si le fichier n'existe pas (échec explicite, règle n°1)."""
    with pytest.raises(FileNotFoundError):
        ingestion.load_raw_data(str(tmp_path / "does_not_exist.csv"))


def test_load_raw_data_strips_suffix_and_sorts_chronologically(tmp_path: Path) -> None:
    """Le suffixe de fuseau est retiré (sans conversion, ADR-010) et les lignes sont triées par created_at."""
    path = _write_raw_csv(
        tmp_path,
        [
            {"created_at": "2021-06-19 00:02:00"},
            {"created_at": "2021-06-19 00:00:05"},
            {"created_at": "2021-06-19 00:01:00"},
        ],
    )
    df = ingestion.load_raw_data(str(path))

    assert list(df["created_at"]) == sorted(df["created_at"])
    assert pd.api.types.is_datetime64_any_dtype(df["created_at"])
    assert not df["created_at"].astype(str).str.contains("CET").any()
    assert df.attrs["source_sha256"] == __import__("hashlib").sha256(path.read_bytes()).hexdigest()


# --- clean_data : nettoyage non destructif ----------------------------------


def test_clean_data_never_drops_rows() -> None:
    """clean_data conserve le même nombre de lignes en entrée et en sortie, quelles que soient les valeurs hors bornes."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": -127.0},
            {"created_at": "2021-06-19 00:01:00", "PH": -5.0},
            {"created_at": "2021-06-19 00:02:00", "Dissolved Oxygen(g/ml)": 41.0},
            {"created_at": "2021-06-19 00:03:00", "Ammonia(g/ml)": 4.27e11},
            {"created_at": "2021-06-19 00:04:00"},
        ]
    )
    clean_df, _ = ingestion.clean_data(df)
    assert len(clean_df) == len(df) == 5


# --- clean_data : bornes température / pH, cas limites ---------------------


def test_clean_data_enforces_temperature_and_ph_bounds_at_edges() -> None:
    """Les valeurs égales aux bornes (0/40 °C, 0/14 pH) sont conservées ; juste hors bornes, marquées hors bornes puis imputées (voisin proche)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 0.0, "PH": 0.0},
            {"created_at": "2021-06-19 00:01:00", "Temperature (C)": 40.0, "PH": 14.0},
            {"created_at": "2021-06-19 00:02:00", "Temperature (C)": 40.0001, "PH": 14.0001},
            # Voisin valide proche après la valeur hors bornes : distingue
            # « hors bornes » de « resté manquant » (D9) — ici elle est
            # comblée (trou de 1 min, bien en-deçà de MAX_INTERPOLATION_GAP).
            {"created_at": "2021-06-19 00:03:00", "Temperature (C)": 39.0, "PH": 13.0},
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    # Valeurs exactement aux bornes : conservées, non marquées (ni imputées ni manquantes).
    assert clean_df.loc[0, "Temperature (C)"] == 0.0
    assert clean_df.loc[0, "Temperature_imputed"] == False  # noqa: E712
    assert clean_df.loc[0, "Temperature_missing"] == False  # noqa: E712
    assert clean_df.loc[1, "Temperature (C)"] == 40.0
    assert clean_df.loc[1, "Temperature_imputed"] == False  # noqa: E712
    assert clean_df.loc[1, "Temperature_missing"] == False  # noqa: E712
    assert clean_df.loc[0, "PH_imputed"] == False  # noqa: E712
    assert clean_df.loc[1, "PH_imputed"] == False  # noqa: E712

    # Juste au-dessus de la borne haute : hors bornes, mais comblée par
    # interpolation grâce au voisin proche (imputed=True, missing=False).
    assert clean_df.loc[2, "Temperature_imputed"] == True  # noqa: E712
    assert clean_df.loc[2, "Temperature_missing"] == False  # noqa: E712
    assert clean_df.loc[2, "PH_imputed"] == True  # noqa: E712
    assert clean_df.loc[2, "PH_missing"] == False  # noqa: E712

    assert report["columns"]["Temperature (C)"]["bounds"] == {"min": 0, "max": 40}
    assert report["columns"]["PH"]["bounds"] == {"min": 0, "max": 14}
    assert report["columns"]["Temperature (C)"]["n_out_of_bounds"] == 1
    assert report["columns"]["PH"]["n_out_of_bounds"] == 1


def test_clean_data_flags_minus_127_temperature_as_out_of_bounds() -> None:
    """Une valeur -127 en température est marquée hors bornes, comblée (voisins proches) et jamais laissée telle quelle."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 25.0},
            {"created_at": "2021-06-19 00:00:20", "Temperature (C)": -127.0},
            {"created_at": "2021-06-19 00:00:40", "Temperature (C)": 25.2},
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert clean_df.loc[1, "Temperature_imputed"] == True  # noqa: E712
    assert clean_df.loc[1, "Temperature_missing"] == False  # noqa: E712
    assert clean_df.loc[1, "Temperature (C)"] != -127.0  # jamais laissée telle quelle
    assert report["columns"]["Temperature (C)"]["n_out_of_bounds"] == 1


def test_clean_data_flags_negative_ph_as_out_of_bounds() -> None:
    """Un pH négatif (impossible sur l'échelle réelle) est marqué hors bornes, comblé (voisins proches) et jamais laissé tel quel."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "PH": 7.4},
            {"created_at": "2021-06-19 00:00:20", "PH": -0.586},
            {"created_at": "2021-06-19 00:00:40", "PH": 7.5},
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert clean_df.loc[1, "PH_imputed"] == True  # noqa: E712
    assert clean_df.loc[1, "PH_missing"] == False  # noqa: E712
    assert clean_df.loc[1, "PH"] != -0.586
    assert report["columns"]["PH"]["n_out_of_bounds"] == 1


# --- clean_data : ammoniac (ADR-003) et oxygène dissous (ADR-010) ----------


def test_clean_data_flags_extreme_ammonia_above_five_as_artifact() -> None:
    """ADR-003 : une valeur d'ammoniac > 5 est marquée hors bornes ; comblée si un voisin est proche (D9 : imputed),
    laissée manquante en fin de série sans voisin suivant (D9 : missing)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Ammonia(g/ml)": 0.458},
            {"created_at": "2021-06-19 00:00:20", "Ammonia(g/ml)": 4.27e11},  # hors bornes, encadrée -> imputée
            {"created_at": "2021-06-19 00:00:40", "Ammonia(g/ml)": 5.0},  # à la borne : conservée
            {"created_at": "2021-06-19 00:01:00", "Ammonia(g/ml)": 5.0001},  # hors bornes, dernière ligne -> manquante
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert clean_df.loc[1, "Ammonia_imputed"] == True  # noqa: E712
    assert clean_df.loc[1, "Ammonia_missing"] == False  # noqa: E712
    assert clean_df.loc[2, "Ammonia_imputed"] == False  # noqa: E712
    assert clean_df.loc[2, "Ammonia_missing"] == False  # noqa: E712
    assert clean_df.loc[2, "Ammonia(g/ml)"] == 5.0
    # Dernière ligne, aucun voisin après elle pour encadrer le trou : reste
    # manquante (D9), jamais extrapolée ni faussement marquée « imputée ».
    assert clean_df.loc[3, "Ammonia_imputed"] == False  # noqa: E712
    assert clean_df.loc[3, "Ammonia_missing"] == True  # noqa: E712
    assert pd.isna(clean_df.loc[3, "Ammonia(g/ml)"])
    assert report["columns"]["Ammonia(g/ml)"]["bounds"] == {"max": 5}
    assert report["columns"]["Ammonia(g/ml)"]["n_out_of_bounds"] == 2
    assert report["columns"]["Ammonia(g/ml)"]["n_imputed"] == 1
    assert report["columns"]["Ammonia(g/ml)"]["n_still_missing"] == 1
    assert "ADR-003" in report["columns"]["Ammonia(g/ml)"]["note"]
    assert report["columns"]["Ammonia(g/ml)"]["absolute_thresholds_applicable"] is False


def test_clean_data_applies_dissolved_oxygen_bound_per_adr_010() -> None:
    """La borne haute DO (15, ADR-010 accepté) est appliquée, référencée dans le rapport, et la valeur hors bornes est comblée (voisin proche)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Dissolved Oxygen(g/ml)": 8.0},
            {"created_at": "2021-06-19 00:00:20", "Dissolved Oxygen(g/ml)": 15.0},  # à la borne : conservée
            {"created_at": "2021-06-19 00:00:40", "Dissolved Oxygen(g/ml)": 15.0001},  # hors bornes
            {"created_at": "2021-06-19 00:01:00", "Dissolved Oxygen(g/ml)": 9.0},  # voisin proche : encadre le trou
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert clean_df.loc[1, "Dissolved Oxygen_imputed"] == False  # noqa: E712
    assert clean_df.loc[1, "Dissolved Oxygen_missing"] == False  # noqa: E712
    assert clean_df.loc[2, "Dissolved Oxygen_imputed"] == True  # noqa: E712
    assert clean_df.loc[2, "Dissolved Oxygen_missing"] == False  # noqa: E712
    assert report["columns"]["Dissolved Oxygen(g/ml)"]["bounds"] == {"max": 15}
    assert report["columns"]["Dissolved Oxygen(g/ml)"]["n_imputed"] == 1
    assert "ADR-010" in report["columns"]["Dissolved Oxygen(g/ml)"]["note"]


def test_clean_data_applies_no_absolute_bound_to_nitrate() -> None:
    """ADR-009 : Nitrate (capteur de gaz) n'a aucune borne absolue — colonne non modifiée, aucune colonne de marquage."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Nitrate(g/ml)": 45},
            {"created_at": "2021-06-19 00:00:20", "Nitrate(g/ml)": 1936},
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert "Nitrate_imputed" not in clean_df.columns
    assert "Nitrate_missing" not in clean_df.columns
    assert list(clean_df["Nitrate(g/ml)"]) == [45, 1936]
    assert report["columns"]["Nitrate(g/ml)"]["bounds"] is None
    assert report["columns"]["Nitrate(g/ml)"]["absolute_thresholds_applicable"] is False


# --- clean_data : colonne de valeur brute conservée en parallèle (décision --
# --- G1 du 2026-09-18, J-20260918-042/044) -----------------------------------


def test_clean_data_preserves_raw_value_in_parallel_column_when_out_of_bounds() -> None:
    """<label>_raw conserve la valeur brute d'origine hors bornes, sans imputation, même quand la colonne nettoyée est marquée manquante."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Dissolved Oxygen(g/ml)": 38.6},  # hors bornes, isolée -> reste manquante
            {"created_at": "2021-06-19 03:00:00", "Dissolved Oxygen(g/ml)": 5.0},   # dans les bornes
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    raw_col = f"Dissolved Oxygen{config.RAW_VALUE_SUFFIX}"
    assert raw_col in clean_df.columns
    # La valeur brute est conservée telle quelle, y compris hors bornes.
    assert clean_df.loc[0, raw_col] == 38.6
    # La colonne nettoyée, elle, ne montre plus la valeur hors bornes brute
    # (trou de 3h > MAX_INTERPOLATION_GAP : reste manquante, D9).
    assert clean_df.loc[0, "Dissolved Oxygen_missing"] == True  # noqa: E712
    assert pd.isna(clean_df.loc[0, "Dissolved Oxygen(g/ml)"])
    # Valeur dans les bornes : la colonne brute et la colonne nettoyée coïncident.
    assert clean_df.loc[1, raw_col] == 5.0
    assert clean_df.loc[1, "Dissolved Oxygen(g/ml)"] == 5.0
    assert report["columns"]["Dissolved Oxygen(g/ml)"]["raw_value_column"] == raw_col


def test_clean_data_raw_value_column_preserved_even_when_cleaned_value_is_imputed() -> None:
    """<label>_raw garde la valeur brute même quand la colonne nettoyée, elle, a été comblée par interpolation (les deux colonnes divergent alors)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 24.0},
            {"created_at": "2021-06-19 00:00:20", "Temperature (C)": -127.0},  # hors bornes, voisins proches -> imputée
            {"created_at": "2021-06-19 00:00:40", "Temperature (C)": 24.2},
        ]
    )
    clean_df, _ = ingestion.clean_data(df)

    raw_col = f"Temperature{config.RAW_VALUE_SUFFIX}"
    assert clean_df.loc[1, raw_col] == -127.0  # jamais modifiée
    assert clean_df.loc[1, "Temperature_imputed"] == True  # noqa: E712
    assert clean_df.loc[1, "Temperature (C)"] != -127.0  # la colonne nettoyée, elle, a bien été comblée
    assert clean_df.loc[1, "Temperature (C)"] != clean_df.loc[1, raw_col]  # les deux colonnes divergent


def test_clean_data_raw_value_column_keeps_nan_when_raw_value_already_missing() -> None:
    """<label>_raw garde NaN si la valeur brute d'origine l'était déjà — jamais une valeur fabriquée."""
    df = _synthetic_clean_input([{"created_at": "2021-06-19 00:00:00", "PH": None}])
    clean_df, _ = ingestion.clean_data(df)
    assert pd.isna(clean_df.loc[0, f"PH{config.RAW_VALUE_SUFFIX}"])


def test_clean_data_raw_value_column_only_for_bounded_variables() -> None:
    """Nitrate et Turbidity (sans borne) n'ont pas de colonne <label>_raw dédiée : la colonne brute est déjà leur seule valeur."""
    df = _synthetic_clean_input(
        [{"created_at": "2021-06-19 00:00:00", "Nitrate(g/ml)": 150, "Turbidity(NTU)": 50}]
    )
    clean_df, report = ingestion.clean_data(df)

    assert "Nitrate_raw" not in clean_df.columns
    assert "Turbidity_raw" not in clean_df.columns
    assert report["columns"]["Nitrate(g/ml)"]["raw_value_column"] is None
    assert report["columns"]["Turbidity(NTU)"]["raw_value_column"] is None


def test_clean_data_raw_value_suffix_comes_from_config_not_hard_coded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le suffixe de la colonne de valeur brute suit config.RAW_VALUE_SUFFIX (aucune valeur en dur, règle data-engineer n°2)."""
    monkeypatch.setattr(config, "RAW_VALUE_SUFFIX", "_original")
    df = _synthetic_clean_input([{"created_at": "2021-06-19 00:00:00", "Temperature (C)": 24.0}])
    clean_df, report = ingestion.clean_data(df)

    assert "Temperature_original" in clean_df.columns
    assert "Temperature_raw" not in clean_df.columns
    assert report["columns"]["Temperature (C)"]["raw_value_column"] == "Temperature_original"


def test_clean_data_episode1_do_plateau_readable_again_in_raw_column_on_regenerated_livrable() -> None:
    """Confirmation par calcul (petit jeu représentatif) que l'épisode 1 (plateau DO 36-41, 30/07-05/08) redevient lisible dans Dissolved Oxygen_raw,
    alors qu'il est entièrement `missing` dans la colonne nettoyée — le problème signalé en J-20260918-039/040, résolu par G1 J-20260918-042/044."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-07-29 23:00:00", "Dissolved Oxygen(g/ml)": 4.0},  # avant l'épisode, dans les bornes
            {"created_at": "2021-07-30 02:00:00", "Dissolved Oxygen(g/ml)": 38.6},  # début du plateau, hors bornes
            {"created_at": "2021-08-01 12:00:00", "Dissolved Oxygen(g/ml)": 39.1},  # milieu du plateau (>1h de trou)
            {"created_at": "2021-08-05 09:00:00", "Dissolved Oxygen(g/ml)": 4.4},   # retour au régime bas, dans les bornes
        ]
    )
    clean_df, _ = ingestion.clean_data(df)
    raw_col = f"Dissolved Oxygen{config.RAW_VALUE_SUFFIX}"

    plateau_mask = clean_df[config.TIMESTAMP_COLUMN].between("2021-07-30 02:00:00", "2021-08-01 12:00:00")
    # Colonne nettoyée : le plateau reste bien manquant (trous >> 1h, non comblés).
    assert clean_df.loc[plateau_mask, "Dissolved Oxygen(g/ml)"].isna().all()
    assert clean_df.loc[plateau_mask, "Dissolved Oxygen_missing"].all()
    # Colonne brute : le plateau est de nouveau exploitable (valeurs réelles, dans la plage attendue 36-41).
    raw_plateau = clean_df.loc[plateau_mask, raw_col]
    assert raw_plateau.notna().all()
    assert raw_plateau.between(35, 41).all()


# --- clean_data : interpolation limitée dans le temps -----------------------


def test_clean_data_interpolates_short_gap_within_limit() -> None:
    """Un trou plus court que config.MAX_INTERPOLATION_GAP est comblé par interpolation temporelle (D9 : imputed=True, missing=False)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 10.0},
            {"created_at": "2021-06-19 00:30:00", "Temperature (C)": -127.0},  # trou de 1h avec les 2 voisins = à la limite
            {"created_at": "2021-06-19 01:00:00", "Temperature (C)": 12.0},
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert clean_df.loc[1, "Temperature_imputed"] == True  # noqa: E712
    assert clean_df.loc[1, "Temperature_missing"] == False  # noqa: E712
    assert clean_df.loc[1, "Temperature (C)"] == pytest.approx(11.0)
    assert report["columns"]["Temperature (C)"]["n_imputed"] == 1
    assert report["columns"]["Temperature (C)"]["n_still_missing"] == 0


def test_clean_data_does_not_interpolate_beyond_max_gap() -> None:
    """Un trou de mesures plus long que la limite configurée n'est PAS comblé (D9 : imputed=False) et reste marqué manquant (missing=True)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": 10.0},
            {"created_at": "2021-06-19 01:30:01", "Temperature (C)": -127.0},  # 1h30 après le dernier point valide
            {"created_at": "2021-06-19 03:00:02", "Temperature (C)": 12.0},  # > MAX_INTERPOLATION_GAP (1h) des 2 côtés
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    # Hors bornes mais PAS comblée (trou > 1h des deux côtés) : imputed=False,
    # missing=True — c'est précisément la distinction introduite par D9.
    assert clean_df.loc[1, "Temperature_imputed"] == False  # noqa: E712
    assert clean_df.loc[1, "Temperature_missing"] == True  # noqa: E712
    assert pd.isna(clean_df.loc[1, "Temperature (C)"])
    assert report["columns"]["Temperature (C)"]["n_imputed"] == 0
    assert report["columns"]["Temperature (C)"]["n_still_missing"] == 1


def test_clean_data_leaves_missing_value_at_series_edge_without_extrapolating() -> None:
    """Une valeur hors bornes sans point valide après elle (fin de série) n'est jamais extrapolée : imputed=False, missing=True (D9)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "PH": 7.4},
            {"created_at": "2021-06-19 00:00:20", "PH": 7.5},
            {"created_at": "2021-06-19 00:00:40", "PH": -1.0},  # dernière ligne : rien après pour encadrer le trou
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert clean_df.loc[2, "PH_imputed"] == False  # noqa: E712
    assert clean_df.loc[2, "PH_missing"] == True  # noqa: E712
    assert pd.isna(clean_df.loc[2, "PH"])
    assert report["columns"]["PH"]["n_still_missing"] == 1


# --- clean_data : doublons d'horodatage -------------------------------------


def test_clean_data_counts_duplicate_timestamps_without_dropping_rows() -> None:
    """Les doublons de timestamp sont comptés dans le rapport, sans qu'aucune ligne ne soit supprimée."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00"},
            {"created_at": "2021-06-19 00:00:00"},  # doublon exact
            {"created_at": "2021-06-19 00:01:00"},
        ]
    )
    clean_df, report = ingestion.clean_data(df)

    assert len(clean_df) == 3
    assert report["n_duplicate_timestamps"] == 1


# --- clean_data : rapport complet -------------------------------------------


def test_clean_data_report_is_complete_per_column() -> None:
    """Le rapport retourné par clean_data couvre les 11 colonnes brutes (D6, reports/validations/jalon-1.md)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Temperature (C)": -127.0},
            {"created_at": "2021-06-19 00:01:00"},
        ]
    )
    df.attrs["source_path"] = "data/raw/IoTpond1.csv"
    df.attrs["source_sha256"] = "deadbeef"

    _, report = ingestion.clean_data(df)

    assert report["source_file"] == {"path": "data/raw/IoTpond1.csv", "sha256": "deadbeef"}
    assert set(report["decisions_applied"]) >= {"ADR-003", "ADR-009", "ADR-010"}
    assert report["max_interpolation_gap"] == config.MAX_INTERPOLATION_GAP
    assert report["n_rows"] == 2
    assert "n_duplicate_timestamps" in report

    bounded_columns = {
        "Temperature (C)", "PH", "Dissolved Oxygen(g/ml)", "Ammonia(g/ml)",
        "Nitrate(g/ml)", "Turbidity(NTU)",
    }
    other_columns = {"created_at", "entry_id", "Population"}
    # D6 : les 11 colonnes brutes sont couvertes — 6 dans "columns" (SENSOR_TYPES),
    # 3 de plus dans "columns" (horodatage + OTHER_RAW_COLUMNS), et les 2
    # colonnes de croissance dans la clé "growth_curve" (vérifié séparément).
    assert bounded_columns | other_columns <= set(report["columns"].keys())
    for col_name in bounded_columns:
        col_report = report["columns"][col_name]
        for key in ("bounds", "n_out_of_bounds", "n_missing_raw", "n_imputed", "n_still_missing", "raw_value_column", "note"):
            assert key in col_report, f"{col_name} : clé '{key}' absente du rapport"
    for col_name in other_columns:
        col_report = report["columns"][col_name]
        for key in ("n_missing_raw", "note"):
            assert key in col_report, f"{col_name} : clé '{key}' absente du rapport"

    # Les colonnes de croissance ne sont volontairement PAS dans "columns"
    # (non nettoyées par bornes) mais bien dans "growth_curve" (D6).
    assert set(report["growth_curve"]["columns"].keys()) == {"Fish_Weight(g)", "Fish_Length(cm)"}
    assert "Fish_Weight(g)" not in report["columns"]
    assert "Fish_Length(cm)" not in report["columns"]
    assert set(report["columns"].keys()) == bounded_columns | other_columns


def test_clean_data_report_includes_growth_curve_reconstruction() -> None:
    """D6 : le résultat de rebuild_growth_curve (paliers, non-monotonies) est persisté dans le rapport, pas seulement loggué."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-20 00:00:00", "Fish_Weight(g)": 3.85, "Fish_Length(cm)": 18.08},
            {"created_at": "2021-06-21 00:00:00", "Fish_Weight(g)": 4.79, "Fish_Length(cm)": 15.31},  # baisse réelle
        ]
    )
    _, report = ingestion.clean_data(df)

    growth = report["growth_curve"]
    assert growth["n_paliers"] == 3
    assert growth["columns"]["Fish_Weight(g)"]["n_non_monotonic"] == 0
    assert growth["columns"]["Fish_Weight(g)"]["flagged_points"] == []
    assert growth["columns"]["Fish_Length(cm)"]["n_non_monotonic"] == 1
    flagged = growth["columns"]["Fish_Length(cm)"]["flagged_points"]
    assert len(flagged) == 1
    assert flagged[0]["value"] == 15.31


def test_clean_data_report_missing_source_metadata_is_none_not_guessed() -> None:
    """Sans DataFrame issu de load_raw_data (pas d'attrs), le rapport indique None plutôt que de deviner l'empreinte."""
    df = _synthetic_clean_input([{"created_at": "2021-06-19 00:00:00"}])
    _, report = ingestion.clean_data(df)
    assert report["source_file"] == {"path": None, "sha256": None}


# --- rebuild_growth_curve ----------------------------------------------------


def test_rebuild_growth_curve_keeps_one_point_per_real_change() -> None:
    """rebuild_growth_curve ne garde qu'un point par changement réel de valeur (pas un point par ligne brute)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-19 00:01:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-19 00:02:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-20 00:00:00", "Fish_Weight(g)": 3.85, "Fish_Length(cm)": 7.50},
        ]
    )
    curve = ingestion.rebuild_growth_curve(df)
    assert len(curve) == 2
    assert list(curve["Fish_Weight(g)"]) == [2.91, 3.85]


def test_rebuild_growth_curve_is_monotonic_or_flags_non_monotonic_points() -> None:
    """rebuild_growth_curve signale toute non-monotonie sans jamais corriger la valeur."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-20 00:00:00", "Fish_Weight(g)": 3.85, "Fish_Length(cm)": 18.08},
            {"created_at": "2021-06-21 00:00:00", "Fish_Weight(g)": 4.79, "Fish_Length(cm)": 15.31},  # baisse réelle
        ]
    )
    curve = ingestion.rebuild_growth_curve(df)

    assert list(curve["Fish_Weight_non_monotonic"]) == [False, False, False]
    assert list(curve["Fish_Length_non_monotonic"]) == [False, False, True]
    # Non corrigée silencieusement : la valeur brute est conservée telle quelle.
    assert curve.loc[2, "Fish_Length(cm)"] == 15.31


def test_rebuild_growth_curve_ignores_missing_raw_values() -> None:
    """Une valeur manquante (NaN) du relevé brut n'est jamais comptée comme un palier ni comme un changement."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-19 00:01:00", "Fish_Weight(g)": None, "Fish_Length(cm)": None},
            {"created_at": "2021-06-19 00:02:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
        ]
    )
    curve = ingestion.rebuild_growth_curve(df)
    assert len(curve) == 1
    assert curve.loc[0, "Fish_Weight(g)"] == 2.91


def test_rebuild_growth_curve_monotonic_real_cycle_has_no_flag() -> None:
    """Sur une croissance réellement monotone, aucune non-monotonie n'est signalée (faux positif)."""
    df = _synthetic_clean_input(
        [
            {"created_at": "2021-06-19 00:00:00", "Fish_Weight(g)": 2.91, "Fish_Length(cm)": 7.11},
            {"created_at": "2021-06-20 00:00:00", "Fish_Weight(g)": 3.85, "Fish_Length(cm)": 7.50},
            {"created_at": "2021-06-21 00:00:00", "Fish_Weight(g)": 4.79, "Fish_Length(cm)": 7.89},
        ]
    )
    curve = ingestion.rebuild_growth_curve(df)
    assert not curve["Fish_Weight_non_monotonic"].any()
    assert not curve["Fish_Length_non_monotonic"].any()


# --- Point d'entrée CLI de régénération (D7, reports/validations/jalon-1.md) --


def test_regenerate_processed_artifacts_writes_both_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`python -m src.ingestion` régénère le CSV nettoyé et le rapport JSON, avec un message clair et un code 0."""
    raw_path = _write_raw_csv(
        tmp_path,
        [
            {"created_at": "2021-06-19 00:00:00"},
            {"created_at": "2021-06-19 00:01:00"},
        ],
    )
    processed_path = tmp_path / "out" / "pond1_clean.csv"
    report_path = tmp_path / "out" / "cleaning_report.json"
    monkeypatch.setattr(config, "PROCESSED_DATA_PATH", processed_path)
    monkeypatch.setattr(config, "CLEANING_REPORT_PATH", report_path)

    exit_code = ingestion.regenerate_processed_artifacts(["--input", str(raw_path)])

    assert exit_code == 0
    assert processed_path.exists()
    assert report_path.exists()
    written = pd.read_csv(processed_path)
    assert len(written) == 2
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["n_rows"] == 2


def test_regenerate_processed_artifacts_returns_nonzero_with_clear_message_on_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """En cas d'échec (fichier brut introuvable), le code de sortie est non nul et le message est explicite sur stderr."""
    missing_path = tmp_path / "does_not_exist.csv"

    exit_code = ingestion.regenerate_processed_artifacts(["--input", str(missing_path)])

    assert exit_code != 0
    captured = capsys.readouterr()
    assert "Erreur" in captured.err
    assert str(missing_path) in captured.err
