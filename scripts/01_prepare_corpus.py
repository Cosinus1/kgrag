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
    
    # Charger les documents
    print("Chargement des documents...")
    loader = DocumentLoader(raw_dir)
    documents = loader.load_all_documents()
    
    # Nettoyer les textes
    print("Nettoyage des textes...")
    cleaner = TextCleaner()
    for doc in documents:
        doc['text'] = cleaner.clean(doc['text'])
        doc['paragraphs'] = cleaner.split_into_paragraphs(doc['text'])
    
    # Sauvegarder
    print(f"Sauvegarde de {len(documents)} documents...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    loader.save_processed(documents, output_file)
    
    print("Terminé!")

if __name__ == "__main__":
    main()
