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

**Statut :** Proposé — à trancher au Jalon 1

**Contexte :** la colonne `Ammonia(g/ml)` contient des valeurs aberrantes extrêmes (jusqu'à ~4,27 × 10^11), incompatibles avec toute plage réaliste en aquaculture.

**Décision :** [À TRANCHER — voir `01-DATA_DICTIONARY.md` section "Décisions à prendre"] Option recommandée : exclure la variable brute du modèle après documentation de l'anomalie, plutôt que de tenter une correction d'échelle non justifiée scientifiquement.

**Alternatives envisagées :**
- Correction d'échelle par un facteur supposé (risqué, non vérifiable)
- Seuillage strict + traitement comme les autres variables (perte d'information potentiellement importante si la majorité des valeurs sont aberrantes)

**Justification :** [à compléter une fois la distribution réelle de la variable analysée après nettoyage — à rapprocher de la question des unités, `01-DATA_DICTIONARY.md` anomalie 7]

**Date :** à trancher au Jalon 1

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

**Statut :** Accepté (2026-09-16)

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
