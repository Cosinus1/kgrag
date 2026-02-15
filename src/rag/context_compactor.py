# src/rag/context_compactor.py

from typing import Dict, List
import re

class ContextCompactor:
    """Compacte intelligemment le contexte pour éviter les dépassements de tokens."""
    
    def __init__(self, max_tokens: int = 100000):
        self.max_tokens = max_tokens
        self.chars_per_token = 4
        self.max_chars = max_tokens * self.chars_per_token
    
    def estimate_tokens(self, text: str) -> int:
        """Estime le nombre de tokens (approximatif)."""
        return len(text) // self.chars_per_token
    
    def compact_document(self, doc_text: str, max_chars: int = 2000) -> str:
        """Compacte un document en gardant début et extraits clés."""
        if len(doc_text) <= max_chars:
            return doc_text
        
        lines = doc_text.split('\n')
        
        title = ""
        for line in lines[:5]:
            if line.startswith('#'):
                title = line.strip()
                break
        
        intro_chars = max_chars // 3
        intro = doc_text[:intro_chars]
        
        paragraphs = [p.strip() for p in doc_text.split('\n\n') if len(p.strip()) > 50]
        important_paragraphs = []
        
        keywords = ['est', 'était', 'sont', 'étaient', 'a été', 'ont été', 'fut', 'furent']
        
        for para in paragraphs:
            para_lower = para.lower()
            score = sum(1 for kw in keywords if kw in para_lower)
            if score > 0:
                important_paragraphs.append((score, para))
        
        important_paragraphs.sort(reverse=True, key=lambda x: x[0])
        
        selected = []
        current_length = len(intro)
        remaining_chars = max_chars - intro_chars
        
        for score, para in important_paragraphs:
            if current_length + len(para) <= max_chars:
                selected.append(para)
                current_length += len(para)
            if current_length >= remaining_chars:
                break
        
        compacted = f"{title}\n\n{intro}\n\n[...]\n\n" + "\n\n".join(selected[:5])
        
        return compacted[:max_chars]
    
    def compact_documents(self, documents: Dict, max_total_chars: int = 50000) -> Dict:
        """Compacte tous les documents."""
        if not documents:
            return {}
        
        num_docs = len(documents)
        chars_per_doc = min(2000, max_total_chars // num_docs)
        
        compacted = {}
        for doc_id, doc_data in documents.items():
            text = doc_data.get('text', '')
            title = doc_data.get('title', doc_id)
            
            compacted_text = self.compact_document(text, chars_per_doc)
            
            compacted[doc_id] = {
                'id': doc_id,
                'title': title,
                'text': compacted_text
            }
        
        return compacted
    
    def compact_context(self, graph_context: Dict) -> Dict:
        """Compacte tout le contexte du graphe."""
        compacted = {
            'entities': graph_context.get('entities', [])[:50],
            'relationships': graph_context.get('relationships', [])[:50],
            'contexts': [],
            'documents': {}
        }
        
        contexts = graph_context.get('contexts', [])
        unique_contexts = {}
        for ctx in contexts:
            entity = ctx['entity']
            if entity not in unique_contexts:
                context_text = ctx.get('context', '')
                if len(context_text) > 400:
                    context_text = context_text[:200] + "..." + context_text[-200:]
                unique_contexts[entity] = {
                    'entity': entity,
                    'doc_id': ctx.get('doc_id'),
                    'doc_title': ctx.get('doc_title'),
                    'context': context_text
                }
        
        compacted['contexts'] = list(unique_contexts.values())[:20]
        
        documents = graph_context.get('documents', {})
        if documents:
            total_chars = sum(len(d.get('text', '')) for d in documents.values())
            
            if total_chars > self.max_chars * 0.7:
                max_doc_chars = int(self.max_chars * 0.7)
                compacted['documents'] = self.compact_documents(documents, max_doc_chars)
            else:
                compacted['documents'] = documents
        
        return compacted
    
    def build_compact_context_string(self, compacted_context: Dict) -> str:
        """Construit une chaîne de contexte compacte."""
        parts = []
        
        if compacted_context.get('entities'):
            entities_by_type = {}
            for entity in compacted_context['entities']:
                etype = entity.get('type', 'unknown')
                if etype not in entities_by_type:
                    entities_by_type[etype] = []
                entities_by_type[etype].append(entity.get('name'))
            
            entities_text = "ENTITÉS:\n"
            for etype, names in entities_by_type.items():
                entities_text += f"{etype}: {', '.join(names[:10])}\n"
            parts.append(entities_text)
        
        if compacted_context.get('relationships'):
            rels = compacted_context['relationships']
            rels_by_type = {}
            for rel in rels:
                rel_type = rel.get('type', 'relates_to')
                if rel_type not in rels_by_type:
                    rels_by_type[rel_type] = []
                rels_by_type[rel_type].append(f"{rel.get('subject')} → {rel.get('object')}")
            
            rels_text = "\nRELATIONS:\n"
            for rel_type, pairs in rels_by_type.items():
                rels_text += f"{rel_type}: " + "; ".join(pairs[:5]) + "\n"
            parts.append(rels_text)
        
        if compacted_context.get('documents'):
            docs_text = "\nDOCUMENTS:\n"
            for doc_id, doc_data in list(compacted_context['documents'].items())[:10]:
                title = doc_data.get('title', doc_id)
                text = doc_data.get('text', '')
                docs_text += f"\n[{title}]\n{text}\n"
            parts.append(docs_text)
        
        context_string = "\n".join(parts)
        
        if len(context_string) > self.max_chars:
            context_string = context_string[:self.max_chars] + "\n\n[Contexte tronqué]"
        
        return context_string