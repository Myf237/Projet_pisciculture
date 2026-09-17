"""Tests du dashboard (`dashboard/app.py`) — Module 5, Jalon 5.

Squelette de préparation : seul le test de fumée est actif. Les autres tests
listés ci-dessous sont désactivés (`skip`) jusqu'à l'implémentation réelle du
Jalon 5 (`docs/04-JALONS_VALIDATION.md`), chacun rattaché au critère qu'il
devra vérifier.
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest

# Chemin construit depuis l'emplacement de ce fichier de test : AppTest.from_file()
# résout les chemins relatifs par rapport au fichier appelant, pas à la racine du
# dépôt ni au répertoire courant de pytest.
APP_PATH = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"

# Texte exigé par R5, écrit littéralement (et non importé de `dashboard.app`) pour
# que le test échoue réellement si la formulation du bandeau est modifiée ou vidée
# dans l'application.
REQUIRED_ACTUATOR_BANNER = "Actionneurs simulés — aucun matériel connecté"


def test_app_runs_without_exception() -> None:
    """L'application se lance sans exception et affiche le bandeau obligatoire (R5)."""
    at = AppTest.from_file(str(APP_PATH))
    at.run()

    assert not at.exception

    body = "\n".join(block.value for block in at.warning)
    assert REQUIRED_ACTUATOR_BANNER in body


@pytest.mark.skip(reason="Jalon 5 — le mode rejeu permet de dérouler pas à pas un scénario de démonstration (docs/04)")
def test_replay_step_by_step() -> None:
    """Le mode rejeu avance d'un pas sans bloquer et sans dépasser les bornes de la fenêtre de démo."""


@pytest.mark.skip(reason="Jalon 5 — l'état du bac est visible et compréhensible sans explication supplémentaire (docs/04)")
def test_pond_state_shown_as_text_and_color() -> None:
    """L'état du bac (normal/vigilance/critique) est affiché à la fois en texte et en couleur."""


@pytest.mark.skip(reason="Jalon 5 — les actions déclenchées sont visibles et compréhensibles sans explication supplémentaire (docs/04)")
def test_action_log_has_time_reason_source() -> None:
    """La liste des actions affiche pour chacune l'heure, la raison et la source (règle ou modèle)."""


@pytest.mark.skip(reason="Jalon 5 — le mode rejeu déroule un scénario de démonstration contenant une anomalie (docs/04)")
def test_demo_window_is_deterministic_and_contains_known_anomaly() -> None:
    """La fenêtre de démo définie dans `src/config.py` est fixe et contient l'anomalie du Jalon 2."""


@pytest.mark.skip(reason="Jalon 5 — le dashboard se lance sans erreur avec une seule commande, sans entraînement (docs/04)")
def test_app_loads_processed_artifacts_without_training() -> None:
    """L'application charge des données traitées et un modèle déjà produits, sans jamais entraîner."""
