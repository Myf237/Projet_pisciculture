# Analyse factuelle des données brutes — Jalon 1

**Agent :** data-engineer · **Date :** 2026-09-18 · **Fichier analysé :** `data/raw/IoTpond1.csv`
**But :** fournir les chiffres nécessaires à l'arbitrage humain (G1) des décisions ouvertes A1, A2, ADR-003, fuseau horaire, limite d'interpolation, fréquence de ré-échantillonnage — voir `docs/11-TABLEAU_DE_BORD.md`, section « Décisions en attente ». **Ce document ne tranche aucune décision et ne modifie ni `src/config.py` ni `data/raw/`.**

Méthode : script Python jetable (pandas 3.0.5 / numpy 2.5.3 / matplotlib 3.11.2, environnement `venv/` du projet), exécuté dans le scratchpad de session, non versionné. Tous les chiffres ci-dessous proviennent d'une exécution réelle sur le fichier brut complet (83 126 lignes), sans arrondi favorable. Les figures sont dans `reports/figures/` (préfixe `jalon1_`).

---

## Résumé pour l'arbitrage humain

Les trois points bloquants du Jalon 1 :

- **A1 — unités de `Dissolved Oxygen`, `Ammonia`, `Nitrate`.** Aucune des trois colonnes n'est exploitable telle quelle avec les seuils mg/L du cahier des charges §5 : DO dépasse la saturation physique sur 16 à 45 % des relevés selon la borne choisie, le nitrate serait « critique » (>100 mg/L) sur **99,98 %** du cycle, et l'ammoniac contient un tiers de valeurs de l'ordre de 10⁵ à 10¹¹. Rien dans les données seules ne permet de reconstituer le facteur d'échelle exact ; voir §1 et §4.
- **A2 — bornes physiques DO et nitrate.** Pas de « coude » net dans la distribution du DO qui isolerait un artefact clair : la distribution est bimodale (creux ~4-8, plateau dense 35-41) et un épisode de 5 jours (30/07-05/08) montre un régime quasi constant à 38-41, très différent du reste du cycle — voir §2 et §11. Le nitrate est également bimodal, avec une tendance journalière croissante sur le cycle plausible biologiquement (accumulation de déchets), mais incompatible en valeur absolue avec le seuil critique de 100 mg/L — voir §3.
- **ADR-003 — ammoniac.** 33,18 % des valeurs non manquantes (27 560 / 83 074) sont > 5 et forment **un continuum de 1 838 valeurs distinctes** (min 5,00082, max 4,27 × 10¹¹, médiane 127,87) — **corrigé le 2026-09-18** : ce n'est pas un plateau de valeur unique répétée comme le -127 °C de la température (erreur initiale de ce rapport, signalée par le `qa-validator`, voir §4). Seuls 25 relevés sur 27 560 sont exactement au maximum. Après exclusion des valeurs > 5, la partie restante (55 514 valeurs, 66,82 %) a une distribution resserrée et plausible : min 0,00677, médiane 0,458, p99 4,497, max 4,982 — voir §4.

Deux épisodes réels, datés précisément, sont proposés pour la démonstration du Jalon 2 (§11) : un plateau DO du **2021-07-30 02:00 au 2021-08-05 09:00**, et une crise combinée DO quasi nul + pH négatif du **2021-09-24 05:55 au 2021-10-01 08:57**, suivie d'une coupure de connexion de 10 jours.

---

## 0. Empreinte et chargement

| Élément | Valeur |
|---|---|
| SHA-256 calculé | `063ea4f0c9fcd24f016fbfc52e5422b655dfb4f3542d40476d99d899655dda76` |
| Correspondance avec `docs/01` | Conforme |
| Shape | 83 126 lignes × 11 colonnes |
| Lignes avec suffixe `" CET"` sur `created_at` | 83 126 / 83 126 (100 %) |
| Échecs de parsing datetime après retrait du suffixe | 0 |
| Ordre chronologique déjà respecté dans le fichier brut (ordre `entry_id`) | Oui |

---

## 1. Unités — `Dissolved Oxygen`, `Ammonia`, `Nitrate` (A1)

### 1.1 Distributions complètes

| Statistique | DO (g/ml, en-tête) | Ammonia (g/ml, en-tête) | Nitrate (g/ml, en-tête) |
|---|---:|---:|---:|
| n (non manquant) | 83 126 | 83 074 (52 manquants) | 83 126 |
| min | 0,007 | 0,00677 | 45,0 |
| q01 | 0,194 | 0,14331 | 115,0 |
| q25 | 3,44 | 0,45842 | 146,0 |
| médiane | 7,133 | 0,61166 | 347,0 |
| moyenne | 12,390 | 203 081 663,97 | 458,29 |
| q75 | 15,819 | 15,58803 | 823,0 |
| p90 | 38,635 | 4 808,43 | 935,0 |
| p95 | 38,694 | 104 917,86 | 989,0 |
| p99 | 40,769 | 49 262 860,0 | 1 189,0 |
| p999 | 40,912 | 19 449 161 728,0 | 1 360,0 |
| max | 41,046 | 427 000 000 000,0 | 1 936,0 |
| écart-type | 12,518 | 7 866 230 860,58 | 338,31 |

### 1.2 Ce que chaque hypothèse d'échelle donnerait

- **DO en mg/L tel quel** : 45,48 % des relevés (37 802) dépassent 8 mg/L (repère de saturation en eau douce à ~26 °C) ; 16,30 % (13 546) dépassent 30 mg/L. Une sursaturation ponctuelle de quelques % est un phénomène connu (photosynthèse), mais une sursaturation touchant 16 à 45 % des relevés sur 116 jours n'est pas plausible pour un bassin réel.
- **Nitrate en mg/L tel quel** : 99,98 % des relevés (83 111 / 83 126) dépassent le seuil critique de 100 mg/L (cahier §5) — voir §3.
- **Ammonia en mg/L tel quel** : incompatible sur 33,18 % des relevés non manquants (valeurs 10⁵ à 10¹¹) ; la partie restante (66,82 %) est en revanche du bon ordre de grandeur pour du mg/L (0,007 à 4,98) — voir §4.
- **Hypothèse « `g/ml` littéral »** : exclue pour les trois colonnes — 1 g/ml de nitrate ou d'ammoniac est physiquement absurde en solution aqueuse diluée (cela dépasserait la densité de l'eau elle-même) ; le DO n'existe pas en g/ml dans une eau non saturée en gaz pur.
- **Ce qui reste invérifiable sans l'article source (Udanor et al.)** : le facteur d'échelle exact qui relierait la valeur brute à une concentration en mg/L (ex. un capteur exprimant une tension ou un pourcentage brut de calibration plutôt qu'une concentration directe). Aucune opération arithmétique simple (÷10, ÷100, ÷1000) testée sur DO ou Nitrate ne fait rentrer la totalité de la distribution dans la plage attendue du cahier des charges sans en exclure une partie substantielle — voir détail par variable ci-dessous.

### 1.3 Compléments par variable

**DO** — quantiles fins en queue de distribution (pas de coude franc, plutôt un plateau dense) :

| q90 | q95 | q98 | q99 | q99.5 | q99.9 | q99.99 | max |
|---|---|---|---|---|---|---|---|
| 38,635 | 38,694 | 38,745 | 40,769 | 40,850 | 40,912 | 40,975 | 41,046 |

Histogramme grossier (bornes en g/ml, unité brute) :

| Tranche | n |
|---|---:|
| [0, 4) | 24 616 |
| [4, 8) | 20 708 |
| [8, 10) | 6 708 |
| [10, 12) | 5 067 |
| [12, 15) | 4 413 |
| [15, 20) | 3 818 |
| [20, 25) | 2 256 |
| [25, 30) | 1 994 |
| [30, 35) | 2 059 |
| [35, 41,1) | 11 487 |

La tranche [35, 41,1) concentre 13,82 % des relevés — un « plateau haut » nettement plus dense que les tranches voisines [30,35) ou [25,30), cohérent avec un épisode de régime soutenu plutôt que des pics isolés (voir §11, épisode 1). Les valeurs proches du maximum ne sont pas un plafond numérique unique et répété (ex. pas de clip exact à 41,0) : entre 39,2 et 41,046, les valeurs restent continues (9 198 valeurs uniques sur l'ensemble de la colonne), ce qui exclut un simple code d'erreur constant comme pour l'ammoniac ou la température.

**Nitrate** — histogramme grossier, nettement bimodal :

| Tranche | n |
|---|---:|
| [0, 50) | 1 |
| [50, 100) | 12 |
| [100, 200) | 36 264 |
| [200, 400) | 8 613 |
| [400, 800) | 15 268 |
| [800, 1200) | 22 209 |
| [1200, 1600) | 754 |
| [1600, 2000) | 5 |

Un premier mode autour de 100-200, un second autour de 800-1000 (figure `jalon1_nitrate_distribution.png`). La moyenne journalière croît sur le cycle : de ~125-145 fin juin (jours les plus bas : 29/06 = 125,06 ; 30/06 = 128,75 ; 28/06 = 128,95) à ~1100-1280 fin septembre (jours les plus hauts : 28/09 = 1283,0 ; 04/09 = 1220,06 ; 30/09 = 1185,67). Cette tendance croissante est biologiquement plausible (accumulation de déchets azotés à mesure que la biomasse augmente sur un cycle d'élevage), mais l'échelle absolue reste incompatible avec le seuil critique de 100 mg/L si on l'applique telle quelle.

**Ammonia** — voir §4 (détail dédié, ADR-003).

---

## 2. Oxygène dissous — saturation physique (A2)

Nombre de relevés dépassant différentes bornes candidates :

| Borne | n dépassant | % |
|---:|---:|---:|
| > 8 | 37 802 | 45,476 % |
| > 10 | 31 094 | 37,406 % |
| > 15 | 21 614 | 26,001 % |
| > 20 | 17 796 | 21,408 % |
| > 25 | 15 540 | 18,695 % |
| > 30 | 13 546 | 16,296 % |
| > 41 | 3 | 0,004 % |

Il n'y a pas de décrochage net qui isolerait un petit nombre d'artefacts : la queue de distribution est épaisse et dense (13,82 % des relevés dans [35, 41,1), §1.3). Deux éléments factuels supplémentaires, utiles pour choisir une borne :

- **Pas de cycle diurne cohérent avec une explication photosynthétique.** La moyenne de DO par heure de la journée (horodatage tel quel, sans conversion) varie de 10,14 (9 h) à 14,67 (2-3 h) — un creux en milieu de matinée et un pic nocturne, soit l'inverse de ce qu'un cycle photosynthétique produirait (pic attendu en après-midi). Corrélation DO/pH sur l'ensemble du fichier : 0,0053 (quasi nulle). Le DO ne se comporte pas comme un signal biologique cohérent à l'échelle du cycle complet.
- **Un régime distinct et daté existe** : le plateau du 30/07 au 05/08 (§11, épisode 1) où 38-41 devient la valeur dominante pendant 5 jours consécutifs, avant de retomber brutalement à 4-6.

Trois bornes candidates, avec leur effet chiffré (nombre de relevés qui basculeraient en « hors borne », donc marqués et interpolés/laissés manquants selon la règle de nettoyage) :

| Borne physique proposée | Relevés au-delà | % du fichier |
|---|---:|---:|
| 8 mg/L (saturation eau douce ~26 °C, sans marge) | 37 802 | 45,48 % |
| 15 mg/L (marge large pour sursaturation ponctuelle) | 21 614 | 26,00 % |
| 20 mg/L (sursaturation très généreuse) | 17 796 | 21,41 % |

Aucune de ces bornes n'est neutre : chacune marquerait entre un cinquième et près de la moitié du fichier comme hors-plage, ce qui n'est pas cohérent avec l'idée d'« artefacts isolés » — c'est un signal supplémentaire que le problème est d'abord une question d'unité/échelle (A1) plutôt qu'une poignée de valeurs aberrantes ponctuelles.

---

## 3. Nitrate — conséquence des seuils (A2)

| Seuil (cahier §5) | n au-dessus | % |
|---|---:|---:|
| > 50 mg/L (optimal) | 83 125 | 100,00 % |
| > 100 mg/L (critique) | 83 111 | 99,98 % |

Si les seuils du cahier des charges sont appliqués tels quels à la colonne brute, le bassin serait classé « critique » en continu sur la quasi-totalité des 116 jours du cycle — une alerte permanente, non exploitable pour un moteur de décision ni pour une démonstration (aucune variation détectable). Un seul relevé sur 83 126 est sous 50. La distribution bimodale et la tendance croissante décrite en §1.3 montrent que la variable *bouge* de façon cohérente dans le temps ; c'est l'échelle absolue, pas la variable elle-même, qui pose problème face aux seuils du cahier.

---

## 4. Ammoniac (ADR-003)

> **Correction du 2026-09-18 (post-Jalon 1), par le data-engineer.** La phrase de synthèse ci-dessous décrivait initialement les valeurs d'ammoniac > 5 comme « un plateau de valeurs strictement identiques à 4,27 × 10¹¹ … pas une distribution continue », conclusion tirée d'un échantillon des 20 valeurs les plus extrêmes seulement (toutes égales au maximum par construction du tri). Le `qa-validator`, en vérifiant le Jalon 1 (`reports/validations/jalon-1.md`, défaut D1), a recalculé la distribution complète du sous-ensemble > 5 et montré que c'est **faux** : c'est un continuum, pas un plateau. Cette description erronée a été transmise à l'humain avant sa décision de seuillage (ADR-003) — voir le constat journalisé en J-20260918-027 et la correction en J-20260918-030. Chiffres corrigés ci-dessous, recalculés indépendamment par le data-engineer sur `data/raw/IoTpond1.csv` et strictement identiques à ceux du qa-validator. Le reste de l'analyse (§1 à §11, y compris le tableau de répartition par seuil ci-dessous, qui était déjà correct) n'est pas modifié.
>
> **Correction du texte :** parmi les 27 560 relevés > 5, il y a **1 838 valeurs distinctes** (pas une seule valeur répétée), de 5,00082 à 4,27 × 10¹¹ — médiane **127,87**, q25 = 15,78, q75 = 10 848,02. Seuls **25 relevés** (0,09 % du sous-ensemble > 5) sont exactement égaux au maximum 4,27 × 10¹¹ ; **3 847 relevés (13,96 %)** sont compris entre 5 et 10 ; **369 relevés (1,34 % du sous-ensemble > 5, 0,44 % de l'ensemble non manquant)** atteignent ou dépassent 10⁹. La comparaison au code d'erreur constant -127 de la température (docs/01, anomalie 1) était donc inexacte pour la majorité du sous-ensemble > 5 : il s'agit d'un continuum de valeurs, avec une queue étendue jusqu'à des valeurs extrêmes, pas d'un artefact à valeur unique.

- **Valeurs manquantes :** 52 / 83 126 (0,063 %).
- **Valeurs extrêmes (corrigé le 2026-09-18) :** 27 560 relevés non manquants (33,18 % des 83 074 valeurs non manquantes) dépassent 5, formant un **continuum de 1 838 valeurs distinctes** (min 5,00082, max 4,27 × 10¹¹, médiane 127,87, q25 15,78, q75 10 848,02) — pas une valeur unique répétée. Répartition par seuil :

| Seuil | n dépassant | % (sur 83 074 non manquants) |
|---:|---:|---:|
| > 1 | 35 877 | 43,19 % |
| > 5 | 27 560 | 33,18 % |
| > 100 | 14 227 | 17,13 % |
| > 1 000 | 10 398 | 12,52 % |
| > 10⁶ | 2 349 | 2,83 % |
| > 10⁹ | 369 | 0,44 % |

- **Après exclusion des valeurs > 5** (n = 55 514, soit 66,82 % des valeurs non manquantes) : distribution resserrée et plausible — min 0,00677, q25 0,45842, médiane 0,45842, moyenne 0,75172, q75 0,61629, p99 4,49651, max 4,98184, écart-type 0,81956, avec 1 265 valeurs uniques (figure `jalon1_ammonia_distribution_apres_exclusion.png`).
- **Exploitabilité :** la partie « normale » (66,82 % des valeurs non manquantes) a une forme de distribution cohérente et resserrée qui garde de l'information (variation entre 0,007 et ~5, avec une majorité de valeurs autour de 0,46-0,62). Le problème reste entier pour les seuils absolus du cahier (0,05 / 0,1 mg/L) : même dans la partie « normale », la quasi-totalité des valeurs dépasse largement 0,1 (la borne à 0,05 la plus basse observée du 1er centile est déjà 0,129), ce qui repose sur la même question d'unité que le DO et le nitrate (A1), indépendamment du problème de valeurs extrêmes traité ici.

---

## 5. Température (A3)

- Valeurs exactement à -127 : **1** relevé (0,001 %) — un artefact isolé et daté (2021-08-30), pas un problème récurrent.
- Distribution du reste (n = 83 125) : min 23,0, q25 24,125, médiane 24,5625, moyenne 24,575, q75 24,9375, p99 26,4375, max 27,75, écart-type 0,683.
- Part < 26 °C (borne basse de la plage optimale du cahier §5) : **79 622 relevés, 95,79 %**.
- Part > 32 °C : 0 (0,00 %).
- Part hors [20, 35] (bornes critiques du cahier §5) : 0 (0,00 %).
- Aucune valeur, à part le -127 unique, n'est hors de [0, 40] °C (borne de nettoyage déjà proposée dans `docs/01`).

La température ne quitte quasiment jamais la moitié basse de sa plage physiquement plausible, et le maximum observé (27,75 °C) est inférieur au bas de la plage optimale (26-32 °C) sur son propre 99e centile. Une règle « hors plage optimale » se déclencherait la quasi-totalité du temps (cf. anomalie 10, `docs/01`) — point déjà signalé, confirmé ici par les chiffres.

---

## 6. pH

- Distribution : min -0,58627, q25 7,15352, médiane 7,35779, moyenne 7,51833, q75 7,83898, p99 8,42457, max 8,55167, écart-type 0,53479. Jamais au-dessus de 10.
- Hors [0, 14] : **40 relevés (0,048 %)**, tous négatifs (moyenne -0,277, min -0,586, max -0,160).
- Hors [4, 10] : **185 relevés (0,223 %)** = les 40 négatifs + 145 valeurs dans [0, 4) (moyenne 3,070, min 1,143, max 3,999).
- **Localisation temporelle** : les 40 valeurs négatives sont concentrées entre le **2021-09-24 05:55:28** et le **2021-10-01 08:57:37** — exactement la fenêtre de la crise DO décrite en §11 (épisode 2). Les 145 valeurs dans [0, 4) débordent cette fenêtre : 4 le 15/09, 10 le 16/09, 13 le 17/09, 24 le 18/09, 11 le 19/09 (juste avant la crise), puis 17 le 11/10, 47 le 12/10, 19 le 13/10 (juste après la coupure de connexion de 10 jours qui suit la crise). Le capteur pH semble dégradé sur une fenêtre plus large que la seule période à valeurs négatives.

---

## 7. Turbidité

- Distribution : min 1,0, q25 91,0, médiane 100,0, q75 100,0, p90 à p999 = 100,0, max 100,0, écart-type 25,86.
- **56,37 % des relevés (46 854 / 83 126) sont exactement à 100**, la valeur plafond — cohérent avec un capteur borné (saturation du capteur ou de l'échelle NTU utilisée) plutôt qu'avec une vraie mesure continue au-delà de 100.
- Le reste de la distribution (1-99) est étalé sur toute la plage avec plusieurs bosses secondaires (ex. 9-12, 70-95, 88-97) — pas une distribution lisse.
- **Éléments pour fixer un seuil au Jalon 2** : la moitié des relevés est au plafond de l'échelle (turbidité maximale déclarée), ce qui suggère soit une eau réellement très trouble une bonne partie du cycle (plausible en pisciculture intensive avec forte densité), soit un capteur souvent saturé. Le cahier des charges (§5) renvoie explicitement à une définition « après exploration » ; cette analyse fournit la matière (proportion au plafond, forme bimodale) mais ne fixe pas de seuil — décision Jalon 2.

---

## 8. Temps

### 8.1 Écarts entre relevés consécutifs (après tri chronologique)

| Statistique | Valeur |
|---|---:|
| Médian | 20,00 s |
| Moyenne | 120,75 s |
| p90 | 98,00 s |
| p95 | 194,00 s |
| p99 | 702,52 s |
| Maximum | 882 283 s = 14 704,7 min = 245,08 h |

| Seuil de trou | n de trous |
|---|---:|
| > 1 min | 12 746 |
| > 5 min | 2 406 |
| > 1 h | 95 |

Les 5 plus grands trous, datés :

| Début du trou | Fin du trou | Durée |
|---|---|---:|
| 2021-10-01 08:57:37 | 2021-10-11 14:02:20 | 10 j 05 h 04 |
| 2021-09-05 23:55:09 | 2021-09-15 14:01:43 | 9 j 14 h 06 |
| 2021-07-02 18:34:56 | 2021-07-10 14:49:25 | 7 j 20 h 14 |
| 2021-08-23 00:49:26 | 2021-08-27 12:12:09 | 4 j 11 h 22 |
| 2021-09-19 21:24:47 | 2021-09-24 05:55:28 | 4 j 08 h 30 |

Le plus grand trou (10 j 05 h) suit immédiatement la crise DO/pH décrite en §11 (épisode 2) — la coupure de connexion semble être la fin de cet épisode, pas un événement indépendant.

### 8.2 Doublons

- Doublons exacts de la chaîne `created_at` brute : **0**.
- Doublons après parsing à la seconde : **0**. Aucun traitement de déduplication de timestamp n'est nécessaire pour ce fichier (le cas doit néanmoins rester géré et testé dans le code, cf. règle n°6 du périmètre, pour rester valide sur d'autres fichiers du même schéma).

### 8.3 Couverture temporelle

- Début : 2021-06-19 00:00:05 — Fin : 2021-10-13 04:14:22.
- Étendue : 116 jours 04:14:17 (116,18 jours).
- Jours calendaires dans l'étendue : 117.
- Jours avec au moins un relevé : 81.
- **Jours sans aucun relevé : 36** (30,77 % des jours calendaires de l'étendue) : 2021-06-26, 06-27, 07-03 à 07-09 (7 j consécutifs), 08-19, 08-24 à 08-26, 09-02, 09-06 à 09-14 (9 j consécutifs), 09-20 à 09-23, 10-02 à 10-10 (9 j consécutifs).

### 8.4 Volume selon la fréquence de ré-échantillonnage

| Fréquence | Bins sur toute l'étendue | Bins vides | % vides | Relevés bruts moyens / bin non vide |
|---|---:|---:|---:|---:|
| 1 minute | 167 295 | 124 848 | 74,63 % | 1,96 |
| 5 minutes | 33 459 | 20 524 | 61,34 % | 6,43 |
| 1 heure | 2 789 | 1 358 | 48,69 % | 58,09 |

Un ré-échantillonnage à la minute laisse près des trois quarts des bins vides (cohérent avec la fréquence nominale observée de ~20 s mais très irrégulière) ; à l'heure, presque la moitié des bins restent vides (cohérent avec les 36 jours sans relevé et les gros trous listés en 8.1). Ces chiffres sont fournis pour éclairer un choix de fréquence de ré-échantillonnage et de limite d'interpolation — non tranchés ici.

---

## 9. Fuseau horaire

Moyenne de température par heure du timestamp brut (suffixe " CET" retiré, **aucune conversion appliquée**) :

| Heure | 0 | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 | 17 | 18 | 20 | 22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T moyenne (°C) | 24,615 | 24,454 | 24,287 | 24,164 | 24,083 | 24,224 | 24,553 | 24,807 | 24,984 | **25,040 (pic)** | 24,974 | 24,870 | 24,720 |

- Creux vers 8 h (24,083 °C), pic vers 17 h (25,040 °C) : amplitude moyenne du cycle diurne 0,957 °C (figure `jalon1_temperature_cycle_diurne.png`).
- **Ce que cela permet de dire, factuellement** : un cycle diurne réel et cohérent existe (creux matinal, pic en fin d'après-midi), ce qui est physiquement attendu pour un plan d'eau extérieur soumis au réchauffement solaire avec un décalage thermique de quelques heures. Les timestamps, pris tels quels sans conversion, produisent donc déjà une physique plausible.
- **Ce que cela ne permet pas de trancher** : « CET » au sens strict (UTC+1 fixe, hiver européen — la donnée couvre juin-octobre, période où l'Europe centrale est réellement en CEST/UTC+2) et « WAT » (heure du Nigeria, UTC+1 fixe toute l'année, sans heure d'été) partagent le **même décalage numérique** (UTC+1) si l'on ignore l'ajustement saisonnier ; les distinguer d'une hypothèse « CEST réel » (UTC+2) demanderait de détecter un décalage d'environ 1 heure sur l'heure du pic, ce qui est **inférieur à la marge d'incertitude naturelle du décalage thermique eau/soleil** (le pic peut se situer entre 14 h et 17 h solaires selon l'inertie du plan d'eau). Les données seules ne permettent donc pas de trancher entre CET-tel-que-libellé et heure locale du Nigeria — c'est un point à documenter comme hypothèse assumée, pas comme un fait vérifié par les données.

---

## 10. Croissance — `Fish_Weight` / `Fish_Length`

| | Fish_Weight(g) | Fish_Length(cm) |
|---|---:|---:|
| Valeurs manquantes | 2 | 2 |
| Valeurs uniques (paliers) | 81 | 81 |
| Points de changement avec timestamp | 81 | 81 |
| Non-monotonie (baisses entre paliers consécutifs) | **0** | **3** |
| Intervalle entre paliers — médiane | 24,00 h | 24,00 h |
| Intervalle entre paliers — min | 9,19 h | 9,19 h |
| Intervalle entre paliers — max | 253,91 h (≈ 10,6 j) | 253,91 h |

- `Fish_Weight` est strictement monotone croissant sur les 81 paliers (2,91 g → 318,64 g).
- `Fish_Length` présente **3 baisses non-monotones**, toutes précisément datées :

| Palier avant | Valeur | Palier après | Valeur | Variation |
|---|---:|---|---:|---:|
| 2021-07-14 00:01:13 | 18,08 cm | 2021-07-15 00:02:47 | 15,31 cm | -2,77 cm |
| 2021-08-21 00:18:06 | 23,93 cm | 2021-08-22 01:43:01 | 23,40 cm | -0,53 cm |
| 2021-09-04 00:02:11 | 25,85 cm | 2021-09-05 00:07:20 | 12,09 cm | -13,76 cm |

La troisième baisse (quasiment une division par deux, 25,85 → 12,09 cm) n'est pas plausible biologiquement pour un silure sur 24 h et ressemble à une erreur de saisie/mesure manuelle plutôt qu'à une vraie régression physique. Ces trois anomalies sont signalées ici, non corrigées (règle n° 7 du périmètre — aucune correction silencieuse).
- Le plus grand intervalle entre deux paliers (253,91 h) correspond au plus grand trou de connexion identifié en §8.1 (01/10 → 11/10).

Figures : `jalon1_croissance_poids.png`, `jalon1_croissance_longueur.png` (points rouges = non-monotonie).

---

## 11. Épisodes exploitables pour la démonstration (Jalon 2)

### Épisode 1 — plateau d'oxygène dissous quasi saturé

**2021-07-30 02:00 → 2021-08-05 09:00** (figure `jalon1_episode1_do_plateau.png`).

- Avant l'épisode (28-29/07), le DO oscille normalement entre ~1,5 et ~15 selon l'heure.
- À partir du 30/07 vers 02h00, le DO horaire moyen bascule de 3,5-4 à 36,4, puis se stabilise entre 36 et 41 quasiment sans interruption jusqu'au 05/08 vers 08-09h (moyennes horaires très proches de 38,6-38,7 pendant plusieurs jours consécutifs, ex. 01/08 : toutes les moyennes horaires entre 38,53 et 38,72).
- Le 05/08 vers 09h, chute brutale à 4,36, puis retour au régime bas habituel (4-6) pour le reste de la journée.
- Sur cette période, les comptages journaliers de relevés > 35 passent de quelques unités/jour (2 à 150 les jours précédents) à **2 255 le 30/07 et 2 386 le 31/07** (quasiment tous les relevés du jour) — signe d'un changement de régime du capteur, pas de pics isolés.

### Épisode 2 — crise combinée DO quasi nul + pH négatif

**2021-09-24 05:55:28 → 2021-10-01 08:57:37** (figure `jalon1_episode2_do_ph_crise.png`).

- Le DO horaire moyen tombe et reste sous 1,5 sur presque toute la fenêtre, avec un minimum absolu de **0,008 le 2021-09-29 à 02:44:47**.
- Les 40 valeurs de pH négatif du fichier entier (§6) sont **toutes** situées dans cette même fenêtre.
- La fenêtre est marquée par de nombreux trous de données (relevés épars, nombreuses heures sans aucune mesure) — cohérent avec une perte de connectivité IoT partielle, déjà documentée comme limite du dataset (`docs/01`, anomalie 6).
- Cette crise est immédiatement suivie du plus grand trou du fichier (10 jours, §8.1) : les relevés ne reprennent que le 11/10, avec une reprise nette de la croissance du poisson (poids 283,84 g → 313,72 g, §10) — le bassin semble avoir été hors ligne, pas le poisson mort, mais cela reste une inférence, pas une donnée directement observée.

Ces deux épisodes sont indépendants, datés précisément à la minute, et visuellement nets sur les figures produites — ils couvrent les deux directions (excès et déficit) pour le Jalon 3 (détection de risque) et le Jalon 5 (mode rejeu du dashboard).

---

## Synthèse des décisions ouvertes — options, conséquences chiffrées, recommandation

Les recommandations ci-dessous sont des propositions du data-engineer, **non des décisions** : elles doivent être validées par l'humain (G1) puis formalisées en ADR.

| Décision | Options | Conséquence chiffrée | Recommandation (non tranchée) |
|---|---|---|---|
| **A1 — unité DO/Ammonia/Nitrate** | (a) mg/L direct ; (b) facteur d'échelle inconnu ; (c) variable non exploitable en absolu | (a) DO : 16-45 % hors plage selon borne ; Nitrate : 99,98 % « critique » ; Ammonia : 33,18 % extrême | Vérifier l'article source si possible dans le temps disponible ; à défaut, traiter DO et Nitrate comme des variables dont **seule la valeur relative/tendance** est exploitable (pas de seuil absolu mg/L) tant que l'unité n'est pas confirmée, et le documenter explicitement comme limite du dataset |
| **A2 — borne physique DO** | 8 / 15 / 20 (candidates testées) | Respectivement 45,48 % / 26,00 % / 21,41 % du fichier au-delà | Dépend entièrement de A1 : pas de borne à fixer avant l'unité ; si une borne provisoire est nécessaire pour la démo, 15 (marge de sursaturation) est la moins extrême des trois |
| **A2 — traitement du nitrate** | seuils tels quels / exclusion / usage relatif uniquement | seuils tels quels → alerte permanente (99,98 %) | Usage relatif (tendance, z-score, écart à la moyenne du cycle) plutôt que seuil absolu, tant que A1 n'est pas tranché |
| **ADR-003 — ammoniac** | exclusion totale / seuillage strict (>5) + conservation du reste / transformation log | seuillage à 5 : 33,18 % marqué extrême, 66,82 % exploitable avec une distribution resserrée | Seuillage à 5 (à documenter comme borne de nettoyage, ADR requis) plutôt qu'exclusion totale — la partie restante contient de l'information réelle, mais reste soumise à A1 pour toute comparaison aux seuils mg/L du cahier |
| **Fuseau horaire** | CET littéral / WAT Nigeria / heure locale non convertie | Les deux hypothèses partagent le même décalage UTC+1 ; le cycle diurne observé (pic 17h, amplitude ~1°C) est physiquement plausible sous les deux | Conserver l'horodatage tel quel (suffixe retiré, aucune conversion), déjà la piste recommandée dans `docs/11` — les données ne permettent pas de faire mieux |
| **Limite d'interpolation max** | ex. 5 min / 30 min / 1 h | 12 746 trous > 1 min, 2 406 > 5 min, 95 > 1 h ; 36 jours entiers sans relevé | Une limite courte (quelques minutes) laissera la majorité des 36 jours vides comme manquant marqué plutôt qu'imputé — cohérent avec la règle n°4 (ne pas imputer au-delà d'un trou raisonnable) ; valeur exacte à trancher par l'humain |
| **Fréquence de ré-échantillonnage** | 1 min / 5 min / 1 h | 74,63 % / 61,34 % / 48,69 % de bins vides respectivement | 1 heure limite le volume de bins vides tout en gardant ~58 relevés bruts par bin non vide pour l'agrégation ; à confirmer par l'humain |
| **Seuil de turbidité (Jalon 2)** | à définir après exploration (cahier §5) | 56,37 % des relevés au plafond de l'échelle (100) | Analyse à approfondir au Jalon 2 ; ce rapport fournit la matière (proportion au plafond, distribution bimodale) sans fixer de seuil |

---

## Limites de cette analyse

- L'article source du dataset (Udanor/Ogbuokiri et al.) n'a pas été consulté ici — l'analyse reste interne aux données fournies. La confirmation définitive de l'unité de DO/Ammonia/Nitrate nécessiterait cette source.
- Seul `IoTpond1.csv` a été analysé (conforme à ADR-001, périmètre MVP) ; les 10 autres fichiers de bassins présents dans `data/raw/` n'ont pas été examinés (hors périmètre).
- Le script d'analyse est jetable (scratchpad de session, non versionné) — les chiffres de ce rapport sont la trace persistante de cette analyse, pas le code lui-même.

## Figures produites (`reports/figures/`)

- `jalon1_temperature_cycle_diurne.png` — température moyenne par heure du timestamp brut
- `jalon1_do_serie_complete.png` — série complète du DO avec repères 8 et 41,046
- `jalon1_episode1_do_plateau.png` — zoom épisode 1 (30/07-05/08)
- `jalon1_episode2_do_ph_crise.png` — zoom épisode 2 (23/09-02/10), DO et pH superposés
- `jalon1_nitrate_distribution.png` — histogramme nitrate avec seuils cahier §5
- `jalon1_ammonia_distribution_apres_exclusion.png` — histogramme ammoniac après exclusion des valeurs > 5
- `jalon1_croissance_poids.png` — courbe de croissance par paliers, Fish_Weight
- `jalon1_croissance_longueur.png` — courbe de croissance par paliers, Fish_Length (non-monotonies en rouge)
- `jalon1_ecarts_temporels_log.png` — distribution log des écarts entre relevés consécutifs

---

## Addendum du 2026-09-18 (Jalon 2) — pH et turbidité, matière chiffrée sans trancher

**Agent :** data-engineer · **Portée :** section ajoutée, aucune ligne existante ci-dessus modifiée (règle n°3 doc-keeper appliquée par analogie — ne pas réécrire une analyse déjà livrée, corriger par ajout daté). Chiffres recalculés sur `data/processed/pond1_clean.csv` régénéré (`ingestion.load_raw_data` + `ingestion.clean_data`, mêmes fonctions que le pipeline réel), pas devinés. Détail et figures dans `notebooks/01_exploration.ipynb` §6 (`reports/figures/jalon2_turbidite_distribution.png`).

### pH — resserrement à une plage réaliste

145 relevés < 4 subsistent dans le livrable nettoyé (0,175 % des 83 086 valeurs valides), répartis en **deux groupes distincts, pas une fenêtre continue** :

| Date | n | Position par rapport à l'épisode 2 |
|---|---:|---|
| 2021-09-15 | 4 | avant |
| 2021-09-16 | 10 | avant |
| 2021-09-17 | 13 | avant |
| 2021-09-18 | 24 | avant |
| 2021-09-19 | 11 | avant |
| 2021-10-11 | 17 | après |
| 2021-10-12 | 47 | après |
| 2021-10-13 | 19 | après |

**Correction factuelle par rapport au brief de délégation reçu** (« 145 relevés subsistent sous 4, tous situés dans l'épisode du 24/09 au 01/10 ») : ce n'est pas exact sur les données du livrable nettoyé — **aucun des 145 ne se situe entre le 20/09 et le 10/10**, c'est-à-dire aucun dans la fenêtre de l'épisode 2 (24/09-01/10) elle-même. Les 40 pH négatifs qui, eux, sont bien dans cette fenêtre (déjà documentés au §6 ci-dessus) sont hors bornes ([0, 14]) et donc marqués manquants dans le livrable nettoyé — ils ne font pas partie des 145 restants. Les 145 encadrent l'épisode 2 (immédiatement avant, puis juste après la coupure de connexion de 10 jours qui le suit) sans le recouvrir.

**Options :**

| Option | Effet chiffré |
|---|---|
| (a) Laisser tel quel (`PH_BOUNDS = {"min": 0, "max": 14}`, différé par l'ADR-010) | 145 valeurs restent dans le livrable, comprises entre 1,14327 et 3,999 |
| (b) Resserrer `PH_BOUNDS` (ex. `min: 4`) | 145 valeurs de plus basculeraient en hors-bornes, puis imputées ou manquantes selon le trou encadrant (`MAX_INTERPOLATION_GAP = "1h"`) — la majorité resterait probablement manquante, ces relevés étant eux-mêmes dans des zones de connectivité dégradée |
| (c) Ne pas resserrer au nettoyage ; filtrer au moment de l'usage (modélisation) si besoin | Aucun changement du livrable ; la décision est déportée au Jalon 3 |

**Recommandation motivée (non tranchée, à confirmer G1) :** option (c). Le nettoyage physique [0, 14] reste défendable (aucune valeur n'est physiquement impossible sur l'échelle pH). Les 145 valeurs, situées sur les bords immédiats d'un épisode de dégradation de capteur déjà identifié (juste avant l'entrée en crise, juste après la reprise de connexion), sont plus utiles **signalées** que supprimées au nettoyage : elles pourraient marquer une dégradation progressive du capteur plus large que la seule fenêtre à valeurs négatives, utile à la détection d'anomalie du Jalon 3. Resserrer au nettoyage risquerait de faire disparaître ce signal plutôt qu'un artefact isolé.

### Turbidité — seuil

56,37 % des relevés (46 854 / 83 126) sont exactement à 100 (plafond de l'échelle) — identique sur le livrable nettoyé (colonne non modifiée, aucune borne de nettoyage appliquée à ce jour). Distribution complète : min 1,0, q25 91,0, médiane 100,0, q75 100,0, moyenne 87,49, écart-type 25,86 (`jalon2_turbidite_distribution.png`).

**Options :**

| Option | Conséquence |
|---|---|
| (a) Seuil critique = 100 (le plafond lui-même) | Capture « capteur saturé » comme signal, mais 56,37 % du temps en alerte — même écueil que le nitrate au Jalon 1 (§3), non exploitable pour une démonstration |
| (b) Seuil sous 100 (ex. 80 ou 90 NTU) | Arbitraire sans source citée pour ce dataset précis ; réduit l'ampleur de l'alerte mais reste une valeur devinée |
| (c) Traiter la turbidité comme `ammonia`/`nitrate` — indicateur relatif, sans seuil absolu, jusqu'à confirmation de la nature du capteur | Cohérent avec `config.get_applicable_thresholds()`, qui exclut déjà la turbidité (`absolute_thresholds_applicable = None`) |

**Recommandation motivée (non tranchée, à confirmer G1) :** option (c), par le même raisonnement que pour le DO/l'ammoniac/le nitrate en A1 (Jalon 1, §1) : avec les seules données disponibles, on ne peut pas distinguer « eau réellement très trouble une bonne partie du cycle » de « capteur souvent saturé en fin d'échelle ». Fixer un seuil absolu sur un signal dont on ne sait pas s'il sature créerait une alerte quasi permanente (56 % du temps), invalidante pour la démonstration comme pour le mémoire — le même problème déjà rencontré et évité pour le nitrate.
