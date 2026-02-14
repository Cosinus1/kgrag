# src/rag/llm_interface.py

import os
from typing import Dict

class LLMInterface:
    """Interface pour interagir avec le LLM."""
    
    def __init__(self, provider: str = None, model: str = None):
        # Auto-detect provider based on available API keys
        if provider is None:
            if os.getenv("DEEPSEEK_API_KEY"):
                provider = "deepseek"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            elif os.getenv("OPENAI_API_KEY"):
                provider = "openai"
            else:
                raise ValueError(
                    "No LLM API key found! Set one of: DEEPSEEK_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY"
                )
        
        self.provider = provider.lower()
        
        # Initialize client based on provider
        if self.provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-sonnet-4-20250514"
            
        elif self.provider in ["deepseek", "openai"]:
            from openai import OpenAI
            
            if self.provider == "deepseek":
                self.client = OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com"
                )
                self.model = model or "deepseek-chat"
            else:
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.model = model or "gpt-4o-mini"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def format_context(self, graph_context: Dict) -> str:
        """Formate le contexte du graphe pour le LLM."""
        context_parts = []
        
        # Entités
        if graph_context.get('entities'):
            entities_str = "\n".join([
                f"- {e.get('name', 'Unknown')} ({e.get('type', 'unknown')})" 
                for e in graph_context['entities'][:20]  # Limit to avoid token overflow
            ])
            context_parts.append(f"Entités pertinentes:\n{entities_str}")
        
        # Relations
        if graph_context.get('relationships'):
            rels_str = "\n".join([
                f"- {r.get('subject', '?')} --[{r.get('type', 'relates to')}]--> {r.get('object', '?')}"
                for r in graph_context['relationships'][:30]  # Limit
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
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = message.content[0].text
                usage = {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens
                }
                
            elif self.provider in ["deepseek", "openai"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un assistant expert qui répond aux questions basées sur un graphe de connaissances."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                answer = response.choices[0].message.content
                usage = {
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens
                }
            
            return {
                'answer': answer,
                'model': self.model,
                'provider': self.provider,
                'usage': usage
            }
            
        except Exception as e:
            return {
                'answer': f"Erreur lors de la génération de la réponse: {e}",
                'model': self.model,
                'provider': self.provider,
                'error': str(e)
            }