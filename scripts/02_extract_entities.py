# scripts/02_extract_entities.py

import sys
sys.path.append('.')

import json
from pathlib import Path
from src.extraction.entity_extractor import EntityExtractor
from src.extraction.relation_extractor import RelationExtractor

def main():
    # Charger les documents
    with open("data/processed/documents.json", 'r') as f:
        documents = json.load(f)
    
    # Extraire les entités
    print("Extraction des entités...")
    entity_extractor = EntityExtractor()
    entities = entity_extractor.extract_from_documents(documents)
    
    # Sauvegarder les entités
    Path("data/entities").mkdir(parents=True, exist_ok=True)
    with open("data/entities/entities.json", 'w') as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)
    
    # Extraire les relations
    print("Extraction des relations...")
    relation_extractor = RelationExtractor(use_llm=True)
    all_relations = []
    
    for doc in documents:
        relations = relation_extractor.extract_relations(doc['text'])
        all_relations.extend(relations)
    
    # Sauvegarder les relations
    Path("data/relations").mkdir(parents=True, exist_ok=True)
    with open("data/relations/relations.json", 'w') as f:
        json.dump(all_relations, f, ensure_ascii=False, indent=2)
    
    print(f"Extrait {len(entities)} ensembles d'entités et {len(all_relations)} relations")

if __name__ == "__main__":
    main()
