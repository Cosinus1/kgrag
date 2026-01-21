# Knowledge Graph RAG - Système de Question-Réponse sur Graphe de Connaissances

Ce projet implémente un système complet de RAG (Retrieval Augmented Generation) basé sur un graphe de connaissances construit à partir d'un corpus de documents.

## 🎯 Fonctionnalités

- **Extraction automatique** d'entités et de relations depuis des documents (PDF, TXT, HTML)
- **Construction d'un graphe de connaissances** dans Neo4j
- **Recherche hybride** : vectorielle (embeddings) + parcours de graphe
- **Interface conversationnelle** avec Streamlit
- **API REST** avec FastAPI
- **Visualisation** du graphe

## 📋 Prérequis

- Python 3.10+
- Neo4j 5.x
- Au moins 8 GB de RAM
- Clé API LLM

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd kgrag
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_lg
```

### 4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

### 5. Lancer Neo4j

#### Option A : Docker
```bash
docker-compose -f docker/docker-compose.yml up -d neo4j
```

#### Option B : Installation locale
Téléchargez et installez Neo4j Desktop depuis https://neo4j.com/download/

## 📊 Préparation des données

### 1. Ajouter vos documents

Placez vos documents (PDF, TXT, HTML) dans `data/raw/`

### 2. Exécuter le pipeline complet

```bash
python scripts/05_run_pipeline.py
```

Ou exécuter étape par étape :

```bash
# Étape 1 : Préparation du corpus
python scripts/01_prepare_corpus.py

# Étape 2 : Extraction des entités et relations
python scripts/02_extract_entities.py

# Étape 3 : Construction du graphe
python scripts/03_build_graph.py

# Étape 4 : Génération des embeddings
python scripts/04_generate_embeddings.py
```

## 🖥️ Utilisation

### Interface Streamlit

```bash
streamlit run app/streamlit_app.py
```

Ouvrez http://localhost:8501 dans votre navigateur.

### API FastAPI

```bash
python app/api.py
```

Documentation API disponible sur http://localhost:8000/docs

#### Exemple d'utilisation de l'API

```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={
        "question": "Qui est le PDG de Microsoft ?",
        "max_depth": 2,
        "top_k": 10
    }
)

print(response.json())
```

## 🧪 Tests

```bash
# Tous les tests
python -m unittest discover tests

# Test spécifique
python -m unittest tests.test_extraction
```

## 📁 Structure du projet

```
knowledge-graph-rag/
├── data/               # Données (documents, entités, embeddings)
├── src/                # Code source
│   ├── preprocessing/  # Chargement et nettoyage
│   ├── extraction/     # Extraction NER et relations
│   ├── graph/          # Gestion du graphe Neo4j
│   ├── embeddings/     # Génération d'embeddings
│   └── rag/            # Pipeline RAG
├── scripts/            # Scripts d'exécution
├── app/                # Interfaces (Streamlit + API)
├── tests/              # Tests unitaires
└── docker/             # Configuration Docker
```

## ⚙️ Configuration

Modifiez `config.yaml` pour ajuster :
- Modèles d'embeddings
- Paramètres d'extraction
- Profondeur de parcours du graphe
- Contexte maximum pour le LLM

## 🐛 Dépannage

### Problème : Neo4j ne démarre pas
- Vérifiez que le port 7687 n'est pas utilisé
- Consultez les logs : `docker logs kg_neo4j`

### Problème : Extraction d'entités échoue
- Vérifiez que le modèle spaCy est installé : `python -m spacy download fr_core_news_lg`

### Problème : Erreur API
- Vérifiez votre clé API dans `.env`
- Vérifiez votre quota/crédit API

## 📝 TODO / Améliorations futures

- [ ] Support de plus de langues
- [ ] Fine-tuning du modèle NER sur votre domaine
- [ ] Clustering d'entités similaires
- [ ] Export du graphe en différents formats
- [ ] Métriques d'évaluation automatiques
- [ ] Support de mises à jour incrémentales

## 📄 Licence

MIT