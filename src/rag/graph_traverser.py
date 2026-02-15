# src/rag/graph_traverser.py

from typing import List, Dict
from src.graph.graph_queries import GraphQueries

class GraphTraverser:
    """Parcourt le graphe avec limites mémoire strictes."""
    
    def __init__(self, graph_queries: GraphQueries):
        self.graph = graph_queries
    
    def traverse_from_entities(self, entity_names: List[str], max_depth: int = 2) -> Dict:
        """Parcourt le graphe avec limites strictes."""
        context = {
            'entities': [],
            'relationships': [],
            'documents': {},
            'contexts': []
        }
        
        seen_entities = set()
        seen_docs = set()
        
        max_entities = 50
        max_docs = 10
        
        for entity_name in entity_names[:5]:
            if len(context['entities']) >= max_entities:
                break
            
            entity_data = self.graph.get_entity_with_documents(entity_name, limit_docs=3)
            if entity_data:
                entity = entity_data['entity']
                if entity['name'] not in seen_entities:
                    context['entities'].append(entity)
                    seen_entities.add(entity['name'])
                
                for doc_info in entity_data['documents']:
                    if len(seen_docs) >= max_docs:
                        break
                    
                    doc_id = doc_info['doc_id']
                    if doc_id and doc_id not in seen_docs:
                        context['documents'][doc_id] = {
                            'id': doc_id,
                            'title': doc_info.get('doc_title', doc_id),
                            'text': doc_info.get('doc_text', '')
                        }
                        seen_docs.add(doc_id)
                    
                    if doc_info.get('context'):
                        context['contexts'].append({
                            'entity': entity['name'],
                            'doc_id': doc_id,
                            'doc_title': doc_info.get('doc_title', doc_id),
                            'context': doc_info['context']
                        })
                
                if len(context['entities']) < max_entities // 2:
                    related = self.graph.get_related_entities(entity_name, limit=5)
                    for rel_data in related[:5]:
                        if len(context['entities']) >= max_entities:
                            break
                        
                        rel_entity = rel_data['entity']
                        if rel_entity['name'] not in seen_entities:
                            context['entities'].append(rel_entity)
                            seen_entities.add(rel_entity['name'])
                        
                        relation = rel_data['relation']
                        context['relationships'].append({
                            'subject': entity_name,
                            'type': relation.get('type', 'relates_to'),
                            'object': rel_entity['name'],
                            'strength': relation.get('strength', 1)
                        })
                        
                        if len(seen_docs) < max_docs:
                            for doc_info in rel_data['documents'][:2]:
                                if len(seen_docs) >= max_docs:
                                    break
                                
                                doc_id = doc_info['doc_id']
                                if doc_id and doc_id not in seen_docs:
                                    context['documents'][doc_id] = {
                                        'id': doc_id,
                                        'title': doc_info.get('doc_title', doc_id),
                                        'text': doc_info.get('doc_text', '')
                                    }
                                    seen_docs.add(doc_id)
                
                if max_depth > 1 and len(context['entities']) < max_entities // 2:
                    neighbors = self.graph.get_neighbors(entity_name, max_depth=max_depth, limit=5)
                    for neighbor_data in neighbors[:5]:
                        if len(context['entities']) >= max_entities:
                            break
                        
                        neighbor = neighbor_data['entity']
                        if neighbor['name'] not in seen_entities:
                            context['entities'].append(neighbor)
                            seen_entities.add(neighbor['name'])
                        
                        if len(seen_docs) < max_docs:
                            for doc_info in neighbor_data['documents'][:1]:
                                if len(seen_docs) >= max_docs:
                                    break
                                
                                doc_id = doc_info['doc_id']
                                if doc_id and doc_id not in seen_docs:
                                    context['documents'][doc_id] = {
                                        'id': doc_id,
                                        'title': doc_info.get('doc_title', doc_id),
                                        'text': doc_info.get('doc_text', '')
                                    }
                                    seen_docs.add(doc_id)
        
        return context
    
    def find_connecting_paths(self, entities: List[str]) -> List[Dict]:
        """Trouve les chemins entre entités avec limite."""
        paths = []
        
        for i, entity1 in enumerate(entities[:3]):
            for entity2 in entities[i+1:i+3]:
                path = self.graph.find_path(entity1, entity2)
                if path:
                    paths.append(path)
                if len(paths) >= 3:
                    return paths
        
        return paths