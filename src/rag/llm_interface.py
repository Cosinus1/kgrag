from openai import OpenAI
import os
from typing import Dict, List

class LLMInterface:
    """Interface pour interagir avec DeepSeek LLM."""
    
    def __init__(self, model: str = None):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("LLM_API_BASE", "https://api.deepseek.com/v1")
        )
        self.model = model or os.getenv("LLM_MODEL", "deepseek-chat")
    
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                'answer': f"Erreur lors de la génération de la réponse: {str(e)}",
                'model': self.model,
                'usage': None
            }