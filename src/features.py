"""Module 2 — Exploration et feature engineering (docs/02 §3, docs/03 `src/features.py`).

Rôle : enrichir les données nettoyées (sortie de `src/ingestion.py`) de
features dérivées causales (fenêtres glissantes tournées vers le passé,
écarts aux seuils, taux de croissance) et produire une agrégation horaire
pour réduire le bruit avant modélisation.

Jalon de rattachement : Jalon 2 — Exploration validée (docs/04).
Propriétaire : data-engineer (`.claude/agents/data-engineer.md`).

Toutes les fenêtres et seuils utilisés ici viennent de `src/config.py`
(`ROLLING_WINDOW_DEFAULT`, `THRESHOLDS`, `RESAMPLING_FREQUENCY`) — aucune
valeur en dur. `RESAMPLING_FREQUENCY` est encore `None` (décision ouverte,
docs/11) : ne pas appliquer de ré-échantillonnage tant qu'elle n'est pas
tranchée.
"""

from __future__ import annotations

import pandas as pd

from src import config


def add_rolling_features(df: pd.DataFrame, window: str = config.ROLLING_WINDOW_DEFAULT) -> pd.DataFrame:
    """Ajoute moyennes/écarts-types glissants par variable de qualité d'eau.

    Entrée : DataFrame nettoyé et trié chronologiquement ; `window`, fenêtre
    temporelle (par défaut `config.ROLLING_WINDOW_DEFAULT`).
    Sortie : DataFrame enrichi de colonnes `<variable>_rolling_mean` /
    `<variable>_rolling_std`.
    Règles à respecter : fenêtre **causale uniquement** (tournée vers le
    passé, jamais `center=True`), pour rester valide en rejeu temps réel et
    éviter toute fuite d'information vers les modèles (règle data-engineer
    n°8) ; implémentation vectorisée (pandas/numpy), pas de boucle ligne à
    ligne sur les ~83 000 relevés (règle data-engineer n°9).
    """
    raise NotImplementedError(
        "Jalon 2 — moyennes/écarts-types glissants causaux par variable de "
        "qualité d'eau (docs/02 §3, docs/03)"
    )


def add_threshold_distance(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Ajoute une variable d'écart signé au seuil critique, par paramètre.

    Entrée : DataFrame nettoyé, dont les colonnes de qualité d'eau portent le
    nom des clés de `thresholds` (ex. `temperature`, `ph` — la correspondance
    avec les noms bruts de `config.RAW_COLUMNS` est assurée en amont, ce
    n'est pas la responsabilité de cette fonction) ; `thresholds`, dict de
    seuils (typiquement `config.THRESHOLDS`).
    Sortie : DataFrame enrichi d'une colonne `<clé>_distance_critical` par
    paramètre dont le seuil critique est exploitable (voir ci-dessous).

    Convention de signe, d'unité et de nommage (lève l'ambiguïté de la
    réserve R6, `reports/validations/preparation-mise-en-place.md`) :
    - **Unité** : identique à la colonne d'entrée, sans conversion — la
      distance est une simple différence entre deux valeurs de même unité,
      jamais un pourcentage ni une valeur normalisée.
    - **Signe** : **positif** = marge de sécurité restante avant d'atteindre
      le seuil critique (valeur encore dans la zone critique/acceptable) ;
      **négatif** = seuil critique déjà dépassé, la valeur absolue donnant
      l'ampleur du dépassement (valeur hors de la zone critique) ; **zéro** =
      valeur exactement égale au seuil critique.
    - **Paramètre à borne critique unique inférieure** (seul `critical_min`
      défini, ex. `dissolved_oxygen`) : `distance = valeur - critical_min`.
    - **Paramètre à borne critique unique supérieure** (seul `critical_max`
      défini, ex. `ammonia`, `nitrate`) : `distance = critical_max - valeur`.
    - **Paramètre à double borne critique** (`critical_min` et
      `critical_max` définis, ex. `temperature`, `ph`) : distance signée à la
      borne critique la plus proche — si `critical_min <= valeur <=
      critical_max`, `distance = min(valeur - critical_min, critical_max -
      valeur)` (>= 0) ; si `valeur < critical_min`, `distance = valeur -
      critical_min` (< 0) ; si `valeur > critical_max`, `distance =
      critical_max - valeur` (< 0).
    - **Seuil non exploitable → colonne non produite** (pas de valeur
      devinée) : si `critical_min` et `critical_max` valent tous deux `None`
      dans `thresholds` (ex. `turbidity`, décision ouverte, docs/11) **ou**
      si le paramètre est `dissolved_oxygen`, `ammonia` ou `nitrate` tant que
      son unité n'est pas tranchée (décision A1 — `config.DISSOLVED_OXYGEN_BOUNDS`,
      `config.AMMONIA_BOUNDS`, `config.NITRATE_BOUNDS` encore `None` alors
      même que `THRESHOLDS` contient des valeurs numériques héritées de
      `docs/03`), alors `<clé>_distance_critical` n'est **pas** calculée pour
      ce paramètre (règle data-engineer n°3 : ne jamais appliquer un seuil à
      une colonne dont l'unité n'est pas tranchée), plutôt que de retourner
      une colonne à `NaN` ou une valeur non fiable.
    - **Nommage** : `<clé>_distance_critical`, où `<clé>` est la clé du
      paramètre dans `thresholds` (ex. `temperature_distance_critical`,
      `ph_distance_critical`), jamais le nom de colonne brut.

    Règles à respecter : ne jamais appliquer un seuil à une colonne dont
    l'unité/la borne n'est pas tranchée (règle data-engineer n°3) ;
    implémentation vectorisée (pandas/numpy), pas de boucle ligne à ligne
    (règle data-engineer n°9).
    """
    raise NotImplementedError(
        "Jalon 2 — distance signée aux seuils critiques par paramètre de "
        "qualité d'eau, seuils/unités non tranchés exclus (docs/02 §3, "
        "docs/03, réserve R6)"
    )


def compute_growth_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le taux de croissance instantané entre deux mesures de poids.

    Entrée : DataFrame issu de `ingestion.rebuild_growth_curve` (un point par
    changement réel de `Fish_Weight`).
    Sortie : DataFrame enrichi d'une colonne de taux de croissance (delta de
    poids / delta de temps entre deux points de mesure consécutifs).
    Règles à respecter : causal (n'utilise que des mesures passées ou
    courantes) ; toute non-monotonie héritée de la courbe de croissance est
    conservée telle quelle, jamais corrigée silencieusement (règle
    data-engineer n°7).
    """
    raise NotImplementedError(
        "Jalon 2 — taux de croissance instantané entre mesures de poids "
        "(docs/02 §3, docs/03)"
    )


def resample_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Agrège les données à la fréquence horaire pour réduire le bruit.

    Entrée : DataFrame nettoyé (et éventuellement enrichi de features),
    indexé ou triable par timestamp.
    Sortie : DataFrame ré-échantillonné à la fréquence horaire (agrégation
    causale, ex. moyenne sur l'heure écoulée).
    Règles à respecter : fréquence de référence = `config.RESAMPLING_FREQUENCY`
    une fois cette décision ouverte tranchée (docs/11) ; pas d'anticipation
    de valeurs futures ; vectorisé.
    """
    raise NotImplementedError(
        "Jalon 2 — agrégation horaire causale des données de qualité d'eau "
        "(docs/02 §3, docs/03)"
    )
