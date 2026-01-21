# src/extraction/entity_extractor.py

import spacy
from typing import List, Dict, Set
from collections import defaultdict

class EntityExtractor:
    """Extrait les entités nommées du texte."""
    
    def __init__(self, model_name: str = "fr_core_news_lg", entity_types: List[str] = None):
        self.nlp = spacy.load(model_name)
        self.entity_types = entity_types or ["PERSON", "ORG", "GPE", "DATE", "EVENT"]
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extrait les entités d'un texte."""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in self.entity_types:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        return entities
    
    def extract_and_normalize(self, text: str) -> Dict[str, Set[str]]:
        """Extrait et normalise les entités par type."""
        entities = self.extract_entities(text)
        normalized = defaultdict(set)
        
        for entity in entities:
            # Normalisation basique
            normalized_text = entity['text'].strip().lower()
            normalized[entity['label']].add(normalized_text)
        
        return dict(normalized)
    
    def extract_from_documents(self, documents: List[Dict]) -> List[Dict]:
        """Extrait les entités de plusieurs documents."""
        results = []
        
        for doc in documents:
            entities = self.extract_entities(doc['text'])
            results.append({
                'document_id': doc.get('filename', 'unknown'),
                'entities': entities
            })
        
        return results
