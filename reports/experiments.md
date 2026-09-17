# Registre des essais de modélisation — Module 3

> Tenu par l'agent `ml-engineer` (Jalon 3). Référence : `docs/02-SPEC_TECHNIQUE.md` §4, `docs/04-JALONS_VALIDATION.md` Jalon 3, ADR-002.

## Rôle

Ce registre conserve **chaque essai** de modélisation (détection de risque et prédiction de croissance), qu'il soit gardé ou rejeté. Il permet de reconstituer après coup ce qui a été essayé, avec quel résultat face à la baseline, et pourquoi un choix a été retenu. Il sert de source aux sections « méthode » et « résultats » du mémoire.

## Règles de tenue

1. **Une ligne par essai**, ajoutée à la fin du tableau, avec un identifiant séquentiel `E-NNN`.
2. **Jamais de suppression ni de réécriture** : un essai rejeté reste visible ; une correction est une nouvelle ligne qui cite l'essai corrigé.
3. **Baseline toujours à côté** : les métriques du modèle sont publiées à côté de celles de la baseline évaluée sur le même jeu de test (« règles de seuils seules » pour la détection de risque, baseline naïve pour la croissance).
4. **Métriques mesurées uniquement** : chaque chiffre provient d'une exécution réelle, tracée dans le journal des agents ; aucune valeur arrondie favorablement.
5. **Métriques adaptées** : détection de risque — précision, rappel et F1 par classe (rappel de la classe critique en premier), résultats par type d'anomalie injectée ; jamais l'accuracy seule. Croissance — MAE et RMSE sur le dernier tiers du cycle.
6. **Décision explicite** : « gardé » ou « rejeté », avec la raison en une phrase dans la colonne Changement ou Décision.
7. **Preuve** : chemin de la fiche du modèle (`models/<nom>_v<N>.json`, avec date, SHA-256 des données, features, paramètres, graine, métriques modèle et baseline) et référence de l'entrée de journal `J-…`.

## Essais

| Id | Date | Changement | Métriques modèle | Métriques baseline | Décision | Fiche modèle | Journal |
|---|---|---|---|---|---|---|---|

*Aucun essai enregistré à ce jour (phase de préparation).*
