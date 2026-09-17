"""Détection de risque qualité d'eau — Module 3, Jalon 3 (docs/02 §4.1, docs/03).

Rôle : produire, pour chaque relevé, un score de risque et une classe
(normal / vigilance / critique), consommés par le moteur de décision et le dashboard.

Principes imposés par la définition de l'agent ml-engineer (ADR-002, risque R9) :

- Baseline d'abord : ``predict_threshold_baseline`` (règles de seuils seules) est évaluée
  avant tout modèle ; chaque métrique du modèle est publiée à côté de la sienne.
- Circularité : des labels dérivés des seuils font réapprendre les seuils. Les anomalies
  injectées doivent aussi couvrir des cas mal détectés par des seuils fixes, et leur type
  est conservé pour une évaluation par type. La stratégie de labels, le choix entre
  Isolation Forest et Random Forest et la cible de rappel de la classe critique restent
  des décisions ouvertes (constat A4) à trancher par ADR avant tout entraînement.
- Split temporel strict : entraînement sur les 2/3 premiers du cycle, test sur le dernier
  tiers, écart au moins égal à la plus longue fenêtre glissante ; jamais de mélange
  aléatoire ; réglage d'hyperparamètres par ``TimeSeriesSplit`` sur l'entraînement seul.
- Aucune fuite : toute transformation (scaler, etc.) est ajustée sur l'entraînement
  uniquement ; aucune feature n'utilise d'information future.
- Métriques adaptées au déséquilibre : précision, rappel et F1 par classe, matrice de
  confusion, courbe précision-rappel du score ; jamais l'accuracy seule.
- Seuils du score (normal / vigilance / critique) calibrés sur une période de validation
  distincte du test et stockés dans ``src/config.py``.
- Explicabilité : importance par permutation sur le jeu de test ; pour Isolation Forest,
  alertes expliquées par les écarts aux seuils des variables.
- Reproductibilité : ``RANDOM_STATE`` de ``src/config.py`` passé à tout composant aléatoire.

État : squelette de la phase de préparation — aucune logique implémentée.
"""

from __future__ import annotations

import pandas as pd


def inject_synthetic_anomalies(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Génère des labels d'anomalie à partir des seuils scientifiques (dataset non labellisé).

    Entrée : données nettoyées et enrichies, plages de ``thresholds``.
    Sortie : copie de ``df`` avec anomalies injectées, label et type d'anomalie par ligne.
    """
    raise NotImplementedError(
        "Jalon 3 — injection d'anomalies synthétiques typées, stratégie de labels "
        "à trancher par ADR (A4) (docs/02 §4.1)"
    )


def predict_threshold_baseline(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Baseline « règles de seuils seules » : classe de risque par ligne, sans apprentissage.

    Entrée : relevés à classer, plages de ``thresholds`` (seule source de décision).
    Sortie : classe (normal / vigilance / critique) par ligne, index aligné sur ``df``,
    comparable directement à la sortie de ``predict_risk``.
    """
    raise NotImplementedError(
        "Jalon 3 — baseline « règles de seuils seules », référence de comparaison "
        "obligatoire de tout modèle (docs/02 §4.1, R9)"
    )


def train_anomaly_model(df: pd.DataFrame) -> object:
    """Entraîne le modèle de détection (Isolation Forest ou Random Forest classifieur).

    Entrée : partie entraînement du split temporel. Sortie : modèle ajusté.
    """
    raise NotImplementedError(
        "Jalon 3 — entraînement du modèle de détection de risque sur split temporel, "
        "choix du modèle lié à A4 (docs/02 §4.1)"
    )


def predict_risk(model: object, df: pd.DataFrame) -> pd.DataFrame:
    """Retourne un score de risque + classe (normal/vigilance/critique) par ligne.

    Entrée : modèle ajusté, relevés. Sortie : une ligne par relevé, index aligné sur ``df``.
    """
    raise NotImplementedError(
        "Jalon 3 — score de risque et classe normal/vigilance/critique, seuils de score "
        "calibrés sur une période de validation (docs/02 §4.1)"
    )


def evaluate_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Retourne les métriques d'évaluation (précision, rappel, matrice de confusion).

    Entrée : modèle ajusté, jeu de test chronologiquement postérieur à l'entraînement.
    Sortie : précision, rappel et F1 par classe, matrice de confusion — jamais l'accuracy seule.
    """
    raise NotImplementedError(
        "Jalon 3 — métriques par classe et matrice de confusion, publiées à côté de la "
        "baseline (docs/02 §4.1)"
    )
