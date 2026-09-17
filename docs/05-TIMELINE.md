# Timeline d'exécution — 7 jours

Hypothèse : sessions de travail quotidiennes avec assistance de Claude Code. Chaque jour se termine par une auto-vérification par rapport aux critères du jalon correspondant (`04-JALONS_VALIDATION.md`).

**Dates retenues :** Jour 1 = mercredi 17/09/2026 → Jour 7 = mardi 23/09/2026 (démonstration).

**Référence de planning :** ce document fait foi. Le plan du cahier des charges (§9) prévoyait un Jour 1 consacré à la seule validation du dataset et un Jour 2 à l'ingestion ; ce document regroupe validation, ingestion et nettoyage au Jour 1. Le cahier des charges étant gelé, l'écart est tracé ici et dans `07-JOURNAL_DECISIONS.md` (ADR-006).

**Pilotage :** chaque journée commence par `/demarrer-session` et se termine par `/cloturer-session` ; un jalon est vérifié par `/valider-jalon N` puis validé par l'humain (voir `10-GOUVERNANCE_AGENTS.md`). L'état réel d'avancement est suivi dans `11-TABLEAU_DE_BORD.md`.

## Jour 1 (mer. 17/09/2026) — Fondations et nettoyage (Jalon 1)
- Mise en place de la structure de dépôt (`03-ARCHITECTURE_CODE.md`)
- Trancher les décisions bloquantes sur les données : unités (A1), bornes physiques (A2), fuseau horaire, ammoniac (ADR-003)
- Implémentation de `ingestion.py` : chargement + nettoyage + reconstruction courbe de croissance
- Génération du rapport de nettoyage
- **Checkpoint fin de journée :** Jalon 1 validé avant de continuer

## Jour 2 (jeu. 18/09/2026) — Exploration et features (Jalon 2)
- Notebook d'exploration : distributions, corrélations, visualisation des anomalies
- Implémentation de `features.py` (rolling features, écart aux seuils, taux de croissance)
- Décision sur la stratégie de ré-échantillonnage (horaire recommandé)
- **Checkpoint fin de journée :** Jalon 2 validé

## Jour 3 (ven. 19/09/2026) — Modèle de détection de risque (Jalon 3, partie 1)
- Baseline « règles de seuils seules » (point de comparaison obligatoire, constat A4)
- Génération des anomalies synthétiques (injection basée sur seuils, complétée par des anomalies non triviales : dérive, capteur figé, saut)
- Entraînement du modèle de détection (Isolation Forest ou Random Forest classifieur)
- Premiers résultats d'évaluation

## Jour 4 (sam. 20/09/2026) — Consolidation modèle + démarrage prédiction croissance (Jalon 3, partie 2)
- Ajustement du modèle de détection selon résultats du Jour 3
- Test sur un passage réel du dataset avec dérive visible (ex. pic d'ammoniac)
- Si temps disponible : premier modèle de prédiction de croissance (priorité 2)
- **Checkpoint fin de journée :** Jalon 3 validé

## Jour 5 (dim. 21/09/2026) — Moteur de décision (Jalon 4)
- Implémentation de `decision_engine.py`
- Tests unitaires sur chaque règle (cas limites)
- Génération d'un fichier de log d'exemple sur un scénario de test
- **Checkpoint fin de journée :** Jalon 4 validé

## Jour 6 (lun. 22/09/2026) — Dashboard et intégration (Jalon 5)
- Développement de `dashboard/app.py` (Streamlit)
- Intégration du mode rejeu historique
- Connexion du dashboard au moteur de décision et au modèle
- **Checkpoint fin de journée :** Jalon 5 validé

## Jour 7 (mar. 23/09/2026) — Intégration finale, démo et documentation (Jalon 6)
- Script/pipeline d'exécution bout-en-bout unique
- Construction et répétition du scénario de démonstration (anomalie → détection → décision → affichage)
- Rédaction du README technique
- **Checkpoint fin de journée :** Jalon 6 validé + validation finale mémoire

## Marges de sécurité

- Le Jour 4 est le point de bascule : si le modèle de détection prend du retard, **couper la prédiction de croissance** (priorité 2, explicitement hors du chemin critique) plutôt que de compresser les jours suivants
- Si un jalon n'est pas validé en fin de journée, traiter le lendemain matin en priorité avant d'entamer le jalon suivant — ne jamais accumuler deux jalons non validés en parallèle
