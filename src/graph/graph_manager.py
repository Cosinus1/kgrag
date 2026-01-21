# src/graph/graph_manager.py

from typing import List, Dict
from .graph_builder import GraphBuilder
from .graph_queries import GraphQueries

class GraphManager:
    """Gestionnaire principal du graphe de connaissances."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.builder = GraphBuilder(uri, user, password)
        self.queries = GraphQueries(uri, user, password)
    
    def close(self):
        """Ferme les connexions."""
        self.builder.close()
        self.queries.close()
    
    def rebuild_graph(self, entities: List[Dict], relations: List[Dict], documents: List[Dict]):
        """Reconstruit le graphe complet."""
        self.builder.clear_database()
        self.builder.build_graph(entities, relations, documents)
    
    def add_documents(self, documents: List[Dict]):
        """Ajoute de nouveaux documents au graphe."""
        # À implémenter
        pass
    
    def update_entity(self, entity_name: str, new_data: Dict):
        """Met à jour une entité existante."""
        # À implémenter
        pass
    
    def get_statistics(self) -> Dict:
        """Récupère les statistiques du graphe."""
        # À implémenter
        return {
            'entities': 0,
            'relationships': 0,
            'documents': 0
        }
