# src/embeddings/vector_store.py

import chromadb
from chromadb.config import Settings
from typing import List, Dict
import json

class VectorStore:
    """Gestion du stockage vectoriel avec ChromaDB."""
    
    def __init__(self, collection_name: str = "kg_entities", persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_entities(self, entities: List[Dict]):
        """Ajoute des entités au store vectoriel."""
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Préparer les données
        texts = [e['text'] for e in entities]
        embeddings = model.encode(texts).tolist()
        ids = [f"entity_{i}" for i in range(len(entities))]
        metadatas = [{'text': e['text'], 'label': e.get('label', 'unknown')} for e in entities]
        
        # Ajouter par batch
        batch_size = 100
        for i in range(0, len(entities), batch_size):
            end = min(i + batch_size, len(entities))
            self.collection.add(
                embeddings=embeddings[i:end],
                documents=texts[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Recherche les entités similaires."""
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        query_embedding = model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )
        
        return results
    
    def save(self, path: str):
        """Sauvegarde l'état du store."""
        # ChromaDB persiste automatiquement
        print(f"Store vectoriel sauvegardé dans {self.client._settings.persist_directory}")
