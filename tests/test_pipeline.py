"""Tests du pipeline (`src/main.py`) — Jalon 6 (docs/03, docs/04).

Phase de préparation : `python src/main.py` doit déjà être exécutable en
tant que tel (parsing des arguments, `--help`, message d'erreur propre) même
si le pipeline n'est pas encore implémenté. Le test d'intégration réel
(petit CSV synthétique, sorties reproductibles) est prévu au Jalon 6 et
marqué `skip` ci-dessous (règles n°10-13 automation-engineer).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import src.main as main_module
from src.main import build_parser, main

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_help_exits_with_code_zero() -> None:
    """`main(["--help"])` doit réussir (code 0) sans que le pipeline soit implémenté."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0


def test_run_without_implementation_returns_nonzero_with_clear_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Sans implémentation, `main([])` retourne un code non nul et un message explicite (règle n°11)."""
    exit_code = main([])
    captured = capsys.readouterr()
    assert exit_code != 0
    assert "Jalon 6" in captured.err
    assert "non implémenté" in captured.err


def test_default_input_path_matches_config() -> None:
    """Le défaut de `--input` est exactement `config.RAW_DATA_PATH`, sans valeur devinée (correction D3)."""
    from src.config import RAW_DATA_PATH

    args = build_parser().parse_args([])
    assert args.input_path == str(RAW_DATA_PATH)


def test_default_input_path_raises_if_config_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Si `src.config` est introuvable, l'erreur remonte clairement plutôt que de deviner un chemin (correction D3)."""
    monkeypatch.setitem(sys.modules, "src.config", None)
    with pytest.raises(ImportError):
        main_module._default_input_path()


def test_script_invocation_from_project_root_help_succeeds() -> None:
    """`python src/main.py --help`, lancé depuis la racine, fonctionne (import `src.*` malgré `sys.path`, règle n°10)."""
    result = subprocess.run(
        [sys.executable, "src/main.py", "--help"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_script_invocation_without_implementation_returns_nonzero() -> None:
    """`python src/main.py`, lancé depuis la racine sans implémentation, retourne un code non nul et un message clair."""
    result = subprocess.run(
        [sys.executable, "src/main.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "non implémenté" in result.stderr


# --- Test d'intégration prévu au Jalon 6 (docs/04, règles n°10-13 automation-engineer) --


@pytest.mark.skip(
    reason=(
        "Jalon 6 — pipeline complet sur un petit CSV synthétique au schéma réel "
        "(ingestion -> features -> modèle -> décisions), sorties identiques sur "
        "deux exécutions (docs/04 — Jalon 6, règles n°10-13 automation-engineer)"
    )
)
def test_pipeline_end_to_end_on_synthetic_csv_is_reproducible() -> None:
    """Deux exécutions du pipeline sur le même CSV synthétique produisent des sorties de même empreinte."""
