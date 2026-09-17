# Timeline d'exécution — 7 jours

Hypothèse : sessions de travail quotidiennes avec assistance de Claude Code. Chaque jour se termine par une auto-vérification par rapport aux critères du jalon correspondant (`04-JALONS_VALIDATION.md`).

**Dates retenues (révisées le 2026-09-18, ADR-008) :** Jour 1 = vendredi 18/09/2026 → Jour 6 = mercredi 23/09/2026 (démonstration, date maintenue). Remplace le planning initial de l'ADR-006 (Jour 1 = mercredi 17/09/2026 → Jour 7 = mardi 23/09/2026).

**Référence de planning :** ce document fait foi. Le plan du cahier des charges (§9) prévoyait un Jour 1 consacré à la seule validation du dataset et un Jour 2 à l'ingestion ; la version initiale de ce document (ADR-006) regroupait déjà validation, ingestion et nettoyage au Jour 1. Le cahier des charges étant gelé, l'écart reste tracé ici et dans `07-JOURNAL_DECISIONS.md`.

**Replanification du 2026-09-18 (ADR-008, remplace l'ADR-006) :** la mise en place du dépôt (structure, garde-fous, pull requests) a occupé la journée du 2026-09-17 ; aucun jalon n'a démarré à la date initialement prévue par l'ADR-006. Décision humaine (G3) : la démonstration reste fixée au 2026-09-23 ; les Jalons 1 et 2 sont regroupés au nouveau Jour 1 (2026-09-18) pour rattraper le retard, sans décaler la fin du projet. Le tableau ci-dessous reflète ce planning révisé ; l'ancien planning (Jour 1 = 17/09 à Jour 7 = 23/09) reste consultable dans l'historique de ce document et dans l'ADR-006 (statut « Remplacé par ADR-008 »).

**Pilotage :** chaque journée commence par `/demarrer-session` et se termine par `/cloturer-session` ; un jalon est vérifié par `/valider-jalon N` puis validé par l'humain (voir `10-GOUVERNANCE_AGENTS.md`). L'état réel d'avancement est suivi dans `11-TABLEAU_DE_BORD.md`.

## Jour 1 (ven. 18/09/2026) — Fondations, nettoyage et exploration (Jalons 1 et 2)
- Trancher les décisions bloquantes sur les données : unités (A1), bornes physiques (A2), fuseau horaire, ammoniac (ADR-003)
- Implémentation de `ingestion.py` : chargement + nettoyage + reconstruction courbe de croissance
- Génération du rapport de nettoyage
- Notebook d'exploration : distributions, corrélations, visualisation des anomalies
- Implémentation de `features.py` (rolling features, écart aux seuils, taux de croissance)
- Décision sur la stratégie de ré-échantillonnage (horaire recommandé)
- **Checkpoint fin de journée :** Jalon 1 **et** Jalon 2 validés (deux vérifications distinctes du qa-validator) avant de continuer

## Jour 2 (sam. 19/09/2026) — Modèle de détection de risque (Jalon 3, partie 1)
- Baseline « règles de seuils seules » (point de comparaison obligatoire, constat A4)
- Génération des anomalies synthétiques (injection basée sur seuils, complétée par des anomalies non triviales : dérive, capteur figé, saut)
- Entraînement du modèle de détection (Isolation Forest ou Random Forest classifieur)
- Premiers résultats d'évaluation

## Jour 3 (dim. 20/09/2026) — Consolidation modèle + démarrage prédiction croissance (Jalon 3, partie 2)
- Ajustement du modèle de détection selon résultats du Jour 2
- Test sur un passage réel du dataset avec dérive visible (ex. pic d'ammoniac)
- Si temps disponible : premier modèle de prédiction de croissance (priorité 2)
- **Point de bascule** (anciennement « règle du Jour 4 » du planning initial, ADR-006 ; nom conservé, appliqué désormais le 2026-09-20 — ADR-008) : si le modèle de détection prend du retard, **couper la prédiction de croissance** (priorité 2, hors du chemin critique) plutôt que de compresser les jours suivants
- **Checkpoint fin de journée :** Jalon 3 validé

## Jour 4 (lun. 21/09/2026) — Moteur de décision (Jalon 4)
- Implémentation de `decision_engine.py`
- Tests unitaires sur chaque règle (cas limites)
- Génération d'un fichier de log d'exemple sur un scénario de test
- **Checkpoint fin de journée :** Jalon 4 validé

## Jour 5 (mar. 22/09/2026) — Dashboard et intégration (Jalon 5)
- Développement de `dashboard/app.py` (Streamlit)
- Intégration du mode rejeu historique
- Connexion du dashboard au moteur de décision et au modèle
- **Checkpoint fin de journée :** Jalon 5 validé

## Jour 6 (mer. 23/09/2026) — Intégration finale, démo et documentation (Jalon 6)
- Script/pipeline d'exécution bout-en-bout unique
- Construction et répétition du scénario de démonstration (anomalie → détection → décision → affichage)
- Rédaction du README technique
- **Checkpoint fin de journée :** Jalon 6 validé + validation finale mémoire

## Marges de sécurité

- Le Jour 3 (2026-09-20) est le point de bascule (anciennement « Jour 4 » dans le planning initial de l'ADR-006) : si le modèle de détection prend du retard, **couper la prédiction de croissance** (priorité 2, explicitement hors du chemin critique) plutôt que de compresser les jours suivants
- Si un jalon n'est pas validé en fin de journée, traiter le lendemain matin en priorité avant d'entamer le jalon suivant — ne jamais accumuler deux jalons non validés en parallèle
- **Plus aucune marge après la replanification du 2026-09-18 (ADR-008)** : la démonstration reste fixée au 2026-09-23 ; un retard supplémentaire n'est plus absorbable par un jour tampon (voir `08-REGISTRE_RISQUES.md`, R1, probabilité relevée)

*Planning révisé le 2026-09-18 (ADR-008, remplace l'ADR-006, J-20260918-012) : Jalons 1 et 2 regroupés au 18/09 après une journée de mise en place non comptée comme jalon ; démonstration maintenue au 23/09.*
