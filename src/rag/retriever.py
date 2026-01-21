# src/rag/retriever.py

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import chromadb

class HybridRetriever:
    """Récupération hybride : vectorielle + graphe."""
    
    def __init__(self, embedding_model: str, collection_name: str = "entities"):
        self.encoder = SentenceTransformer(embedding_model)
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(collection_name)
    
    def add_entities(self, entities: List[Dict]):
        """Ajoute des entités à l'index vectoriel."""
        texts = [e['text'] for e in entities]
        embeddings = self.encoder.encode(texts)
        
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=entities,
            ids=[f"entity_{i}" for i in range(len(entities))]
        )
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Recherche vectorielle."""
        query_embedding = self.encoder.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        
        return results['metadatas'][0] if results['metadatas'] else []
