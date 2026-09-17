# Conventions de code et de reproductibilité — tous les agents

## Structure

- Respecter l'arborescence de `docs/03-ARCHITECTURE_CODE.md`. Tout nouveau module ou dossier non prévu = justification dans le journal ; si structurant, ADR.
- Code de production dans `src/` et `dashboard/` uniquement. Les notebooks (`notebooks/`) servent à l'exploration et importent `src/` : aucune logique réutilisable n'y est définie.
- Une fonction = une responsabilité ; privilégier les fonctions pures (entrée → sortie, sans I/O) pour la logique métier.

## Configuration

- **Aucune valeur en dur** : seuils, chemins, colonnes, fenêtres temporelles, graines aléatoires et paramètres de démo sont dans `src/config.py`.
- Les chemins sont construits à partir de la racine du projet (`pathlib`), jamais relatifs au répertoire courant.
- Modifier un seuil scientifique ou une borne de nettoyage exige un ADR accepté.

## Style

- Type hints sur toutes les fonctions publiques ; docstring courte (entrée → sortie).
- Noms de code en anglais (cohérence avec `03`), commentaires et documentation en français.
- Pas de `print` dans `src/` : utiliser `logging` (le journal métier du moteur de décision reste `logs/decisions.log`). Seule exception : les messages destinés à l'utilisateur d'un point d'entrée en ligne de commande (`src/main.py`, blocs `if __name__ == "__main__":`), écrits sur `sys.stderr` (`docs/03`).
- Échec explicite : lever une exception claire (schéma inattendu, fichier manquant) plutôt que de continuer silencieusement.

## Tests

- `pytest`, fichiers `tests/test_<module>.py`, exécutables en quelques secondes.
- Tests sur petits jeux synthétiques construits dans le test (ou `tests/conftest.py`), pas sur le CSV complet.
- Toute règle métier (seuil, règle de décision, règle de nettoyage) a au moins un test de cas limite : juste sous, égal, juste au-dessus.
- Un bug corrigé = un test qui le reproduit.
- Ne jamais désactiver, supprimer ou affaiblir un test pour le faire passer.

## Reproductibilité

- Graine fixe (`RANDOM_STATE` dans `config.py`) passée explicitement à tout composant aléatoire.
- Séries temporelles : ordre chronologique préservé, jamais de split ou de mélange aléatoire.
- Tout artefact produit (données nettoyées, modèle, rapport) est régénérable par le code ; aucune modification manuelle de fichier de sortie.
- `data/raw/` est immuable (permission `deny`) : les sorties vont dans `data/processed/`.
- Dépendances dans `requirements.txt` ; tout ajout est justifié dans le journal.
