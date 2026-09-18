"""Tests de `src/config.py` — sections data-engineer et sections communes.

Ces tests ne dépendent d'aucune bibliothèque tierce (pas de pandas) : ils
vérifient la forme du fichier de configuration (chemins, schéma, seuils),
pas la logique de traitement des données.
"""

from __future__ import annotations

from pathlib import Path

from src import config


# --- Chemins (data-engineer) ---------------------------------------------

def test_project_root_is_repository_root() -> None:
    """PROJECT_ROOT pointe vers la racine du dépôt (contient pytest.ini)."""
    assert (config.PROJECT_ROOT / "pytest.ini").exists()


def test_data_engineer_paths_are_under_project_root() -> None:
    """Tous les chemins de la section data-engineer sont construits sous PROJECT_ROOT."""
    paths = [
        config.RAW_DATA_PATH,
        config.PROCESSED_DATA_PATH,
        config.REPORTS_DIR,
        config.FIGURES_DIR,
        config.CLEANING_REPORT_PATH,
        config.MODELS_DIR,
        config.LOGS_DIR,
        config.DECISIONS_LOG_PATH,
    ]
    for path in paths:
        assert isinstance(path, Path), f"{path!r} doit être un pathlib.Path"
        assert path.is_relative_to(config.PROJECT_ROOT), f"{path} doit être sous PROJECT_ROOT"


def test_raw_data_path_targets_iotpond1_csv_in_raw_dir() -> None:
    """RAW_DATA_PATH pointe vers data/raw/IoTpond1.csv (docs/03)."""
    assert config.RAW_DATA_PATH == config.PROJECT_ROOT / "data" / "raw" / "IoTpond1.csv"


def test_processed_data_path_targets_processed_dir() -> None:
    """PROCESSED_DATA_PATH pointe vers data/processed/pond1_clean.csv (docs/03)."""
    assert config.PROCESSED_DATA_PATH == config.PROJECT_ROOT / "data" / "processed" / "pond1_clean.csv"


def test_figures_dir_is_inside_reports_dir() -> None:
    """FIGURES_DIR est un sous-dossier de REPORTS_DIR."""
    assert config.FIGURES_DIR.is_relative_to(config.REPORTS_DIR)


def test_cleaning_report_path_is_json_inside_reports_dir() -> None:
    """CLEANING_REPORT_PATH est un fichier .json sous REPORTS_DIR (docs/02 §2)."""
    assert config.CLEANING_REPORT_PATH.is_relative_to(config.REPORTS_DIR)
    assert config.CLEANING_REPORT_PATH.suffix == ".json"


# --- Schéma brut (data-engineer) ------------------------------------------

def test_raw_columns_has_exactly_11_expected_names() -> None:
    """Les 11 colonnes brutes exactes de docs/01-DATA_DICTIONARY.md sont présentes, sans doublon."""
    expected = {
        "created_at",
        "entry_id",
        "Temperature (C)",
        "Turbidity(NTU)",
        "Dissolved Oxygen(g/ml)",
        "PH",
        "Ammonia(g/ml)",
        "Nitrate(g/ml)",
        "Population",
        "Fish_Length(cm)",
        "Fish_Weight(g)",
    }
    assert len(config.RAW_COLUMNS) == 11
    assert len(set(config.RAW_COLUMNS)) == 11, "pas de colonne dupliquée"
    assert set(config.RAW_COLUMNS) == expected


def test_timestamp_column_is_created_at() -> None:
    """La colonne d'horodatage brute est `created_at` (docs/01)."""
    assert config.TIMESTAMP_COLUMN == "created_at"


def test_timestamp_suffix_to_strip_is_cet() -> None:
    """Le suffixe de fuseau à retirer est bien celui observé dans le fichier brut (docs/01)."""
    assert config.TIMESTAMP_SUFFIX.strip() == "CET"


# --- Seuils scientifiques (commun, identique à docs/03) -------------------

def test_thresholds_has_expected_parameter_keys() -> None:
    """THRESHOLDS couvre exactement les paramètres scientifiques de docs/03."""
    assert set(config.THRESHOLDS.keys()) == {
        "temperature",
        "dissolved_oxygen",
        "ph",
        "ammonia",
        "nitrate",
        "turbidity",
    }


def test_thresholds_matches_docs_03_values() -> None:
    """Les valeurs de THRESHOLDS reprennent exactement docs/03-ARCHITECTURE_CODE.md."""
    assert config.THRESHOLDS["temperature"] == {"min": 26, "max": 32, "critical_min": 20, "critical_max": 35}
    assert config.THRESHOLDS["dissolved_oxygen"] == {"min": 4, "critical_min": 3}
    assert config.THRESHOLDS["ph"] == {"min": 6.5, "max": 8.5, "critical_min": 6, "critical_max": 9}
    assert config.THRESHOLDS["ammonia"] == {"max": 0.05, "critical_max": 0.1}
    assert config.THRESHOLDS["nitrate"] == {"max": 50, "critical_max": 100}
    assert config.THRESHOLDS["turbidity"] == {"max": None, "critical_max": None}


def test_thresholds_critical_bounds_are_coherent_when_both_defined() -> None:
    """Quand min/max et critical_min/critical_max existent, critical <= optimal <= critical (cohérence physique)."""
    for name, bounds in config.THRESHOLDS.items():
        if "min" in bounds and "critical_min" in bounds and bounds["critical_min"] is not None and bounds["min"] is not None:
            assert bounds["critical_min"] <= bounds["min"], f"{name}: critical_min doit être <= min"
        if "max" in bounds and "critical_max" in bounds and bounds["critical_max"] is not None and bounds["max"] is not None:
            assert bounds["max"] <= bounds["critical_max"], f"{name}: max doit être <= critical_max"


# --- Nettoyage (data-engineer) ---------------------------------------------

def test_temperature_bounds_match_data_dictionary() -> None:
    """TEMPERATURE_BOUNDS = [0, 40] °C, borne physique documentée (docs/01 anomalie 1)."""
    assert config.TEMPERATURE_BOUNDS == {"min": 0, "max": 40}


def test_ph_bounds_match_data_dictionary() -> None:
    """PH_BOUNDS = [0, 14], borne physique documentée (docs/01 anomalie 2)."""
    assert config.PH_BOUNDS == {"min": 0, "max": 14}


def test_open_decisions_are_none_not_guessed_values() -> None:
    """RESAMPLING_FREQUENCY reste None (décision tranchée par ADR-010 mais appliquée seulement au Jalon 2, pas au nettoyage)."""
    assert config.RESAMPLING_FREQUENCY is None


def test_ammonia_bounds_match_adr_003_and_adr_010() -> None:
    """AMMONIA_BOUNDS = borne haute 5 (ADR-003 accepté, ADR-010)."""
    assert config.AMMONIA_BOUNDS == {"max": 5}


def test_dissolved_oxygen_bounds_match_adr_010() -> None:
    """DISSOLVED_OXYGEN_BOUNDS = borne haute définitive 15 (ADR-010, accepté y compris pour cette borne, 2026-09-18)."""
    assert config.DISSOLVED_OXYGEN_BOUNDS == {"max": 15}


def test_nitrate_bounds_is_permanently_none_per_adr_009() -> None:
    """NITRATE_BOUNDS reste None de façon durable (ADR-009 : capteur de gaz, pas un artefact à filtrer)."""
    assert config.NITRATE_BOUNDS is None


def test_max_interpolation_gap_is_one_hour_per_adr_010() -> None:
    """MAX_INTERPOLATION_GAP = "1h" (ADR-010) — conversion effective en pandas.Timedelta vérifiée côté test_ingestion.py."""
    assert config.MAX_INTERPOLATION_GAP == "1h"


def test_sensor_types_covers_all_water_quality_columns_with_expected_keys() -> None:
    """SENSOR_TYPES couvre les 6 colonnes de qualité d'eau, chacune avec label/sensor/bounds/applicabilité (ADR-009)."""
    expected_raw_columns = {
        "Temperature (C)", "PH", "Dissolved Oxygen(g/ml)",
        "Ammonia(g/ml)", "Nitrate(g/ml)", "Turbidity(NTU)",
    }
    assert set(config.SENSOR_TYPES.keys()) == expected_raw_columns
    for raw_col, meta in config.SENSOR_TYPES.items():
        assert set(meta.keys()) == {
            "label", "sensor", "bounds", "threshold_key", "absolute_thresholds_applicable", "note",
        }
        assert meta["sensor"] in {"immersed", "gas"}
        assert meta["threshold_key"] in config.THRESHOLDS


def test_get_applicable_thresholds_excludes_gas_sensors_and_undecided_turbidity() -> None:
    """D2 (reports/validations/jalon-1.md) : accès protégé — ammonia/nitrate/turbidity ne peuvent jamais en sortir."""
    applicable = config.get_applicable_thresholds()

    assert "ammonia" not in applicable
    assert "nitrate" not in applicable
    assert "turbidity" not in applicable
    assert set(applicable.keys()) == {"temperature", "ph", "dissolved_oxygen"}
    for key in applicable:
        assert applicable[key] == config.THRESHOLDS[key]


def test_get_applicable_thresholds_stays_protected_even_if_thresholds_has_numeric_values() -> None:
    """Même si THRESHOLDS contient des valeurs numériques pour ammonia/nitrate, elles ne sont jamais exposées comme applicables."""
    assert config.THRESHOLDS["ammonia"]["critical_max"] is not None
    assert config.THRESHOLDS["nitrate"]["critical_max"] is not None
    assert "ammonia" not in config.get_applicable_thresholds()
    assert "nitrate" not in config.get_applicable_thresholds()


def test_sensor_types_distinguishes_immersed_probes_from_gas_sensors_per_adr_009() -> None:
    """Température/pH/DO = sondes immergées (seuils applicables) ; ammoniac/nitrate = capteurs de gaz (non applicables)."""
    immersed = {"Temperature (C)", "PH", "Dissolved Oxygen(g/ml)"}
    gas = {"Ammonia(g/ml)", "Nitrate(g/ml)"}
    for raw_col in immersed:
        assert config.SENSOR_TYPES[raw_col]["sensor"] == "immersed"
        assert config.SENSOR_TYPES[raw_col]["absolute_thresholds_applicable"] is True
    for raw_col in gas:
        assert config.SENSOR_TYPES[raw_col]["sensor"] == "gas"
        assert config.SENSOR_TYPES[raw_col]["absolute_thresholds_applicable"] is False


def test_other_raw_columns_covers_entry_id_and_population() -> None:
    """OTHER_RAW_COLUMNS documente les colonnes brutes ni bornées ni reconstruites (D6, reports/validations/jalon-1.md)."""
    assert set(config.OTHER_RAW_COLUMNS.keys()) == {"entry_id", "Population"}
    for note in config.OTHER_RAW_COLUMNS.values():
        assert isinstance(note, str) and note


def test_growth_columns_map_raw_names_to_short_labels() -> None:
    """GROWTH_COLUMNS associe les colonnes brutes de croissance à un nom court sans unité."""
    assert config.GROWTH_COLUMNS == {
        "Fish_Weight(g)": "Fish_Weight",
        "Fish_Length(cm)": "Fish_Length",
    }


def test_rolling_window_default_is_1h_as_in_docs_03() -> None:
    """La fenêtre glissante par défaut est '1h', conforme à la signature de docs/03."""
    assert config.ROLLING_WINDOW_DEFAULT == "1h"


# --- Modèles (ml-engineer, réservé) ----------------------------------------

def test_random_state_is_fixed_integer() -> None:
    """RANDOM_STATE est un entier fixe pour la reproductibilité (conventions-code.md)."""
    assert isinstance(config.RANDOM_STATE, int)


def test_risk_classes_match_spec() -> None:
    """RISK_CLASSES reprend les 3 classes de risque de docs/02 §4.1."""
    assert config.RISK_CLASSES == ("normal", "vigilance", "critique")


def test_train_fraction_is_two_thirds() -> None:
    """TRAIN_FRACTION = 2/3, split temporel de docs/02 §4.2."""
    assert config.TRAIN_FRACTION == 2 / 3
    assert 0 < config.TRAIN_FRACTION < 1
