import spacy
from typing import List, Dict
from openai import OpenAI
import os

class RelationExtractor:
    """Extrait les relations entre entités."""
    
    def __init__(self, use_llm: bool = True):
        self.nlp = spacy.load("fr_core_news_lg")
        self.use_llm = use_llm
        if use_llm:
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("LLM_API_BASE", "https://api.deepseek.com/v1")
            )
            self.model = os.getenv("LLM_MODEL", "deepseek-chat")
    
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
        """Extrait les relations en utilisant DeepSeek."""
        # Tronquer le texte si trop long
        text = text[:max_length]
        
        prompt = f"""Extrait les triplets (sujet, prédicat, objet) du texte suivant.
        
Texte: {text}

Réponds uniquement avec un JSON contenant une liste de triplets:
{{"relations": [{{"subject": "...", "predicate": "...", "object": "..."}}]}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            import json
            response_text = response.choices[0].message.content
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