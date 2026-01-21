# src/rag/context_builder.py

from typing import List, Dict

class ContextBuilder:
    """Construit le contexte pour le LLM à partir des résultats."""
    
    def __init__(self, max_context_length: int = 3000):
        self.max_context_length = max_context_length
    
    def build_context(self, 
                     vector_results: List[Dict],
                     graph_results: Dict,
                     include_citations: bool = True) -> str:
        """Construit un contexte structuré."""
        
        context_parts = []
        
        # Section 1 : Entités pertinentes
        if graph_results.get('entities'):
            entities_text = "## Entités pertinentes\n\n"
            for entity in graph_results['entities'][:10]:  # Limiter à 10
                entities_text += f"- **{entity.get('name', 'N/A')}** ({entity.get('type', 'unknown')})\n"
            context_parts.append(entities_text)
        
        # Section 2 : Relations
        if graph_results.get('relationships'):
            rels_text = "## Relations identifiées\n\n"
            for rel in graph_results['relationships'][:15]:  # Limiter à 15
                subject = rel.get('subject', '?')
                predicate = rel.get('type', 'relates to')
                obj = rel.get('object', '?')
                rels_text += f"- {subject} → [{predicate}] → {obj}\n"
            context_parts.append(rels_text)
        
        # Section 3 : Chemins dans le graphe
        if graph_results.get('paths'):
            paths_text = "## Chemins dans le graphe\n\n"
            for i, path in enumerate(graph_results['paths'][:3], 1):
                nodes = " → ".join([n.get('name', '?') for n in path.get('nodes', [])])
                paths_text += f"{i}. {nodes}\n"
            context_parts.append(paths_text)
        
        # Assembler et tronquer si nécessaire
        full_context = "\n\n".join(context_parts)
        
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "\n\n[Contexte tronqué...]"
        
        return full_context
    
    def format_sources(self, graph_results: Dict) -> List[str]:
        """Extrait les sources citables."""
        sources = set()
        
        # Extraire les documents mentionnés
        for entity in graph_results.get('entities', []):
            if 'source_document' in entity:
                sources.add(entity['source_document'])
        
        return list(sources)
