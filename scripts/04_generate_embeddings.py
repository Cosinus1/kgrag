# scripts/04_generate_embeddings.py

import sys
sys.path.append('.')

import json
from pathlib import Path
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.embeddings.vector_store import VectorStore

def main():
    print("="*60)
    print("Génération des Embeddings")
    print("="*60)
    
    # Vérifier que le fichier existe
    entities_file = Path("data/entities/entities.json")
    if not entities_file.exists():
        print(f"\n❌ Erreur: {entities_file} n'existe pas!")
        print("   Exécutez d'abord: python scripts/02_extract_entities.py")
        return
    
    # Charger les entités avec UTF-8
    print(f"\n📂 Chargement des entités depuis {entities_file}...")
    with open(entities_file, 'r', encoding='utf-8') as f:
        entities_data = json.load(f)
    
    print(f"✓ Chargé: {len(entities_data)} documents avec entités")
    
    # Préparer la liste d'entités
    print("\n🔄 Préparation des entités...")
    all_entities = []
    for doc_entities in entities_data:
        all_entities.extend(doc_entities['entities'])
    
    print(f"✓ Total d'entités: {len(all_entities):,}")
    
    if len(all_entities) == 0:
        print("\n❌ Aucune entité trouvée!")
        print("   Vérifiez que l'extraction d'entités a bien fonctionné.")
        return
    
    # Statistiques des entités
    entity_types = {}
    for entity in all_entities:
        entity_type = entity.get('label', 'unknown')
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    print(f"\n📊 Répartition par type:")
    for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {entity_type}: {count:,}")
    
    # Générer les embeddings
    print(f"\n{'='*60}")
    print("Génération des Embeddings")
    print("="*60)
    print("\n⚙️  Chargement du modèle sentence-transformers...")
    print("(Cela peut prendre un moment au premier lancement)")
    
    generator = EmbeddingGenerator()
    print(f"✓ Modèle chargé: dimension {generator.dimension}")
    
    print(f"\n🔄 Initialisation du vector store...")
    vector_store = VectorStore()
    
    # Ajouter les entités au store vectoriel
    print(f"\n📝 Génération des embeddings pour {len(all_entities):,} entités...")
    print("(Cela peut prendre quelques minutes)")
    
    try:
        vector_store.add_entities(all_entities)
        print("✓ Embeddings générés")
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération: {e}")
        return
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde du vector store...")
    embeddings_dir = Path("data/embeddings")
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        vector_store.save("data/embeddings/entity_vectors")
        print(f"✓ Sauvegardé dans {embeddings_dir.absolute()}")
    except Exception as e:
        print(f"\n⚠️  Erreur lors de la sauvegarde: {e}")
        print("   Note: ChromaDB sauvegarde automatiquement dans ./chroma_db/")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("TERMINÉ!")
    print("="*60)
    print(f"✅ Entités encodées: {len(all_entities):,}")
    print(f"✅ Dimension des vecteurs: {generator.dimension}")
    print(f"💾 Vector store: ./chroma_db/")
    print(f"\n🎉 Le système RAG est prêt!")
    print(f"\nProchaines étapes:")
    print(f"  - Lancer l'interface: streamlit run app/streamlit_app.py")
    print(f"  - Ou lancer l'API: python app/api.py")
    print("="*60)

if __name__ == "__main__":
    main()