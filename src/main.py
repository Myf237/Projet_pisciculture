"""Point d'entrée unique du pipeline (Jalon 6, docs/03 `src/main.py`).

Rôle : enchaîner ingestion -> features -> modèle (entraînement ou chargement)
-> décisions simulées, en une seule commande (`docs/02` §7 — un seul point
d'entrée pour rejouer tout le pipeline ; `docs/04`, Jalon 6).

Jalon de rattachement : Jalon 6 — MVP intégré et démontrable (docs/04).
Propriétaire : automation-engineer (`.claude/agents/automation-engineer.md`).

Note d'import (règle n°10 automation-engineer) : lorsque ce fichier est lancé
directement avec `python src/main.py`, Python place le dossier `src/` (et non
la racine du projet) en tête de `sys.path` — `import src...` échouerait alors
que la racine, elle, est bien sur `sys.path` quand on lance `python -m
src.main` ou les tests (`pytest.ini`, `pythonpath = .`). On insère donc la
racine du projet dans `sys.path` avant tout import du paquet `src`, mais
uniquement quand ce fichier est exécuté comme script (`__package__` vide) —
jamais quand il est importé normalement (`from src.main import main`).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger(__name__)


def _default_input_path() -> str:
    """Retourne le chemin brut par défaut : `config.RAW_DATA_PATH`.

    Import différé (à l'intérieur de la fonction, pas en tête de module) :
    voir la note d'import du module. Aucune valeur de repli codée en dur —
    `.claude/rules/conventions-code.md` (« aucune valeur en dur », « chemins
    construits depuis la racine ») : si `src/config.py` est introuvable ou
    invalide, l'`ImportError` remonte telle quelle plutôt que de deviner un
    chemin (correction D3, qa-validator, `reports/validations/preparation-mise-en-place.md`).
    """
    from src.config import RAW_DATA_PATH  # import différé, voir docstring du module

    return str(RAW_DATA_PATH)


def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur d'arguments du pipeline (option `--input`, docs/03)."""
    parser = argparse.ArgumentParser(
        prog="src/main.py",
        description=(
            "Pipeline Pisciculture IA : ingestion -> features -> modèle -> "
            "décisions simulées (docs/02 §7-8, docs/04 — Jalon 6)."
        ),
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        default=_default_input_path(),
        help=(
            "Chemin du CSV brut en entrée du pipeline "
            "(défaut : chemin configuré dans src/config.py, RAW_DATA_PATH)."
        ),
    )
    return parser


def run_pipeline(input_path: str) -> int:
    """Enchaîne les étapes du pipeline et retourne un code de sortie.

    Étapes prévues (règle n°10-12 automation-engineer, docs/02 §7-8) :
    ingestion (`src/ingestion.py`) -> features (`src/features.py`) -> modèle
    (entraînement ou chargement, `src/models/`) -> décisions
    (`src/decision_engine.py`). Chaque étape doit être journalisée via
    `logging` (début, fin, durée, volumes), réexécutable sans effet de bord,
    et le pipeline doit être reproductible (mêmes sorties à empreinte égale
    sur deux exécutions).

    Non implémenté avant le Jalon 6 (docs/04 — Jalon 6).
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logger.info("Pipeline démarré (squelette) — entrée : %s", input_path)
    for step in ("ingestion", "features", "modèle", "décisions"):
        logger.info("Étape prévue (non implémentée) : %s", step)
    raise NotImplementedError(
        "Jalon 6 — pipeline non implémenté (docs/04 — Jalon 6 ; docs/02 §7-8 ; "
        "docs/03 src/main.py)"
    )


def main(argv: list[str] | None = None) -> int:
    """Point d'entrée unique du pipeline (`python src/main.py [--input <csv>]`).

    Entrée : `argv`, arguments de ligne de commande (par défaut `sys.argv[1:]`
    via `argparse`, ou liste explicite pour les tests/appels programmatiques).
    Sortie : code de sortie du processus (0 = succès ; non nul = échec, avec
    message d'erreur clair sur `stderr`, sans trace d'exception brute).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run_pipeline(args.input_path)
    except NotImplementedError as exc:
        print(f"Erreur : pipeline non implémenté (Jalon 6) — {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - garde-fou générique (règle n°11)
        print(f"Erreur : échec du pipeline — {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
