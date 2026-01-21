# src/extraction/relation_extractor.py

import spacy
from typing import List, Dict
import anthropic
import os

class RelationExtractor:
    """Extrait les relations entre entités."""
    
    def __init__(self, use_llm: bool = True):
        self.nlp = spacy.load("fr_core_news_lg")
        self.use_llm = use_llm
        if use_llm:
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
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
    
    def extract_with_llm(self, text: str, max_length: int = 2000) -> List[Dict]:
        """Extrait les relations en utilisant un LLM."""
        # Tronquer le texte si trop long
        text = text[:max_length]
        
        prompt = f"""Extrait les triplets (sujet, prédicat, objet) du texte suivant.
        
Texte: {text}

Réponds uniquement avec un JSON contenant une liste de triplets:
{{"relations": [{{"subject": "...", "predicate": "...", "object": "..."}}]}}"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            import json
            response_text = message.content[0].text
            # Nettoyage des balises markdown si présentes
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(response_text)
            
            for rel in result.get('relations', []):
                rel['method'] = 'llm'
            
            return result.get('relations', [])
        except Exception as e:
            print(f"Erreur LLM: {e}")
            return []
    
    def extract_relations(self, text: str) -> List[Dict]:
        """Extrait les relations (méthode hybride)."""
        relations = []
        
        # Relations syntaxiques
        relations.extend(self.extract_with_dependencies(text))
        
        # Relations via LLM si activé
        if self.use_llm:
            relations.extend(self.extract_with_llm(text))
        
        return relations
