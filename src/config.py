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
# Suffixe présent dans la colonne brute, retiré avant parsing, sans aucune
# conversion de fuseau (ADR-010, accepté 2026-09-18) : les données ne
# permettent pas de trancher entre « CET » littéral et l'heure locale du
# Nigeria (WAT), les deux hypothèses partageant le même décalage UTC+1
# (reports/analyse-donnees-jalon1.md §9). L'horodatage est conservé tel quel.
TIMESTAMP_SUFFIX = " CET"

# Colonnes de la courbe de croissance (mesures manuelles périodiques,
# propagées sur les relevés intermédiaires — docs/01 anomalie 5), utilisées
# par `ingestion.rebuild_growth_curve`. Clé = nom court sans unité, utilisé
# pour les colonnes signalant une non-monotonie (`<clé>_non_monotonic`).
GROWTH_COLUMNS = {
    "Fish_Weight(g)": "Fish_Weight",
    "Fish_Length(cm)": "Fish_Length",
}

# =====================================================================
# Seuils scientifiques — commun à tous les agents, ADR requis pour toute
# modification (identique à docs/03-ARCHITECTURE_CODE.md)
# =====================================================================
THRESHOLDS = {
    "temperature": {"min": 26, "max": 32, "critical_min": 20, "critical_max": 35},
    "dissolved_oxygen": {"min": 4, "critical_min": 3},
    "ph": {"min": 6.5, "max": 8.5, "critical_min": 6, "critical_max": 9},
    # Valeurs numériques héritées du cahier §5, mais NON applicables telles
    # quelles (D2, reports/validations/jalon-1.md) : `ammonia`/`nitrate`
    # proviennent de capteurs de gaz suspendus au-dessus de l'eau, pas de
    # sondes immergées (ADR-009 — ce n'était pas une question d'unité non
    # tranchée, l'unité mg/L est confirmée). Ne jamais lire ces deux entrées
    # comme des seuils absolus : utiliser `get_applicable_thresholds()`
    # ci-dessous, qui les exclut automatiquement via `SENSOR_TYPES`.
    "ammonia": {"max": 0.05, "critical_max": 0.1},
    "nitrate": {"max": 50, "critical_max": 100},
    # ADR-011 (accepté, 2026-09-18) : décision durable, pas ouverte — 56,37 %
    # des relevés saturent à 100 NTU (plafond du capteur), un seuil absolu
    # déclencherait une alerte non exploitable. Turbidité traitée en
    # indicateur relatif, comme ammonia/nitrate ci-dessus (mêmes valeurs
    # `None`, mais ici parce qu'aucun seuil absolu n'est retenu, pas parce
    # que l'unité serait en cause).
    "turbidity": {"max": None, "critical_max": None},
}

# =====================================================================
# Nettoyage — propriétaire : data-engineer (Jalon 1)
# =====================================================================
# Bornes physiques déjà documentées dans docs/01 (anomalies 1 et 2).
TEMPERATURE_BOUNDS = {"min": 0, "max": 40}   # °C — docs/01 anomalie 1
PH_BOUNDS = {"min": 0, "max": 14}            # docs/01 anomalie 2

# ADR-003 (accepté) + ADR-010 (accepté) : au-delà de 5, valeur exclue par
# seuillage de plausibilité aquacole — marquée hors borne puis imputée
# comme les autres variables bornées. Correction du 2026-09-18 (D1,
# reports/validations/jalon-1.md) : ce sous-ensemble n'est PAS un plateau de
# valeur unique répétée (contrairement à la description initiale de
# l'ADR-003) — c'est un continuum de 1 838 valeurs distinctes (5,00082 à
# 4,27e11, médiane 127,87), voir reports/analyse-donnees-jalon1.md §4
# corrigé. Usage en modélisation : indicateur relatif uniquement (ADR-009 —
# capteur de gaz MQ137 suspendu au-dessus de l'eau, pas une concentration
# dissoute) ; cette borne sert au nettoyage par seuillage, pas à un seuil
# aquacole absolu.
AMMONIA_BOUNDS = {"max": 5}

# ADR-010 (accepté, y compris pour cette borne — confirmation humaine du
# 2026-09-18, J-20260918-021/022) : borne haute DÉFINITIVE, 15 mg/L, retenue
# parmi les trois candidates chiffrées (8 mg/L = 45,48 % du fichier au-delà ;
# 15 mg/L = 26,00 % ; 20 mg/L = 21,41 % — reports/analyse-donnees-jalon1.md
# §2). Les deux alternatives sont écartées.
DISSOLVED_OXYGEN_BOUNDS = {"max": 15}

# ADR-009 (accepté) : Nitrate provient d'un capteur de gaz (MQ135) suspendu
# au-dessus de l'eau, pas d'une sonde immergée — ce n'est pas une valeur en
# attente d'arbitrage (contrairement à l'ancien A1/A2) mais une décision
# durable : aucune borne physique absolue de nettoyage ne s'applique à cette
# colonne (nature de la mesure, pas un artefact ponctuel à filtrer).
NITRATE_BOUNDS = None

# ADR-010 (accepté) : trou temporel maximal interpolable. Au-delà, la valeur
# reste manquante et marquée (pas d'imputation) — conséquence chiffrée : les
# 36 jours calendaires entiers sans aucun relevé (sur 117 jours de l'étendue,
# reports/analyse-donnees-jalon1.md §8) resteront entièrement manquants.
# Chaîne compatible `pandas.Timedelta`, même convention que
# `ROLLING_WINDOW_DEFAULT` ci-dessous.
MAX_INTERPOLATION_GAP = "1h"

# ADR-010 (accepté) : fréquence de ré-échantillonnage horaire — décidée dès
# le Jalon 1 mais dont l'application était différée au Jalon 2, hors
# périmètre du nettoyage. Appliquée depuis le Jalon 2 par
# `src/features.py::resample_hourly` (Module 2, docs/02 §3). Chaîne
# compatible `pandas.Timedelta`/`DataFrame.resample`, même convention que
# `MAX_INTERPOLATION_GAP` et `ROLLING_WINDOW_DEFAULT`. Ce n'est pas une
# nouvelle décision : la valeur ne change pas depuis l'ADR-010, seule son
# exploitation dans le code change.
RESAMPLING_FREQUENCY = "1h"

# Fenêtre glissante par défaut (signature `add_rolling_features`, docs/03).
ROLLING_WINDOW_DEFAULT = "1h"

# Décision G1 du 2026-09-18 (J-20260918-042/044) : la borne de nettoyage
# reste appliquée à la colonne nettoyée (comportement inchangé), mais la
# valeur brute d'origine — y compris hors bornes, sans imputation — est
# conservée en parallèle dans une colonne `<label>{RAW_VALUE_SUFFIX}`, pour
# chaque variable bornée de `SENSOR_TYPES` (température, pH, oxygène
# dissous, ammoniac). Objectif : les dérives de capteur (ex. plateau DO
# 36-41 mg/L du 30/07-05/08, entièrement `missing` dans la colonne nettoyée)
# redeviennent visibles et exploitables au Jalon 3 et pour la démonstration,
# sans renoncer au nettoyage. Même famille de convention que `_imputed`/
# `_missing` (suffixes eux-mêmes non dupliqués ici, littéraux dans
# `src/ingestion.py`, cohérent avec D8, reports/validations/jalon-1.md) ;
# celui-ci est explicitement déclaré ici à la demande de la décision G1.
RAW_VALUE_SUFFIX = "_raw"

# Structure déclarant, pour chaque variable de qualité d'eau, le type de
# capteur réel (ADR-009, article source Udanor et al.) et l'applicabilité
# des seuils aquacoles absolus — évite d'appliquer un seuil du cahier des
# charges §5 à une mesure de gaz suspendu (`ammonia`, `nitrate`). Référence
# les bornes déjà définies ci-dessus (pas de duplication de valeur). Clé =
# nom de colonne brut (`config.RAW_COLUMNS`) ; `label` = nom court sans
# unité utilisé pour les colonnes de marquage `<label>_imputed` /
# `<label>_missing` (docs/03 — voir `src/ingestion.py::clean_data` pour la
# distinction entre les deux) ; `threshold_key` = clé correspondante dans
# `THRESHOLDS` ci-dessus (utilisée par `get_applicable_thresholds()`) ;
# `absolute_thresholds_applicable` : `True` (sonde immergée, seuils du
# cahier §5 applicables) ou `False` (usage relatif uniquement — capteur de
# gaz comme ammonia/nitrate, ADR-009, ou indicateur saturé comme turbidity,
# ADR-011 ; ces deux raisons sont distinctes mais produisent le même
# comportement via `get_applicable_thresholds()`). `None` resterait
# réservé à une variable dont l'applicabilité n'est pas encore tranchée —
# aucune entrée de `SENSOR_TYPES` n'est plus dans ce cas depuis l'ADR-011 ;
# `note` = texte de contexte inclus tel quel dans `reports/cleaning_report.json`
# par colonne (construit ici, jamais par comparaison à un nom de colonne en
# dur dans `src/ingestion.py` — D8, reports/validations/jalon-1.md), ou
# `None` si aucune note spécifique n'est nécessaire.
SENSOR_TYPES = {
    "Temperature (C)": {
        "label": "Temperature",
        "sensor": "immersed",
        "bounds": TEMPERATURE_BOUNDS,
        "threshold_key": "temperature",
        "absolute_thresholds_applicable": True,
        "note": None,
    },
    "PH": {
        "label": "PH",
        "sensor": "immersed",
        "bounds": PH_BOUNDS,
        "threshold_key": "ph",
        "absolute_thresholds_applicable": True,
        "note": None,
    },
    "Dissolved Oxygen(g/ml)": {
        "label": "Dissolved Oxygen",
        "sensor": "immersed",
        "bounds": DISSOLVED_OXYGEN_BOUNDS,
        "threshold_key": "dissolved_oxygen",
        "absolute_thresholds_applicable": True,
        # Construite depuis DISSOLVED_OXYGEN_BOUNDS lui-même (pas de valeur
        # dupliquée en dur, D8) : si la borne change, la note suit.
        "note": (
            f"ADR-010 : borne haute définitive {DISSOLVED_OXYGEN_BOUNDS['max']} "
            "mg/L (confirmée par décision humaine le 2026-09-18), retenue "
            "parmi les candidates 8 / 15 / 20 mg/L."
        ),
    },
    "Ammonia(g/ml)": {
        "label": "Ammonia",
        "sensor": "gas",
        "bounds": AMMONIA_BOUNDS,
        "threshold_key": "ammonia",
        "absolute_thresholds_applicable": False,
        # Construite depuis AMMONIA_BOUNDS (D8) ; texte corrigé le
        # 2026-09-18 (D1) : continuum de valeurs, pas un plateau constant.
        "note": (
            f"ADR-003 : au-delà de {AMMONIA_BOUNDS['max']}, valeur exclue par "
            "seuillage de plausibilité aquacole (continuum de 1 838 valeurs "
            "distinctes, pas un code d'erreur unique — voir "
            "reports/analyse-donnees-jalon1.md §4, corrigé le 2026-09-18). "
            "Usage relatif en modélisation (ADR-009, capteur de gaz)."
        ),
    },
    "Nitrate(g/ml)": {
        "label": "Nitrate",
        "sensor": "gas",
        "bounds": NITRATE_BOUNDS,
        "threshold_key": "nitrate",
        "absolute_thresholds_applicable": False,
        "note": (
            "ADR-009 : capteur de gaz (MQ135) suspendu au-dessus de l'eau — "
            "aucune borne absolue appliquée, colonne non modifiée par le "
            "nettoyage."
        ),
    },
    "Turbidity(NTU)": {
        "label": "Turbidity",
        "sensor": "immersed",
        # ADR-011 (accepté) : décision durable, pas ouverte — même statut que
        # NITRATE_BOUNDS (aucune borne physique absolue), pour une raison
        # différente (saturation du capteur à 100 NTU sur 56,37 % des
        # relevés, pas une question d'unité ou de nature de capteur).
        "bounds": None,
        "threshold_key": "turbidity",
        "absolute_thresholds_applicable": False,
        "note": (
            "ADR-011 : indicateur relatif, aucun seuil absolu retenu (56,37 % "
            "des relevés saturés au plafond du capteur, 100 NTU — voir "
            "reports/analyse-donnees-jalon1.md, addendum du Jalon 2) — "
            "colonne non modifiée par le nettoyage."
        ),
    },
}


def get_applicable_thresholds() -> dict[str, dict]:
    """Sous-ensemble de `THRESHOLDS` dont les seuils absolus sont réellement
    applicables au paramètre (D2, `reports/validations/jalon-1.md`).

    Sortie : dict `{clé_threshold: bornes}`, restreint aux paramètres dont
    `SENSOR_TYPES[...]["absolute_thresholds_applicable"] is True` (sondes
    immergées — température, pH, oxygène dissous). Accès protégé plutôt que
    seulement documenté : contrairement à une lecture directe de
    `THRESHOLDS`, cette fonction ne peut **jamais** renvoyer de seuil pour
    `ammonia`/`nitrate` (capteurs de gaz, ADR-009) ni pour `turbidity`
    (indicateur relatif, ADR-011 — capteur saturé sur 56,37 % des relevés),
    même si `THRESHOLDS` contient une valeur numérique héritée pour ces
    clés — un appelant qui l'utilise ne peut pas appliquer par erreur un
    seuil aquacole absolu à une mesure de gaz ou à un capteur saturé.
    """
    return {
        meta["threshold_key"]: THRESHOLDS[meta["threshold_key"]]
        for meta in SENSOR_TYPES.values()
        if meta["absolute_thresholds_applicable"] is True
    }


# Colonnes brutes ni bornées (SENSOR_TYPES ci-dessus) ni reconstruites
# (GROWTH_COLUMNS ci-dessus) ni l'horodatage (TIMESTAMP_COLUMN) : identifiant
# technique et métadonnée constante du bac. Non nettoyées par des bornes
# physiques ; documentées ici (au lieu d'un littéral dans `src/ingestion.py`)
# pour que `clean_data` couvre les 11 colonnes brutes dans son rapport (D6,
# reports/validations/jalon-1.md).
OTHER_RAW_COLUMNS = {
    "entry_id": "Identifiant séquentiel du relevé, non concerné par le nettoyage physique.",
    "Population": (
        "Métadonnée constante du bac (docs/01 anomalie 4), pas une variable "
        "dynamique de qualité d'eau — non nettoyée."
    ),
}

# =====================================================================
# Modèles — propriétaire : ml-engineer (Jalon 3)
# =====================================================================
# Graine arbitraire mais fixe (aucune portée scientifique, aucune valeur
# « optimale » recherchée) : valeur confirmée par la ml-engineer, réserve R5.
# À passer explicitement à tout composant aléatoire — `IsolationForest`,
# `RandomForestClassifier`, `permutation_importance`, injection d'anomalies
# synthétiques (`train_test_split` non utilisé : le split est temporel, voir
# `TRAIN_FRACTION`). Deux exécutions identiques doivent donner les mêmes
# métriques : la reproductibilité est vérifiée aux Jalons 3 et 6 (docs/04).
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
