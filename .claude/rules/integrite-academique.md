# Intégrité académique — tous les agents

Ce projet sert de support à un mémoire soutenu devant un jury : la démarche compte autant que le résultat.

## Honnêteté des résultats

- Ne jamais inventer, arrondir favorablement ou extrapoler un résultat, une métrique ou un chiffre. Tout chiffre cité provient d'une exécution réelle, avec sa source (commande, fichier de sortie).
- Rapporter les résultats décevants ou négatifs tels quels : ils sont discutables dans le mémoire, pas à cacher.
- Toute métrique d'un modèle est présentée **à côté de la baseline « règles de seuils seules »** : un modèle qui n'apporte rien au-delà des seuils doit être dit comme tel.
- Distinguer clairement ce qui a été **mesuré** (données réelles), **injecté** (anomalies synthétiques) et **supposé** (hypothèses).

## Données et limites

- Les anomalies du dataset (capteurs, unités, fréquence irrégulière, absence de labels) sont documentées explicitement dans `docs/01-DATA_DICTIONARY.md` et `docs/08-REGISTRE_RISQUES.md`.
- Toute hypothèse sur les données (unité réelle d'une colonne, fuseau horaire, nature d'une valeur aberrante) est marquée comme hypothèse et tranchée par ADR.

## Références scientifiques

- Aucune référence bibliographique, DOI, auteur ou valeur de seuil inventé.
- Une référence non vérifiée dans une base académique est marquée « à vérifier ».
- Les seuils du silure proviennent du cahier des charges §5 ou d'une source citée ; toute nouvelle valeur cite sa source.

## Vocabulaire

- Toujours « actionneur simulé », « action simulée », « flux temps réel simulé (rejeu) » — jamais de formulation laissant croire à un contrôle matériel réel (risque R5).
- « Prédiction » et « détection » ne sont pas synonymes : utiliser le terme exact.
- Ne pas qualifier un modèle de « performant » sans métrique et sans comparaison à la baseline.
