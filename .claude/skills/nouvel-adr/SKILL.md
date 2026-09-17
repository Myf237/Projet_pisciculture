---
name: nouvel-adr
description: Crée un ADR (Architecture Decision Record) numéroté au statut « Proposé » dans docs/07-JOURNAL_DECISIONS.md, ou enregistre son acceptation / rejet après validation humaine, puis met à jour le tableau de bord et le journal. À utiliser dès qu'une décision technique ou méthodologique structurante doit être prise (unités, seuils, exclusion de variable, stratégie de modèle, anti-oscillation, périmètre).
argument-hint: "<titre de la décision> | accepter ADR-XXX | rejeter ADR-XXX"
---

# Nouvel ADR / changement de statut

Exécuté par le **doc-keeper** (seul autorisé à écrire dans `docs/`). Si tu es l'orchestrateur : délègue à `doc-keeper` en lui transmettant le contexte, les options et la recommandation.

Arguments reçus : `$ARGUMENTS`

## Mode 1 — Créer un ADR « Proposé »

1. Lire `docs/07-JOURNAL_DECISIONS.md` ; numéro = plus grand `ADR-XXX` existant + 1 (3 chiffres).
2. Rassembler les faits **sourcés** : extraits de `docs/01`, rapports (`reports/`), métriques, littérature (`docs/06`), contraintes du cahier des charges.
3. Lister au moins deux alternatives réellement envisageables, avec avantages et inconvénients.
4. Insérer l'ADR **avant** la section « Template pour les prochaines décisions » (le template reste en fin de fichier) :

```markdown
## ADR-XXX — <Titre>

**Statut :** Proposé (AAAA-MM-JJ)

**Contexte :** problème, faits observés avec leur source.

**Décision :** option recommandée (reste une recommandation tant que le statut est « Proposé »).

**Alternatives envisagées :**
- Option A — avantages / inconvénients
- Option B — avantages / inconvénients

**Justification :** pourquoi l'option recommandée, sources à l'appui.

**Conséquences :** impacts sur le code, `src/config.py`, les docs, les risques ; ce que la décision rend plus facile ou plus difficile.

**Traçabilité :** J-AAAAMMJJ-NNN · Jalon N · risques liés (RX)

**Date :** proposé le AAAA-MM-JJ · accepté le —

---
```

5. Ajouter l'ADR dans la section « Décisions en attente » de `docs/11-TABLEAU_DE_BORD.md`.
6. Entrée de journal `doc-keeper · DÉCISION` : « ADR-XXX proposé », fichiers modifiés, pourquoi (jalon / constat), suite = « validation humaine G1 ».
7. Compte rendu : options + recommandation, pour que l'orchestrateur les présente à l'humain.

## Mode 2 — `accepter ADR-XXX` ou `rejeter ADR-XXX`

Uniquement sur validation humaine explicite, rapportée par l'orchestrateur (citer la réponse).

1. Modifier **seulement** le champ Statut (`Accepté (AAAA-MM-JJ)` ou `Rejeté (AAAA-MM-JJ) — raison`) et la date d'acceptation. Si l'humain a choisi une autre option que la recommandation : ne pas réécrire l'ADR, ajouter une ligne `**Décision finale :** …` sous le statut.
2. Si l'ADR remplace une décision antérieure : statut de l'ancien → `Remplacé par ADR-XXX`.
3. Retirer l'ADR des « Décisions en attente » de `docs/11` et l'ajouter aux « Décisions prises ».
4. Entrée de journal `doc-keeper · DÉCISION` citant la validation humaine.
5. Signaler à l'orchestrateur les impacts à répercuter (config, code, autres docs) et les agents propriétaires concernés.
