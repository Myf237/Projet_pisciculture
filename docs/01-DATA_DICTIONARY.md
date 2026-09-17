# Dictionnaire de données — IoTpond1.csv

Fichier fourni : `IoTpond1.csv` — un des jeux de données du dataset *Sensor Based Aquaponics Fish Pond Datasets* (Udanor/Ogbuokiri et al.), un bac parmi ceux disponibles dans le dataset complet.

## Vue d'ensemble

- **Lignes :** 83 126
- **Période couverte :** 19 juin 2021 → 13 octobre 2021 (≈ 116 jours, un cycle d'élevage quasi complet)
- **Fréquence nominale :** ~20 secondes entre relevés (variable, avec des écarts occasionnels plus longs — voir section anomalies)
- **Fuseau horaire des timestamps :** CET (indiqué dans la colonne brute, à retirer/normaliser)

## Colonnes

| Colonne | Type | Description | Plage observée | Valeurs manquantes |
|---|---|---|---|---|
| `created_at` | datetime (string, suffixe " CET") | Horodatage du relevé | 2021-06-19 → 2021-10-13 | 0 |
| `entry_id` | int | Identifiant séquentiel du relevé | 1889 → 247405 | 0 |
| `Temperature (C)` | float | Température de l'eau | **-127.0 → 27.75** ⚠️ | 0 |
| `Turbidity(NTU)` | int | Turbidité de l'eau | 1 → 100 | 0 |
| `Dissolved Oxygen(g/ml)` | float | Oxygène dissous | 0.007 → 41.046 | 0 |
| `PH` | float | pH de l'eau | **-0.586 → 8.552** ⚠️ | 0 |
| `Ammonia(g/ml)` | float | Ammoniac | **0.0068 → 4.27e11** ⚠️⚠️ | 52 |
| `Nitrate(g/ml)` | int | Nitrate | 45 → 1936 | 0 |
| `Population` | int | Population de poissons dans le bac | constante = 50 | 0 |
| `Fish_Length(cm)` | float | Longueur du poisson (mesure périodique, pas continue) | 7.11 → 33.45 | 2 |
| `Fish_Weight(g)` | float | Poids du poisson (mesure périodique) | 2.91 → 318.64 | 2 |

## Anomalies identifiées (à traiter dans le module de nettoyage)

1. **Température :** valeur plancher de -127°C physiquement impossible pour de l'eau liquide → artefact de capteur (probablement une valeur d'erreur type -127 renvoyée par un capteur DS18B20 déconnecté). **Règle de nettoyage : exclure/imputer toute valeur < 0°C ou > 40°C.**
2. **pH :** valeur négative (-0.586) impossible sur l'échelle pH réelle de l'eau douce. **Règle : exclure/imputer valeurs < 0 ou > 14 (et probablement < 4 ou > 10 pour rester réaliste en aquaculture).**
3. **Ammoniac :** valeurs extrêmes de l'ordre de 10^11, alors que la plage réaliste en aquaculture est de l'ordre de 0–1 mg/L. **Règle : traiter comme artefact de capteur/unité — envisager un seuillage strict (ex. exclure > 5) ou une transformation logarithmique après filtrage des outliers extrêmes.** À documenter explicitement dans le mémoire comme limite du dataset brut.
4. **`Population` constante (50) :** n'apporte pas d'information temporelle (pas de mortalité enregistrée dans ce fichier) — à traiter comme métadonnée du bac plutôt que variable dynamique.
5. **`Fish_Length` / `Fish_Weight` :** seulement 81 valeurs uniques sur 83k lignes → ces mesures ne sont pas prises en continu comme les capteurs d'eau, mais probablement à intervalles espacés (mesures manuelles périodiques) et propagées/répétées entre deux mesures. **Implication : la courbe de croissance doit être reconstruite à partir des points de changement de valeur, pas ligne par ligne.**
6. **Fréquence irrégulière :** l'intervalle médian est de 20s mais avec une distribution étalée (39s, 57s, 94s...) → suggère des pertes de connexion IoT ponctuelles. Pas bloquant pour le MVP mais à mentionner comme limite. *Écart documentaire :* le cahier des charges (§4) indique une collecte « ~5 secondes » (fréquence nominale de l'ESP32 décrite par les auteurs) ; la fréquence **observée** dans ce fichier est d'environ 20 s — c'est cette dernière qui fait foi pour le traitement.

*Anomalies 7 à 10 ajoutées le 2026-09-16 lors de l'analyse de cadrage (constats A1 à A3 de `11-TABLEAU_DE_BORD.md`), à partir des plages observées du tableau ci-dessus.*

7. **Unités des en-têtes incohérentes (A1) :** `Dissolved Oxygen`, `Ammonia` et `Nitrate` sont annoncés en `g/ml`, ce qui est physiquement impossible pour les valeurs observées (ex. ammoniac minimal 0,0068 g/ml = 6 800 mg/L ; oxygène dissous 41 g/ml). Les seuils de référence du silure (cahier des charges §5) sont en **mg/L**. **Implication : l'unité réelle de chaque colonne doit être tranchée (hypothèse la plus probable : mg/L mal étiqueté, à vérifier dans l'article source Udanor et al., 2022) avant d'appliquer le moindre seuil.**
8. **Oxygène dissous irréaliste (A2) :** maximum observé 41,046, alors que la saturation de l'eau douce est d'environ 8 mg/L vers 26 °C. **Règle à définir : borne physique supérieure, à justifier par une source (une forte activité photosynthétique peut provoquer une sursaturation au-delà de 100 %, la borne ne doit donc pas être la saturation elle-même), et traitement des valeurs au-delà comme artefacts.**
9. **Nitrate très élevé (A2) :** plage observée 45 → 1 936 pour un seuil critique de référence à 100 mg/L. Selon la distribution réelle, une grande partie des relevés pourrait être classée « critique ». **À analyser : distribution, part des relevés > 100, cohérence avec l'unité (anomalie 7), avant de décider si la variable est exploitable telle quelle, rééchelonnée ou exclue.**
10. **Température sous la plage optimale (A3) :** maximum observé 27,75 °C alors que la plage optimale du silure est 26–32 °C : l'eau n'atteint jamais le haut de la plage et une part potentiellement importante des relevés est sous 26 °C. **Implication : une règle « température hors plage optimale » se déclencherait en quasi-permanence ; il faut préciser quelle plage (optimale ou critique) déclenche l'alerte de régulation thermique.**
11. **Fuseau horaire ambigu :** suffixe « CET » sur des relevés de juin à octobre (période où l'Europe centrale est en heure d'été, CEST) collectés au Nigeria (WAT, UTC+1). **Règle à définir : hypothèse de fuseau retenue, documentée et appliquée de façon cohérente (sans impact sur les durées relatives).**

## Empreinte du fichier source

- `IoTpond1.csv` — SHA-256 : *à renseigner au Jalon 1 lors du premier chargement (le fichier brut n'est pas versionné dans git)*

## Décisions à prendre avant le développement

- [ ] Définir les bornes de nettoyage définitives pour Temperature, pH, Ammonia (proposées ci-dessus, à valider/ajuster après visualisation des distributions)
- [ ] Décider si `Ammonia` est réutilisable après nettoyage ou si son unité/échelle rend la variable trop peu fiable pour la modélisation (option : l'exclure du modèle et le documenter comme limite du dataset)
- [ ] Décider de la stratégie de ré-échantillonnage temporel (ex. agrégation par minute ou par heure) pour lisser le bruit et réduire le volume avant modélisation
- [ ] Vérifier si le dataset complet contient d'autres fichiers (IoTpond2.csv, etc.) qu'on pourrait vouloir intégrer plus tard (hors MVP initial)
- [ ] Trancher l'unité réelle de `Dissolved Oxygen`, `Ammonia` et `Nitrate` (anomalie 7) — ADR requis, bloquant pour le Jalon 1
- [ ] Définir la borne physique de l'oxygène dissous et le traitement du nitrate (anomalies 8-9) — ADR requis
- [ ] Préciser la plage de température qui déclenche l'alerte thermique (anomalie 10) — ADR requis avant le Jalon 4
- [ ] Fixer l'hypothèse de fuseau horaire (anomalie 11) et la limite maximale d'un trou interpolable
- [ ] Fixer le seuil de turbidité (« à définir après exploration », cahier des charges §5) — au Jalon 2
