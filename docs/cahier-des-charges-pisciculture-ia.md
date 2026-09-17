# Cahier des charges — Système IA de suivi, prédiction et automatisation pour bac de pisciculture (Silure)

## 1. Contexte et problématique

Le silure (*Clarias gariepinus* / poisson-chat africain) est une espèce d'élevage majeure en Afrique subsaharienne, appréciée pour sa résistance et sa forte demande locale. Cependant, la production reste souvent sous-optimale à cause d'un manque de suivi rigoureux des paramètres de qualité d'eau (température, oxygène dissous, pH, ammoniac, nitrate, turbidité) et d'une gestion manuelle sujette à l'erreur humaine, qui peut entraîner stress, ralentissement de croissance, voire mortalité des poissons.

**Problématique retenue :** Comment un système combinant suivi en temps réel, prédiction par IA et automatisation des actions correctives peut-il garantir une production optimale dans un bac de pisciculture de silure ?

## 2. Objectifs du projet

### Objectif général
Concevoir un MVP (Minimum Viable Product) démontrant un pipeline complet : **données → analyse → prédiction → décision → action**, appliqué à un bac de pisciculture de silure.

### Objectifs spécifiques
1. Collecter et valider un jeu de données réel de qualité d'eau en aquaculture de silure
2. Développer un module de suivi (monitoring) visualisant l'état du bac et les alertes
3. Développer un ou plusieurs modèles IA de prédiction (anomalies qualité d'eau et/ou croissance)
4. Développer une logique d'automatisation simulée qui réagit aux prédictions/seuils critiques
5. Livrer une démonstration fonctionnelle bout-en-bout en 7 jours

## 3. Périmètre (scope)

### Dans le périmètre (MVP)
- Traitement d'un dataset réel téléchargé (pas de génération de données fictives comme source primaire)
- Nettoyage, exploration et structuration des données
- Modèle(s) IA simple(s) et explicable(s) (pas de deep learning complexe)
- Dashboard de visualisation (simulé temps réel à partir des données historiques)
- Moteur de règles/automatisation simulé (pas de matériel physique réel)
- Documentation technique du pipeline

### Hors périmètre
- Rédaction du mémoire académique (texte, mise en forme) — traitée séparément par Alfred
- Déploiement matériel réel (capteurs IoT physiques, actionneurs physiques)
- Interface mobile
- Authentification / multi-utilisateurs / production réelle

## 4. Source de données

**Dataset retenu :** *Sensor Based Aquaponics Fish Pond Datasets* (Udanor, Ogbuokiri et al., Université du Nigeria Nsukka)
- URL : https://www.kaggle.com/datasets/ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets
- Contexte : bacs aquaponiques de silure (catfish), Nigeria
- Capteurs : température, turbidité, oxygène dissous (DO), pH, ammoniac, nitrate
- Données additionnelles : caractéristiques physiques du poisson (longueur, largeur, population)
- Fréquence de collecte : ~5 secondes (via microcontrôleur ESP32)
- Référence académique : Udanor et al., *Data in Brief*, 2022, DOI: 10.1016/j.dib.2022.108400

**Dataset de secours (si volume/qualité insuffisants) :** *Pondsdata* — 74 759 relevés IoT sur un an (Inde, autres espèces), utilisable pour enrichir/comparer si besoin.

**Étape de validation à faire en premier (avant tout développement) :**
- Télécharger le dataset et vérifier : nombre de lignes, colonnes réelles disponibles, valeurs manquantes, plage de dates, cohérence des unités
- Confirmer si des labels d'anomalies ou de croissance sont présents, ou s'ils doivent être dérivés/simulés à partir des seuils scientifiques connus pour le silure

## 5. Paramètres de référence pour le silure (à utiliser pour les seuils et la validation)

| Paramètre | Plage optimale | Seuil critique (indicatif) |
|---|---|---|
| Température | 26–32°C | < 20°C ou > 35°C |
| Oxygène dissous (DO) | > 4 mg/L | < 3 mg/L |
| pH | 6.5–8.5 | < 6 ou > 9 |
| Ammoniac (NH3) | < 0.05 mg/L | > 0.1 mg/L |
| Nitrate | < 50 mg/L | > 100 mg/L |
| Turbidité | selon dataset | à définir après exploration |

*(Ces valeurs sont indicatives et doivent être recoupées avec la littérature scientifique citée dans le mémoire.)*

## 6. Architecture fonctionnelle

```
[Dataset Kaggle brut]
        ↓
[Module 1 — Ingestion & nettoyage]
   - chargement, typage, gestion valeurs manquantes/aberrantes
   - normalisation des unités et du format temporel
        ↓
[Module 2 — Exploration & feature engineering]
   - statistiques descriptives, corrélations
   - création de variables dérivées (moyennes glissantes, écarts aux seuils)
        ↓
[Module 3 — Modèle(s) IA]
   a) Détection d'anomalies / classification de risque qualité d'eau
   b) (optionnel si temps) Prédiction de croissance/poids
        ↓
[Module 4 — Moteur de décision / automatisation simulée]
   - règles + sorties du modèle → déclenchement d'actions simulées
     (aération, renouvellement d'eau, alerte alimentation)
   - journal des décisions (log)
        ↓
[Module 5 — Dashboard de suivi]
   - visualisation des paramètres, alertes actives, état des actionneurs simulés
   - rejoue les données historiques comme un flux "temps réel" simulé
```

## 7. Stack technique retenue

- **Langage :** Python
- **Traitement de données :** pandas, numpy
- **Modélisation :** scikit-learn (Random Forest, Isolation Forest, régression) — modèles simples et interprétables, privilégiés pour la soutenance
- **Dashboard :** Streamlit (rapide à mettre en place, adapté au MVP)
- **Environnement de dev :** assisté par Claude Code
- **Stockage :** fichiers CSV/Parquet locaux (pas de base de données nécessaire pour le MVP)

## 8. Livrables attendus du MVP

1. Script(s) d'ingestion et nettoyage du dataset réel
2. Notebook ou script d'exploration (EDA) avec visualisations clés
3. Modèle(s) IA entraîné(s) et évalué(s) (métriques de performance incluses)
4. Moteur de règles/automatisation simulé avec journal des décisions
5. Dashboard Streamlit fonctionnel présentant les 3 briques (suivi, prédiction, automatisation)
6. Scénario de démonstration reproductible (ex : rejouer une séquence avec anomalie et montrer la réaction du système)
7. README technique expliquant comment lancer le projet

## 9. Plan d'exécution — 7 jours

| Jour | Objectif |
|---|---|
| 1 | Téléchargement + validation du dataset, cadrage final des colonnes/seuils |
| 2 | Ingestion, nettoyage, structuration des données |
| 3 | Exploration (EDA), feature engineering |
| 4 | Développement et évaluation du/des modèle(s) IA |
| 5 | Moteur de règles/automatisation simulé |
| 6 | Dashboard Streamlit + intégration bout-en-bout |
| 7 | Tests du scénario de démo, corrections, README technique |

## 10. Critères de succès du MVP

- Le pipeline fonctionne de bout en bout sans intervention manuelle une fois lancé
- Le modèle IA produit des prédictions/alertes cohérentes avec les seuils scientifiques du silure
- Le dashboard permet de visualiser clairement l'état du bac et les décisions prises
- Le système est démontrable en direct (scénario reproductible) devant un jury
- Le code est structuré et commenté suffisamment pour être repris/expliqué dans le mémoire

## 11. Notes pour Claude Code

- Prioriser la simplicité et l'explicabilité des modèles sur la sophistication
- Structurer le projet en modules séparés (voir section 6) pour faciliter l'explication de chaque brique
- Prévoir des logs clairs à chaque étape de décision automatisée (traçabilité pour la soutenance)
- Ne pas développer de fonctionnalités hors périmètre (section 3) sans validation préalable
