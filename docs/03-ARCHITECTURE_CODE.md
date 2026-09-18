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
- **Schéma brut attendu** — `RAW_COLUMNS` (les 11 colonnes exactes de `IoTpond1.csv`, `docs/01-DATA_DICTIONARY.md`, un écart au chargement doit lever une exception explicite) ; `TIMESTAMP_COLUMN = "created_at"` ; `TIMESTAMP_SUFFIX = " CET"` (suffixe retiré avant parsing, **sans conversion de fuseau**, ADR-010) ; `GROWTH_COLUMNS` (dict colonne brute → nom court sans unité, ex. `"Fish_Weight(g)": "Fish_Weight"`, utilisé par `rebuild_growth_curve` pour nommer les colonnes `<clé>_non_monotonic`).
- **Seuils scientifiques** (`THRESHOLDS`, commun à tous les agents, tout changement exige un ADR — inchangé depuis le cadrage) :

```python
THRESHOLDS = {
    "temperature": {"min": 26, "max": 32, "critical_min": 20, "critical_max": 35},
    "dissolved_oxygen": {"min": 4, "critical_min": 3},
    "ph": {"min": 6.5, "max": 8.5, "critical_min": 6, "critical_max": 9},
    "ammonia": {"max": 0.05, "critical_max": 0.1},
    "nitrate": {"max": 50, "critical_max": 100},        # capteur de gaz, usage relatif — ADR-009
    "turbidity": {"max": None, "critical_max": None},   # indicateur relatif, aucun seuil absolu — ADR-011 (décision durable, comme nitrate/ADR-009)
}
```

- **Nettoyage** (data-engineer, Jalon 1 — toutes les bornes tranchées le 2026-09-18) : `TEMPERATURE_BOUNDS = {"min": 0, "max": 40}` et `PH_BOUNDS = {"min": 0, "max": 14}` (`docs/01`, anomalies 1-2 ; plage inchangée par ADR-011, aucun resserrement du pH) ; `AMMONIA_BOUNDS = {"max": 5}` (ADR-003 — artefact de capteur au-delà, traité au nettoyage ; la variable reste ensuite un indicateur relatif, ADR-009) ; `DISSOLVED_OXYGEN_BOUNDS = {"max": 15}` (ADR-010, borne haute **définitive**, confirmée par l'humain le 2026-09-18 — 26,00 % du fichier au-delà, alternatives 8 et 20 mg/L écartées) ; `NITRATE_BOUNDS = None` (décision **durable**, pas ouverte : capteur de gaz, ADR-009, pas de borne physique absolue) ; `MAX_INTERPOLATION_GAP = "1h"` (ADR-010, trou max interpolable) ; `RESAMPLING_FREQUENCY = "1h"` (ADR-010, fréquence tranchée dès le Jalon 1, **désormais appliquée** par `src/features.py::resample_hourly` depuis le Jalon 2 — ce n'est pas une nouvelle décision, seule son exploitation dans le code change). `ROLLING_WINDOW_DEFAULT = "1h"` (valeur par défaut de la fenêtre glissante, signature `add_rolling_features`). `RAW_VALUE_SUFFIX = "_raw"` (ADR-011, décision G1 du 2026-09-18) : suffixe de la colonne conservant la valeur brute d'origine de chaque variable bornée, jamais imputée (voir schéma du DataFrame nettoyé, `src/ingestion.py` ci-dessous).
- **`SENSOR_TYPES`** (data-engineer, ADR-009) — dict clé = nom de colonne brut (`config.RAW_COLUMNS`), déclarant pour chaque variable de qualité d'eau : `label` (nom court, utilisé par `src/ingestion.py::clean_data` pour les colonnes de marquage `<label>_imputed`, `<label>_missing` **et** la colonne de valeur brute `<label>{config.RAW_VALUE_SUFFIX}` (ADR-011) — voir ci-dessous), `sensor` (`"immersed"` ou `"gas"`), `bounds` (référence à la borne définie ci-dessus, sans duplication de valeur), `threshold_key` (clé correspondante dans `THRESHOLDS`), `absolute_thresholds_applicable` (`True` pour température/pH/oxygène dissous — sondes immergées, seuils du cahier §5 applicables ; `False` pour ammoniac/nitrate — capteurs de gaz, usage relatif uniquement ; `None` pour la turbidité, tranchée en indicateur relatif par ADR-011), `note` (texte de contexte inclus dans `reports/cleaning_report.json`, construit depuis les bornes elles-mêmes, jamais un littéral en dur).
- **`get_applicable_thresholds() -> dict[str, dict]`** (data-engineer) — sous-ensemble de `THRESHOLDS` restreint aux clés dont `SENSOR_TYPES[...]["absolute_thresholds_applicable"] is True` (température, pH, oxygène dissous). Ne renvoie jamais de seuil pour `ammonia`/`nitrate`/`turbidity`, même si `THRESHOLDS` contient une valeur numérique héritée pour ces clés : c'est l'accès protégé qui lève la réserve D2 du rapport `reports/validations/jalon-1.md` (3 tests dédiés font échouer une régression injectée sur `SENSOR_TYPES`).
- **`OTHER_RAW_COLUMNS`** (data-engineer) — dict des colonnes brutes ni bornées (`SENSOR_TYPES`) ni reconstruites (`GROWTH_COLUMNS`) ni l'horodatage : `entry_id` et `Population`, chacune avec sa note ; utilisé par `clean_data` pour que le rapport de nettoyage couvre les 11 colonnes brutes.
- **Modèles** (ml-engineer, Jalon 3) — `RANDOM_STATE = 42` (confirmée, réserve R5 : graine arbitraire mais fixe, sans portée scientifique, à passer explicitement à tout composant aléatoire — voir le commentaire justificatif dans `src/config.py`) ; `RISK_CLASSES = ("normal", "vigilance", "critique")` (`docs/02` §4.1) ; `TRAIN_FRACTION = 2 / 3` (split temporel — 2/3 premiers du cycle pour l'entraînement, jamais de mélange aléatoire, `docs/02` §4.2).
- **Moteur de décision** (automation-engineer, Jalon 4) — section réservée : aucune constante avant le Jalon 4 (les règles déclaratives de `docs/02` §5 y seront ajoutées).
- **Dashboard** (dashboard-developer, Jalon 5) — section réservée : aucune constante avant le Jalon 5.

*(Extrait `THRESHOLDS` identique au code réel de `src/config.py` au 2026-09-18 — voir aussi `01-DATA_DICTIONARY.md`. Réserve D2 du rapport `reports/validations/jalon-1.md` (`SENSOR_TYPES` déclarait l'applicabilité des seuils sans l'imposer techniquement) **levée** le 2026-09-18 (itération 2) par `get_applicable_thresholds()` ci-dessus.)*

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

Schéma du DataFrame retourné par `clean_data` (mis à jour ADR-011, décision G1 J-20260918-042, implémentation J-20260918-044) : **23 colonnes** au total — les 11 colonnes brutes, plus **trois** colonnes par variable bornée de `config.SENSOR_TYPES` (température, pH, oxygène dissous, ammoniac, soit 4 × 3 = 12 colonnes supplémentaires) :
- `<label>_imputed` (`True` seulement si la valeur d'origine était hors bornes ou manquante **et** a été comblée par interpolation) ;
- `<label>_missing` (`True` si elle est hors bornes ou manquante et **reste** `NaN`, trou trop long ou bord de série) — les deux drapeaux ne sont jamais vrais simultanément, et aucun des deux ne l'est sur une valeur d'origine valide (D9, `reports/validations/jalon-1.md`, vérifié par recalcul indépendant) ;
- `<label>{config.RAW_VALUE_SUFFIX}` (suffixe `"_raw"`, ADR-011) : valeur brute d'origine telle que lue, sans aucune modification — y compris hors bornes, y compris `NaN` si elle l'était déjà — copiée depuis la série brute avant tout nettoyage, jamais imputée ni recalculée depuis la colonne nettoyée ; existe pour **toutes** les lignes (y compris les valeurs valides, où elle est égale à la colonne nettoyée). Conserve le signal des dérives de capteur que le nettoyage rend invisibles : sur l'épisode du plateau d'oxygène dissous (30/07-05/08, 13 422 relevés), la colonne nettoyée ne garde que 368 valeurs non manquantes contre 13 422 dans `Dissolved Oxygen_raw` (moyenne 36,47 mg/L) — J-20260918-044.

Nitrate et turbidité n'ont pas de colonne de marquage ni de colonne `_raw` dédiée (pas de borne absolue applicable, donc colonne brute jamais modifiée par le nettoyage : ADR-009 pour le nitrate, ADR-011 pour la turbidité — indicateur relatif) ; `raw_value_column` vaut `None` pour ces deux entrées dans `reports/cleaning_report.json`.

Point d'entrée CLI implémenté au Jalon 1 (D7, `reports/validations/jalon-1.md`) : `python -m src.ingestion [--input CSV]` (fonction `regenerate_processed_artifacts`) régénère `config.PROCESSED_DATA_PATH` (`data/processed/pond1_clean.csv`) et `config.CLEANING_REPORT_PATH` (`reports/cleaning_report.json`) à partir du CSV brut (défaut : `config.RAW_DATA_PATH`). Code de sortie 0 en cas de succès (message sur `stderr`), non nul avec message d'erreur clair sur `stderr` en cas d'échec (ex. fichier introuvable) — pas de trace d'exception brute. Ne couvre que le Module 1 (ingestion + nettoyage) : distinct de `src/main.py` (pipeline complet ingestion → features → modèle → décision, Jalon 6, toujours `NotImplementedError`).

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

Implémentées au Jalon 2 (data-engineer, J-20260918-039), vectorisées (pandas/numpy, aucune boucle ligne à ligne — règle data-engineer n°9), 0 `skip` restant dans `tests/test_features.py` :

- **`add_rolling_features`** : fenêtre temporelle causale (`Series.rolling(window, min_periods=1)`, convention pandas par défaut `closed="right"` — jamais `center=True`), une paire `<label>_rolling_mean` / `<label>_rolling_std` par colonne de `config.SENSOR_TYPES` présente en entrée ; premier point d'une série sans historique : écart-type `NaN` (jamais de valeur inventée).
- **`add_threshold_distance`** : formule de la convention ci-dessous, restreinte aux clés de `config.get_applicable_thresholds()` (température, pH, oxygène dissous), même si le dict `thresholds` passé en paramètre contient `ammonia`/`nitrate`/`turbidity` — aucune colonne n'est produite pour ces clés.
- **`compute_growth_rate`** : `<label>_growth_rate` = delta de la valeur / delta de temps (heures) entre deux paliers consécutifs de `ingestion.rebuild_growth_curve` ; `NaN` au premier palier (aucun point précédent, jamais extrapolé) ; une non-monotonie de la courbe (`<label>_non_monotonic`, si présente en entrée) se traduit par un taux négatif, jamais corrigée ni masquée.
- **`resample_hourly`** : agrégation horaire (`config.RESAMPLING_FREQUENCY = "1h"`, ADR-010), une ligne par créneau de l'étendue temporelle couverte, y compris les créneaux vides (`n_readings = 0`, `<label>_mean = NaN`, compteurs à 0 — jamais de valeur inventée). Pour chaque variable de `config.SENSOR_TYPES` présente : `<label>_mean` (moyenne du créneau, ignore les `NaN`) et **trois compteurs séparés**, jamais confondus — `<label>_n_measured` (valeurs réellement mesurées : présentes et non `<label>_imputed`), `<label>_n_imputed` (valeurs comblées par interpolation, `<label>_imputed = True`) et `<label>_n_missing` (`<label>_missing = True` pour les variables bornées ; `n_readings - n_présentes` pour Nitrate/Turbidity, sans borne de nettoyage — ADR-009/ADR-011). Invariant garanti par construction : `n_measured + n_imputed + n_missing == n_readings` pour chaque créneau et chaque variable — réponse directe au risque R16 (`docs/08`), pour qu'aucune fonction en aval ne traite une moyenne agrégée comme une moyenne de mesures réelles quand `n_measured` est nul ou faible.

Convention de `add_threshold_distance` (réserve R6, précisée dans le code par le data-engineer ; reformulée D3 le 2026-09-18 après ADR-009/ADR-010, cohérente avec la description ci-dessus) : colonne `<clé>_distance_critical` par paramètre, dans la même unité que la colonne d'entrée (sans conversion). Signe : positif = marge de sécurité restante avant le seuil critique ; négatif = seuil déjà dépassé (valeur absolue = ampleur du dépassement) ; zéro = valeur au seuil. Borne critique unique inférieure (ex. `dissolved_oxygen`) : `distance = valeur - critical_min` ; borne unique supérieure : `distance = critical_max - valeur` (aucun paramètre actuellement applicable n'est dans ce cas) ; double borne (ex. `temperature`, `ph`) : distance signée à la borne critique la plus proche. Colonne **non produite** (pas de valeur devinée) pour toute clé absente de `config.get_applicable_thresholds()` (sondes immergées à seuils aquacoles applicables — température, pH, oxygène dissous) : sont donc exclus `ammonia`/`nitrate` (capteurs de gaz, ADR-009 — pas une question d'unité) et `turbidity` (indicateur relatif sans seuil absolu, ADR-011 — décision tranchée, pas ouverte).

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
