# Jalons de travail et critères de validation

Chaque jalon correspond à un module fonctionnel. Un jalon n'est considéré "validé" que si tous ses critères sont remplis — ne pas avancer au jalon suivant sur une base non validée, sous peine de propager des erreurs de données dans les modèles.

## Jalon 1 — Données nettoyées et fiables

**Livrable :** `data/processed/pond1_clean.csv` + rapport de nettoyage

**Critères de validation :**
- [ ] Aucune valeur de température hors de [0, 40]°C
- [ ] Aucune valeur de pH hors de [0, 14] (idéalement resserré à une plage réaliste)
- [ ] Ammoniac : outliers extrêmes traités et justifiés (exclusion documentée ou transformation)
- [ ] La courbe de croissance (poids/longueur) est monotone croissante ou quasi-monotone après reconstruction des paliers
- [ ] Le rapport de nettoyage indique le nombre de valeurs corrigées par colonne

## Jalon 2 — Exploration validée

**Livrable :** notebook d'exploration + figures clés

**Critères de validation :**
- [ ] Les distributions post-nettoyage sont cohérentes avec les seuils scientifiques du silure
- [ ] Une figure montre clairement au moins une période d'anomalie détectable à l'œil (utile pour la démo et le mémoire)
- [ ] Les corrélations entre qualité d'eau et croissance sont calculées et interprétées, même si faibles

## Jalon 3 — Modèle de détection de risque opérationnel

**Livrable :** modèle entraîné + script d'évaluation

**Critères de validation :**
- [ ] Le modèle atteint une performance jugée acceptable sur les anomalies synthétiques injectées (à définir : ex. rappel > 80% sur la classe critique)
- [ ] Le modèle est testé sur au moins un passage réel du dataset contenant une dérive visible (ex. pic d'ammoniac) et produit une alerte cohérente
- [ ] Les features importantes du modèle sont identifiées et interprétables

## Jalon 4 — Moteur de décision fonctionnel

**Livrable :** `decision_engine.py` + tests unitaires + fichier de log d'exemple

**Critères de validation :**
- [ ] Pour chaque règle définie dans la spec technique, un test unitaire dédié passe (cas limite juste sous/au-dessus du seuil)
- [ ] Le journal de décisions est lisible et contient les informations nécessaires pour reconstituer une décision a posteriori
- [ ] Le moteur fonctionne indépendamment du dashboard (appelable en ligne de commande ou script isolé)

## Jalon 5 — Dashboard démontrable

**Livrable :** application Streamlit fonctionnelle

**Critères de validation :**
- [ ] Le dashboard se lance sans erreur avec une seule commande
- [ ] Le mode rejeu permet de dérouler un scénario de démonstration contenant une anomalie
- [ ] L'état du bac et les actions déclenchées sont visibles et compréhensibles sans explication supplémentaire

## Jalon 6 — MVP intégré et démontrable

**Livrable :** pipeline complet + scénario de démo scripté

**Critères de validation :**
- [ ] Un seul point d'entrée permet de dérouler tout le pipeline (données → nettoyage → features → modèle → décision → dashboard)
- [ ] Le scénario de démonstration est reproductible : deux exécutions produisent des **sorties de données identiques** (empreintes des CSV, des JSON et du journal de décisions `logs/decisions.log`). Les **images sont explicitement exclues** de ce critère — un rendu matplotlib dépend des polices installées sur la machine d'exécution, pas seulement des versions épinglées, et une empreinte d'image serait un critère invérifiable (ADR-012, 2026-09-19)
- [ ] Le README technique permet à quelqu'un d'autre (ex. un membre du jury curieux) de relancer le projet sans assistance

## Validation finale — Alignement avec le mémoire

- [ ] Chaque choix technique (seuils, modèle, règles) a une justification traçable (scientifique ou méthodologique) réutilisable dans la rédaction
- [ ] Les limites du dataset (anomalies de capteurs, absence de labels) sont explicitement documentées — c'est un point de discussion académique valorisable, pas une faiblesse à cacher
