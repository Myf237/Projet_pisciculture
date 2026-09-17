"""Tests du Module 4 — moteur de décision (`src/decision_engine.py`).

Phase de préparation : seul le contrat d'interface (docs/03) est vérifié ;
les tests fonctionnels du Jalon 4 sont prévus et marqués `skip`, chacun
rattaché au critère qu'il devra vérifier (docs/02 §5, docs/04 — Jalon 4,
règles de l'agent automation-engineer).
"""

from __future__ import annotations

import inspect

import pytest

from src import decision_engine

# Fonctions publiques attendues et noms de paramètres (docs/03 ; format d'action
# complet : {timestamp, action, reason, triggered_by, values, threshold,
# priority, simulated} — règle n°3 automation-engineer).
EXPECTED_API = {
    "evaluate_conditions": ["reading", "risk_class", "thresholds"],
    "log_decision": ["action", "log_path"],
}


def test_public_api_matches_architecture() -> None:
    """Le module s'importe et expose les fonctions attendues, appelables, avec les paramètres de docs/03."""
    for name, expected_params in EXPECTED_API.items():
        function = getattr(decision_engine, name, None)
        assert function is not None, f"decision_engine.{name} est absente"
        assert callable(function), f"decision_engine.{name} n'est pas appelable"
        params = list(inspect.signature(function).parameters)
        assert params == expected_params, f"decision_engine.{name} : paramètres {params}"


def test_functions_raise_not_implemented_before_jalon_4() -> None:
    """Avant le Jalon 4, les deux fonctions signalent explicitement l'absence d'implémentation."""
    with pytest.raises(NotImplementedError):
        decision_engine.evaluate_conditions({}, "normal", {})
    with pytest.raises(NotImplementedError):
        decision_engine.log_decision({})


# --- Tests prévus au Jalon 4 (docs/02 §5, docs/04, règles automation-engineer) ---------


@pytest.mark.skip(reason="Jalon 4 — règle n°6 : cas limite dissolved_oxygen, juste sous le seuil critique déclenche l'aérateur")
def test_dissolved_oxygen_just_below_critical_triggers_aerator() -> None:
    """DO juste sous `critical_min` déclenche l'action simulée « aérateur ON »."""


@pytest.mark.skip(reason="Jalon 4 — règle n°6 : cas limite dissolved_oxygen, égal au seuil critique (comparaison à trancher au Jalon 4)")
def test_dissolved_oxygen_equal_to_critical_threshold() -> None:
    """DO exactement égal à `critical_min` a un comportement défini et testé (inclusif ou non)."""


@pytest.mark.skip(reason="Jalon 4 — règle n°6 : cas limite dissolved_oxygen, juste au-dessus du seuil critique ne déclenche rien")
def test_dissolved_oxygen_just_above_critical_does_not_trigger() -> None:
    """DO juste au-dessus de `critical_min` ne déclenche aucune action."""


@pytest.mark.skip(reason="Jalon 4 — docs/02 §5 : ammoniac (nettoyé) au-dessus du seuil critique déclenche le renouvellement d'eau")
def test_ammonia_above_critical_triggers_water_change() -> None:
    """Ammoniac nettoyé au-dessus de `critical_max` déclenche l'action simulée « renouvellement d'eau »."""


@pytest.mark.skip(reason="Jalon 4 — décision ouverte A3 (docs/11) : plage de température déclenchant l'alerte régulation thermique")
def test_temperature_out_of_range_triggers_thermal_alert() -> None:
    """Température hors de la plage tranchée par ADR (A3) déclenche l'action simulée « alerte régulation thermique »."""


@pytest.mark.skip(reason="Jalon 4 — docs/02 §5 : risque « critique » du modèle déclenche l'alerte prioritaire + action préventive")
def test_model_critical_risk_triggers_priority_alert() -> None:
    """`risk_class == \"critique\"` déclenche « alerte prioritaire » avec `triggered_by == \"model\"`."""


@pytest.mark.skip(reason="Jalon 4 — règle n°4 : une valeur absente ou imputée-manquante ne déclenche jamais d'action")
def test_missing_or_imputed_value_never_triggers_action() -> None:
    """Une valeur manquante ou marquée `<variable>_imputed` ne produit aucune action et l'absence est visible dans `reason`."""


@pytest.mark.skip(reason="Jalon 4 — règle n°2 : plusieurs règles déclenchées simultanément sont ordonnées par priorité explicite")
def test_multiple_triggered_actions_are_ordered_by_priority() -> None:
    """Quand plusieurs règles se déclenchent sur le même relevé, la liste retournée est triée par priorité croissante."""


@pytest.mark.skip(reason="Jalon 4 — règle n°1 : evaluate_conditions est pure et déterministe (aucune I/O, pas d'horloge système)")
def test_evaluate_conditions_is_deterministic() -> None:
    """Deux appels avec les mêmes arguments produisent exactement la même liste d'actions."""


@pytest.mark.skip(reason="Jalon 4 — règle n°7 : chaque ligne du journal JSON Lines suffit à reconstituer la décision a posteriori")
def test_log_decision_writes_complete_json_line() -> None:
    """`log_decision` ajoute une ligne JSON complète (timestamp, action, reason, triggered_by, values, threshold, priority, simulated)."""


@pytest.mark.skip(reason="Jalon 4 — règle n°9 (R5) : toute action produite est marquée simulated=True, jamais présentée comme réelle")
def test_all_actions_are_marked_simulated() -> None:
    """Chaque action retournée par `evaluate_conditions` a `simulated is True`."""
