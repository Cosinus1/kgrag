# src/embeddings/vector_store.py

import chromadb
from typing import List, Dict
import json

class VectorStore:
    """Gestion du stockage vectoriel avec ChromaDB."""
    
    def __init__(self, collection_name: str = "kg_entities", persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client and collection."""
        # Use PersistentClient for newer ChromaDB versions
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
        except AttributeError:
            # Fallback for older versions
            self.client = chromadb.Client(chromadb.Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
        
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Get or create collection
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Warning: Could not set metadata: {e}")
            self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_entities(self, entities: List[Dict]):
        """Ajoute des entités au store vectoriel."""
        from sentence_transformers import SentenceTransformer
        
        print(f"  Chargement du modèle d'embeddings...")
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        # Préparer les données
        texts = [e['text'] for e in entities]
        
        print(f"  Génération des embeddings...")
        embeddings = model.encode(texts, show_progress_bar=True).tolist()
        
        ids = [f"entity_{i}" for i in range(len(entities))]
        metadatas = [
            {
                'text': e['text'], 
                'label': e.get('label', 'unknown'),
                'start': str(e.get('start', 0)),
                'end': str(e.get('end', 0))
            } 
            for e in entities
        ]
        
        # Ajouter par batch pour éviter les problèmes de mémoire
        batch_size = 1000
        print(f"  Ajout au vector store par batches de {batch_size}...")
        
        for i in range(0, len(entities), batch_size):
            end = min(i + batch_size, len(entities))
            
            try:
                self.collection.add(
                    embeddings=embeddings[i:end],
                    documents=texts[i:end],
                    metadatas=metadatas[i:end],
                    ids=ids[i:end]
                )
                
                if (end % 5000 == 0) or (end == len(entities)):
                    print(f"    Ajouté {end}/{len(entities)} entités...")
                    
            except Exception as e:
                print(f"  Erreur lors de l'ajout du batch {i}-{end}: {e}")
                continue
        
        print(f"  ✓ {len(entities)} entités ajoutées au vector store")
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Recherche les entités similaires."""
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        query_embedding = model.encode([query]).tolist()
        
        try:
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results and 'documents' in results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'document': doc,
                        'metadata': results['metadatas'][0][i] if results.get('metadatas') else {},
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def save(self, path: str = None):
        """Sauvegarde l'état du store."""
        # ChromaDB with PersistentClient saves automatically
        print(f"  ✓ Vector store sauvegardé automatiquement dans {self.persist_directory}")
    
    def count(self) -> int:
        """Retourne le nombre d'entités dans le store."""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Erreur lors du comptage: {e}")
            return 0
    
    def delete_collection(self):
        """Supprime la collection (pour réinitialiser)."""
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Collection {self.collection_name} supprimée")
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")