# Journal des décisions techniques (ADR — Architecture Decision Records)

Chaque décision technique importante doit être ajoutée ici au moment où elle est prise, avec le contexte, les alternatives envisagées et la justification. Ce journal sert de preuve de démarche méthodologique pour le mémoire.

Format : `## ADR-XXX — Titre` / Statut / Contexte / Décision / Alternatives envisagées / Justification / Conséquences / Traçabilité / Date

**Cycle de vie d'un ADR** (depuis le 2026-09-16, voir ADR-005) : `Proposé` → `Accepté` (après validation humaine) → éventuellement `Remplacé par ADR-XXX` ou `Rejeté`. Un ADR accepté n'est jamais réécrit : un changement de décision fait l'objet d'un nouvel ADR. Les ADR sont créés avec la procédure `/nouvel-adr` par l'agent `doc-keeper`.

*Note du 2026-09-16 : les ADR 001 à 004 ont été rédigés lors du cadrage ; leur date est celle des documents de cadrage (2026-09-15) et le champ Statut leur a été ajouté a posteriori, sans modifier leur contenu.*

---

## ADR-001 — Choix du dataset

**Statut :** Accepté (2026-09-15)

**Contexte :** besoin d'un jeu de données réel de qualité d'eau pour un bac de silure, plutôt qu'une simulation purement synthétique.

**Décision :** utilisation du dataset *Sensor Based Aquaponics Fish Pond Datasets* (Udanor/Ogbuokiri et al.), fichier `IoTpond1.csv`.

**Alternatives envisagées :**
- *Pondsdata* (Inde, autres espèces, 74k lignes) — écarté en priorité 1 car espèces différentes, gardé comme dataset de secours
- Génération de données 100% synthétiques — écartée pour privilégier la crédibilité académique de données réelles

**Justification :** correspondance directe avec l'espèce cible (silure), contexte géographique proche (Afrique subsaharienne), variables alignées avec les besoins du projet.

**Date :** 2026-09-15 (cadrage du projet)

---

## ADR-002 — Choix des modèles de machine learning

**Statut :** Accepté (2026-09-15)

**Contexte :** besoin d'un modèle de détection de risque qualité d'eau et, en priorité 2, d'un modèle de prédiction de croissance.

**Décision :** modèles classiques et interprétables — Isolation Forest et/ou Random Forest — plutôt que du deep learning (LSTM, réseaux de neurones).

**Alternatives envisagées :**
- LSTM / réseaux de neurones récurrents (état de l'art avancé pour les séries temporelles) — écarté pour le MVP (complexité, temps d'entraînement, moins interprétable en soutenance)

**Justification :** littérature récente montrant de bonnes performances avec des modèles Random Forest sur ce type de données ; interprétabilité valorisée pour une soutenance de mémoire ; contrainte de temps (7 jours). Voir `06-ETAT_DE_L_ART.md`, section 6.

**Date :** 2026-09-15 (cadrage du projet)

*Points de vigilance identifiés le 2026-09-16 (sans modifier la décision) : circularité possible des labels synthétiques dérivés des seuils (constat A4, risque R9) et incapacité d'un Random Forest à extrapoler une courbe de croissance dans le temps (constat A5, risque R11). À traiter par ADR dédiés au Jalon 3.*

---

## ADR-003 — Traitement de la variable Ammonia

**Statut :** Accepté (2026-09-18)

**Contexte :** la colonne `Ammonia(g/ml)` contient des valeurs aberrantes extrêmes (jusqu'à ~4,27 × 10^11), incompatibles avec toute plage réaliste en aquaculture.

**Décision :** ammoniac **seuillé à 5** : les valeurs strictement supérieures à 5 (27 560 relevés, soit 33,18 % des 83 074 valeurs non manquantes) sont marquées comme artefact de capteur et traitées comme valeur manquante — ce sous-ensemble est en réalité un plateau de valeurs strictement identiques à 4,27 × 10¹¹ (les 20 valeurs les plus extrêmes échantillonnées sont toutes égales), même nature qu'un code d'erreur constant que la valeur -127 °C déjà identifiée sur la température (`docs/01`, anomalie 1). Les 66,82 % restants (55 514 valeurs non manquantes) sont **conservés** : distribution resserrée et plausible (min 0,00677, q25 0,45842, médiane 0,45842, p99 4,49651, max 4,98184, écart-type 0,81956).

**Alternatives envisagées :**
- Correction d'échelle par un facteur supposé (risqué, non vérifiable)
- Exclusion totale de la variable (perte de l'information réelle contenue dans les 66,82 % de valeurs plausibles)

**Justification :** un seuillage à 5 isole un artefact clairement identifiable (valeur constante répétée, non une distribution continue) sans perdre l'information de la majorité des relevés, contrairement à l'exclusion totale. Reste soumis à la question des unités et de la nature du capteur (ADR-009) : même conservée, la variable ammoniac est utilisée comme **indicateur relatif** (capteur de gaz, pas une concentration dissoute), pas avec les seuils absolus 0,05/0,1 mg/L du cahier des charges §5. Chiffres : `reports/analyse-donnees-jalon1.md`, §4.

**Correction du 2026-09-18 :** la justification ci-dessus décrit à tort les 27 560 relevés supérieurs à 5 comme « un plateau de valeurs strictement identiques à 4,27 × 10¹¹ », assimilable à un code d'erreur constant comme le -127 °C de la température — cette description est **fausse**. Mesure indépendante du `qa-validator` (`reports/validations/jalon-1.md`, défaut D1) : **1 838 valeurs distinctes** parmi les relevés > 5, médiane 127,87, **25 relevés seulement** à la valeur maximale exacte (4,27 × 10¹¹), 3 847 relevés (13,96 %) situés entre 5 et 10 — un **continuum**, pas une constante répétée. Cause : l'analyse initiale (`reports/analyse-donnees-jalon1.md` §4) s'appuyait sur un échantillon de 20 valeurs extrêmes, non représentatif de l'ensemble des 27 560 relevés au-dessus du seuil. La **décision de seuil à 5 reste inchangée** et a été **reconfirmée par l'humain en connaissance de cause** le 2026-09-18 (J-20260918-028), pour deux motifs indépendants de la nature exacte des valeurs écartées : au-delà de 5, aucune valeur n'est compatible avec un bassin viable ; la variable est en tout état de cause utilisée en indicateur relatif, puisqu'elle provient d'un capteur de gaz et non d'une sonde immergée (ADR-009). Traçabilité de la correction : J-20260918-027 (constat de l'information erronée), J-20260918-028 (reconfirmation humaine).

**Traçabilité :** J-20260918-014, J-20260918-016, J-20260918-027, J-20260918-028 · Jalon 1 · risque R3

**Date :** proposé le 2026-09-15 · accepté le 2026-09-18 (décision humaine G1, transmise par l'orchestrateur — J-20260918-016)

---

## ADR-004 — Stack technique

**Statut :** Accepté (2026-09-15)

**Contexte :** besoin d'un stack rapide à mettre en œuvre pour un MVP en 7 jours, avec assistance de Claude Code.

**Décision :** Python, pandas/scikit-learn pour le traitement et la modélisation, Streamlit pour le dashboard.

**Alternatives envisagées :**
- Dash/Plotly pour le dashboard — écarté, Streamlit plus rapide à mettre en place pour un MVP
- Base de données (PostgreSQL/SQLite) — écartée, volume de données gérable en fichiers plats pour le MVP

**Justification :** rapidité de mise en œuvre, écosystème mature pour la data science, cohérence avec le profil de développeur d'Alfred (full stack, à l'aise avec Python assisté par Claude Code).

**Date :** 2026-09-15 (cadrage du projet)

---

## ADR-005 — Gouvernance du développement par agents spécialisés et traçabilité systémique

**Statut :** Accepté (2026-09-16)

**Contexte :** le MVP est développé en 7 jours avec l'assistance de Claude Code. Sans organisation explicite, le risque est double : dérive de périmètre ou enchaînement de jalons non validés (R1, R6), et impossibilité de reconstituer a posteriori qui a fait quoi et pourquoi — alors que la démarche est elle-même évaluée dans le mémoire (R8).

**Décision :**
- La session principale de Claude Code joue le rôle d'**orchestrateur** (`.claude/CLAUDE.md`) ; six **sous-agents spécialisés** sont propriétaires d'un périmètre : `data-engineer`, `ml-engineer`, `automation-engineer`, `dashboard-developer`, `qa-validator` (vérification indépendante), `doc-keeper` (documentation).
- Workflow par jalon : cadrer → décider → réaliser → vérifier → documenter → valider, avec quatre **points de validation humaine** (G1 décision structurante, G2 validation de jalon, G3 périmètre/planning, G4 action irréversible).
- **Règle transversale de traçabilité** (`.claude/rules/tracabilite.md`) : journal automatique de chaque action par hooks (`logs/agents/actions.jsonl`, agent identifié) + journal sémantique obligatoire écrit par l'agent (`logs/agents/journal/AAAA-MM-JJ.md`, avec le pourquoi et la preuve) + garde-fou bloquant en fin de sous-agent + audit croisé + commit git par jalon validé.
- Garanties techniques plutôt que simples consignes quand c'est possible : `data/raw/` et le journal automatique protégés en écriture (permissions), écritures de `qa-validator` et `doc-keeper` limitées à leur périmètre (hooks).

**Alternatives envisagées :**
- Session unique sans agents ni règles formalisées — plus simple, mais aucune séparation réaliser/vérifier et traçabilité dépendante de la discipline du moment.
- Journal manuel seul (sans hooks) — trace du « pourquoi » mais oublis probables et aucune garantie d'exhaustivité.
- Journal automatique seul — exhaustif mais muet sur les justifications, donc peu exploitable pour le mémoire.
- Organisation plus fine (un agent par fonction, agent expert métier distinct) — surcoût de coordination disproportionné pour un projet de 7 jours.

**Justification :** la séparation entre agents réalisateurs et agent vérificateur applique le principe de revue indépendante ; la double journalisation combine exhaustivité (machine) et sens (agent) ; les points de validation humaine gardent les décisions scientifiques et de périmètre sous le contrôle du porteur du projet ; le nombre d'agents suit le découpage en modules déjà défini (`02`, `03`).

**Conséquences :**
- Chaque session commence par `/demarrer-session` et se termine par `/cloturer-session` ; un jalon se vérifie par `/valider-jalon N`.
- Le cahier des charges est gelé : tout écart est tracé par ADR.
- La mise en place de cette organisation a été réalisée par l'orchestrateur lui-même (les agents n'existaient pas encore) et est journalisée comme telle.
- Claude Code doit être lancé depuis la racine du projet pour charger `.claude/`.
- Documentation de référence : `10-GOUVERNANCE_AGENTS.md`.

**Traçabilité :** J-20260916-001 à J-20260916-011 · préalable au Jalon 1 · risques R1, R6, R8

**Date :** proposé le 2026-09-16 · accepté le 2026-09-16 (validation du plan par le porteur du projet)

---

## ADR-006 — Référence de planning : `05-TIMELINE.md` fait foi sur le cahier des charges §9

**Statut :** Remplacé par ADR-008 (2026-09-18)

**Contexte :** deux plannings divergent. Le cahier des charges (§9) consacre le Jour 1 à la validation du dataset et le Jour 2 à l'ingestion/nettoyage ; `05-TIMELINE.md` regroupe structure du dépôt, ingestion et nettoyage au Jour 1, décalant les étapes suivantes. Les jalons de `04-JALONS_VALIDATION.md` suivent `05`.

**Décision :** `05-TIMELINE.md` est la référence de planning ; les dates retenues sont Jour 1 = 2026-09-17 → Jour 7 = 2026-09-23. Le cahier des charges n'est pas modifié.

**Alternatives envisagées :**
- Aligner `05` sur le cahier des charges — ajoute une journée entière de validation de données sans jalon associé, au détriment de la marge du Jour 4.
- Modifier le cahier des charges — contraire au principe de document racine gelé.

**Justification :** `05` est plus détaillé, cohérent avec les jalons de `04`, et intègre la validation du dataset dans le Jalon 1 (première étape du Jour 1).

**Conséquences :** les décisions bloquantes sur les données (unités, bornes, fuseau, ammoniac) sont à trancher en tout début de Jour 1.

**Traçabilité :** J-20260916-009

**Date :** proposé le 2026-09-16 · accepté le 2026-09-16 (validation du plan par le porteur du projet)

---

## ADR-007 — Conventions Git et flux par pull requests

**Statut :** Accepté (2026-09-16)

**Contexte :** le dépôt distant public `https://github.com/Myf237/Projet_pisciculture.git` a été configuré le 2026-09-16 (identité locale `Myf237`, `origin/main` = 1 commit contenant la LICENSE MIT — J-20260916-014) ; 37 fichiers de la mise en place de la gouvernance n'étaient encore jamais commités. Le dépôt étant public, un historique publié sans convention risquait de mélanger travail non validé et travail validé sur `main`, et de rompre le lien avec la traçabilité déjà en place (journal, ADR, jalons — ADR-005).

**Décision :** règle systémique `.claude/rules/git-workflow.md`, appliquée par tous les agents et garantie techniquement par le hook `.claude/hooks/guard_git.py` :
- Seul l'orchestrateur écrit dans l'historique git (commit, push, merge, tag) ; les sous-agents restent en lecture seule (`status`, `diff`, `log`, `show`…).
- `main` = état validé uniquement : jamais de commit, merge ni push direct dessus.
- Une branche par jalon ou par sujet (`feat/jalon-N-sujet`, `chore/…`, `docs/…`, `fix/…`), créée depuis `origin/main` à jour.
- Commits au format Conventional Commits, avec trailers obligatoires `Agent`, `Jalon`, `Journal` (et `Refs` si un ADR ou un risque est concerné).
- Commits et push autonomes sur la branche de travail, sans validation humaine à ce stade.
- Une pull request par jalon vers `main`, avec le modèle `.github/pull_request_template.md`.
- Fusion uniquement après verdict `qa-validator` et go humain (G2), par **merge commit**.
- Tag annoté `jalon-N` après fusion d'un jalon.
- Garde-fou technique : opérations irréversibles bloquées pour tous (force push, commit/merge/push sur `main`, rebase, `reset --hard`, amend d'un commit déjà poussé, etc.).

**Alternatives envisagées :**
- Commits directs sur `main` — aucune validation possible avant publication ; contraire au principe G2 (ADR-005) sur un dépôt public.
- GitFlow (branches `develop`/`release`) — cycle de release trop lourd pour un projet de 7 jours à un seul intégrateur.
- Fusion en squash — perd les commits atomiques par agent et leurs trailers de traçabilité (`Agent`, `Journal`), contraire au principe de traçabilité fine (ADR-005).
- Fusion par rebase — réécrit les hashes de commits déjà poussés et efface la frontière visuelle de chaque jalon dans l'historique.

**Justification :** applique à git le principe « garantir plutôt que recommander » déjà retenu pour la traçabilité (ADR-005) ; le merge commit et le tag par jalon rendent l'historique directement réutilisable comme preuve de démarche dans le mémoire ; le choix des conventions a été explicitement délégué par l'utilisateur (voir citation en date).

**Conséquences :**
- `gh` CLI nécessaire pour créer les pull requests depuis le terminal.
- Protection de la branche `main` côté GitHub recommandée à l'humain (action hors de portée des agents) ; tant qu'elle n'est pas activée, le garde-fou reste local (voir R14, `08-REGISTRE_RISQUES.md`).
- Précise, sans le réécrire, l'ADR-005 : sa conséquence « commit git par jalon validé » devient « commits sur branche de travail, fusion dans `main` à G2 ». Le champ Statut de l'ADR-005 reste inchangé (Accepté, 2026-09-16) — un ADR accepté n'est jamais réécrit.
- Documentation de référence : `.claude/rules/git-workflow.md`, `.github/pull_request_template.md`, `10-GOUVERNANCE_AGENTS.md` (section « Gestion de version »).

**Traçabilité :** J-20260916-014, J-20260916-015 · préparation (avant Jalon 1) · risques R13, R14

**Date :** proposé le 2026-09-16 · accepté le 2026-09-16 (validation humaine explicite, rapportée par l'orchestrateur : « ajouter une règle systémique pour gérer les commits, PR et push en suivant les meilleures règles et conventions alignées avec le projet »)

---

## ADR-008 — Replanification : démonstration maintenue au 2026-09-23

**Statut :** Accepté (2026-09-18)

**Contexte :** la mise en place du dépôt (structure, garde-fous, pull requests) a occupé la journée du 2026-09-17 ; aucun jalon n'a démarré à la date initialement prévue par l'ADR-006 (Jour 1 = 2026-09-17). Le rapport de vérification et la levée des réserves ont occupé la nuit du 17 au 18/09 (PR #1 fusionnée le 2026-09-17T23:13:11Z, PR #2 le 2026-09-17T23:50:18Z). Au 2026-09-18, un jour de retard est constaté sur le planning de l'ADR-006 (`08-REGISTRE_RISQUES.md`, R1).

**Décision :** la démonstration reste fixée au **2026-09-23** ; les Jalons 1 et 2 sont regroupés au 2026-09-18 (nouveau Jour 1) pour rattraper le jour perdu, sans décaler la fin du projet. Nouveau planning : Jour 1 = 18/09 (Jalons 1 et 2) → Jour 6 = 23/09 (Jalon 6, démonstration). Détail complet : `05-TIMELINE.md`.

**Alternatives envisagées :**
- Décaler la démonstration d'un jour (24/09) — écarté : aucune contrainte ne l'imposait, et la date du 23/09 avait déjà été communiquée comme repère de mémoire ; le retard d'un jour reste rattrapable en regroupant deux jalons déjà proches par nature (nettoyage et exploration reposent sur les mêmes données et le même agent propriétaire).
- Recalculer l'ensemble du planning à rebours depuis une autre date de soutenance — écarté : aucune autre date n'a été fournie ; solution disproportionnée pour un seul jour de retard.

**Justification :** les Jalons 1 et 2 sont réalisés par le même agent (`data-engineer`) et portent sur les mêmes données ; les regrouper absorbe le retard sans complexifier les jours suivants ni toucher au chemin critique du Jalon 3 (modélisation) ni à la marge de sécurité déjà prévue au Jour 4 initial (règle du Jour 4).

**Conséquences :**
- La marge de sécurité du planning est supprimée dès le départ : plus aucun jour tampon avant la démonstration du 2026-09-23.
- Risque R1 (délai) accru : probabilité relevée dans `08-REGISTRE_RISQUES.md`, avec justification.
- La « règle du Jour 4 » (point de bascule pour couper la prédiction de croissance si retard) s'applique désormais le 2026-09-20 (nouveau Jour 3 du planning révisé) ; le nom de la règle est conservé pour la continuité de traçabilité avec l'ADR-006.
- Les Jalons 1 et 2 sont vérifiés le même jour, par deux rapports distincts du `qa-validator` (un par jalon), sans les fusionner en une seule vérification.
- L'ADR-006 n'est pas réécrit : son champ Statut passe à « Remplacé par ADR-008 ».

**Traçabilité :** J-20260918-012 · préparation → Jalon 1 · risque R1

**Date :** proposé le 2026-09-18 · accepté le 2026-09-18 (validation humaine explicite, rapportée par l'orchestrateur : « Tenir la démo du 23/09 »)

---

## ADR-009 — Unités des colonnes et nature réelle des capteurs

**Statut :** Accepté (2026-09-18)

**Contexte :** l'en-tête du CSV Kaggle annonce `g/ml` pour `Dissolved Oxygen`, `Ammonia` et `Nitrate`, incompatible avec les valeurs observées (`docs/01`, anomalie 7) et avec les seuils du cahier des charges §5 (mg/L). L'analyse factuelle du data-engineer (`reports/analyse-donnees-jalon1.md`, §1) montre qu'aucun facteur d'échelle simple ne fait rentrer les trois colonnes dans les plages attendues, et que les seuils du cahier appliqués tels quels classeraient le nitrate « critique » sur 99,98 % du cycle. L'article source du dataset a été consulté (`docs/AquaponicsDatapaper.pdf` — Udanor, Ossai, Nweke, Ogbuokiri, Eneh, *Data in Brief* 43 (2022) 108400) : sa Table 1 déclare les unités **mg/l** pour les trois colonnes ; il précise que l'ammoniac est mesuré par un « Ammonia detection sensor NH3 gas sensor module MQ137 » et le nitrate par un « Nitrate detection sensor NO3 gas sensor module MQ135 », tous deux décrits comme « suspended above the pond water » ; l'oxygène dissous provient d'une sonde immergée DFRobot, en mg/l.

**Décision :**
- L'unité réelle des trois colonnes est **mg/L** ; l'en-tête `g/ml` du CSV Kaggle est une **erreur d'étiquetage** — aucune conversion numérique n'est appliquée aux valeurs.
- `Ammonia` et `Nitrate` proviennent de **capteurs de gaz suspendus au-dessus de l'eau** (MQ137, MQ135) : ils ne mesurent pas une concentration dissoute dans l'eau, contrairement à ce que leur nom de colonne suggère. En conséquence, **aucun seuil aquacole absolu** (cahier des charges §5) ne leur est appliqué ; elles sont utilisées comme **indicateurs relatifs** (tendance, écart à la moyenne du cycle, ruptures) dans les modules suivants.
- `Temperature`, `PH` et `Dissolved Oxygen` proviennent de sondes **immergées** : les seuils du cahier des charges §5 leur restent applicables tels quels.

**Alternatives envisagées :**
- Exclure entièrement `Ammonia` et `Nitrate` du pipeline — écarté : la partie exploitable de l'ammoniac après seuillage (ADR-003, 66,82 % des valeurs) et la tendance croissante plausible du nitrate (`reports/analyse-donnees-jalon1.md`, §1.3) contiennent de l'information réutilisable en indicateur relatif.
- Appliquer les seuils absolus du cahier des charges à toutes les colonnes sans distinction — écarté : classerait le nitrate « critique » en continu sur 99,98 % du cycle (`reports/analyse-donnees-jalon1.md`, §3), non exploitable pour un moteur de décision ni démontrable.

**Justification :** l'article source est la seule preuve directement vérifiable de l'unité déclarée par les auteurs du dataset ; la description physique des capteurs (« suspended above the pond water ») explique directement pourquoi les valeurs d'ammoniac et de nitrate sont incompatibles avec des concentrations dissoutes classiques, sans recourir à une hypothèse de facteur d'échelle non vérifiable.

**Conséquences :**
- Limite majeure à exposer explicitement dans le mémoire : deux des six variables de qualité d'eau ne mesurent pas ce que leur nom suggère.
- `docs/06-ETAT_DE_L_ART.md` à compléter au moment de la rédaction du mémoire avec cette limite et sa source.
- Le modèle de risque du Jalon 3 doit être construit en tenant compte de cette distinction (features relatives pour ammoniac/nitrate, seuils absolus pour température/pH/DO) — `docs/03`, `src/features.py`, `src/models/`.
- Précise, sans la modifier autrement, la table `THRESHOLDS` de `src/config.py` : les clés `ammonia` et `nitrate` restent présentes mais ne sont plus interprétées comme des seuils aquacoles absolus.

**Traçabilité :** J-20260918-014, J-20260918-015, J-20260918-016 · Jalon 1 · risques R3, R10 et nouveau risque de validité des capteurs de gaz

**Date :** proposé le 2026-09-18 · accepté le 2026-09-18 (décision humaine G1 : « Distinguer par capteur », rapportée par l'orchestrateur — J-20260918-016)

---

## ADR-010 — Bornes de nettoyage, fuseau horaire et ré-échantillonnage

**Statut :** Accepté (2026-09-18) — y compris la borne haute d'oxygène dissous, confirmée par l'humain le 2026-09-18 (J-20260918-021 : « garde 15 »)

**Contexte :** l'analyse factuelle (`reports/analyse-donnees-jalon1.md`) fournit les chiffres nécessaires pour trancher les bornes de nettoyage, le fuseau horaire et la stratégie temporelle, décisions ouvertes de `docs/11-TABLEAU_DE_BORD.md` bloquantes pour le Jalon 1.

**Décision :**
- **Température** : bornes physiques **[0, 40] °C** (déjà documentées, `docs/01` anomalie 1) ; **alerte thermique déclenchée sur la plage critique** [20, 35] °C (0,00 % des relevés hors de cette plage), et non sur la plage optimale [26, 32] °C (95,79 % des relevés seraient sous 26 °C, ce qui déclencherait une alerte quasi permanente) — tranche le constat A3.
- **pH** : bornes physiques **[0, 14]** ; resserrement à une plage plus réaliste pour l'aquaculture laissé à discuter au Jalon 2, sur la base des 185 relevés hors [4, 10] déjà chiffrés (`reports/analyse-donnees-jalon1.md`, §6).
- **Oxygène dissous — borne haute : 15 mg/L, définitive** (confirmée par l'humain le 2026-09-18, J-20260918-021). Conséquence chiffrée : 21 614 relevés, soit **26,00 % du fichier**, marqués hors borne physique et traités comme les autres valeurs hors borne (nettoyage/interpolation selon la règle générale).
- **Ammoniac** : borne de nettoyage **5** (voir ADR-003, déjà accepté).
- **Nitrate** : **pas de borne physique absolue** — usage relatif uniquement, cohérent avec l'ADR-009 (capteur de gaz).
- **Fuseau horaire** : le suffixe « CET » est retiré de `created_at`, **sans conversion** ; l'horodatage est conservé tel quel. Les données ne permettent pas de trancher entre « CET » littéral et l'heure locale du Nigeria (WAT), les deux hypothèses partageant le même décalage UTC+1 (`reports/analyse-donnees-jalon1.md`, §9).
- **Limite d'interpolation** : trou maximal interpolable **1 heure** ; au-delà, la valeur reste **manquante et marquée** (pas d'imputation). Conséquence chiffrée : les 36 jours calendaires entiers sans aucun relevé (sur 117 jours de l'étendue) resteront entièrement manquants.
- **Ré-échantillonnage** : fréquence **horaire**, appliquée au Jalon 2 dans `src/features.py` (`resample_hourly`) — 48,69 % de créneaux horaires vides, 58,09 relevés bruts en moyenne par créneau non vide.

**Alternatives envisagées :**
- Borne DO à 8 mg/L (saturation eau douce sans marge) — écartée : marquerait 45,48 % du fichier (37 802 relevés), jugé trop large.
- Borne DO à 20 mg/L (marge très généreuse) — écartée : ne marque que 21,41 % du fichier (17 796 relevés) mais laisserait passer une part d'un régime de capteur déjà identifié comme distinct (épisode du 30/07-05/08, `reports/analyse-donnees-jalon1.md`, §11).
- Interpolation sans limite (imputation de tous les trous) — écartée : imputerait des jours entiers sans aucune mesure réelle, contraire à la règle de ne jamais imputer au-delà d'un trou raisonnable.
- Ré-échantillonnage à la minute ou à 5 minutes — écarté : respectivement 74,63 % et 61,34 % de bins vides.

**Justification :** chaque valeur retenue s'appuie sur un chiffre vérifié du rapport d'analyse, pas sur une estimation ; la plage critique de température évite une alerte permanente non exploitable pour la démonstration (R12) ; la limite d'interpolation à 1 h respecte la règle de ne pas deviner de valeur sur un trou de plusieurs jours ; le ré-échantillonnage horaire est le meilleur compromis observé entre volume de bins vides et densité de données par bin.

**Conséquences :**
- `src/config.py` (data-engineer) : `AMMONIA_BOUNDS = 5` (ADR-003) ; `DISSOLVED_OXYGEN_BOUNDS` = **15** (borne haute, définitive) — le commentaire « provisoire » est à retirer du code ; `NITRATE_BOUNDS` reste sans borne absolue ; `MAX_INTERPOLATION_GAP` = 1 h ; `RESAMPLING_FREQUENCY` = horaire.
- Le data-engineer implémente le nettoyage avec l'ensemble de ces valeurs, plus aucune n'étant en attente.
- `docs/01-DATA_DICTIONARY.md` : statut des anomalies 7 à 11 mis à jour (toutes tranchées).

**Traçabilité :** J-20260918-014, J-20260918-016, J-20260918-021 · Jalon 1 · risques R1 (marge), R9, R10, R12

**Date :** proposé le 2026-09-18 · accepté le 2026-09-18 (décision humaine G1, rapportée par l'orchestrateur — J-20260918-016 ; borne haute d'oxygène dissous confirmée le 2026-09-18, J-20260918-021 : « garde 15 »)

---

## ADR-011 — Conservation du signal brut, plage de pH et traitement de la turbidité

**Statut :** Accepté (2026-09-18)

**Contexte :** l'exploration du Jalon 2 (data-engineer, J-20260918-039) a mis en évidence une conséquence non anticipée de la borne haute d'oxygène dissous à 15 mg/L (ADR-010, confirmée par l'humain le 2026-09-18) : l'intégralité de l'épisode 1 (plateau brut 36-41 mg/L, du 30/07/2021 au 05/08/2021, 13 422 lignes) est marquée `Dissolved Oxygen_missing=True` dans `data/processed/pond1_clean.csv` — le trou qui en résulte (environ 6 jours) dépasse `MAX_INTERPOLATION_GAP` (1 h), donc aucune valeur de cet épisode ne survit au nettoyage (constat vérifié J-20260918-041). C'est précisément l'anomalie que le projet cherche à détecter (Jalon 3) et à démontrer (Jalon 5). Pour l'épisode 2, le volet oxygène dissous reste visible dans le fichier nettoyé (valeurs proches de 0, dans les bornes), mais le volet pH ne l'est pas : les 40 relevés bruts de sa fenêtre ont tous un pH négatif, donc hors bornes [0, 14] et marqués manquants. Par ailleurs, un brief de délégation erroné affirmait que les 145 relevés de pH sous 4 étaient tous situés dans la fenêtre du 24/09 au 01/10 ; vérification du data-engineer (corrigée en J-20260918-040) : ils se répartissent en 62 relevés du 15 au 19/09 et 83 du 11 au 13/10, un ensemble disjoint des 40 pH négatifs déjà hors bornes. Enfin, la turbidité sature à 100 NTU sur 56,37 % des relevés (`reports/analyse-donnees-jalon1.md`, addendum daté du Jalon 2), une limite déjà connue du capteur.

**Décision :**
- **Conservation du signal brut** : la borne de nettoyage de 15 mg/L (ADR-010) reste appliquée à la colonne `Dissolved Oxygen(g/ml)` nettoyée, sans modification de ce comportement. En parallèle, chaque variable bornée de `config.SENSOR_TYPES` (température, pH, oxygène dissous, ammoniac) conserve sa valeur brute d'origine — y compris hors bornes, y compris `NaN` si elle l'était déjà — dans une colonne dédiée `<label>{config.RAW_VALUE_SUFFIX}` (suffixe `"_raw"`, déclaré dans `src/config.py`), jamais imputée ni recalculée depuis la colonne nettoyée. Conséquence mesurée sur l'épisode 1 (13 422 lignes) : la colonne nettoyée ne garde que 368 valeurs d'oxygène dissous, la colonne `Dissolved Oxygen_raw` les 13 422, moyenne 36,47 mg/L (J-20260918-044).
- **pH** : aucun resserrement de la plage de nettoyage, qui reste [0, 14] (`PH_BOUNDS`, inchangée). Les 145 relevés sous 4 (62 du 15 au 19/09, 83 du 11 au 13/10 — deux fenêtres disjointes de celle du 24/09 au 01/10, contrairement à ce qu'affirmait le brief de délégation initial, corrigé en J-20260918-040) restent visibles dans le fichier nettoyé comme anomalies de capteur, sans être marqués manquants ni imputés. Un filtrage plus strict reste possible au Jalon 3, sur la base de ces chiffres.
- **Turbidité** : traitée en indicateur relatif, sans seuil absolu — la saturation à 100 NTU sur 56,37 % des relevés est documentée comme une limite du capteur plutôt que comme un état réel du bac.

**Alternatives envisagées :**
- Supprimer ou relever la borne d'oxygène dissous pour laisser passer l'épisode 1 dans la colonne nettoyée — écarté : reviendrait sur l'ADR-010 (borne déjà confirmée par l'humain) et laisserait des valeurs physiquement discutables (jusqu'à 41 mg/L) contaminer la colonne utilisée pour l'analyse physiologique.
- Traiter l'oxygène dissous comme les capteurs de gaz (ammoniac, nitrate — sans seuil absolu, ADR-009) — écarté : l'article source (Udanor et al.) confirme une sonde immergée, donc une mesure dissoute réelle, contrairement aux capteurs de gaz suspendus ; supprimer la borne reviendrait à renoncer au nettoyage d'une variable dont la nature de mesure le justifie.
- Se contenter de détecter l'absence de données (drapeau `_missing` seul, sans conserver la valeur brute) — écarté : un drapeau seul indique qu'une donnée manque mais ne permet pas de montrer la forme de l'anomalie (plateau à 36-41 mg/L) au Jalon 5 ni de l'exploiter en détection au Jalon 3.

**Justification :** la conservation de la valeur brute en colonne parallèle restaure le signal recherché sans renoncer au nettoyage de la colonne principale ni rouvrir une décision déjà tranchée (ADR-010) ; les chiffres mesurés (368 vs 13 422 valeurs, moyenne 36,47 mg/L) montrent que le signal est effectivement récupéré (J-20260918-044). Le maintien de la plage de pH [0, 14] laisse les 145 relevés sous 4 visibles comme matière à décision du Jalon 3, plutôt que de les exclure sur la base d'un brief dont l'erreur de localisation temporelle (corrigée en J-20260918-040) aurait pu orienter à tort un resserrement. L'absence de seuil absolu sur la turbidité suit le même raisonnement déjà retenu pour l'ammoniac et le nitrate (ADR-009) : un seuil sur une variable dont 56,37 % des relevés sont saturés au maximum du capteur déclencherait une alerte non exploitable pour la démonstration.

**Conséquences :**
- `src/config.py` (data-engineer) : nouvelle constante `RAW_VALUE_SUFFIX = "_raw"` ; `PH_BOUNDS` et le traitement de la turbidité inchangés (aucune borne appliquée à `Turbidity(NTU)`, `SENSOR_TYPES["Turbidity(NTU)"]["bounds"] = None`).
- Schéma du fichier nettoyé : 23 colonnes (11 brutes + 3 colonnes par variable bornée — `_imputed`, `_missing`, `_raw` — pour température, pH, oxygène dissous, ammoniac), contre 19 avant cette décision ; la taille du fichier nettoyé augmente en conséquence.
- Le Jalon 3 dispose du signal brut pour la détection et doit choisir explicitement quelle colonne il utilise (nettoyée ou `_raw`) selon l'objectif (analyse physiologique vs détection de dérive de capteur) ; le Jalon 5 peut montrer l'épisode 1 dans le scénario de démonstration.
- `docs/01-DATA_DICTIONARY.md`, `docs/03-ARCHITECTURE_CODE.md` et `docs/08-REGISTRE_RISQUES.md` (R16) mis à jour en conséquence par le doc-keeper.
- Ne modifie ni ne réécrit l'ADR-009 ni l'ADR-010 : ADR-011 les complète et les précise, sans changer la borne de 15 mg/L ni la nature des capteurs déjà tranchées.

**Traçabilité :** J-20260918-039, J-20260918-040, J-20260918-041, J-20260918-042, J-20260918-044 · Jalon 2 · risque R16

**Date :** proposé le 2026-09-18 · accepté le 2026-09-18 (décision humaine G1, rapportée par l'orchestrateur — J-20260918-042)

---

## Template pour les prochaines décisions

```
## ADR-XXX — [Titre de la décision]

**Statut :** Proposé (AAAA-MM-JJ)

**Contexte :**

**Décision :**

**Alternatives envisagées :**

**Justification :**

**Conséquences :**

**Traçabilité :** J-AAAAMMJJ-NNN · Jalon N · risques liés

**Date :** proposé le AAAA-MM-JJ · accepté le —
```
