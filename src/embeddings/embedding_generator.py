# src/embeddings/embedding_generator.py

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
from tqdm import tqdm

class EmbeddingGenerator:
    """Génère des embeddings pour les entités et textes."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        print(f"Chargement du modèle {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    def encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode une liste de textes."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def encode_entities(self, entities: List[Dict]) -> Dict[str, np.ndarray]:
        """Encode les entités avec leurs métadonnées."""
        # Créer des descriptions enrichies
        texts = []
        for entity in entities:
            text = f"{entity['text']} ({entity.get('label', 'unknown')})"
            texts.append(text)
        
        # Générer les embeddings
        embeddings = self.encode_texts(texts)
        
        # Associer aux entités
        result = {}
        for i, entity in enumerate(entities):
            result[entity['text']] = embeddings[i]
        
        return result
