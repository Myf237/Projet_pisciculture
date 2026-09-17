"""Module 4 — Moteur de décision (docs/02 §5, docs/03 `src/decision_engine.py`).

Rôle : à partir d'un relevé de qualité d'eau et de la classe de risque
prédite par le Module 3, calculer la liste des actions **simulées** à
déclencher (aucune commande matérielle réelle — vocabulaire imposé « action
simulée », règle R5 et `.claude/rules/integrite-academique.md`).

Jalon de rattachement : Jalon 4 — Moteur de décision fonctionnel (docs/04).
Propriétaire : automation-engineer (`.claude/agents/automation-engineer.md`).

Principes retenus pour l'implémentation du Jalon 4 (règles de l'agent
automation-engineer, ci-après « règle n° X ») :
- `evaluate_conditions` est une **fonction pure** : aucune I/O, ne lit pas
  l'horloge système (le timestamp vient du relevé), déterministe (règle n°1).
- Les règles de déclenchement (id, variable, comparaison, clé de seuil,
  action, priorité) sont **déclaratives**, définies dans `src/config.py`
  (section « Moteur de décision », réservée pour le Jalon 4) — pas de
  `if`/`elif` dispersés ici ; plusieurs actions simultanées sont ordonnées
  par priorité explicite (règle n°2).
- Chaque action produite par `evaluate_conditions` est un dict complet :
  `{timestamp, action, reason, triggered_by, values, threshold, priority,
  simulated}`, avec `triggered_by` = identifiant de règle ou `"model"` et
  `simulated` toujours `True` (règle n°3).
- Une valeur absente ou imputée-manquante (voir `<variable>_imputed` produit
  par `src/ingestion.py`) ne déclenche jamais d'action ; le cas est testé et
  rendu visible dans `reason` (règle n°4).
- Le mécanisme anti-oscillation (hystérésis ou temporisation, pour éviter
  qu'une action simulée n'alterne ON/OFF à chaque relevé en démo) reste une
  **décision ouverte** à trancher par ADR avant implémentation (règle n°5 ;
  voir `docs/11-TABLEAU_DE_BORD.md`, décision « Mécanisme anti-oscillation »).
  Si elle est acceptée, l'état précédent sera passé en argument explicite
  pour préserver la pureté de la fonction — pas de variable globale.
- La plage de température déclenchant « alerte régulation thermique »
  (constat A3 — plage optimale ou plage critique de `THRESHOLDS`) est elle
  aussi une décision ouverte non tranchée ici (docs/11).
- `log_decision` écrit chaque action en **JSON Lines** (UTF-8, mode ajout)
  dans `logs/decisions.log` — le journal **du produit**, distinct du journal
  des agents (`logs/agents/journal/`, voir `.claude/rules/tracabilite.md`).
  Chaque ligne doit suffire à reconstituer la décision a posteriori
  (règle n°7).

Ce fichier est un **squelette** (phase de préparation, avant le Jalon 4) :
les corps de fonction lèvent `NotImplementedError` référencé à `docs/02` §5.
Aucune décision ouverte (A3, unités, anti-oscillation) n'est tranchée ici.
"""

from __future__ import annotations

import sys


def evaluate_conditions(reading: dict, risk_class: str, thresholds: dict) -> list[dict]:
    """Fonction pure : relevé + risque prédit -> liste d'actions simulées déclenchées.

    Entrée :
        reading : un relevé de qualité d'eau (dict de variables + timestamp,
            éventuellement avec des marqueurs `<variable>_imputed`).
        risk_class : classe de risque prédite par le Module 3
            (`"normal"` / `"vigilance"` / `"critique"`, voir `config.RISK_CLASSES`).
        thresholds : table des seuils scientifiques (voir `src/config.py`,
            `THRESHOLDS`).

    Sortie :
        Liste de dicts d'action, chacun au format
        `{timestamp, action, reason, triggered_by, values, threshold,
        priority, simulated}` (`triggered_by` = identifiant de règle
        déclarative ou `"model"` pour une alerte issue de `risk_class`,
        `simulated` toujours `True`). Liste vide si aucune règle ne se
        déclenche. Si plusieurs actions se déclenchent simultanément, elles
        sont ordonnées par priorité explicite (règle n°2). Une valeur absente
        ou imputée-manquante ne déclenche jamais d'action (règle n°4).

    Non implémenté avant le Jalon 4 (docs/02 §5, docs/04 — Jalon 4).
    """
    raise NotImplementedError(
        "Jalon 4 — evaluate_conditions non implémenté (docs/02 §5 ; règles "
        "n°1-5 automation-engineer)"
    )


def log_decision(action: dict, log_path: str = "logs/decisions.log") -> None:
    """Ajoute une action simulée au journal de décisions (JSON Lines, UTF-8, ajout).

    Entrée :
        action : dict d'action au format produit par `evaluate_conditions`
            (`{timestamp, action, reason, triggered_by, values, threshold,
            priority, simulated}`).
        log_path : chemin du fichier journal (défaut : `"logs/decisions.log"`,
            voir `src/config.py` — `DECISIONS_LOG_PATH`, section « Chemins »).

    Sortie :
        Aucune valeur de retour ; effet de bord voulu : une ligne JSON ajoutée
        à `log_path` (append, jamais de réécriture du fichier). Cette ligne
        seule doit suffire à reconstituer la décision a posteriori (règle
        n°7). Distinct du journal des agents (`logs/agents/journal/`).

    Non implémenté avant le Jalon 4 (docs/02 §5, docs/04 — Jalon 4).
    """
    raise NotImplementedError(
        "Jalon 4 — log_decision non implémenté (docs/02 §5 ; règle n°7 "
        "automation-engineer)"
    )


if __name__ == "__main__":
    # `python -m src.decision_engine` doit rejouer un scénario de test défini
    # et produire un log d'exemple, sans dashboard (règle n°8
    # automation-engineer, docs/04 — Jalon 4). Squelette : message clair et
    # code de sortie non nul, sans trace d'exception brute.
    print(
        "Erreur : moteur de décision non implémenté (Jalon 4). "
        "Voir docs/04-JALONS_VALIDATION.md, Jalon 4, et docs/02 §5.",
        file=sys.stderr,
    )
    sys.exit(1)
