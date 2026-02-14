# scripts/check_system_status.py

"""
Diagnostic script to check if all components are ready before launching Streamlit.
"""

import sys
sys.path.append('.')

import os
from pathlib import Path
from dotenv import load_dotenv
import json

def check_files():
    """Check if required data files exist."""
    print("\n" + "="*60)
    print("📁 Vérification des Fichiers")
    print("="*60)
    
    files = {
        "Documents traités": "data/processed/documents.json",
        "Entités extraites": "data/entities/entities.json",
        "Relations extraites": "data/relations/relations.json",
        "Vector store (ChromaDB)": "chroma_db",
    }
    
    all_good = True
    for name, filepath in files.items():
        path = Path(filepath)
        if path.exists():
            if path.is_file():
                try:
                    # Try to load JSON files
                    if filepath.endswith('.json'):
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        count = len(data)
                        print(f"  ✓ {name}: {count:,} items")
                    else:
                        size = path.stat().st_size / 1024 / 1024
                        print(f"  ✓ {name}: {size:.2f} MB")
                except Exception as e:
                    print(f"  ⚠️  {name}: exists but error reading ({e})")
            else:
                print(f"  ✓ {name}: directory exists")
        else:
            print(f"  ✗ {name}: NOT FOUND")
            all_good = False
    
    return all_good

def check_neo4j():
    """Check Neo4j connection."""
    print("\n" + "="*60)
    print("🔌 Vérification de Neo4j")
    print("="*60)
    
    load_dotenv()
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not all([uri, user, password]):
        print("  ✗ Configuration Neo4j manquante dans .env")
        return False
    
    print(f"  URI: {uri}")
    print(f"  User: {user}")
    
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        
        with driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]
            
            print(f"  ✓ Connexion réussie")
            print(f"  ✓ Nœuds dans le graphe: {node_count:,}")
            print(f"  ✓ Relations dans le graphe: {rel_count:,}")
            
            if node_count == 0:
                print(f"  ⚠️  Le graphe est vide! Exécutez: python scripts/03_build_graph.py")
                return False
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Erreur de connexion: {e}")
        print(f"\n  💡 Assurez-vous que Neo4j est démarré:")
        print(f"     - Neo4j Desktop: Cliquez 'Start' sur votre base")
        print(f"     - Docker: docker start neo4j-kg")
        return False

def check_llm_api():
    """Check if LLM API key is configured."""
    print("\n" + "="*60)
    print("🤖 Vérification de l'API LLM")
    print("="*60)
    
    load_dotenv()
    
    apis = {
        "DeepSeek": os.getenv("DEEPSEEK_API_KEY"),
        "Anthropic Claude": os.getenv("ANTHROPIC_API_KEY"),
        "OpenAI": os.getenv("OPENAI_API_KEY")
    }
    
    found = False
    for name, key in apis.items():
        if key:
            print(f"  ✓ {name}: Configuré ({key[:10]}...)")
            found = True
        else:
            print(f"  - {name}: Non configuré")
    
    if not found:
        print(f"\n  ✗ Aucune clé API LLM trouvée!")
        print(f"  💡 Ajoutez une des clés suivantes dans .env:")
        print(f"     DEEPSEEK_API_KEY=sk-...")
        print(f"     ANTHROPIC_API_KEY=sk-ant-...")
        print(f"     OPENAI_API_KEY=sk-...")
        return False
    
    return True

def check_vector_store():
    """Check if vector store is accessible."""
    print("\n" + "="*60)
    print("🔍 Vérification du Vector Store")
    print("="*60)
    
    try:
        from src.embeddings.vector_store import VectorStore
        
        vector_store = VectorStore()
        
        # Try a simple search
        results = vector_store.search("test", top_k=1)
        
        print(f"  ✓ Vector store accessible")
        print(f"  ✓ ChromaDB fonctionne correctement")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        print(f"  💡 Exécutez: python scripts/04_generate_embeddings.py")
        return False

def main():
    """Run all checks."""
    print("="*60)
    print("🔧 DIAGNOSTIC DU SYSTÈME")
    print("="*60)
    print("\nVérification que tous les composants sont prêts...")
    
    checks = [
        ("Fichiers de données", check_files),
        ("Neo4j", check_neo4j),
        ("API LLM", check_llm_api),
        ("Vector Store", check_vector_store),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Erreur lors de la vérification de {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    all_passed = all(results.values())
    
    for name, passed in results.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("="*60)
        print("\n🎉 Le système est prêt!")
        print("\nVous pouvez maintenant lancer:")
        print("  streamlit run app/streamlit_app.py")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("="*60)
        print("\n💡 Étapes à suivre:")
        
        if not results.get("Fichiers de données"):
            print("\n1. Générer les données:")
            print("   python scripts/01_prepare_corpus.py")
            print("   python scripts/02_extract_entities.py")
        
        if not results.get("Neo4j"):
            print("\n2. Démarrer Neo4j et construire le graphe:")
            print("   - Démarrer Neo4j Desktop")
            print("   - python scripts/03_build_graph.py")
        
        if not results.get("Vector Store"):
            print("\n3. Générer les embeddings:")
            print("   python scripts/04_generate_embeddings.py")
        
        if not results.get("API LLM"):
            print("\n4. Configurer une clé API LLM dans .env:")
            print("   DEEPSEEK_API_KEY=sk-...")
    
    print("\n" + "="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)