# test_install.py
import sys

print("🔍 Vérification des imports...")

try:
    import spacy
    print("✅ spacy:", spacy.__version__)
    
    import torch
    print("✅ torch:", torch.__version__)
    
    import openai
    print("✅ openai:", openai.__version__)
    
    import neo4j
    print("✅ neo4j:", neo4j.__version__)
    
    import chromadb
    print("✅ chromadb OK")
    
    import streamlit
    print("✅ streamlit:", streamlit.__version__)
    
    import sentence_transformers
    print("✅ sentence-transformers OK")
    
    # Test spaCy français
    nlp = spacy.load("fr_core_news_lg")
    print("✅ Modèle français spaCy chargé")
    
    print("\n🎉 Tous les packages sont fonctionnels!")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)