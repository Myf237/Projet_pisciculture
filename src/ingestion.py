"""Module 1 — Ingestion et nettoyage (docs/02 §2, docs/03 `src/ingestion.py`).

Rôle : charger le CSV brut IoT du bac de pisciculture, valider son schéma,
appliquer les règles de nettoyage non destructives (bornes physiques,
imputation par interpolation temporelle limitée) et reconstruire une courbe
de croissance propre pour `Fish_Length`/`Fish_Weight`.

Jalon de rattachement : Jalon 1 — Données nettoyées et fiables (docs/04).
Propriétaire : data-engineer (`.claude/agents/data-engineer.md`).

Aucune valeur en dur : toutes les colonnes, bornes et limites utilisées ici
viennent de `src/config.py`. Toute borne encore à `None` dans `config.py`
correspond à une décision ouverte (`docs/11-TABLEAU_DE_BORD.md`) : ne pas
appliquer de seuil tant qu'elle n'est pas tranchée par ADR.
"""

from __future__ import annotations

import pandas as pd


def load_raw_data(path: str) -> pd.DataFrame:
    """Charge le CSV brut, valide son schéma et parse les timestamps.

    Entrée : `path`, chemin du fichier CSV brut (paramètre, jamais en dur —
    docs/02 §1).
    Sortie : DataFrame brut avec `created_at` en datetime (suffixe timezone
    retiré, trié chronologiquement).
    Règles à respecter : colonnes exactement égales à `config.RAW_COLUMNS`
    (schéma validé au chargement, règle data-engineer n°1) — un écart doit
    lever une exception explicite plutôt que de continuer silencieusement.
    """
    raise NotImplementedError(
        "Jalon 1 — chargement + validation du schéma brut et parsing des "
        "timestamps (docs/02 §2, docs/01)"
    )


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Applique les règles de nettoyage (bornes physiques, imputation).

    Entrée : DataFrame brut (sortie de `load_raw_data`).
    Sortie : tuple (DataFrame nettoyé, rapport de nettoyage sous forme de
    dict — sérialisable en JSON dans `config.CLEANING_REPORT_PATH`).
    Règles à respecter : aucune ligne supprimée ; chaque valeur hors bornes
    est d'abord marquée dans une colonne booléenne `<variable>_imputed`, puis
    imputée par interpolation temporelle limitée à `config.MAX_INTERPOLATION_GAP`
    (au-delà, la valeur reste manquante et marquée) ; un seuil n'est jamais
    appliqué à une colonne dont l'unité n'est pas tranchée (docs/01 anomalie 7,
    règle data-engineer n°3) ; le rapport retourné contient, par colonne, le
    nombre de valeurs hors bornes, imputées et restées manquantes, ainsi que
    l'empreinte SHA-256 du fichier brut et les bornes appliquées.
    """
    raise NotImplementedError(
        "Jalon 1 — nettoyage non destructif par bornes physiques et "
        "imputation limitée + rapport de nettoyage (docs/02 §2, docs/01 "
        "anomalies 1-3 et 7-9)"
    )


def rebuild_growth_curve(df: pd.DataFrame) -> pd.DataFrame:
    """Reconstruit la courbe de croissance à partir des paliers de mesure.

    Entrée : DataFrame nettoyé contenant `Fish_Length(cm)`/`Fish_Weight(g)`
    (mesures périodiques propagées sur les relevés intermédiaires, docs/01
    anomalie 5).
    Sortie : DataFrame ne conservant qu'un point par changement réel de
    valeur, avec son timestamp.
    Règles à respecter : dédupliquer les paliers (pas un point par ligne
    brute) ; toute non-monotonie de la courbe reconstruite est signalée
    (ex. colonne ou log dédié), jamais corrigée silencieusement (règle
    data-engineer n°7).
    """
    raise NotImplementedError(
        "Jalon 1 — reconstruction de la courbe de croissance par "
        "déduplication des paliers de mesure (docs/02 §2, docs/01 anomalie 5)"
    )
