<!-- Titre de la PR au format Conventional Commits, ex. : feat(ingestion): jalon 1 — données nettoyées et fiables -->
<!-- Conventions : .claude/rules/git-workflow.md -->

## Contexte

- **Jalon :** <!-- 1 à 6, ou « préparation » -->
- **Branche :** <!-- feat/jalon-N-sujet -->
- **Objectif :** <!-- en une ou deux phrases, avec la référence docs/04 ou docs/02 -->

## Changements

<!-- Liste courte par agent : ce qui a été créé ou modifié, et pourquoi -->
- 

## Critères du jalon (`docs/04-JALONS_VALIDATION.md`)

<!-- Recopier les critères du jalon ; cocher uniquement ceux prouvés, avec la preuve -->
- [ ] Critère — preuve : <!-- commande, sortie, fichier -->

## Décisions et risques

- **ADR :** <!-- ADR créés, acceptés ou appliqués -->
- **Risques :** <!-- risques du registre concernés ou nouveaux -->
- **Limites connues :** <!-- ce qui n'est pas couvert, réserves -->

## Traçabilité

- **Journal :** <!-- J-AAAAMMJJ-NNN … -->
- **Rapport de validation :** <!-- reports/validations/jalon-N.md — verdict qa-validator -->
- **Audit de traçabilité :** <!-- python .claude/hooks/audit_trace.py --date … → verdict -->

## Checklist avant fusion (G2)

- [ ] `pytest -q` vert
- [ ] Audit de traçabilité conforme pour chaque jour du jalon
- [ ] Commits conformes (Conventional Commits, trailers `Agent` / `Jalon` / `Journal`)
- [ ] Aucun fichier interdit (`data/raw/`, secret, `venv/`, artefact régénérable, fichier > 5 Mo)
- [ ] Documentation à jour (`docs/11`, ADR, risques, dictionnaire si concerné)
- [ ] Verdict `qa-validator` : VALIDÉ ou VALIDÉ AVEC RÉSERVES
- [ ] Go humain obtenu (G2)
