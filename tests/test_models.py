"""Tests du Module 3 — modèles IA (src/models/).

Phase de préparation : seul le contrat d'interface (docs/03) est vérifié ; les tests
fonctionnels sont prévus et marqués ``skip`` jusqu'au Jalon 3.
"""

from __future__ import annotations

import inspect

import pytest

from src.models import anomaly_detection, growth_prediction

# Fonctions publiques attendues et noms de paramètres (docs/03 ; baseline : règle n° 1 ml-engineer).
EXPECTED_API = {
    anomaly_detection: {
        "inject_synthetic_anomalies": ["df", "thresholds"],
        "predict_threshold_baseline": ["df", "thresholds"],
        "train_anomaly_model": ["df"],
        "predict_risk": ["model", "df"],
        "evaluate_model": ["model", "X_test", "y_test"],
    },
    growth_prediction: {
        "train_growth_model": ["df"],
        "evaluate_growth_model": ["model", "X_test", "y_test"],
    },
}


def test_public_api_matches_architecture() -> None:
    """Les modules s'importent et exposent les fonctions attendues, appelables, avec les paramètres de docs/03."""
    for module, functions in EXPECTED_API.items():
        for name, expected_params in functions.items():
            function = getattr(module, name, None)
            assert function is not None, f"{module.__name__}.{name} est absente"
            assert callable(function), f"{module.__name__}.{name} n'est pas appelable"
            params = list(inspect.signature(function).parameters)
            assert params == expected_params, f"{module.__name__}.{name} : paramètres {params}"


# --- Tests prévus au Jalon 3 ---------------------------------------------------------


@pytest.mark.skip(reason="Jalon 3 — règle n° 3 ml-engineer : split temporel strict, jamais de mélange")
def test_temporal_split_has_no_shuffling() -> None:
    """Toutes les dates d'entraînement précèdent toutes les dates de test, dans l'ordre chronologique."""


@pytest.mark.skip(reason="Jalon 3 — règle n° 3 ml-engineer : écart train/test ≥ plus longue fenêtre glissante")
def test_temporal_split_leaves_gap_between_train_and_test() -> None:
    """L'écart entre la dernière date d'entraînement et la première date de test couvre la plus longue fenêtre glissante."""


@pytest.mark.skip(reason="Jalon 3 — règle n° 5 ml-engineer : reproductibilité à graine fixe (RANDOM_STATE)")
def test_training_is_deterministic_with_fixed_seed() -> None:
    """Deux entraînements avec la même graine produisent des prédictions et des métriques identiques."""


@pytest.mark.skip(reason="Jalon 3 — docs/02 §4.1 et règle n° 13 ml-engineer : score + classe normal/vigilance/critique")
def test_predict_risk_returns_valid_classes() -> None:
    """predict_risk renvoie une ligne par relevé, un score et une classe parmi normal, vigilance, critique."""


@pytest.mark.skip(reason="Jalon 3 — docs/04 critère 1 : rappel de la classe critique, cible à fixer par ADR (A4)")
def test_critical_recall_meets_adr_target() -> None:
    """Le rappel de la classe critique sur les anomalies injectées atteint la cible fixée par ADR."""


@pytest.mark.skip(reason="Jalon 3 — règles n° 1-2 ml-engineer et R9 : comparaison à la baseline « seuils seuls »")
def test_evaluation_reports_baseline_alongside_model() -> None:
    """L'évaluation publie les métriques de la baseline à côté de celles du modèle, globalement et par type d'anomalie."""


@pytest.mark.skip(reason="Jalon 3 — docs/04 critère 2 : alerte cohérente sur un passage réel avec dérive visible")
def test_real_drift_episode_triggers_coherent_alert() -> None:
    """L'épisode réel de dérive identifié au Jalon 2 produit une alerte de niveau cohérent."""


@pytest.mark.skip(reason="Jalon 3 — docs/04 critère 3 et règle n° 9 ml-engineer : importance par permutation sur le test")
def test_feature_importances_are_reported() -> None:
    """Les importances par permutation calculées sur le test sont produites pour chaque feature du modèle."""


@pytest.mark.skip(reason="Jalon 3 — règle n° 10 ml-engineer : fiche modèle traçable")
def test_model_card_is_complete() -> None:
    """La fiche JSON contient date, SHA-256 des données, features, paramètres, graine, métriques du modèle et de la baseline."""


@pytest.mark.skip(reason="Jalon 3 (priorité 2) — docs/02 §4.2 et règle n° 11 ml-engineer : approche à trancher (A5)")
def test_growth_model_is_compared_to_naive_baseline() -> None:
    """L'évaluation de croissance publie MAE et RMSE du modèle et d'une baseline naïve sur le même split temporel."""
