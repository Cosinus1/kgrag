# scripts/01_prepare_corpus.py

import sys
sys.path.append('.')

from src.preprocessing.document_loader import DocumentLoader
from src.preprocessing.text_cleaner import TextCleaner
from pathlib import Path

def main():
    # Configuration
    raw_dir = Path("data/raw")
    output_file = Path("data/processed/documents.json")
    
    print("="*60)
    print("Préparation du Corpus")
    print("="*60)
    
    # Vérifier que le répertoire existe
    if not raw_dir.exists():
        print(f"\n❌ Erreur: Le répertoire {raw_dir} n'existe pas!")
        print("   Exécutez d'abord: python scripts/00_load_data.py")
        return
    
    # Compter les fichiers
    txt_files = list(raw_dir.glob("*.txt"))
    print(f"\n📁 Répertoire: {raw_dir.absolute()}")
    print(f"📄 Fichiers trouvés: {len(txt_files)} fichiers .txt")
    
    if len(txt_files) == 0:
        print("\n⚠️  Aucun fichier trouvé!")
        print("   Exécutez d'abord: python scripts/00_load_data.py")
        return
    
    # NOUVEAU: Demander combien de documents traiter
    print(f"\n{'='*60}")
    print("Sélection du nombre de documents")
    print("="*60)
    print(f"\nNombre total de fichiers disponibles: {len(txt_files)}")
    print("\nOptions:")
    print("  1. Tous les documents (défaut)")
    print("  2. Choisir un nombre spécifique")
    
    choice = input("\nVotre choix (1 ou 2, défaut=1): ").strip()
    
    num_docs_to_process = len(txt_files)  # Par défaut, tous
    
    if choice == "2":
        while True:
            try:
                num_input = input(f"\nNombre de documents à traiter (1-{len(txt_files)}): ").strip()
                num_docs = int(num_input)
                
                if 1 <= num_docs <= len(txt_files):
                    num_docs_to_process = num_docs
                    break
                else:
                    print(f"⚠️  Veuillez entrer un nombre entre 1 et {len(txt_files)}")
            except ValueError:
                print("⚠️  Veuillez entrer un nombre valide")
    
    print(f"\n✓ Traitement de {num_docs_to_process} document(s)")
    
    # Charger les documents
    print(f"\n{'='*60}")
    print("Étape 1/3: Chargement des documents")
    print("="*60)
    
    loader = DocumentLoader(raw_dir)
    all_documents = loader.load_all_documents()
    
    # Limiter au nombre choisi
    documents = all_documents[:num_docs_to_process]
    
    print(f"\n✓ Chargé: {len(documents)} documents (sur {len(all_documents)} disponibles)")
    
    if len(documents) == 0:
        print("❌ Aucun document chargé! Vérifiez les fichiers.")
        return
    
    # Nettoyer les textes
    print(f"\n{'='*60}")
    print("Étape 2/3: Nettoyage des textes")
    print("="*60)
    
    cleaner = TextCleaner()
    cleaned_count = 0
    
    for i, doc in enumerate(documents):
        try:
            original_length = len(doc['text'])
            doc['text'] = cleaner.clean(doc['text'])
            doc['paragraphs'] = cleaner.split_into_paragraphs(doc['text'])
            cleaned_length = len(doc['text'])
            
            # Statistiques de nettoyage
            reduction = 0
            if original_length > 0:
                reduction = ((original_length - cleaned_length) / original_length) * 100
            
            doc['cleaning_stats'] = {
                'original_length': original_length,
                'cleaned_length': cleaned_length,
                'reduction_percent': reduction,
                'num_paragraphs': len(doc['paragraphs'])
            }
            
            cleaned_count += 1
            
            # Afficher la progression tous les 100 docs ou tous les 10% si moins de 100
            progress_interval = min(100, max(1, len(documents) // 10))
            if (i + 1) % progress_interval == 0 or (i + 1) == len(documents):
                print(f"Progress: {i + 1}/{len(documents)} documents nettoyés...")
                
        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage du document {doc.get('filename', 'unknown')}: {e}")
            continue
    
    print(f"\n✓ Nettoyé: {cleaned_count}/{len(documents)} documents")
    
    # Sauvegarder
    print(f"\n{'='*60}")
    print("Étape 3/3: Sauvegarde")
    print("="*60)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    loader.save_processed(documents, output_file)
    
    # Statistiques finales
    total_chars = sum(len(doc['text']) for doc in documents)
    total_paragraphs = sum(len(doc.get('paragraphs', [])) for doc in documents)
    
    print(f"\n{'='*60}")
    print("TERMINÉ!")
    print("="*60)
    print(f"✅ Documents traités: {len(documents)}")
    print(f"📊 Caractères totaux: {total_chars:,}")
    print(f"📄 Paragraphes totaux: {total_paragraphs:,}")
    print(f"💾 Sauvegardé dans: {output_file.absolute()}")
    print(f"\n📌 Prochain étape: python scripts/02_extract_entities.py")
    print("="*60)

if __name__ == "__main__":
    main()