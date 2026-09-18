"""Module 1 — Ingestion et nettoyage (docs/02 §2, docs/03 `src/ingestion.py`).

Rôle : charger le CSV brut IoT du bac de pisciculture, valider son schéma,
appliquer les règles de nettoyage non destructives (bornes physiques,
imputation par interpolation temporelle limitée) et reconstruire une courbe
de croissance propre pour `Fish_Length`/`Fish_Weight`.

Jalon de rattachement : Jalon 1 — Données nettoyées et fiables (docs/04).
Propriétaire : data-engineer (`.claude/agents/data-engineer.md`).

Aucune valeur en dur : toutes les colonnes, bornes et limites utilisées ici
viennent de `src/config.py`. Décisions appliquées : ADR-003 (ammoniac),
ADR-009 (unités mg/L, nature réelle des capteurs), ADR-010 (bornes
température/pH/oxygène dissous/nitrate, fuseau horaire, limite
d'interpolation) — `docs/07-JOURNAL_DECISIONS.md`.

Notes de conception :
- `load_raw_data` attache l'empreinte SHA-256 et le chemin du fichier source
  au DataFrame retourné via `DataFrame.attrs` (`source_path`, `source_sha256`)
  plutôt que de changer la signature de `clean_data` (fixée par docs/03) —
  c'est ce mécanisme qui permet au rapport de nettoyage de citer l'empreinte
  du fichier brut sans que `clean_data` ait besoin du chemin en paramètre.
  Un DataFrame construit autrement (ex. jeu de test synthétique) donne
  simplement `source_path`/`source_sha256` à `None` dans le rapport.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src import config

logger = logging.getLogger(__name__)


def load_raw_data(path: str) -> pd.DataFrame:
    """Charge le CSV brut, valide son schéma et parse les timestamps.

    Entrée : `path`, chemin du fichier CSV brut (paramètre, jamais en dur —
    docs/02 §1).
    Sortie : DataFrame brut avec `created_at` en datetime (suffixe timezone
    retiré, sans conversion — ADR-010), trié chronologiquement. L'empreinte
    SHA-256 et le chemin du fichier source sont attachés dans
    `DataFrame.attrs["source_sha256"]` / `["source_path"]`.
    Règles à respecter : colonnes exactement égales à `config.RAW_COLUMNS`
    (schéma validé au chargement, règle data-engineer n°1) — un écart doit
    lever une exception explicite plutôt que de continuer silencieusement.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Fichier brut introuvable : {file_path}")

    df = pd.read_csv(file_path)

    actual_columns = list(df.columns)
    if actual_columns != config.RAW_COLUMNS:
        missing = [c for c in config.RAW_COLUMNS if c not in actual_columns]
        unexpected = [c for c in actual_columns if c not in config.RAW_COLUMNS]
        raise ValueError(
            f"Schéma brut invalide pour {file_path} — colonnes attendues "
            f"(docs/01) : {config.RAW_COLUMNS!r} ; colonnes obtenues : "
            f"{actual_columns!r} ; manquantes : {missing!r} ; "
            f"inattendues : {unexpected!r}"
        )

    ts_col = config.TIMESTAMP_COLUMN
    numeric_columns = [c for c in config.RAW_COLUMNS if c != ts_col]
    non_numeric = {c: str(df[c].dtype) for c in numeric_columns if not pd.api.types.is_numeric_dtype(df[c])}
    if non_numeric:
        raise ValueError(
            f"Schéma brut invalide pour {file_path} — colonnes non numériques "
            f"alors qu'elles doivent l'être (docs/01) : {non_numeric!r}"
        )

    suffix = config.TIMESTAMP_SUFFIX
    stripped = df[ts_col].astype(str).str.replace(f"{re.escape(suffix)}$", "", regex=True)
    try:
        parsed = pd.to_datetime(stripped, errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Horodatages invalides dans la colonne '{ts_col}' de {file_path} "
            f"après retrait du suffixe {suffix!r} : {exc}"
        ) from exc
    df[ts_col] = parsed

    df = df.sort_values(ts_col, kind="mergesort").reset_index(drop=True)

    sha256 = hashlib.sha256(file_path.read_bytes()).hexdigest()
    df.attrs["source_path"] = str(file_path)
    df.attrs["source_sha256"] = sha256

    logger.info(
        "load_raw_data : %s lignes chargées depuis %s (SHA-256 %s)",
        len(df), file_path, sha256,
    )
    return df


def _gap_limited_interpolation(
    raw_series: pd.Series,
    timestamps: pd.Series,
    invalid_mask: pd.Series,
    max_gap: pd.Timedelta | None,
) -> tuple[pd.Series, pd.Series]:
    """Interpole `raw_series` aux positions `invalid_mask`, dans la limite
    temporelle `max_gap` (au-delà, la position reste manquante).

    Entrée : `raw_series` triée chronologiquement (mêmes index que
    `timestamps`/`invalid_mask`) ; `timestamps`, horodatages correspondants ;
    `invalid_mask`, positions à traiter comme manquantes (hors bornes ou déjà
    `NaN`) ; `max_gap`, durée maximale entre les deux points valides
    encadrant un trou pour l'autoriser à être interpolé (`None` = aucune
    imputation, toute position invalide reste manquante).
    Sortie : (série finale, masque des positions effectivement imputées).

    Implémentation vectorisée (règle data-engineer n°9) : interpolation
    linéaire pondérée par le temps via `numpy.interp` sur les timestamps
    convertis en nanosecondes, sans extrapolation au-delà du premier/dernier
    point valide ; la limite de trou est calculée par `ffill`/`bfill` du
    dernier et du prochain horodatage valide (pas de boucle ligne à ligne).
    """
    nulled = raw_series.where(~invalid_mask)
    valid_mask = nulled.notna()

    if max_gap is None or not invalid_mask.any() or not valid_mask.any():
        # Rien à imputer : soit aucune limite configurée (ne jamais deviner),
        # soit rien d'invalide, soit aucun point valide pour interpoler.
        return nulled, pd.Series(False, index=raw_series.index)

    valid_positions = np.flatnonzero(valid_mask.to_numpy())
    time_values = pd.Series(timestamps.to_numpy(), index=raw_series.index)
    last_valid_time = time_values.where(valid_mask.to_numpy()).ffill()
    next_valid_time = time_values.where(valid_mask.to_numpy()).bfill()
    gap = next_valid_time - last_valid_time
    fillable = gap.notna() & (gap <= max_gap)

    t_ns = timestamps.to_numpy().astype("int64").astype("float64")
    interpolated_vals = np.interp(t_ns, t_ns[valid_positions], nulled.to_numpy()[valid_positions])

    fill_values = np.where(fillable.to_numpy(), interpolated_vals, np.nan)
    final = nulled.where(~invalid_mask, pd.Series(fill_values, index=raw_series.index))
    imputed_mask = invalid_mask & fillable

    return final, imputed_mask


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Applique les règles de nettoyage (bornes physiques, imputation).

    Entrée : DataFrame brut (sortie de `load_raw_data`).
    Sortie : tuple (DataFrame nettoyé, rapport de nettoyage sous forme de
    dict — sérialisable en JSON dans `config.CLEANING_REPORT_PATH`).
    Règles à respecter : aucune ligne supprimée ; chaque valeur hors bornes
    est d'abord marquée, puis imputée par interpolation temporelle limitée à
    `config.MAX_INTERPOLATION_GAP` (au-delà, la valeur reste manquante et
    marquée) ; un seuil n'est jamais appliqué à une colonne dont l'unité ou
    la nature du capteur ne le permet pas (docs/01 anomalie 7, ADR-009,
    règle data-engineer n°3) ; le rapport retourné contient, pour les 11
    colonnes brutes, le nombre de valeurs hors bornes, imputées et restées
    manquantes (quand applicable), ainsi que l'empreinte SHA-256 du fichier
    brut, les bornes appliquées et le résultat de `rebuild_growth_curve`
    (D6, `reports/validations/jalon-1.md`).

    Schéma du DataFrame nettoyé (D9, `reports/validations/jalon-1.md` ;
    complété par la décision G1 du 2026-09-18, J-20260918-042/044) : les
    11 colonnes brutes, plus **trois** colonnes supplémentaires par variable
    bornée de `config.SENSOR_TYPES` (température, pH, oxygène dissous,
    ammoniac) — `<label>_imputed` (`True` **seulement** si la valeur
    d'origine était hors bornes ou manquante **et** a été comblée par
    interpolation), `<label>_missing` (`True` si elle est hors bornes ou
    manquante et **reste** `NaN` dans la colonne, trou trop long ou bord de
    série), et `<label>{config.RAW_VALUE_SUFFIX}` (valeur brute d'origine,
    **telle que lue, sans aucune modification** — y compris hors bornes,
    y compris `NaN` si la valeur brute l'était déjà — jamais imputée). Les
    deux drapeaux booléens ne sont jamais vrais simultanément ; ni l'un ni
    l'autre ne l'est pour une valeur d'origine valide. La colonne
    `<label>{config.RAW_VALUE_SUFFIX}` est indépendante des deux drapeaux :
    elle existe pour **toutes** les lignes (y compris les valeurs valides,
    où elle est simplement égale à la colonne nettoyée) et permet de
    retrouver une dérive de capteur (ex. plateau DO 36-41 mg/L du
    30/07-05/08, intégralement `missing` dans la colonne nettoyée faute de
    pouvoir être interpolée sur un trou aussi long) sans renoncer au
    nettoyage de la colonne principale. Nitrate et turbidité n'ont pas de
    borne absolue (ADR-009 pour le nitrate, décision ouverte pour la
    turbidité, Jalon 2) : colonnes non modifiées, sans colonne de marquage
    ni colonne `_raw` dédiée (la colonne brute est déjà, par construction,
    la seule colonne existante), seulement documentées dans le rapport pour
    rester complet par colonne (règle data-engineer n°5). `entry_id`,
    `Population`, `Fish_Length(cm)` et `Fish_Weight(g)` ne sont pas
    concernées par ce nettoyage par bornes physiques (`Population` =
    métadonnée constante, docs/01 anomalie 4 ; `Fish_Length`/`Fish_Weight`
    reconstruites par `rebuild_growth_curve`, appelée ici uniquement pour
    alimenter le rapport, sans modifier ces deux colonnes dans le DataFrame
    retourné).
    """
    ts_col = config.TIMESTAMP_COLUMN
    if ts_col not in df.columns:
        raise ValueError(f"Colonne d'horodatage '{ts_col}' absente du DataFrame passé à clean_data.")

    working = df.sort_values(ts_col, kind="mergesort").reset_index(drop=True).copy()
    n_rows = len(working)
    n_duplicate_timestamps = int(working[ts_col].duplicated().sum())
    timestamps = working[ts_col]

    max_gap = None if config.MAX_INTERPOLATION_GAP is None else pd.Timedelta(config.MAX_INTERPOLATION_GAP)

    columns_report: dict[str, dict] = {}

    for raw_col, meta in config.SENSOR_TYPES.items():
        if raw_col not in working.columns:
            continue
        label = meta["label"]
        bounds = meta["bounds"]
        raw_series = working[raw_col]
        n_missing_raw = int(raw_series.isna().sum())

        if bounds is None:
            columns_report[raw_col] = {
                "label": label,
                "sensor": meta["sensor"],
                "absolute_thresholds_applicable": meta["absolute_thresholds_applicable"],
                "bounds": None,
                "n_out_of_bounds": 0,
                "n_missing_raw": n_missing_raw,
                "n_imputed": 0,
                "n_still_missing": n_missing_raw,
                # Pas de colonne "_raw" dédiée : sans borne, la colonne brute
                # n'est jamais modifiée, elle est déjà sa propre valeur d'origine.
                "raw_value_column": None,
                "note": meta["note"],
            }
            continue

        lower = bounds.get("min")
        upper = bounds.get("max")
        out_of_bounds = pd.Series(False, index=working.index)
        if lower is not None:
            out_of_bounds |= raw_series < lower
        if upper is not None:
            out_of_bounds |= raw_series > upper
        out_of_bounds &= raw_series.notna()
        n_out_of_bounds = int(out_of_bounds.sum())

        invalid_mask = out_of_bounds | raw_series.isna()
        final_series, imputed_mask = _gap_limited_interpolation(raw_series, timestamps, invalid_mask, max_gap)
        still_missing_mask = invalid_mask & ~imputed_mask

        raw_value_column = f"{label}{config.RAW_VALUE_SUFFIX}"
        # Valeur brute conservée telle quelle (décision G1, J-20260918-042/044) :
        # copie de `raw_series` AVANT tout nettoyage, jamais recalculée à
        # partir de la colonne nettoyée — aucune imputation, aucune borne.
        working[raw_value_column] = raw_series.to_numpy()

        working[raw_col] = final_series
        working[f"{label}_imputed"] = imputed_mask.to_numpy()
        working[f"{label}_missing"] = still_missing_mask.to_numpy()

        n_imputed = int(imputed_mask.sum())
        n_still_missing = int(still_missing_mask.sum())

        columns_report[raw_col] = {
            "label": label,
            "sensor": meta["sensor"],
            "absolute_thresholds_applicable": meta["absolute_thresholds_applicable"],
            "bounds": bounds,
            "n_out_of_bounds": n_out_of_bounds,
            "n_missing_raw": n_missing_raw,
            "n_imputed": n_imputed,
            "n_still_missing": n_still_missing,
            "raw_value_column": raw_value_column,
            "note": meta["note"],
        }

        logger.info(
            "clean_data : %s — %s hors bornes, %s imputées, %s restées manquantes",
            raw_col, n_out_of_bounds, n_imputed, n_still_missing,
        )

    # Colonnes brutes restantes, non bornées : horodatage + identifiant +
    # métadonnée constante (D6, config.OTHER_RAW_COLUMNS — aucune valeur en
    # dur ici, la liste et les notes viennent de la configuration).
    columns_report[ts_col] = {
        "label": ts_col,
        "role": "timestamp",
        "n_missing_raw": 0,
        "note": (
            f"Colonne d'horodatage (config.TIMESTAMP_COLUMN) — doublons et "
            f"couverture rapportés séparément (n_duplicate_timestamps={n_duplicate_timestamps})."
        ),
    }
    for raw_col, note in config.OTHER_RAW_COLUMNS.items():
        if raw_col not in working.columns:
            continue
        columns_report[raw_col] = {
            "label": raw_col,
            "role": "metadata",
            "n_missing_raw": int(working[raw_col].isna().sum()),
            "note": note,
        }

    # Courbe de croissance : persistée dans le rapport plutôt que seulement
    # dans un `logging.warning` d'exécution (D6, reports/validations/jalon-1.md).
    # `working` n'est pas modifié par cet appel : Fish_Length/Fish_Weight
    # restent les colonnes brutes propagées, seul un résumé est extrait.
    growth_curve = rebuild_growth_curve(working)
    growth_report: dict = {"n_paliers": int(len(growth_curve)), "columns": {}}
    for raw_col, label in config.GROWTH_COLUMNS.items():
        flag_col = f"{label}_non_monotonic"
        flagged = growth_curve.loc[growth_curve[flag_col], [ts_col, raw_col]]
        growth_report["columns"][raw_col] = {
            "label": label,
            "n_missing_raw": int(working[raw_col].isna().sum()),
            "n_non_monotonic": int(growth_curve[flag_col].sum()),
            "flagged_points": [
                {"created_at": row[ts_col].isoformat(), "value": row[raw_col]}
                for _, row in flagged.iterrows()
            ],
        }
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": {
            "path": df.attrs.get("source_path"),
            "sha256": df.attrs.get("source_sha256"),
        },
        "decisions_applied": ["ADR-003", "ADR-009", "ADR-010"],
        "timestamp_suffix_removed": config.TIMESTAMP_SUFFIX.strip(),
        "timestamp_conversion": "none (ADR-010 : suffixe retiré, horodatage conservé tel quel)",
        "max_interpolation_gap": config.MAX_INTERPOLATION_GAP,
        "n_rows": n_rows,
        "n_duplicate_timestamps": n_duplicate_timestamps,
        "columns": columns_report,
        "growth_curve": growth_report,
    }

    return working, report


def rebuild_growth_curve(df: pd.DataFrame) -> pd.DataFrame:
    """Reconstruit la courbe de croissance à partir des paliers de mesure.

    Entrée : DataFrame nettoyé contenant `Fish_Length(cm)`/`Fish_Weight(g)`
    (mesures périodiques propagées sur les relevés intermédiaires, docs/01
    anomalie 5).
    Sortie : DataFrame ne conservant qu'un point par changement réel de
    valeur (colonnes `config.TIMESTAMP_COLUMN`, `Fish_Weight(g)`,
    `Fish_Length(cm)`), trié chronologiquement, enrichi de deux colonnes
    booléennes `Fish_Weight_non_monotonic` / `Fish_Length_non_monotonic`
    (`True` quand la valeur est strictement inférieure au palier précédent).
    Règles à respecter : dédupliquer les paliers (pas un point par ligne
    brute) ; toute non-monotonie de la courbe reconstruite est signalée
    (colonne dédiée + `logging.warning`), jamais corrigée silencieusement
    (règle data-engineer n°7). Les valeurs manquantes du relevé brut
    (`NaN`) ne sont jamais comptées comme un palier ni comme un changement.
    """
    ts_col = config.TIMESTAMP_COLUMN
    growth_raw_columns = list(config.GROWTH_COLUMNS.keys())
    missing_cols = [c for c in [ts_col, *growth_raw_columns] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Colonnes requises absentes pour rebuild_growth_curve : {missing_cols!r}")

    working = df[[ts_col, *growth_raw_columns]].sort_values(ts_col, kind="mergesort").reset_index(drop=True)

    def _change_point_positions(series: pd.Series) -> pd.Index:
        valid = series.notna()
        valid_series = series[valid]
        if valid_series.empty:
            return pd.Index([], dtype=working.index.dtype)
        is_change = valid_series.ne(valid_series.shift(1))
        is_change.iloc[0] = True
        return valid_series.index[is_change.to_numpy()]

    change_positions = pd.Index([], dtype=working.index.dtype)
    for raw_col in growth_raw_columns:
        change_positions = change_positions.union(_change_point_positions(working[raw_col]))

    curve = working.loc[change_positions].sort_values(ts_col, kind="mergesort").reset_index(drop=True)

    for raw_col, label in config.GROWTH_COLUMNS.items():
        flag_col = f"{label}_non_monotonic"
        diffs = curve[raw_col].diff()
        curve[flag_col] = (diffs < 0).fillna(False)
        n_flagged = int(curve[flag_col].sum())
        if n_flagged:
            flagged_points = curve.loc[curve[flag_col], [ts_col, raw_col]]
            logger.warning(
                "rebuild_growth_curve : %s non-monotonie(s) détectée(s) sur %s, "
                "signalée(s) dans '%s' sans correction : %s",
                n_flagged, raw_col, flag_col, flagged_points.to_dict("records"),
            )

    return curve


# ---------------------------------------------------------------------------
# Point d'entrée CLI de régénération des artefacts (D7,
# reports/validations/jalon-1.md) : `python -m src.ingestion [--input CSV]`.
# Régénère `config.PROCESSED_DATA_PATH` et `config.CLEANING_REPORT_PATH` à
# partir du CSV brut. Ne remplace pas le pipeline complet du Jalon 6
# (`src/main.py`, propriété de l'automation-engineer, non modifié ici) : ce
# point d'entrée ne couvre que le Module 1 (ingestion + nettoyage).
# ---------------------------------------------------------------------------


def _build_cli_parser() -> argparse.ArgumentParser:
    """Construit le parseur d'arguments de `python -m src.ingestion`."""
    parser = argparse.ArgumentParser(
        prog="python -m src.ingestion",
        description=(
            "Régénère data/processed/pond1_clean.csv et "
            "reports/cleaning_report.json à partir du CSV brut (Module 1, "
            "Jalon 1 — docs/02 §2)."
        ),
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        default=str(config.RAW_DATA_PATH),
        help="Chemin du CSV brut en entrée (défaut : config.RAW_DATA_PATH, jamais une valeur en dur — docs/02 §1).",
    )
    return parser


def regenerate_processed_artifacts(argv: list[str] | None = None) -> int:
    """Charge, nettoie et écrit les deux livrables du nettoyage sur disque.

    Entrée : `argv`, arguments de ligne de commande (`--input`, par défaut
    `sys.argv[1:]` via `argparse`, ou liste explicite pour les tests).
    Sortie : code de sortie (0 = succès ; non nul = échec, avec message clair
    sur `sys.stderr` plutôt qu'une trace d'exception brute — même convention
    que `src/main.py`).
    Effets de bord (seule fonction du module à en avoir) : écrit
    `config.PROCESSED_DATA_PATH` (CSV) et `config.CLEANING_REPORT_PATH`
    (JSON), en créant les dossiers parents si besoin.
    """
    args = _build_cli_parser().parse_args(argv)
    try:
        raw = load_raw_data(args.input_path)
        cleaned, report = clean_data(raw)

        config.PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(config.PROCESSED_DATA_PATH, index=False)

        config.CLEANING_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with config.CLEANING_REPORT_PATH.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
    except Exception as exc:  # échec explicite, message clair (conventions-code.md)
        print(f"Erreur : régénération du nettoyage échouée — {exc}", file=sys.stderr)
        return 1

    print(
        f"OK : {len(cleaned)} lignes écrites dans {config.PROCESSED_DATA_PATH} ; "
        f"rapport écrit dans {config.CLEANING_REPORT_PATH}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(regenerate_processed_artifacts())
