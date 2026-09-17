# Données du projet Pisciculture IA

## `data/raw/` — données brutes, immuables

Ce dossier n'est **pas versionné** (voir `.gitignore` : `data/raw/*` ignoré, à
l'exception d'un futur `.gitkeep`) et **protégé en écriture** pour tous les
agents (permission `deny` sur `Edit`, ainsi que par convention pour toute
autre opération d'écriture — voir `.claude/rules/conventions-code.md`).

**À faire soi-même avant le Jalon 1** : créer le dossier `data/raw/` (absent
du dépôt) et y placer le fichier source :

```
data/raw/IoTpond1.csv
```

### Source et référence du dataset

- **Dataset :** *Sensor Based Aquaponics Fish Pond Datasets* (Udanor,
  Ogbuokiri et al., Université du Nigeria Nsukka) — fichier `IoTpond1.csv`,
  un bac parmi ceux du dataset complet (ADR-001, `docs/07-JOURNAL_DECISIONS.md`).
- **URL :** https://www.kaggle.com/datasets/ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets
- **Référence académique :** Udanor et al., *Data in Brief*, 2022,
  DOI: 10.1016/j.dib.2022.108400
- Détail : `docs/cahier-des-charges-pisciculture-ia.md` §4, `docs/01-DATA_DICTIONARY.md`.

### Empreinte SHA-256

L'empreinte du fichier brut (calculée par `src/ingestion.py` au premier
chargement, incluse dans `reports/cleaning_report.json`) doit être consignée
dans `docs/01-DATA_DICTIONARY.md`, section « Empreinte du fichier source ».
Elle permet de vérifier que tout le monde travaille sur exactement le même
fichier, en l'absence de versionnement git du CSV brut.

## `data/processed/` — données nettoyées, régénérables

Contient `pond1_clean.csv` (et éventuels artefacts intermédiaires), produits
par `src/ingestion.py` / `src/features.py`. **Non versionné** (voir
`.gitignore`) : entièrement régénérable en rejouant le pipeline sur
`data/raw/IoTpond1.csv`, jamais modifié à la main (`.claude/rules/conventions-code.md`).
Un `.gitkeep` conserve le dossier vide dans git en l'absence de données
générées.
