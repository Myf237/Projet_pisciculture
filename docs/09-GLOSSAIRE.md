# Glossaire

| Terme | Définition |
|---|---|
| **DO (Dissolved Oxygen)** | Oxygène dissous dans l'eau, en mg/L — paramètre vital pour la respiration des poissons |
| **NTU** | Nephelometric Turbidity Unit — unité de mesure de la turbidité (trouble) de l'eau |
| **pH** | Mesure de l'acidité/basicité de l'eau (échelle 0–14) |
| **Ammoniac (NH3)** | Composé toxique pour les poissons issu des déjections et de la décomposition organique, à surveiller de près |
| **Nitrate** | Produit final du cycle de l'azote dans l'eau, moins toxique que l'ammoniac mais à surveiller à haute concentration |
| **Silure (Clarias gariepinus)** | Poisson-chat africain, espèce d'élevage résistante, largement utilisée en aquaculture en Afrique subsaharienne |
| **IoT (Internet of Things)** | Réseau de capteurs connectés collectant et transmettant des données en continu |
| **Isolation Forest** | Algorithme de machine learning non supervisé utilisé pour la détection d'anomalies |
| **Random Forest** | Algorithme de machine learning basé sur un ensemble d'arbres de décision, utilisé ici pour la classification de risque et/ou la régression de croissance |
| **MVP (Minimum Viable Product)** | Version minimale mais fonctionnelle d'un produit, démontrant sa valeur sans être complète |
| **ADR (Architecture Decision Record)** | Document court traçant une décision technique, son contexte et sa justification |
| **Feature engineering** | Processus de création de variables dérivées à partir des données brutes pour améliorer la performance d'un modèle |
| **Rolling feature (feature glissante)** | Statistique calculée sur une fenêtre temporelle mobile (ex. moyenne sur la dernière heure) |
| **Split temporel** | Découpage d'un jeu de données en train/test respectant l'ordre chronologique (par opposition à un découpage aléatoire), nécessaire pour les séries temporelles |
| **RMSE / MAE** | Root Mean Squared Error / Mean Absolute Error — métriques d'erreur pour évaluer un modèle de régression |
| **Baseline** | Méthode de référence simple (ici : règles de seuils seules) à laquelle un modèle est comparé ; un modèle n'a de valeur que s'il fait mieux que sa baseline |
| **Fuite de données (data leakage)** | Utilisation, pendant l'entraînement, d'une information qui ne serait pas disponible au moment de la prédiction (données futures, statistiques calculées sur le jeu de test) ; elle gonfle artificiellement les performances |
| **Feature causale** | Variable calculée uniquement à partir d'observations passées ou présentes (fenêtre glissante tournée vers le passé), utilisable en temps réel |
| **Hystérésis** | Écart volontaire entre le seuil de déclenchement et le seuil d'arrêt d'une action (ex. aérateur activé sous 3 mg/L, arrêté au-dessus de 4 mg/L) pour éviter les oscillations marche/arrêt |
| **Agent (Claude Code)** | Instance de Claude chargée d'un rôle précis ; la session principale joue l'orchestrateur et délègue aux sous-agents |
| **Sous-agent** | Agent spécialisé défini dans `.claude/agents/`, avec sa mission, ses outils autorisés et ses règles, qui exécute une tâche déléguée et rend un compte rendu |
| **Orchestrateur** | Rôle de la session principale : planifier, déléguer, contrôler le rythme et tenir les points de validation humaine |
| **Skill** | Procédure réutilisable de Claude Code (`.claude/skills/`), invoquée par une commande, ex. `/valider-jalon 1` |
| **Hook** | Script exécuté automatiquement par Claude Code à un moment précis (après un outil, à la fin d'un sous-agent…) ; utilisé ici pour la journalisation et les garde-fous |
| **Point de validation humaine (gate)** | Étape du workflow où l'autonomie des agents s'arrête et où une décision humaine est requise (G1 à G4) |
| **Jalon** | Étape du projet associée à un livrable et à des critères de validation vérifiables (`04-JALONS_VALIDATION.md`) |
| **Traçabilité** | Capacité à reconstituer après coup quelle action a été effectuée, par quel agent, pourquoi et avec quel résultat |
| **Dépôt distant (`origin`)** | Copie du dépôt git hébergée en ligne (ici `https://github.com/Myf237/Projet_pisciculture.git`, public) vers laquelle les branches locales sont poussées |
| **Branche** | Ligne de développement isolée dans git ; ce projet utilise une branche par jalon ou par sujet, créée depuis `main` à jour, jamais modifiée directement sur `main` (`.claude/rules/git-workflow.md`) |
| **Conventional Commits** | Convention de rédaction des messages de commit (`type(portée): résumé`, ex. `feat(ingestion): …`) qui rend l'historique lisible et exploitable automatiquement |
| **Trailer git** | Ligne `Clé: valeur` en fin de message de commit (ex. `Agent:`, `Jalon:`, `Journal:`) qui relie un commit à sa traçabilité (agent, jalon, entrée de journal) |
| **Pull request (PR)** | Proposition de fusion d'une branche vers `main`, revue avant intégration ; ce projet impose le modèle `.github/pull_request_template.md` et le go humain (G2) |
| **Merge commit** | Commit de fusion qui intègre tous les commits d'une branche dans `main` en conservant leur historique individuel (par opposition à un squash ou un rebase) |
| **Tag** | Repère nommé sur un commit précis ; ce projet pose un tag annoté `jalon-N` après la fusion de chaque jalon validé |
