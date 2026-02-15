# src/extraction/relation_extractor.py

import spacy
from typing import List, Dict
import os

class RelationExtractor:
    """Extrait les relations entre entités."""
    
    def __init__(self, use_llm: bool = False, llm_provider: str = "deepseek"):
        self.nlp = spacy.load("fr_core_news_lg")
        self.use_llm = use_llm
        self.llm_provider = llm_provider.lower()
        
        if use_llm:
            if self.llm_provider == "anthropic":
                try:
                    import anthropic
                    self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                    self.model = "claude-sonnet-4-20250514"
                except Exception as e:
                    print(f"⚠️  Erreur Anthropic: {e}")
                    print("Basculement vers le mode syntaxique")
                    self.use_llm = False
                    
            elif self.llm_provider in ["deepseek", "openai"]:
                try:
                    from openai import OpenAI
                    
                    if self.llm_provider == "deepseek":
                        api_key = os.getenv("DEEPSEEK_API_KEY")
                        if not api_key:
                            raise ValueError("DEEPSEEK_API_KEY not found in environment")
                        
                        self.client = OpenAI(
                            api_key=api_key,
                            base_url="https://api.deepseek.com"
                        )
                        self.model = "deepseek-chat"
                        print(f"✓ DeepSeek configuré avec le modèle {self.model}")
                    else:
                        api_key = os.getenv("OPENAI_API_KEY")
                        if not api_key:
                            raise ValueError("OPENAI_API_KEY not found in environment")
                        
                        self.client = OpenAI(api_key=api_key)
                        self.model = "gpt-4o-mini"
                        print(f"✓ OpenAI configuré avec le modèle {self.model}")
                        
                except Exception as e:
                    print(f"⚠️  Erreur {self.llm_provider}: {e}")
                    print("Basculement vers le mode syntaxique")
                    self.use_llm = False
            else:
                print(f"⚠️  Provider '{self.llm_provider}' non supporté")
                self.use_llm = False
    
    def extract_with_dependencies(self, text: str) -> List[Dict]:
        """Extrait les relations via les dépendances syntaxiques - SEULEMENT entre entités nommées."""
        doc = self.nlp(text)
        relations = []
        
        # CRITICAL FIX: Extract entities first
        entity_texts = {ent.text for ent in doc.ents}
        
        if len(entity_texts) < 2:
            return []  # Need at least 2 entities
        
        # Only create relations where BOTH subject AND object are entities
        for token in doc:
            if token.text not in entity_texts:
                continue
                
            if token.dep_ in ['nsubj', 'dobj', 'pobj']:
                subject = token.text
                predicate = token.head.text
                
                for child in token.head.children:
                    if child.dep_ in ['dobj', 'pobj'] and child != token:
                        # CRITICAL: object must also be an entity
                        if child.text in entity_texts:
                            relations.append({
                                'subject': subject,
                                'predicate': predicate,
                                'object': child.text,
                                'method': 'dependency'
                            })
        
        return relations
    
    def extract_with_llm(self, text: str, max_length: int = 2000) -> List[Dict]:
        """Extrait les relations en utilisant un LLM."""
        text = text[:max_length]
        
        prompt = f"""Extrait les triplets (sujet, prédicat, objet) du texte suivant.

Texte: {text}

Réponds uniquement avec un JSON contenant une liste de triplets:
{{"relations": [{{"subject": "...", "predicate": "...", "object": "..."}}]}}"""
        
        try:
            if self.llm_provider == "anthropic":
                import anthropic
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = message.content[0].text
                
            elif self.llm_provider in ["deepseek", "openai"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un expert en extraction d'informations. Réponds toujours en JSON valide."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                response_text = response.choices[0].message.content
            
            import json
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(response_text)
            
            for rel in result.get('relations', []):
                rel['method'] = f'llm_{self.llm_provider}'
            
            return result.get('relations', [])
            
        except Exception as e:
            print(f"⚠️  Erreur LLM: {e}")
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