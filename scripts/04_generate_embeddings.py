# scripts/04_generate_embeddings.py

import sys
sys.path.append('.')

import json
from pathlib import Path
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.embeddings.vector_store import VectorStore

def main():
    # Charger les entités
    with open("data/entities/entities.json", 'r') as f:
        entities_data = json.load(f)
    
    # Préparer la liste d'entités
    all_entities = []
    for doc_entities in entities_data:
        all_entities.extend(doc_entities['entities'])
    
    print(f"Génération des embeddings pour {len(all_entities)} entités...")
    
    # Générer les embeddings
    generator = EmbeddingGenerator()
    vector_store = VectorStore()
    
    # Ajouter les entités au store vectoriel
    vector_store.add_entities(all_entities)
    
    # Sauvegarder
    Path("data/embeddings").mkdir(parents=True, exist_ok=True)
    vector_store.save("data/embeddings/entity_vectors")
    
    print("Embeddings générés et sauvegardés!")

if __name__ == "__main__":
    main()
