# src/rag/llm_interface.py

import anthropic
import os
from typing import Dict, List

class LLMInterface:
    """Interface pour interagir avec le LLM."""
    
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
    
    def format_context(self, graph_context: Dict) -> str:
        """Formate le contexte du graphe pour le LLM."""
        context_parts = []
        
        # Entités
        if graph_context.get('entities'):
            entities_str = "\n".join([
                f"- {e['name']} ({e.get('type', 'unknown')})" 
                for e in graph_context['entities']
            ])
            context_parts.append(f"Entités pertinentes:\n{entities_str}")
        
        # Relations
        if graph_context.get('relationships'):
            rels_str = "\n".join([
                f"- {r.get('subject', '?')} --[{r.get('type', 'relates to')}]--> {r.get('object', '?')}"
                for r in graph_context['relationships']
            ])
            context_parts.append(f"\nRelations:\n{rels_str}")
        
        return "\n\n".join(context_parts)
    
    def answer_question(self, question: str, context: str) -> Dict:
        """Génère une réponse basée sur le contexte."""
        prompt = f"""Tu es un assistant qui répond aux questions en te basant sur un graphe de connaissances.

Contexte du graphe:
{context}

Question: {question}

Réponds de manière précise en te basant uniquement sur le contexte fourni. Si l'information n'est pas dans le contexte, dis-le clairement."""
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            'answer': message.content[0].text,
            'model': self.model,
            'usage': message.usage
        }
