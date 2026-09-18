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

## Unités réelles et nature des capteurs (ADR-009, tranché le 2026-09-18)

Source : `docs/AquaponicsDatapaper.pdf`, versionné dans ce dépôt (commit `c679040`, DOI [10.1016/j.dib.2022.108400](https://doi.org/10.1016/j.dib.2022.108400), accès libre sous licence CC BY 4.0 — voir `00-INDEX.md`). Consulté le 2026-09-18 : le PDF n'est accessible qu'en local (déposé par l'utilisateur), ScienceDirect, Europe PMC et ResearchGate renvoyant HTTP 403 en ligne sans authentification ; le versionner ici garantit l'accès à la source exacte utilisée pour ADR-009.

- **Unité réelle** de `Dissolved Oxygen`, `Ammonia` et `Nitrate` : **mg/L** (Table 1 de l'article). L'en-tête `g/ml` du fichier CSV Kaggle est une **erreur d'étiquetage** — aucune conversion numérique n'est appliquée.
- **Ammoniac** : « Ammonia detection sensor NH3 gas sensor module MQ137 », décrit comme **« suspended above the pond water »** — un capteur de **gaz**, pas une sonde immergée : il ne mesure pas une concentration dissoute dans l'eau.
- **Nitrate** : « Nitrate detection sensor NO3 gas sensor module MQ135 », également **« suspended above the pond water »** — même nature de capteur de gaz.
- **Oxygène dissous** : sonde **immergée** DFRobot, en mg/l — une vraie mesure dissoute, contrairement à l'ammoniac et au nitrate.
- **Conséquence retenue (décision humaine G1, « Distinguer par capteur »)** : les seuils aquacoles absolus du cahier des charges §5 s'appliquent à `Temperature`, `PH` et `Dissolved Oxygen` (sondes immergées) ; `Ammonia` et `Nitrate` (capteurs de gaz) sont utilisés comme **indicateurs relatifs** (tendance, écart à la moyenne du cycle), sans seuil absolu — limite majeure du dataset, à exposer explicitement dans le mémoire.
- **Plages de référence de l'article** : température 25,5–30,5 °C, pH 6,5–8,2 — différentes de celles du cahier des charges §5 (26–32 °C, 6,5–8,5). **Le cahier des charges fait foi** (décision humaine, document gelé) ; l'écart est documenté ici sans amender le cahier.

Chiffres et méthode complets : `reports/analyse-donnees-jalon1.md`, §1 (unités), §9 (fuseau horaire, sans lien avec les capteurs).

## Anomalies identifiées (à traiter dans le module de nettoyage)

1. **Température :** valeur plancher de -127°C physiquement impossible pour de l'eau liquide → artefact de capteur (probablement une valeur d'erreur type -127 renvoyée par un capteur DS18B20 déconnecté). **Règle de nettoyage : exclure/imputer toute valeur < 0°C ou > 40°C.**
2. **pH :** valeur négative (-0.586) impossible sur l'échelle pH réelle de l'eau douce. **Règle : exclure/imputer valeurs < 0 ou > 14 (et probablement < 4 ou > 10 pour rester réaliste en aquaculture).**
3. **Ammoniac :** valeurs extrêmes de l'ordre de 10^11, alors que la plage réaliste en aquaculture est de l'ordre de 0–1 mg/L. **Tranché par ADR-003 (2026-09-18) : seuillé à 5 (33,18 % des valeurs non manquantes marquées artefact, valeur constante 4,27 × 10¹¹), les 66,82 % restants conservés.** À documenter explicitement dans le mémoire comme limite du dataset brut.
4. **`Population` constante (50) :** n'apporte pas d'information temporelle (pas de mortalité enregistrée dans ce fichier) — à traiter comme métadonnée du bac plutôt que variable dynamique.
5. **`Fish_Length` / `Fish_Weight` :** seulement 81 valeurs uniques sur 83k lignes → ces mesures ne sont pas prises en continu comme les capteurs d'eau, mais probablement à intervalles espacés (mesures manuelles périodiques) et propagées/répétées entre deux mesures. **Implication : la courbe de croissance doit être reconstruite à partir des points de changement de valeur, pas ligne par ligne.**
6. **Fréquence irrégulière :** l'intervalle médian est de 20s mais avec une distribution étalée (39s, 57s, 94s...) → suggère des pertes de connexion IoT ponctuelles. Pas bloquant pour le MVP mais à mentionner comme limite. *Écart documentaire :* le cahier des charges (§4) indique une collecte « ~5 secondes » (fréquence nominale de l'ESP32 décrite par les auteurs) ; la fréquence **observée** dans ce fichier est d'environ 20 s — c'est cette dernière qui fait foi pour le traitement.

*Anomalies 7 à 10 ajoutées le 2026-09-16 lors de l'analyse de cadrage (constats A1 à A3 de `11-TABLEAU_DE_BORD.md`), à partir des plages observées du tableau ci-dessus.*

7. **Unités des en-têtes incohérentes (A1) — TRANCHÉ (ADR-009, 2026-09-18) :** `Dissolved Oxygen`, `Ammonia` et `Nitrate` sont annoncés en `g/ml`, ce qui est physiquement impossible pour les valeurs observées. L'article source confirme l'unité réelle **mg/L** (en-tête `g/ml` = erreur d'étiquetage, sans conversion) ; il révèle en outre qu'`Ammonia` et `Nitrate` proviennent de capteurs de **gaz** suspendus au-dessus de l'eau, pas de sondes immergées — voir section « Unités réelles et nature des capteurs » ci-dessus.
8. **Oxygène dissous irréaliste (A2) — TRANCHÉ (ADR-010, 2026-09-18) :** maximum observé 41,046 mg/L. Les seuils du cahier §5 restent applicables (sonde immergée, ADR-009). Borne physique supérieure : **15 mg/L, définitive** (confirmée par l'humain le 2026-09-18), 21 614 relevés (26,00 % du fichier) marqués hors borne ; alternatives écartées : 8 mg/L (45,48 % du fichier au-delà) et 20 mg/L (21,41 %) — chiffres : `reports/analyse-donnees-jalon1.md`, §2.
9. **Nitrate très élevé (A2) — TRANCHÉ (ADR-009/ADR-010, 2026-09-18) :** plage observée 45 → 1 936 (mg/L déclarés par l'article, capteur de gaz). Le seuil critique de 100 mg/L classerait 99,98 % des relevés « critique » s'il était appliqué tel quel — non retenu. Décision : **pas de borne physique absolue**, la variable est utilisée en **indicateur relatif** (tendance, écart à la moyenne du cycle), cohérent avec sa nature de capteur de gaz (ADR-009).
10. **Température sous la plage optimale (A3) — TRANCHÉ (ADR-010, 2026-09-18) :** maximum observé 27,75 °C alors que la plage optimale du silure est 26–32 °C : l'eau n'atteint jamais le haut de la plage et 95,79 % des relevés sont sous 26 °C. Décision : l'**alerte thermique se déclenche sur la plage critique** [20, 35] °C (0,00 % des relevés hors de cette plage), pas sur la plage optimale.
11. **Fuseau horaire ambigu — TRANCHÉ (ADR-010, 2026-09-18) :** suffixe « CET » sur des relevés de juin à octobre (période où l'Europe centrale est en heure d'été, CEST) collectés au Nigeria (WAT, UTC+1). Les deux hypothèses (CET littéral et WAT) partagent le même décalage numérique UTC+1 ; le cycle diurne observé (pic vers 17 h, amplitude ~1 °C) est physiquement plausible sous les deux et ne permet pas de trancher entre elles (`reports/analyse-donnees-jalon1.md`, §9). Décision : suffixe retiré, **horodatage conservé tel quel, sans conversion**, hypothèse assumée et documentée plutôt que vérifiée.

## Empreinte du fichier source

- `IoTpond1.csv` — SHA-256 : `063ea4f0c9fcd24f016fbfc52e5422b655dfb4f3542d40476d99d899655dda76` — taille 6,8 Mo — 83 126 relevés (plus l'en-tête) — 11 colonnes conformes au schéma ci-dessus, suffixe « CET » confirmé sur `created_at`. Vérifié le 2026-09-18, à réception du fichier déposé par l'utilisateur dans `data/raw/` (J-20260918-001). Fichier non versionné dans git (`.gitignore`).
- `data/raw/` contient aussi 10 autres fichiers de bassins (`IoTPond2.csv` à `IoTPond12.csv`, **`IoTPond5.csv` absent** du dépôt fourni), déposés par l'utilisateur en même temps qu'`IoTpond1.csv` : **hors périmètre du MVP** (ADR-001, un seul bac retenu), tous ignorés par git comme le reste de `data/raw/`. Le dataset complet compte 12 bassins ; l'absence d'`IoTPond5` est une caractéristique de ce dépôt fourni, à ne pas présenter comme une collection complète (correction N2, J-20260918-009).

## Décisions à prendre avant le développement

- [x] Définir les bornes de nettoyage définitives pour Temperature, pH, Ammonia — ADR-003 et ADR-010 (2026-09-18)
- [x] Décider si `Ammonia` est réutilisable après nettoyage — ADR-003 : seuillée à 5, 66,82 % conservés, utilisée en indicateur relatif (ADR-009)
- [x] Décider de la stratégie de ré-échantillonnage temporel — ADR-010 : horaire
- [x] Vérifier si le dataset complet contient d'autres fichiers (`IoTPond2` à `IoTPond12`, `IoTPond5` absent) — présents dans `data/raw/`, hors périmètre du MVP (ADR-001), voir « Empreinte du fichier source »
- [x] Trancher l'unité réelle de `Dissolved Oxygen`, `Ammonia` et `Nitrate` (anomalie 7) — ADR-009 (2026-09-18)
- [x] Définir la borne physique haute de l'oxygène dissous (anomalie 8) — ADR-010 : **15 mg/L, définitive** (confirmée le 2026-09-18) ; traitement du nitrate tranché (anomalie 9, ADR-009/ADR-010 : pas de borne absolue)
- [x] Préciser la plage de température qui déclenche l'alerte thermique (anomalie 10) — ADR-010 : plage critique
- [x] Fixer l'hypothèse de fuseau horaire (anomalie 11) et la limite maximale d'un trou interpolable — ADR-010 : sans conversion, trou max 1 h
- [ ] Fixer le seuil de turbidité (« à définir après exploration », cahier des charges §5) — au Jalon 2
