"""Prédiction de croissance (``Fish_Weight``) — Module 3, priorité 2, Jalon 3 (docs/02 §4.2, docs/03).

Rôle : prédire le poids des poissons à partir des variables de qualité d'eau agrégées et
du temps écoulé depuis l'empoissonnement.

Principes imposés par la définition de l'agent ml-engineer (ADR-002, risque R11) :

- Priorité 2 : travail arrêté immédiatement si la règle du Jour 4 est déclenchée (G3).
- Approche à trancher par ADR (constat A5) : une courbe croissante courte ne s'extrapole
  pas avec un Random Forest (il ne prédit pas au-delà du maximum vu à l'entraînement).
- Baseline d'abord : toute approche retenue est comparée à une baseline naïve ; ses
  métriques sont publiées à côté de celles du modèle.
- Split temporel strict : entraînement sur les 2/3 premiers du cycle, test sur le dernier
  tiers ; jamais de mélange aléatoire.
- Aucune fuite : toute transformation est ajustée sur l'entraînement uniquement.
- Métriques : MAE et RMSE sur le dernier tiers du cycle.
- Explicabilité : chaque prédiction doit pouvoir être justifiée (docs/02 §7).
- Reproductibilité : ``RANDOM_STATE`` de ``src/config.py`` passé à tout composant aléatoire.

État : squelette de la phase de préparation — aucune logique implémentée.
"""

from __future__ import annotations

import pandas as pd


def train_growth_model(df: pd.DataFrame) -> object:
    """Entraîne un modèle de régression pour prédire Fish_Weight.

    Entrée : partie entraînement du split temporel de la courbe de croissance reconstruite.
    Sortie : modèle ajusté.
    """
    raise NotImplementedError(
        "Jalon 3 (priorité 2) — modèle de croissance sur split temporel, approche "
        "à trancher par ADR (A5) (docs/02 §4.2)"
    )


def evaluate_growth_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Retourne MAE/RMSE sur split temporel.

    Entrée : modèle ajusté, dernier tiers du cycle. Sortie : MAE et RMSE, à publier à côté
    de la baseline naïve.
    """
    raise NotImplementedError(
        "Jalon 3 (priorité 2) — MAE/RMSE sur le dernier tiers du cycle, comparés à une "
        "baseline naïve (docs/02 §4.2)"
    )
