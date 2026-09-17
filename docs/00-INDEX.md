# Index des documents — Projet Pisciculture IA

Ordre de lecture recommandé selon le besoin :

## Pour comprendre le projet globalement
1. `README_PROJET.md` — vue d'ensemble et démarrage rapide
2. `cahier-des-charges-pisciculture-ia.md` — contexte, problématique, objectifs (document racine, **gelé** : tout écart passe par un ADR)

## Pour développer (Claude Code)
3. `01-DATA_DICTIONARY.md` — comprendre les données réelles et leurs anomalies
4. `02-SPEC_TECHNIQUE.md` — exigences détaillées par module
5. `03-ARCHITECTURE_CODE.md` — structure de dépôt et signatures de fonctions
6. `04-JALONS_VALIDATION.md` — critères de validation à chaque étape
7. `05-TIMELINE.md` — planning jour par jour (17/09/2026 → 23/09/2026)

## Pour piloter le projet
8. `10-GOUVERNANCE_AGENTS.md` — organisation par agents : rôles, workflow, points de validation humaine, traçabilité
9. `11-TABLEAU_DE_BORD.md` — état vivant du projet : jalon actif, décisions en attente, blocages, prochaine action

## Pour la rédaction du mémoire
10. `06-ETAT_DE_L_ART.md` — revue de littérature IoT/IA en aquaculture
11. `07-JOURNAL_DECISIONS.md` — décisions techniques justifiées (ADR)
12. `08-REGISTRE_RISQUES.md` — risques et limites du projet
13. `09-GLOSSAIRE.md` — définitions des termes techniques

## Configuration et traces (hors de `docs/`)
- `../README.md` — présentation du dépôt, installation, utilisation, scénario de démo (Jalon 6)
- `../requirements.txt` — dépendances Python du projet (à la racine)
- `../LICENSE` — licence MIT
- `../.claude/` — configuration opérationnelle des agents : `CLAUDE.md` (orchestrateur), `agents/`, `skills/`, `rules/` (dont `git-workflow.md` — branches, commits, push, pull requests, ADR-007), `hooks/`, `settings.json`
- `../.github/pull_request_template.md` — modèle de pull request (contexte, critères du jalon, décisions, traçabilité, checklist)
- `../logs/agents/actions.jsonl` — journal automatique de toutes les actions des agents (hooks)
- `../logs/agents/journal/AAAA-MM-JJ.md` — journal sémantique : pourquoi chaque action a été faite, et son résultat
- `../reports/validations/` — rapports de validation des jalons (qa-validator)
- `../logs/decisions.log` — journal du **produit** (décisions du moteur d'automatisation simulé), à ne pas confondre avec les journaux des agents

## Règle de mise à jour

Ces documents ne sont pas figés : `07-JOURNAL_DECISIONS.md`, `08-REGISTRE_RISQUES.md` et `11-TABLEAU_DE_BORD.md` doivent être complétés au fil de l'avancement (pas seulement en fin de projet), pour rester une trace fidèle de la démarche — c'est ce qui sera valorisé dans le mémoire. Leur tenue est confiée à l'agent `doc-keeper` (voir `10-GOUVERNANCE_AGENTS.md`).
