# scripts/02_extract_entities.py

import sys
sys.path.append('.')

import json
from pathlib import Path
from src.extraction.entity_extractor import EntityExtractor
from src.extraction.relation_extractor import RelationExtractor
from tqdm import tqdm

def main():
    print("="*60)
    print("Extraction d'Entités et de Relations")
    print("="*60)
    
    # Vérifier que le fichier existe
    input_file = Path("data/processed/documents.json")
    if not input_file.exists():
        print(f"\n❌ Erreur: {input_file} n'existe pas!")
        print("   Exécutez d'abord: python scripts/01_prepare_corpus.py")
        return
    
    # Charger les documents avec UTF-8
    print(f"\n📂 Chargement des documents depuis {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:  # ← UTF-8 encoding added!
        documents = json.load(f)
    
    print(f"✓ Chargé: {len(documents)} documents")
    
    if len(documents) == 0:
        print("❌ Aucun document trouvé!")
        return
    
    # Initialiser les extracteurs
    print(f"\n{'='*60}")
    print("Étape 1/2: Extraction des entités")
    print("="*60)
    print("\n⚙️  Initialisation du modèle spaCy (cela peut prendre un moment)...")
    
    entity_extractor = EntityExtractor()
    
    # Extraire les entités
    print("\n🔍 Extraction des entités en cours...")
    entities = entity_extractor.extract_from_documents(documents)
    
    # Statistiques des entités
    total_entities = sum(len(doc_entities['entities']) for doc_entities in entities)
    entity_types = {}
    for doc_entities in entities:
        for entity in doc_entities['entities']:
            entity_type = entity.get('label', 'unknown')
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    print(f"\n✓ Extraction terminée!")
    print(f"  - Total d'entités: {total_entities:,}")
    print(f"  - Documents avec entités: {len(entities)}")
    print(f"\n  Répartition par type:")
    for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {entity_type}: {count:,}")
    
    # Sauvegarder les entités
    entities_dir = Path("data/entities")
    entities_dir.mkdir(parents=True, exist_ok=True)
    entities_file = entities_dir / "entities.json"
    
    print(f"\n💾 Sauvegarde des entités dans {entities_file}...")
    with open(entities_file, 'w', encoding='utf-8') as f:  # ← UTF-8 encoding!
        json.dump(entities, f, ensure_ascii=False, indent=2)
    
    print("✓ Entités sauvegardées")
    
    # Extraire les relations
    print(f"\n{'='*60}")
    print("Étape 2/2: Extraction des relations")
    print("="*60)
    
    # Demander à l'utilisateur s'il veut utiliser le LLM
    use_llm = input("\n❓ Utiliser le LLM pour l'extraction de relations? (y/n, défaut=n): ").strip().lower() == 'y'
    
    llm_provider = "deepseek"  # Default to DeepSeek
    
    if use_llm:
        print("\n⚙️  Choisir le provider LLM:")
        print("  1. DeepSeek (rapide et pas cher)")
        print("  2. OpenAI GPT-4")
        print("  3. Anthropic Claude")
        
        choice = input("Choix (1-3, défaut=1): ").strip()
        
        if choice == "2":
            llm_provider = "openai"
        elif choice == "3":
            llm_provider = "anthropic"
        else:
            llm_provider = "deepseek"
        
        print(f"✓ Mode LLM activé avec {llm_provider.upper()}")
        print(f"⚠️  Assurez-vous d'avoir défini {llm_provider.upper()}_API_KEY dans votre .env")
    else:
        print("⚙️  Mode syntaxique - rapide mais moins précis")
    
    relation_extractor = RelationExtractor(use_llm=use_llm, llm_provider=llm_provider)
    all_relations = []
    
    print(f"\n🔗 Extraction des relations en cours...")
    
    # Limiter le nombre de documents pour le LLM (c'est coûteux)
    max_docs_for_relations = 100 if use_llm else len(documents)
    docs_to_process = documents[:max_docs_for_relations]
    
    if use_llm and len(documents) > max_docs_for_relations:
        print(f"⚠️  Mode LLM: traitement des {max_docs_for_relations} premiers documents seulement")
    
    for doc in tqdm(docs_to_process, desc="Extraction relations"):
        try:
            # Limiter la longueur du texte pour éviter les timeouts
            text = doc['text'][:5000] if use_llm else doc['text']
            relations = relation_extractor.extract_relations(text)
            all_relations.extend(relations)
        except Exception as e:
            print(f"\n⚠️  Erreur pour {doc.get('filename', 'unknown')}: {e}")
            continue
    
    print(f"\n✓ Extraction terminée!")
    print(f"  - Total de relations: {len(all_relations):,}")
    
    # Statistiques des relations
    if all_relations:
        relation_methods = {}
        for rel in all_relations:
            method = rel.get('method', 'unknown')
            relation_methods[method] = relation_methods.get(method, 0) + 1
        
        print(f"\n  Répartition par méthode:")
        for method, count in sorted(relation_methods.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {method}: {count:,}")
    
    # Sauvegarder les relations
    relations_dir = Path("data/relations")
    relations_dir.mkdir(parents=True, exist_ok=True)
    relations_file = relations_dir / "relations.json"
    
    print(f"\n💾 Sauvegarde des relations dans {relations_file}...")
    with open(relations_file, 'w', encoding='utf-8') as f:  # ← UTF-8 encoding!
        json.dump(all_relations, f, ensure_ascii=False, indent=2)
    
    print("✓ Relations sauvegardées")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("TERMINÉ!")
    print("="*60)
    print(f"✅ Entités extraites: {total_entities:,}")
    print(f"✅ Relations extraites: {len(all_relations):,}")
    print(f"📁 Entités: {entities_file.absolute()}")
    print(f"📁 Relations: {relations_file.absolute()}")
    print(f"\nProchaine étape: python scripts/03_build_graph.py")
    print("="*60)

if __name__ == "__main__":
    main()