# src/graph/graph_queries.py

from neo4j import GraphDatabase
from typing import List, Dict

class GraphQueries:
    """Requêtes pour interroger le graphe."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def find_entity(self, entity_name: str) -> Dict:
        """Trouve une entité par nom."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.name = $name OR e.normalized_name = $normalized
                RETURN e
            """, name=entity_name, normalized=entity_name.lower())
            
            record = result.single()
            return dict(record['e']) if record else None
    
    def get_neighbors(self, entity_name: str, max_depth: int = 1) -> List[Dict]:
        """Récupère les voisins d'une entité."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (start:Entity)-[*1..%d]-(neighbor:Entity)
                WHERE start.name = $name
                RETURN DISTINCT neighbor, length(path) as depth
                ORDER BY depth
            """ % max_depth, name=entity_name)
            
            return [{'entity': dict(record['neighbor']), 
                    'depth': record['depth']} 
                   for record in result]
    
    def find_path(self, entity1: str, entity2: str) -> List[Dict]:
        """Trouve le plus court chemin entre deux entités."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (a:Entity {name: $entity1})-[*]-(b:Entity {name: $entity2})
                )
                RETURN path
            """, entity1=entity1, entity2=entity2)
            
            record = result.single()
            if record:
                path = record['path']
                nodes = [dict(node) for node in path.nodes]
                relationships = [dict(rel) for rel in path.relationships]
                return {'nodes': nodes, 'relationships': relationships}
            return None
    
    def search_entities_by_type(self, entity_type: str, limit: int = 10) -> List[Dict]:
        """Recherche des entités par type."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)
                WHERE e.type = $type
                RETURN e
                LIMIT $limit
            """, type=entity_type, limit=limit)
            
            return [dict(record['e']) for record in result]
