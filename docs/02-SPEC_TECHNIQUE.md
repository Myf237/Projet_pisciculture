# Spécification technique — MVP Suivi/Prédiction/Automatisation Pisciculture (Silure)

Référence : voir `cahier-des-charges-pisciculture-ia.md` pour le contexte projet complet. Ce document détaille les exigences techniques d'implémentation.

## 1. Entrée du système

- Fichier source : `IoTpond1.csv` (voir `01-DATA_DICTIONARY.md` pour le détail des colonnes et anomalies)
- Le système doit être conçu pour accepter potentiellement d'autres fichiers du même schéma (IoTpond2.csv, etc.) sans modification de code — le chemin du fichier est un paramètre, pas une valeur en dur.

## 2. Module 1 — Ingestion & nettoyage

**Entrée :** CSV brut
**Sortie :** DataFrame nettoyé (+ fichier `data/processed/pond1_clean.csv`)

Exigences :
- Parser `created_at` en datetime, retirer le suffixe timezone, trier chronologiquement
- Appliquer les règles de nettoyage définies dans `01-DATA_DICTIONARY.md` (bornes physiques réalistes par variable)
- Stratégie d'imputation pour valeurs exclues : interpolation temporelle (pas de suppression pure des lignes, pour ne pas casser la continuité temporelle) — à documenter et justifier
- Reconstruire une courbe de croissance propre pour `Fish_Length`/`Fish_Weight` en dédupliquant les paliers de mesure (garder un point par changement de valeur, avec son timestamp)
- Produire un rapport de nettoyage (nombre de valeurs corrigées/exclues par colonne) — utile pour le mémoire

## 3. Module 2 — Exploration & feature engineering

**Entrée :** données nettoyées
**Sortie :** dataset enrichi avec features dérivées + notebook/rapport d'exploration

Features à créer :
- Moyennes/écarts-types glissants (ex. fenêtre 1h) par variable de qualité d'eau
- Écart par rapport aux seuils optimaux définis pour le silure (variable binaire ou continue "distance au seuil critique")
- Taux de croissance instantané (dérivée de `Fish_Weight` entre deux mesures)
- Agrégation temporelle (ex. moyenne horaire) pour réduire le bruit et le volume avant modélisation

Livrable exploration :
- Distributions avant/après nettoyage
- Corrélations entre variables de qualité d'eau et croissance
- Visualisation de la série temporelle complète avec les anomalies mises en évidence

## 4. Module 3 — Modèle(s) IA

### 4.1 Détection d'anomalies / risque qualité d'eau (obligatoire pour le MVP)
- Approche : Isolation Forest **ou** règles de seuils combinées à un classifieur simple (Random Forest) sur des anomalies synthétiques injectées à partir des seuils scientifiques (car le dataset ne fournit pas de label d'anomalie explicite)
- Sortie : score de risque + classe (normal / vigilance / critique)
- Évaluation : matrice de confusion sur un jeu de test avec anomalies injectées connues, + inspection visuelle sur la série temporelle réelle

### 4.2 Prédiction de croissance (si le temps le permet — priorité 2)
- Approche : régression (Random Forest Regressor ou régression linéaire) prédisant `Fish_Weight` à partir des variables de qualité d'eau agrégées et du temps écoulé depuis l'empoissonnement
- Évaluation : MAE/RMSE sur un split temporel (train sur les 2/3 premiers du cycle, test sur le dernier tiers — pas de split aléatoire, car série temporelle)

**Principe directeur :** privilégier des modèles simples et interprétables (feature importances exploitables) plutôt que des architectures complexes — c'est un critère de soutenabilité en soutenance de mémoire.

## 5. Module 4 — Moteur de décision / automatisation simulée

**Entrée :** relevé courant (réel ou rejoué) + sortie du modèle de risque
**Sortie :** décision(s) d'action + entrée de log

Règles de base (déclenchement simulé, pas de matériel réel) :

| Condition | Action simulée |
|---|---|
| DO < seuil critique | Déclencher "aérateur ON" |
| Ammoniac (nettoyé) > seuil critique | Déclencher "renouvellement d'eau" |
| Température hors plage | Déclencher "alerte régulation thermique" |
| Modèle de risque = "critique" | Déclencher "alerte prioritaire" + action préventive associée |

Exigences :
- Chaque décision doit être journalisée avec : timestamp, valeurs déclenchantes, action prise, source (règle ou modèle)
- Le moteur doit être testable indépendamment du dashboard (fonction pure entrée→décision)

## 6. Module 5 — Dashboard de suivi

**Techno :** Streamlit

Fonctionnalités minimales :
- Graphique des paramètres de qualité d'eau dans le temps, avec seuils affichés
- Indicateur d'état actuel du bac (normal / vigilance / critique)
- Liste des actions/alertes déclenchées (issues du log du Module 4)
- Mode "rejeu" : possibilité de faire défiler les données historiques comme un flux simulé pour la démonstration

## 7. Exigences non-fonctionnelles

- Code modulaire : chaque module (1 à 5) doit être un module Python indépendant et testable isolément
- Reproductibilité : un seul point d'entrée (script ou notebook principal) doit permettre de rejouer tout le pipeline
- Explicabilité : toute décision automatisée ou prédiction doit pouvoir être justifiée (feature importance, seuils déclenchants)
- Pas de dépendance à du matériel ou une API externe payante

## 8. Critères d'acceptation du MVP (Definition of Done)

- [ ] Les données nettoyées ne contiennent plus de valeurs physiquement impossibles
- [ ] Le modèle de détection de risque produit des alertes cohérentes sur au moins un scénario d'anomalie connu
- [ ] Le moteur de décision déclenche les bonnes actions simulées face à des cas de test définis à l'avance
- [ ] Le dashboard affiche correctement l'état du bac et permet de rejouer un scénario de démonstration
- [ ] L'ensemble du pipeline peut être exécuté de bout en bout sans intervention manuelle
