# src/rag/graph_traverser.py

from typing import List, Dict
from src.graph.graph_queries import GraphQueries

class GraphTraverser:
    """Parcourt le graphe pour récupérer du contexte."""
    
    def __init__(self, graph_queries: GraphQueries):
        self.graph = graph_queries
    
    def traverse_from_entities(self, entity_names: List[str], max_depth: int = 2) -> Dict:
        """Parcourt le graphe à partir d'entités."""
        context = {
            'entities': [],
            'relationships': [],
            'paths': []
        }
        
        for entity_name in entity_names:
            # Récupérer l'entité
            entity = self.graph.find_entity(entity_name)
            if entity:
                context['entities'].append(entity)
                
                # Récupérer les voisins
                neighbors = self.graph.get_neighbors(entity_name, max_depth)
                context['entities'].extend([n['entity'] for n in neighbors])
        
        return context
    
    def find_connecting_paths(self, entities: List[str]) -> List[Dict]:
        """Trouve les chemins entre plusieurs entités."""
        paths = []
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                path = self.graph.find_path(entity1, entity2)
                if path:
                    paths.append(path)
        
        return paths
