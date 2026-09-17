"""Configuration centralisée du projet Pisciculture IA.

Rôle : source unique des constantes (chemins, schéma, seuils scientifiques,
bornes de nettoyage, paramètres de modélisation, de décision et de dashboard)
pour éviter toute valeur en dur dispersée dans `src/`, `dashboard/` et les
notebooks (voir `.claude/rules/conventions-code.md`).

Règle d'édition : ce fichier est partagé entre agents. **Chaque agent n'édite
que sa section** (voir les en-têtes ci-dessous). Modifier un seuil scientifique
ou une borne de nettoyage exige un ADR accepté (`docs/07-JOURNAL_DECISIONS.md`) ;
la valeur ne doit pas être changée en anticipant la décision.

Convention : une valeur à `None` signifie une **décision ouverte**, non
tranchée — elle est accompagnée d'un commentaire renvoyant à la référence de
la décision (`docs/11-TABLEAU_DE_BORD.md`, section « Décisions en attente »,
ou l'ADR correspondant). Ne jamais remplacer un `None` par une valeur devinée :
attendre l'ADR « Accepté ».

Références : `docs/01-DATA_DICTIONARY.md`, `docs/02-SPEC_TECHNIQUE.md`,
`docs/03-ARCHITECTURE_CODE.md`, `docs/11-TABLEAU_DE_BORD.md`.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# =====================================================================
# Chemins — propriétaire : data-engineer (Jalons 1-2)
# =====================================================================
# Le chemin du fichier source est un paramètre des fonctions d'ingestion
# (docs/02 §1) : ces constantes ne sont que la valeur par défaut du projet,
# pas une valeur en dur dans le code de traitement.

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "IoTpond1.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "pond1_clean.csv"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
CLEANING_REPORT_PATH = REPORTS_DIR / "cleaning_report.json"

MODELS_DIR = PROJECT_ROOT / "models"

LOGS_DIR = PROJECT_ROOT / "logs"
DECISIONS_LOG_PATH = LOGS_DIR / "decisions.log"

# --- Schéma brut attendu (docs/01-DATA_DICTIONARY.md) ---
# 11 colonnes exactes du fichier IoTpond1.csv ; un écart au chargement doit
# lever une exception explicite (règle data-engineer n°1).
RAW_COLUMNS = [
    "created_at",
    "entry_id",
    "Temperature (C)",
    "Turbidity(NTU)",
    "Dissolved Oxygen(g/ml)",
    "PH",
    "Ammonia(g/ml)",
    "Nitrate(g/ml)",
    "Population",
    "Fish_Length(cm)",
    "Fish_Weight(g)",
]

TIMESTAMP_COLUMN = "created_at"
# Suffixe présent dans la colonne brute, à retirer avant parsing (docs/01 —
# fuseau horaire ambigu, anomalie 11 ; hypothèse retenue = décision ouverte
# ci-dessous, `MAX_INTERPOLATION_GAP`).
TIMESTAMP_SUFFIX = " CET"

# =====================================================================
# Seuils scientifiques — commun à tous les agents, ADR requis pour toute
# modification (identique à docs/03-ARCHITECTURE_CODE.md)
# =====================================================================
THRESHOLDS = {
    "temperature": {"min": 26, "max": 32, "critical_min": 20, "critical_max": 35},
    "dissolved_oxygen": {"min": 4, "critical_min": 3},
    "ph": {"min": 6.5, "max": 8.5, "critical_min": 6, "critical_max": 9},
    "ammonia": {"max": 0.05, "critical_max": 0.1},
    "nitrate": {"max": 50, "critical_max": 100},        # unité non tranchée — décision A1 (docs/11)
    "turbidity": {"max": None, "critical_max": None},   # à définir après exploration — Jalon 2 (docs/11)
}

# =====================================================================
# Nettoyage — propriétaire : data-engineer (Jalon 1)
# =====================================================================
# Bornes physiques déjà documentées dans docs/01 (anomalies 1 et 2).
TEMPERATURE_BOUNDS = {"min": 0, "max": 40}   # °C — docs/01 anomalie 1
PH_BOUNDS = {"min": 0, "max": 14}            # docs/01 anomalie 2

# Décisions ouvertes — ne pas deviner de valeur avant l'ADR correspondant.
AMMONIA_BOUNDS = None            # décision ouverte — ADR-003 (docs/11) : unité à trancher avant toute borne
DISSOLVED_OXYGEN_BOUNDS = None   # décision ouverte — A1/A2 (docs/11) : unité + borne physique (max observé 41)
NITRATE_BOUNDS = None            # décision ouverte — A1/A2 (docs/11) : unité à trancher avant toute borne
MAX_INTERPOLATION_GAP = None     # décision ouverte — docs/11 : trou max interpolable, dépend du fuseau/de la fréquence
RESAMPLING_FREQUENCY = None      # décision ouverte — docs/01 "Décisions à prendre" : fréquence de ré-échantillonnage

# Fenêtre glissante par défaut (signature `add_rolling_features`, docs/03).
ROLLING_WINDOW_DEFAULT = "1h"

# =====================================================================
# Modèles — propriétaire : ml-engineer (Jalon 3)
# =====================================================================
RANDOM_STATE = 42
RISK_CLASSES = ("normal", "vigilance", "critique")  # docs/02 §4.1
TRAIN_FRACTION = 2 / 3  # docs/02 §4.2 — split temporel (2/3 premiers du cycle), jamais aléatoire

# =====================================================================
# Moteur de décision — propriétaire : automation-engineer (Jalon 4)
# =====================================================================
# Réservé : pas de constante avant le Jalon 4 (règles de docs/02 §5,
# journal `DECISIONS_LOG_PATH` défini dans la section « Chemins » ci-dessus).

# =====================================================================
# Dashboard — propriétaire : dashboard-developer (Jalon 5, démo Jalon 6)
# =====================================================================
# Réservé : pas de constante avant le Jalon 5 (docs/03 `dashboard/app.py`).
