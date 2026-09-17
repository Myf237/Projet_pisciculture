"""Tests du module de features (`src/features.py`) — Module 2, Jalon 2.

Squelette de préparation : seul le test de fumée est actif. Les autres tests
listés ci-dessous sont désactivés (`skip`) jusqu'à l'implémentation réelle
du feature engineering (`docs/04-JALONS_VALIDATION.md`), chacun rattaché au
critère ou à la règle qu'il devra vérifier.
"""

from __future__ import annotations

import pytest

pytest.importorskip("pandas")

from src import features


def test_module_exposes_expected_callable_functions() -> None:
    """Le module expose les 4 fonctions de feature engineering, appelables et documentées."""
    for name in ("add_rolling_features", "add_threshold_distance", "compute_growth_rate", "resample_hourly"):
        func = getattr(features, name, None)
        assert callable(func), f"{name} doit être une fonction appelable"
        assert func.__doc__, f"{name} doit avoir une docstring (entrée -> sortie)"


@pytest.mark.skip(reason="Jalon 2 — les fenêtres glissantes sont causales : aucune information future n'entre dans la valeur au temps t (règle data-engineer n°8, docs/02 §3)")
def test_add_rolling_features_uses_only_past_information() -> None:
    """add_rolling_features ne doit jamais utiliser center=True ; la valeur à t ne dépend que de t et d'avant."""


@pytest.mark.skip(reason="Jalon 2 — distance signée au seuil critique : positif = marge de sécurité, négatif = dépassement ; colonne absente si le seuil ou l'unité (A1) n'est pas tranché (docs/02 §3, docs/03, réserve R6)")
def test_add_threshold_distance_computes_signed_gap_per_parameter() -> None:
    """add_threshold_distance ajoute `<clé>_distance_critical` (positif dans la zone critique, négatif au-delà) et omet les paramètres à seuil/unité non tranchés."""


@pytest.mark.skip(reason="Jalon 2 — taux de croissance instantané entre deux mesures de poids consécutives (docs/02 §3, docs/03)")
def test_compute_growth_rate_between_consecutive_weight_measurements() -> None:
    """compute_growth_rate calcule delta_poids / delta_temps entre deux points de la courbe de croissance reconstruite."""


@pytest.mark.skip(reason="Jalon 2 — agrégation horaire causale, réduit bruit et volume avant modélisation (docs/02 §3, docs/03)")
def test_resample_hourly_aggregates_without_looking_ahead() -> None:
    """resample_hourly agrège les relevés par heure écoulée sans utiliser de données futures à l'intérieur du pas."""
