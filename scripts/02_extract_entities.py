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
    print("Extraction d'Entités et de Relations (Optimisée)")
    print("="*60)
    
    input_file = Path("data/processed/documents.json")
    if not input_file.exists():
        print(f"\n❌ Erreur: {input_file} n'existe pas!")
        print("   Exécutez d'abord: python scripts/01_prepare_corpus.py")
        return
    
    print(f"\n📂 Chargement des documents depuis {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    print(f"✓ Chargé: {len(documents)} documents")
    
    if len(documents) == 0:
        print("❌ Aucun document trouvé!")
        return
    
    print(f"\n{'='*60}")
    print("Étape 1/4: Extraction des entités")
    print("="*60)
    print("\n⚙️  Initialisation du modèle spaCy...")
    
    entity_extractor = EntityExtractor()
    
    print("\n🔍 Extraction des entités en cours...")
    entities = entity_extractor.extract_from_documents(documents)
    
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
    
    entities_dir = Path("data/entities")
    entities_dir.mkdir(parents=True, exist_ok=True)
    entities_file = entities_dir / "entities.json"
    
    print(f"\n💾 Sauvegarde des entités dans {entities_file}...")
    with open(entities_file, 'w', encoding='utf-8') as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)
    
    print("✓ Entités sauvegardées")
    
    print(f"\n{'='*60}")
    print("Étape 2/4: Extraction des relations syntaxiques")
    print("="*60)
    
    relation_extractor = RelationExtractor()
    syntactic_relations = []
    
    print(f"\n🔗 Extraction des relations syntaxiques (limitée)...")
    
    for doc in tqdm(documents[:50], desc="Relations syntaxiques"):
        try:
            text = doc['text'][:3000]
            relations = relation_extractor.extract_relations(text)
            syntactic_relations.extend(relations[:20])
        except Exception as e:
            continue
    
    print(f"\n✓ Relations syntaxiques brutes: {len(syntactic_relations):,}")
    
    print(f"\n{'='*60}")
    print("Étape 3/4: Relations de co-occurrence (filtrées)")
    print("="*60)
    
    print(f"\n🔗 Extraction des co-occurrences significatives (≥3 documents)...")
    cooccurrence_relations = relation_extractor.extract_cooccurrence_relations(
        entities, 
        min_strength=3
    )
    
    print(f"✓ Relations de co-occurrence: {len(cooccurrence_relations):,}")
    
    print(f"\n🔗 Extraction des relations de proximité (limitées)...")
    proximity_relations = []
    for doc_entities in tqdm(entities, desc="Relations de proximité"):
        proximity_relations.extend(
            relation_extractor.extract_proximity_relations(
                doc_entities, 
                window=150, 
                max_per_doc=20
            )
        )
    
    print(f"✓ Relations de proximité brutes: {len(proximity_relations):,}")
    
    print(f"\n{'='*60}")
    print("Étape 4/4: Déduplication et filtrage")
    print("="*60)
    
    all_relations = syntactic_relations + cooccurrence_relations + proximity_relations
    
    print(f"\n🔄 Total avant déduplication: {len(all_relations):,}")
    
    print("🔄 Déduplication des relations...")
    deduplicated = relation_extractor.deduplicate_relations(all_relations)
    print(f"✓ Après déduplication: {len(deduplicated):,}")
    
    print("🔄 Filtrage par fréquence des entités (≥3 mentions)...")
    filtered = relation_extractor.filter_by_entity_frequency(
        deduplicated, 
        entities, 
        min_mentions=3
    )
    print(f"✓ Après filtrage: {len(filtered):,}")
    
    final_relations = filtered
    
    relation_methods = {}
    for rel in final_relations:
        method = rel.get('method', 'unknown')
        relation_methods[method] = relation_methods.get(method, 0) + 1
    
    print(f"\n  Répartition finale par méthode:")
    for method, count in sorted(relation_methods.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {method}: {count:,}")
    
    relations_dir = Path("data/relations")
    relations_dir.mkdir(parents=True, exist_ok=True)
    relations_file = relations_dir / "relations.json"
    
    print(f"\n💾 Sauvegarde des relations dans {relations_file}...")
    with open(relations_file, 'w', encoding='utf-8') as f:
        json.dump(final_relations, f, ensure_ascii=False, indent=2)
    
    print("✓ Relations sauvegardées")
    
    reduction = ((len(all_relations) - len(final_relations)) / len(all_relations) * 100) if all_relations else 0
    
    print(f"\n{'='*60}")
    print("TERMINÉ!")
    print("="*60)
    print(f"✅ Entités extraites: {total_entities:,}")
    print(f"✅ Relations extraites: {len(final_relations):,}")
    print(f"📉 Réduction: {reduction:.1f}% (de {len(all_relations):,} à {len(final_relations):,})")
    print(f"📁 Entités: {entities_file.absolute()}")
    print(f"📁 Relations: {relations_file.absolute()}")
    print(f"\nProchaine étape: python scripts/03_build_graph.py")
    print("="*60)

if __name__ == "__main__":
    main()