# État de l'art — IoT et IA appliqués à l'aquaculture

## 1. Contexte général de la recherche

Le nombre de publications sur l'association IoT/IA et aquaculture a fortement augmenté depuis 2020, porté par la pression économique et environnementale sur une filière qui doit produire plus tout en réduisant les pertes liées à une mauvaise gestion de la qualité de l'eau. Une revue bibliométrique récente portant sur 217 articles (Scopus, 2020–2024) rapporte une hausse de recherche d'environ 75% sur cette période, avec le pH comme paramètre le plus étudié (dans la quasi-totalité des études), suivi de la température et de l'oxygène dissous — ce qui confirme la pertinence des variables retenues dans ce projet (source : revue systématique sur les capteurs IoT en aquaculture, 2020–2024).

## 2. Approches de monitoring IoT

Plusieurs travaux décrivent des architectures similaires : capteurs bas coût (température, pH, oxygène dissous, turbidité) reliés à un microcontrôleur (Arduino, ESP32), transmission des données vers une plateforme cloud, puis visualisation en temps réel. Une étude de 2024 propose une méthode d'intégration de capteurs IoT en aquaculture avec des composants Arduino pour mesurer précisément température, pH et oxygène dissous, soulignant l'importance de la fiabilité du matériel pour éviter les artefacts de mesure — un point directement pertinent ici puisque le dataset utilisé présente justement ce type d'anomalies de capteur (température à -127°C, par exemple).

Ce constat rejoint une revue de 2022 sur les systèmes de surveillance de la qualité de l'eau pour les bassins piscicoles, qui identifie le bruit de capteur et les pertes de connectivité comme des limitations récurrentes des déploiements IoT en environnement réel — ce qui légitime la nécessité d'un module de nettoyage robuste plutôt que l'usage direct des données brutes.

## 3. Approches de prédiction et de machine learning

Les modèles de type Random Forest reviennent fréquemment dans la littérature pour la prédiction de paramètres de qualité d'eau ou la classification de risque, en raison de leur bon compromis performance/interprétabilité. Une étude combinant IoT et machine learning pour la prédiction de la qualité d'eau rapporte des performances élevées (R² proche de 1) pour la prédiction de variables comme l'oxygène dissous à partir de capteurs IoT, en s'appuyant notamment sur des modèles Random Forest. De même, un système de recommandation pour la pisciculture basé sur le machine learning rapporte qu'un modèle Random Forest surpasse d'autres algorithmes testés, avec une précision autour de 92-93%.

Ces résultats confortent le choix méthodologique de ce projet : privilégier un modèle simple et interprétable (Random Forest / Isolation Forest) plutôt qu'une architecture complexe, en cohérence avec les pratiques largement documentées dans la littérature récente pour ce type de cas d'usage.

## 4. Automatisation et systèmes de décision

Plusieurs travaux vont au-delà du simple monitoring pour proposer des systèmes de décision automatisée : déclenchement d'aérateurs, de systèmes d'alimentation ou de renouvellement d'eau à partir de règles ou de sorties de modèles prédictifs. Un système de prise de décision IoT pour le suivi en temps réel de bassins piscicoles illustre cette approche en combinant capteurs, seuils et logique de décision pour l'aide à la gestion. Ce projet s'inscrit dans cette même logique, avec un moteur de décision basé sur des règles combinées aux sorties du modèle de détection de risque.

## 5. Tendances plus récentes (au-delà du périmètre du MVP)

La littérature la plus récente (2024–2025) s'oriente vers des approches plus avancées : deep learning pour la détection visuelle (comptage de poissons, détection de poissons morts via YOLOv8), IA générative appliquée à l'aquaculture, jumeaux numériques ("digital twins"), et optimisation quantique combinée au machine learning pour la prédiction de qualité d'eau. Ces approches représentent l'état de l'art avancé du domaine, mais dépassent le périmètre raisonnable d'un MVP réalisé en 7 jours. Ce choix de simplicité (modèles classiques de machine learning plutôt que deep learning) doit être explicitement assumé et justifié dans le mémoire comme une décision de scope, et non comme une méconnaissance de l'état de l'art.

## 6. Positionnement du projet par rapport à la littérature

- Le projet reprend une architecture IoT → nettoyage → modèle → décision → dashboard cohérente avec les pratiques documentées dans la littérature
- Le choix de modèles interprétables (Random Forest, Isolation Forest) est aligné avec plusieurs études récentes obtenant de bonnes performances avec ces approches
- La gestion des artefacts de capteurs (anomalies physiquement impossibles) est un axe explicitement discuté dans la littérature comme un défi réel des déploiements IoT — ce projet le traite frontalement plutôt que de l'ignorer
- Limite de mesure distincte des artefacts : deux des six paramètres de qualité d'eau du dataset (`Ammonia`, `Nitrate`) sont en réalité mesurés par des capteurs de **gaz** suspendus au-dessus de l'eau, et non par des sondes immergées (article source du dataset, ADR-009, `07-JOURNAL_DECISIONS.md`) — une limitation de mesure à assumer explicitement dans le mémoire, distincte du bruit de capteur classique discuté dans la littérature
- Le projet ne prétend pas être à la pointe de la recherche (deep learning, jumeaux numériques) mais applique un état de l'art "raisonnable et éprouvé", pertinent pour un MVP académique en temps contraint

## 7. Références principales

- Chiu, Yan, Bhat, Huang (2022). *Development of smart aquaculture farm management system using IoT and AI-based surrogate models.* Journal of Agriculture and Food Research.
- Manoj, Dhilip Kumar, Arif, Bulai, Bulai, Geman (2022). *State of the art techniques for water quality monitoring systems for fishponds using IoT and underwater sensors: a review.* Sensors, 22(6), 2088.
- Revue sur le rôle de l'IA dans la surveillance de la croissance et de la santé des poissons pour une aquaculture durable (2023), Aquaculture International.
- IoT-enabled effective real-time water quality monitoring method for aquaculture (2024), MethodsX.
- Intelligent Prediction and Continuous Monitoring of Water Quality in Aquaculture: Integration of Machine Learning and IoT for Sustainable Management (2025), Water (MDPI).
- Monitoring water quality metrics of ponds with IoT sensors and machine learning to predict fish species survival — revue bibliométrique 2020–2024.
- Hossain Apu, Rahman, Ahmed (2024). *IoT-Based Fish Recommendation System: A Machine Learning Approach via Mobile Application for Precision Agriculture.* International Journal of Information Engineering and Electronic Business, 16(6), 71-85.
- A Review of Generative AI in Aquaculture: Foundations, Applications, and Future Directions for Smart and Sustainable Farming (2025), arXiv.
- IoT-Based Environmental Control System for Fish Farms with Sensor Integration and Machine Learning Decision Support (2023), arXiv.

*Note : cette liste doit être complétée et vérifiée dans les bases académiques (Google Scholar, ScienceDirect, IEEE Xplore) avant intégration finale au mémoire — les résumés ci-dessus sont des synthèses de travail, pas des citations à reprendre telles quelles.*
