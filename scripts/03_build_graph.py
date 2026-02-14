# scripts/03_build_graph.py

import sys
sys.path.append('.')

import json
import os
from dotenv import load_dotenv
from src.graph.graph_builder import GraphBuilder
from pathlib import Path

def main():
    print("="*60)
    print("Construction du Graphe de Connaissances")
    print("="*60)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier que les fichiers existent
    files_to_check = {
        "documents": Path("data/processed/documents.json"),
        "entities": Path("data/entities/entities.json"),
        "relations": Path("data/relations/relations.json")
    }
    
    missing_files = []
    for name, filepath in files_to_check.items():
        if not filepath.exists():
            missing_files.append(f"{name}: {filepath}")
    
    if missing_files:
        print("\n❌ Fichiers manquants:")
        for f in missing_files:
            print(f"   - {f}")
        print("\nExécutez les étapes précédentes:")
        print("  1. python scripts/01_prepare_corpus.py")
        print("  2. python scripts/02_extract_entities.py")
        return
    
    # Charger les données avec UTF-8
    print(f"\n📂 Chargement des données...")
    
    print("  - Chargement des documents...")
    with open("data/processed/documents.json", 'r', encoding='utf-8') as f:
        documents = json.load(f)
    print(f"    ✓ {len(documents)} documents chargés")
    
    print("  - Chargement des entités...")
    with open("data/entities/entities.json", 'r', encoding='utf-8') as f:
        entities = json.load(f)
    
    # Compter le total d'entités
    total_entities = sum(len(doc['entities']) for doc in entities)
    print(f"    ✓ {total_entities:,} entités chargées ({len(entities)} documents)")
    
    print("  - Chargement des relations...")
    with open("data/relations/relations.json", 'r', encoding='utf-8') as f:
        relations = json.load(f)
    print(f"    ✓ {len(relations):,} relations chargées")
    
    # Vérifier la configuration Neo4j
    print(f"\n{'='*60}")
    print("Configuration Neo4j")
    print("="*60)
    
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        print("\n❌ Configuration Neo4j manquante dans .env!")
        print("Ajoutez ces variables dans votre fichier .env:")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=votre_mot_de_passe")
        return
    
    print(f"  URI: {neo4j_uri}")
    print(f"  User: {neo4j_user}")
    print(f"  Password: {'*' * len(neo4j_password)}")
    
    # Connexion à Neo4j
    print(f"\n🔌 Connexion à Neo4j...")
    try:
        builder = GraphBuilder(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )
        print("✓ Connexion établie")
    except Exception as e:
        print(f"\n❌ Erreur de connexion à Neo4j: {e}")
        print("\nAssurez-vous que:")
        print("  1. Neo4j est installé et en cours d'exécution")
        print("  2. Les identifiants dans .env sont corrects")
        print("  3. Le port 7687 est accessible")
        return
    
    # Demander si on efface la base
    print(f"\n{'='*60}")
    print("Options")
    print("="*60)
    
    response = input("\n⚠️  Effacer la base de données existante ? (y/n, défaut=n): ").strip().lower()
    
    if response == 'y':
        print("\n🗑️  Effacement de la base...")
        try:
            builder.clear_database()
            print("✓ Base effacée")
        except Exception as e:
            print(f"⚠️  Erreur lors de l'effacement: {e}")
            builder.close()
            return
    else:
        print("\n➕ Ajout des données à la base existante")
    
    # Construire le graphe
    print(f"\n{'='*60}")
    print("Construction du Graphe")
    print("="*60)
    print("\nCela peut prendre plusieurs minutes...")
    
    try:
        builder.build_graph(entities, relations, documents)
        print("\n✓ Graphe construit avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors de la construction: {e}")
        builder.close()
        return
    
    builder.close()
    
    # Résumé final
    print(f"\n{'='*60}")
    print("TERMINÉ!")
    print("="*60)
    print(f"✅ Documents: {len(documents)}")
    print(f"✅ Entités: {total_entities:,}")
    print(f"✅ Relations: {len(relations):,}")
    print(f"\n📊 Le graphe de connaissances est prêt!")
    print(f"\nProchaine étape: python scripts/04_generate_embeddings.py")
    print("="*60)

if __name__ == "__main__":
    main()