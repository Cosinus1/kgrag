# src/extraction/relation_extractor.py

import spacy
from typing import List, Dict, Set, Tuple
from collections import defaultdict

class RelationExtractor:
    """Extrait les relations entre entités avec déduplication intelligente."""
    
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_lg")
    
    def extract_with_dependencies(self, text: str) -> List[Dict]:
        """Extrait les relations via les dépendances syntaxiques."""
        doc = self.nlp(text)
        relations = []
        
        for token in doc:
            if token.dep_ in ['nsubj', 'dobj', 'pobj']:
                subject = token.text
                predicate = token.head.text
                
                for child in token.head.children:
                    if child.dep_ in ['dobj', 'pobj'] and child != token:
                        relations.append({
                            'subject': subject,
                            'predicate': predicate,
                            'object': child.text,
                            'method': 'dependency'
                        })
        
        return relations
    
    def extract_relations(self, text: str) -> List[Dict]:
        """Extrait les relations syntaxiques."""
        return self.extract_with_dependencies(text)
    
    def normalize_relation(self, relation: Dict) -> Tuple[str, str, str]:
        """Normalise une relation pour la déduplication."""
        subject = relation['subject'].lower().strip()
        predicate = relation.get('predicate', 'relates_to').lower().strip()
        obj = relation['object'].lower().strip()
        
        # Ordre canonique : alphabétique pour les relations symétriques
        if predicate in ['co_occurs_with', 'near']:
            if subject > obj:
                subject, obj = obj, subject
        
        return (subject, predicate, obj)
    
    def deduplicate_relations(self, relations: List[Dict]) -> List[Dict]:
        """Déduplique les relations identiques."""
        seen = {}
        deduplicated = []
        
        for rel in relations:
            key = self.normalize_relation(rel)
            
            if key not in seen:
                seen[key] = rel
                deduplicated.append(rel)
            else:
                # Fusionner les informations (ex: augmenter strength)
                existing = seen[key]
                if 'strength' in rel:
                    existing['strength'] = existing.get('strength', 1) + 1
                if 'common_docs' in rel:
                    existing_docs = set(existing.get('common_docs', []))
                    new_docs = set(rel.get('common_docs', []))
                    existing['common_docs'] = list(existing_docs | new_docs)
        
        return deduplicated
    
    def extract_cooccurrence_relations(self, entities_by_doc: List[Dict], min_strength: int = 2) -> List[Dict]:
        """Extrait uniquement les co-occurrences significatives (≥2 documents)."""
        entity_docs = defaultdict(list)
        
        for doc_entities in entities_by_doc:
            doc_id = doc_entities['document_id']
            seen_in_doc = set()
            
            for entity in doc_entities['entities']:
                entity_key = (entity['text'].lower(), entity['label'])
                if entity_key not in seen_in_doc:
                    entity_docs[entity_key].append(doc_id)
                    seen_in_doc.add(entity_key)
        
        entity_pairs = defaultdict(set)
        
        for doc_entities in entities_by_doc:
            doc_id = doc_entities['document_id']
            doc_entities_list = doc_entities['entities']
            seen_pairs = set()
            
            for i, entity1 in enumerate(doc_entities_list):
                for entity2 in doc_entities_list[i+1:]:
                    if entity1['text'].lower() == entity2['text'].lower():
                        continue
                    
                    e1_norm = entity1['text'].lower()
                    e2_norm = entity2['text'].lower()
                    
                    pair_key = tuple(sorted([e1_norm, e2_norm]))
                    if pair_key in seen_pairs:
                        continue
                    
                    seen_pairs.add(pair_key)
                    entity_pairs[pair_key].add(doc_id)
        
        relations = []
        for (e1, e2), docs in entity_pairs.items():
            strength = len(docs)
            if strength >= min_strength:
                relations.append({
                    'subject': e1,
                    'predicate': 'co_occurs_with',
                    'object': e2,
                    'method': 'cooccurrence',
                    'common_docs': list(docs),
                    'strength': strength
                })
        
        return relations
    
    def extract_proximity_relations(self, doc_entities: Dict, window: int = 100, max_per_doc: int = 50) -> List[Dict]:
        """Extrait uniquement les relations de proximité les plus proches."""
        relations = []
        entities = sorted(doc_entities['entities'], key=lambda e: e['start'])
        
        seen_pairs = set()
        
        for i, entity1 in enumerate(entities):
            proximity_count = 0
            
            for entity2 in entities[i+1:]:
                if entity1['text'].lower() == entity2['text'].lower():
                    continue
                
                distance = entity2['start'] - entity1['end']
                
                if distance > window:
                    break
                
                if distance < 0:
                    continue
                
                pair_key = tuple(sorted([entity1['text'].lower(), entity2['text'].lower()]))
                if pair_key in seen_pairs:
                    continue
                
                seen_pairs.add(pair_key)
                
                relations.append({
                    'subject': entity1['text'].lower(),
                    'predicate': 'near',
                    'object': entity2['text'].lower(),
                    'method': 'proximity',
                    'distance': distance,
                    'doc_id': doc_entities['document_id']
                })
                
                proximity_count += 1
                if proximity_count >= max_per_doc:
                    break
        
        return relations[:max_per_doc]
    
    def filter_by_entity_frequency(self, relations: List[Dict], entities_by_doc: List[Dict], min_mentions: int = 2) -> List[Dict]:
        """Ne garde que les relations entre entités mentionnées plusieurs fois."""
        entity_counts = defaultdict(int)
        
        for doc_entities in entities_by_doc:
            seen_in_doc = set()
            for entity in doc_entities['entities']:
                entity_norm = entity['text'].lower()
                if entity_norm not in seen_in_doc:
                    entity_counts[entity_norm] += 1
                    seen_in_doc.add(entity_norm)
        
        filtered = []
        for rel in relations:
            subject = rel['subject'].lower()
            obj = rel['object'].lower()
            
            if entity_counts[subject] >= min_mentions or entity_counts[obj] >= min_mentions:
                filtered.append(rel)
        
        return filtered