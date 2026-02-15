# src/rag/context_builder.py

from typing import List, Dict

class ContextBuilder:
    """Construit le contexte pour le LLM à partir des résultats."""
    
    def __init__(self, max_context_length: int = 8000):
        self.max_context_length = max_context_length
    
    def build_context(self, 
                     vector_results: List[Dict],
                     graph_results: Dict,
                     include_citations: bool = True) -> str:
        """Construit un contexte structuré avec documents complets."""
        
        context_parts = []
        
        if graph_results.get('entities'):
            entities_text = "Entités trouvées:\n"
            for entity in graph_results['entities'][:20]:
                entities_text += f"- {entity.get('name', 'N/A')} ({entity.get('type', 'unknown')})\n"
            context_parts.append(entities_text)
        
        if graph_results.get('relationships'):
            rels_text = "\nRelations identifiées:\n"
            for rel in graph_results['relationships'][:30]:
                subject = rel.get('subject', '?')
                predicate = rel.get('type', 'relates to')
                obj = rel.get('object', '?')
                strength = rel.get('strength', 1)
                rels_text += f"- {subject} --[{predicate}]--> {obj}"
                if strength > 1:
                    rels_text += f" (force: {strength})"
                rels_text += "\n"
            context_parts.append(rels_text)
        
        if graph_results.get('contexts'):
            contexts_text = "\nContextes des mentions:\n"
            for ctx in graph_results['contexts'][:10]:
                doc_title = ctx.get('doc_title', ctx.get('doc_id', 'Document'))
                contexts_text += f"\nEntité '{ctx['entity']}' dans '{doc_title}':\n"
                contexts_text += f"...{ctx['context']}...\n"
            context_parts.append(contexts_text)
        
        if graph_results.get('documents'):
            docs_text = "\nDocuments sources (extraits):\n"
            for doc_id, doc_data in list(graph_results['documents'].items())[:5]:
                title = doc_data.get('title', doc_id)
                text = doc_data.get('text', '')
                excerpt = text[:500] if len(text) > 500 else text
                docs_text += f"\n[{title}]\n{excerpt}...\n"
            context_parts.append(docs_text)
        
        full_context = "\n".join(context_parts)
        
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "\n\n[Contexte tronqué pour longueur]"
        
        return full_context
    
    def build_full_context(self, graph_results: Dict) -> str:
        """Construit un contexte complet avec tous les documents."""
        context_parts = []
        
        if graph_results.get('entities'):
            entities_text = "=== ENTITÉS TROUVÉES ===\n"
            for entity in graph_results['entities']:
                entities_text += f"- {entity.get('name')} (Type: {entity.get('type')})\n"
            context_parts.append(entities_text)
        
        if graph_results.get('relationships'):
            rels_text = "\n=== RELATIONS ===\n"
            for rel in graph_results['relationships']:
                rels_text += f"{rel.get('subject')} --[{rel.get('type')}]--> {rel.get('object')}\n"
            context_parts.append(rels_text)
        
        if graph_results.get('documents'):
            docs_text = "\n=== DOCUMENTS COMPLETS ===\n"
            for doc_id, doc_data in graph_results['documents'].items():
                title = doc_data.get('title', doc_id)
                docs_text += f"\n--- {title} ---\n"
                docs_text += doc_data.get('text', '') + "\n"
            context_parts.append(docs_text)
        
        return "\n".join(context_parts)
    
    def format_sources(self, graph_results: Dict) -> List[str]:
        """Extrait les sources citables avec titres."""
        sources = []
        
        if graph_results.get('documents'):
            for doc_id, doc_data in graph_results['documents'].items():
                title = doc_data.get('title', doc_id)
                sources.append(f"{title}")
        
        return sources