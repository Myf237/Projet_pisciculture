"""Tests du module d'ingestion (`src/ingestion.py`) — Module 1, Jalon 1.

Squelette de préparation : seul le test de fumée est actif. Les autres tests
listés ci-dessous sont désactivés (`skip`) jusqu'à l'implémentation réelle
des règles de nettoyage (`docs/04-JALONS_VALIDATION.md`), chacun rattaché au
critère ou à la règle qu'il devra vérifier.
"""

from __future__ import annotations

import pytest

pytest.importorskip("pandas")

from src import ingestion


def test_module_exposes_expected_callable_functions() -> None:
    """Le module expose load_raw_data, clean_data et rebuild_growth_curve, appelables et documentées."""
    for name in ("load_raw_data", "clean_data", "rebuild_growth_curve"):
        func = getattr(ingestion, name, None)
        assert callable(func), f"{name} doit être une fonction appelable"
        assert func.__doc__, f"{name} doit avoir une docstring (entrée -> sortie)"


@pytest.mark.skip(reason="Jalon 1 — un schéma brut invalide (colonne manquante/renommée) lève une exception explicite (docs/02 §2, règle data-engineer n°1)")
def test_load_raw_data_raises_on_invalid_schema() -> None:
    """load_raw_data lève une exception claire si les colonnes ne correspondent pas à config.RAW_COLUMNS."""


@pytest.mark.skip(reason="Jalon 1 — aucune valeur de température/pH hors bornes après nettoyage, cas limites aux bornes incluses (docs/04, docs/01 anomalies 1-2)")
def test_clean_data_enforces_temperature_and_ph_bounds_at_edges() -> None:
    """Les valeurs égales aux bornes (0/40 °C, 0/14 pH) sont conservées ; hors bornes, marquées et imputées/manquantes."""


@pytest.mark.skip(reason="Jalon 1 — valeur -127 °C (artefact capteur DS18B20 déconnecté) marquée hors borne, jamais laissée telle quelle (docs/01 anomalie 1)")
def test_clean_data_flags_minus_127_temperature_as_out_of_bounds() -> None:
    """Une valeur -127 en température est marquée dans Temperature_imputed et traitée comme hors bornes."""


@pytest.mark.skip(reason="Jalon 1 — nettoyage non destructif : le nombre de lignes ne change jamais (docs/02 §2, règle data-engineer n°4)")
def test_clean_data_never_drops_rows() -> None:
    """clean_data conserve le même nombre de lignes en entrée et en sortie, quelles que soient les valeurs hors bornes."""


@pytest.mark.skip(reason="Jalon 1 — un trou plus long que config.MAX_INTERPOLATION_GAP reste manquant et marqué, jamais interpolé (règle data-engineer n°4)")
def test_clean_data_does_not_interpolate_beyond_max_gap() -> None:
    """Un trou de mesures plus long que la limite configurée n'est pas comblé et reste marqué manquant."""


@pytest.mark.skip(reason="Jalon 1 — le rapport de nettoyage contient, par colonne, hors-bornes/imputées/manquantes + SHA-256 du brut + bornes appliquées (docs/02 §2, règle data-engineer n°5)")
def test_clean_data_report_is_complete_per_column() -> None:
    """Le rapport retourné par clean_data contient les comptages et métadonnées attendus pour chaque colonne nettoyée."""


@pytest.mark.skip(reason="Jalon 1 — la courbe de croissance reconstruite est monotone croissante ou quasi, toute non-monotonie signalée jamais corrigée silencieusement (docs/04, règle data-engineer n°7)")
def test_rebuild_growth_curve_is_monotonic_or_flags_non_monotonic_points() -> None:
    """rebuild_growth_curve ne garde qu'un point par changement réel de valeur et signale toute non-monotonie."""
