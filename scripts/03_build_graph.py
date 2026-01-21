# scripts/03_build_graph.py

import sys
sys.path.append('.')

import json
import os
from dotenv import load_dotenv
from src.graph.graph_builder import GraphBuilder

def main():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Charger les données
    with open("data/processed/documents.json", 'r') as f:
        documents = json.load(f)
    
    with open("data/entities/entities.json", 'r') as f:
        entities = json.load(f)
    
    with open("data/relations/relations.json", 'r') as f:
        relations = json.load(f)
    
    # Construire le graphe
    print("Connexion à Neo4j...")
    builder = GraphBuilder(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # Optionnel : effacer la base existante
    response = input("Effacer la base de données existante ? (y/n): ")
    if response.lower() == 'y':
        print("Effacement de la base...")
        builder.clear_database()
    
    # Construire le graphe
    print("Construction du graphe...")
    builder.build_graph(entities, relations, documents)
    
    builder.close()
    print("Graphe construit avec succès!")

if __name__ == "__main__":
    main()
