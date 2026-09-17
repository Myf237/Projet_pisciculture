# Système IA de suivi, prédiction et automatisation — Bac de pisciculture (Silure)

MVP développé dans le cadre d'un mémoire académique, démontrant un pipeline complet de gestion intelligente d'un bac d'élevage de silure à partir de données IoT réelles.

## Contenu du dépôt

```
pisciculture-ia/
├── data/           # données brutes et nettoyées
├── src/            # code source (ingestion, features, modèles, décision)
├── notebooks/      # exploration
├── dashboard/      # application Streamlit
├── logs/           # journal des décisions automatisées
├── docs/           # documentation projet (voir docs/00-INDEX.md)
├── tests/          # tests unitaires
└── requirements.txt
```

## Installation

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

## Utilisation

1. Placer le fichier `IoTpond1.csv` dans `data/raw/`
2. Lancer le pipeline complet :
   ```bash
   python src/main.py
   ```
3. Lancer le dashboard :
   ```bash
   streamlit run dashboard/app.py
   ```

## Documentation

Voir `docs/00-INDEX.md` pour la liste complète des documents de cadrage (spec technique, architecture, jalons, timeline, état de l'art, décisions techniques, risques).

## Avertissement

Ce projet est un MVP académique basé sur des données réelles mais avec des actionneurs **simulés** (pas de matériel physique connecté). Voir `docs/07-JOURNAL_DECISIONS.md` pour les choix techniques justifiés et `docs/08-REGISTRE_RISQUES.md` pour les limites connues.
