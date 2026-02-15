# src/rag/llm_interface.py

import os
from typing import Dict

class LLMInterface:
    """Interface pour interagir avec le LLM."""
    
    def __init__(self, provider: str = None, model: str = None):
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
    
    def answer_question(self, question: str, context: str) -> Dict:
        """Génère une réponse basée sur le contexte du graphe."""
        
        system_prompt = """Tu es un assistant expert qui analyse un graphe de connaissances pour répondre à des questions.

INSTRUCTIONS:
1. Analyse attentivement le contexte fourni (entités, relations, documents)
2. Identifie les informations pertinentes pour la question
3. Synthétise une réponse claire et précise basée UNIQUEMENT sur le contexte
4. Si l'information n'est pas disponible, indique-le clairement
5. Cite les sources quand c'est pertinent

FORMAT DE RÉPONSE:
- Commence directement par la réponse
- Sois concis et factuel
- Utilise des paragraphes courts
- Ne répète pas le contexte, synthétise-le"""

        user_prompt = f"""CONTEXTE DU GRAPHE:
{context}

QUESTION: {question}

Réponds de manière concise en te basant sur le contexte fourni."""
        
        try:
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=3000,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=3000
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