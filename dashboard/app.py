"""Dashboard de suivi — Module 5 (Jalon 5, `docs/02-SPEC_TECHNIQUE.md` §6).

Rôle : rendre la chaîne données → prédiction → décision compréhensible par un
jury sans explication orale, via un scénario de démo déterministe (rejeu des
données historiques). Voir `docs/03-ARCHITECTURE_CODE.md` (section
`dashboard/app.py`) et `docs/04-JALONS_VALIDATION.md` (Jalon 5).

État actuel : squelette de préparation (aucune fonctionnalité réelle). La
structure complète (graphiques, état du bac, journal des actions, rejeu) sera
implémentée au Jalon 5, une fois `src/config.py`, les données traitées
(`data/processed/`) et le modèle entraîné (`models/`) disponibles.

Règles à respecter à l'implémentation (`.claude/agents/dashboard-developer.md`) :
- Zéro logique métier ici : l'application appelle uniquement les fonctions de
  `src/` (dont `decision_engine.evaluate_conditions` à chaque pas de rejeu) et
  se contente de présenter leurs résultats.
- Aucun entraînement ni nettoyage dans l'application : elle charge des
  artefacts déjà produits (`data/processed/`, `models/`) ; si absents, un
  message clair indique la commande à lancer (`python src/main.py`).
- Performance : `st.cache_data` pour le chargement des données,
  `st.cache_resource` pour le modèle, pour un démarrage en quelques secondes.
- Rejeu non bloquant : position et état de lecture dans `st.session_state` ;
  contrôles lecture/pause/pas-à-pas/curseur ; pas de boucle `while`
  bloquante (préférer `st.fragment(run_every=...)`, qui exige
  Streamlit >= 1.37 — mise à jour de `requirements.txt` à justifier le
  moment venu — sinon `st.rerun`).
- Scénario de démo déterministe : la fenêtre temporelle rejouée est définie
  dans `src/config.py` (section dashboard) et contient l'anomalie réelle
  identifiée au Jalon 2 ; même déroulé à chaque lancement.
- Lisibilité : seuils tracés sur les graphiques ; état du bac (normal /
  vigilance / critique) signalé par couleur ET texte, jamais la couleur
  seule ; actions listées avec heure, raison et source (règle ou modèle).

Import de `src/` — non implémenté à ce stade, à faire au Jalon 5 :
`streamlit run dashboard/app.py` place le dossier `dashboard/` en tête de
`sys.path`, pas la racine du projet, donc `import src...` échouerait tel
quel. Solution prévue : insérer la racine du projet dans `sys.path` avant
tout import de `src`, par exemple :

    import sys
    from pathlib import Path
    ROOT_DIR = Path(__file__).resolve().parent.parent
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

Cette solution est documentée ici mais pas encore codée : ce squelette
n'importe rien de `src/` (hors périmètre de la tâche de préparation).
"""

import streamlit as st

ACTUATOR_BANNER = "Actionneurs simulés — aucun matériel connecté"

# Les 4 zones fonctionnelles minimales du dashboard, telles que définies par
# `docs/02-SPEC_TECHNIQUE.md` §6. Simples intitulés à ce stade (squelette) :
# aucun graphique ni donnée tant que le Jalon 5 n'est pas engagé (risque R6).
PLANNED_ZONES = [
    "1. Paramètres de qualité d'eau dans le temps, avec seuils affichés",
    "2. État actuel du bac (normal / vigilance / critique)",
    "3. Actions et alertes déclenchées (journal du moteur de décision)",
    "4. Mode rejeu — déroulé du scénario de démonstration",
]


def main() -> None:
    """Point d'entrée de l'application Streamlit (squelette, Jalon 5 à venir)."""
    st.set_page_config(page_title="Pisciculture IA — Dashboard", layout="wide")

    st.title("Pisciculture IA — Dashboard de suivi")

    st.warning(ACTUATOR_BANNER)

    st.info(
        "Dashboard en construction (Jalon 5, voir `docs/02-SPEC_TECHNIQUE.md` "
        "§6 et `docs/04-JALONS_VALIDATION.md`). Cette page est un squelette : "
        "aucune donnée réelle, aucun graphique, aucune logique métier n'est "
        "encore branché."
    )

    st.subheader("Zones prévues")
    for zone in PLANNED_ZONES:
        st.write(zone)


if __name__ == "__main__":
    main()
