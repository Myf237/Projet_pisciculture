# Architecture du code — Structure de dépôt et fonctions attendues

Ce document décrit les **contrats d'interface** du code : noms de fonctions, paramètres et types attendus. Le test `tests/test_models.py::test_public_api_matches_architecture` (ml-engineer) vérifie par introspection que les modules exposent ces fonctions avec exactement ces noms de paramètres — toute modification de signature doit d'abord être répercutée ici.

## Arborescence proposée

```
Projet_pisiculture/
├── .claude/                     <- configuration des agents (voir 10-GOUVERNANCE_AGENTS.md)
├── .github/
│   └── pull_request_template.md <- modèle de pull request (ADR-007)
├── data/
│   ├── README.md                <- provenance, empreinte, obtention du CSV brut
│   ├── raw/                     <- immuable, non versionné
│   │   └── IoTpond1.csv
│   └── processed/               <- régénérable par le pipeline
│       └── pond1_clean.csv
├── src/
│   ├── __init__.py
│   ├── main.py                  <- point d'entrée unique du pipeline (Jalon 6)
│   ├── ingestion.py
│   ├── features.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── anomaly_detection.py
│   │   └── growth_prediction.py
│   ├── decision_engine.py
│   └── config.py
├── models/                      <- modèles entraînés (.joblib) + fiches (.json)
├── notebooks/
│   └── 01_exploration.ipynb
├── dashboard/
│   └── app.py
├── reports/
│   ├── cleaning_report.json     <- rapport de nettoyage (Jalon 1)
│   ├── figures/                 <- figures clés (EDA, modèles)
│   ├── experiments.md           <- registre des essais de modélisation
│   └── validations/             <- rapports de validation des jalons
├── logs/
│   ├── decisions.log            <- journal du produit (moteur de décision)
│   └── agents/                  <- journaux de traçabilité des agents
├── docs/                        <- les documents de cadrage (ce dossier)
├── tests/
│   ├── test_config.py
│   ├── test_ingestion.py
│   ├── test_features.py
│   ├── test_models.py
│   ├── test_decision_engine.py
│   ├── test_pipeline.py
│   └── test_dashboard.py
├── LICENSE                      <- MIT
├── .gitattributes               <- fins de ligne (LF, exceptions Windows), fichiers binaires
├── pytest.ini                   <- configuration pytest (pythonpath = .)
├── README.md
└── requirements.txt
```

*Arborescence complétée le 2026-09-16 : ajout de `src/main.py` (cité par le README mais absent), des emplacements des modèles entraînés et des rapports (non définis jusque-là), des journaux des agents et des tests manquants.*

*Arborescence complétée le 2026-09-16 (soir) : fichiers partagés créés avant la délégation des squelettes (`pytest.ini`, `src/__init__.py` — J-20260916-017) ; `src/models/__init__.py` (ml-engineer) et `tests/test_config.py`, `data/README.md` (data-engineer) créés pendant la délégation (J-20260916-019 et 020) ; fichiers liés à la mise en place de la gestion de version (`LICENSE`, `.gitattributes`, `.github/pull_request_template.md` — J-20260916-015, ADR-007).*

## `src/config.py`

Source unique des constantes du projet (chemins, schéma, seuils, bornes de nettoyage, paramètres de modélisation). Fichier **partagé** : chaque agent n'édite que sa section ; tout seuil scientifique ou borne de nettoyage modifié exige un ADR accepté. Une valeur à `None` signifie une **décision ouverte**, non tranchée (voir `docs/11-TABLEAU_DE_BORD.md`) — jamais remplacée par une valeur devinée.

Structure réelle, par section et agent propriétaire :

- **Chemins** (data-engineer) — construits depuis `PROJECT_ROOT = Path(__file__).resolve().parents[1]` : `RAW_DATA_PATH`, `PROCESSED_DATA_PATH`, `REPORTS_DIR`, `FIGURES_DIR`, `CLEANING_REPORT_PATH`, `MODELS_DIR`, `LOGS_DIR`, `DECISIONS_LOG_PATH`.
- **Schéma brut attendu** — `RAW_COLUMNS` (les 11 colonnes exactes de `IoTpond1.csv`, `docs/01-DATA_DICTIONARY.md`, un écart au chargement doit lever une exception explicite) ; `TIMESTAMP_COLUMN = "created_at"` ; `TIMESTAMP_SUFFIX = " CET"` (suffixe à retirer avant parsing — fuseau horaire = décision ouverte, `docs/11`).
- **Seuils scientifiques** (`THRESHOLDS`, commun à tous les agents, tout changement exige un ADR) :

```python
THRESHOLDS = {
    "temperature": {"min": 26, "max": 32, "critical_min": 20, "critical_max": 35},
    "dissolved_oxygen": {"min": 4, "critical_min": 3},
    "ph": {"min": 6.5, "max": 8.5, "critical_min": 6, "critical_max": 9},
    "ammonia": {"max": 0.05, "critical_max": 0.1},
    "nitrate": {"max": 50, "critical_max": 100},        # unité non tranchée — décision A1 (docs/11)
    "turbidity": {"max": None, "critical_max": None},   # à définir après exploration — Jalon 2 (docs/11)
}
```

- **Nettoyage** (data-engineer, Jalon 1) — bornes physiques déjà documentées : `TEMPERATURE_BOUNDS = {"min": 0, "max": 40}` et `PH_BOUNDS = {"min": 0, "max": 14}` (`docs/01`, anomalies 1-2). Décisions ouvertes, à `None` tant que l'ADR correspondant n'est pas accepté : `AMMONIA_BOUNDS` (ADR-003), `DISSOLVED_OXYGEN_BOUNDS` (A1/A2), `NITRATE_BOUNDS` (A1/A2), `MAX_INTERPOLATION_GAP` (fuseau horaire / fréquence), `RESAMPLING_FREQUENCY`. `ROLLING_WINDOW_DEFAULT = "1h"` (valeur par défaut de la fenêtre glissante, signature `add_rolling_features`).
- **Modèles** (ml-engineer, Jalon 3) — `RANDOM_STATE = 42` (confirmée, réserve R5 : graine arbitraire mais fixe, sans portée scientifique, à passer explicitement à tout composant aléatoire — voir le commentaire justificatif dans `src/config.py`) ; `RISK_CLASSES = ("normal", "vigilance", "critique")` (`docs/02` §4.1) ; `TRAIN_FRACTION = 2 / 3` (split temporel — 2/3 premiers du cycle pour l'entraînement, jamais de mélange aléatoire, `docs/02` §4.2).
- **Moteur de décision** (automation-engineer, Jalon 4) — section réservée : aucune constante avant le Jalon 4 (les règles déclaratives de `docs/02` §5 y seront ajoutées).
- **Dashboard** (dashboard-developer, Jalon 5) — section réservée : aucune constante avant le Jalon 5.

*(Extrait `THRESHOLDS` identique au code réel de `src/config.py` au 2026-09-16 — voir aussi `01-DATA_DICTIONARY.md`.)*

## `src/ingestion.py`

```python
def load_raw_data(path: str) -> pd.DataFrame:
    """Charge le CSV brut et parse les timestamps."""

def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Applique les règles de nettoyage (bornes physiques, imputation).
    Retourne le DataFrame nettoyé + un rapport de nettoyage (dict des corrections faites).
    """

def rebuild_growth_curve(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dédoublonne les paliers de Fish_Length/Fish_Weight pour ne garder
    qu'un point par changement de valeur réel.
    """
```

## `src/features.py`

```python
def add_rolling_features(df: pd.DataFrame, window: str = "1h") -> pd.DataFrame:
    """Ajoute moyennes/écarts-types glissants par variable de qualité d'eau."""

def add_threshold_distance(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Ajoute une variable d'écart signé au seuil critique, par paramètre."""

def compute_growth_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le taux de croissance instantané entre deux mesures de poids."""

def resample_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Agrège les données à la fréquence horaire pour réduire le bruit."""
```

Convention de `add_threshold_distance` (réserve R6, précisée dans le code par le data-engineer) : colonne `<clé>_distance_critical` par paramètre, dans la même unité que la colonne d'entrée (sans conversion). Signe : positif = marge de sécurité restante avant le seuil critique ; négatif = seuil déjà dépassé (valeur absolue = ampleur du dépassement) ; zéro = valeur au seuil. Borne critique unique inférieure (ex. `dissolved_oxygen`) : `distance = valeur - critical_min` ; borne unique supérieure (ex. `ammonia`, `nitrate`) : `distance = critical_max - valeur` ; double borne (ex. `temperature`, `ph`) : distance signée à la borne critique la plus proche. Colonne **non produite** (pas de valeur devinée) si `critical_min` et `critical_max` valent tous deux `None` (ex. `turbidity`) ou si le paramètre est `dissolved_oxygen`, `ammonia` ou `nitrate` tant que son unité n'est pas tranchée (décision A1).

## `src/models/anomaly_detection.py`

```python
def inject_synthetic_anomalies(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """Génère des labels d'anomalie à partir des seuils scientifiques (dataset non labellisé)."""

def predict_threshold_baseline(df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Baseline « règles de seuils seules » : classe de risque par ligne, sans apprentissage.
    Référence de comparaison obligatoire de tout modèle (règle n° 1 ml-engineer, risque R9) ;
    sortie comparable directement à celle de predict_risk.
    """

def train_anomaly_model(df: pd.DataFrame) -> object:
    """Entraîne le modèle de détection (Isolation Forest ou Random Forest classifieur)."""

def predict_risk(model: object, df: pd.DataFrame) -> pd.DataFrame:
    """Retourne un score de risque + classe (normal/vigilance/critique) par ligne."""

def evaluate_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Retourne les métriques d'évaluation (précision, rappel, matrice de confusion)."""
```

## `src/models/growth_prediction.py` (priorité 2)

```python
def train_growth_model(df: pd.DataFrame) -> object:
    """Entraîne un modèle de régression pour prédire Fish_Weight."""

def evaluate_growth_model(model: object, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Retourne MAE/RMSE sur split temporel."""
```

## `src/decision_engine.py`

```python
def evaluate_conditions(reading: dict, risk_class: str, thresholds: dict) -> list[dict]:
    """
    Fonction pure : entrée = un relevé + le risque prédit, sortie = liste d'actions simulées déclenchées.
    Chaque action est un dict {timestamp, action, reason, triggered_by, values, threshold, priority, simulated}
    (triggered_by = identifiant de règle déclarative ou "model" ; simulated toujours True).
    Actions simultanées ordonnées par priorité explicite ; une valeur absente ou imputée-manquante
    ne déclenche jamais d'action.
    """

def log_decision(action: dict, log_path: str | Path | None = None) -> None:
    """
    Ajoute l'action au journal de décisions, en JSON Lines, UTF-8, mode ajout.
    log_path : None (défaut) = chemin par défaut du projet, résolu depuis
    config.DECISIONS_LOG_PATH (import différé) — plus de littéral relatif en
    dur (correction du défaut D6, réserve R2) ; une valeur explicite (str ou
    Path) prend le pas, pour les tests notamment.
    """
```

`python -m src.decision_engine` doit, une fois implémenté, rejouer un scénario de test et produire un log d'exemple sans dashboard. À l'état de squelette (avant le Jalon 4) : affiche un message d'erreur clair sur `stderr` et sort avec le code 1, sans trace d'exception brute.

## `src/main.py`

```python
def build_parser() -> argparse.ArgumentParser:
    """Construit le parseur d'arguments du pipeline (option --input, défaut : config.RAW_DATA_PATH)."""

def run_pipeline(input_path: str) -> int:
    """Enchaîne les étapes du pipeline et retourne un code de sortie."""

def main(argv: list[str] | None = None) -> int:
    """
    Point d'entrée unique du pipeline (python src/main.py [--input <csv>]).
    Retourne le code de sortie du processus (0 = succès ; non nul = échec, message clair sur stderr).
    """
```

Étapes nommées de `run_pipeline` (non implémentées avant le Jalon 6) : ingestion (`src/ingestion.py`) → features (`src/features.py`) → modèle, entraînement ou chargement (`src/models/`) → décisions (`src/decision_engine.py`) ; chaque étape journalisée via `logging` (début, fin, durée, volumes), réexécutable sans effet de bord.

## `dashboard/app.py`

Application Streamlit qui :
1. Charge les données nettoyées + le modèle entraîné
2. Simule un flux "temps réel" en rejouant les données historiques (slider ou bouton play)
3. Affiche graphiques, état du bac, et journal des décisions
4. Appelle `decision_engine.evaluate_conditions()` à chaque pas de rejeu

## Conventions de code

- Type hints obligatoires sur toutes les fonctions publiques
- Docstrings courtes (une phrase suffit pour ce MVP) expliquant entrée/sortie
- Pas de notebook pour le code de production — les notebooks sont réservés à l'exploration (`notebooks/`)
- Tests unitaires a minima sur `decision_engine.py` (logique métier critique et facilement testable sans données réelles)
