# src/graph/graph_queries.py

from neo4j import GraphDatabase
from typing import List, Dict

class GraphQueries:
    """Requêtes pour interroger le graphe avec optimisation mémoire."""
    
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
                LIMIT 1
            """, name=entity_name, normalized=entity_name.lower())
            
            record = result.single()
            return dict(record['e']) if record else None
    
    def get_entity_with_documents(self, entity_name: str, limit_docs: int = 5) -> Dict:
        """Récupère une entité avec documents limités."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)-[r:MENTIONED_IN]->(d:Document)
                WHERE e.name = $name OR e.normalized_name = $normalized
                WITH e, r, d
                LIMIT $doc_limit
                RETURN e, collect({
                    doc_id: d.id,
                    doc_title: d.title,
                    doc_text: substring(d.text, 0, 3000),
                    context: r.context
                }) as documents
            """, name=entity_name, normalized=entity_name.lower(), doc_limit=limit_docs)
            
            record = result.single()
            if record:
                return {
                    'entity': dict(record['e']),
                    'documents': record['documents']
                }
            return None
    
    def get_neighbors(self, entity_name: str, max_depth: int = 1, limit: int = 10) -> List[Dict]:
        """Récupère les voisins avec limite stricte."""
        with self.driver.session() as session:
            query_text = """
                MATCH path = (start:Entity)-[*1..%d]-(neighbor:Entity)
                WHERE start.name = $name
                WITH DISTINCT neighbor, length(path) as depth
                ORDER BY depth
                LIMIT $neighbor_limit
                OPTIONAL MATCH (neighbor)-[r:MENTIONED_IN]->(d:Document)
                WITH neighbor, depth, r, d
                LIMIT $total_limit
                RETURN neighbor, 
                       depth,
                       collect(DISTINCT {
                           doc_id: d.id,
                           doc_title: d.title,
                           doc_text: substring(d.text, 0, 2000),
                           context: r.context
                       })[0..3] as documents
            """ % max_depth
            
            result = session.run(query_text, 
                               name=entity_name, 
                               neighbor_limit=limit,
                               total_limit=limit * 3)
            
            return [{
                'entity': dict(record['neighbor']), 
                'depth': record['depth'],
                'documents': record['documents']
            } for record in result]
    
    def find_path(self, entity1: str, entity2: str) -> Dict:
        """Trouve le plus court chemin."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (a:Entity {name: $entity1})-[*..5]-(b:Entity {name: $entity2})
                )
                RETURN path
                LIMIT 1
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
    
    def get_related_entities(self, entity_name: str, limit: int = 10) -> List[Dict]:
        """Récupère les entités reliées avec limite stricte."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e:Entity {name: $name})-[r:RELATES_TO]-(related:Entity)
                WITH DISTINCT related, r
                LIMIT $rel_limit
                OPTIONAL MATCH (related)-[m:MENTIONED_IN]->(d:Document)
                WITH related, r, m, d
                LIMIT $total_limit
                RETURN related, r, collect(DISTINCT {
                    doc_id: d.id,
                    doc_title: d.title,
                    doc_text: substring(d.text, 0, 2000),
                    context: m.context
                })[0..2] as documents
            """, name=entity_name, rel_limit=limit, total_limit=limit * 2)
            
            return [{
                'entity': dict(record['related']),
                'relation': dict(record['r']),
                'documents': record['documents']
            } for record in result]
    
    def search_by_query(self, query_text: str, limit: int = 10) -> Dict:
        """Recherche optimisée avec limite de texte."""
        with self.driver.session() as session:
            normalized_query = query_text.lower()
            
            cypher_query = """
                MATCH (e:Entity)
                WHERE e.normalized_name CONTAINS $search_term
                WITH e
                LIMIT $result_limit
                OPTIONAL MATCH (e)-[r:MENTIONED_IN]->(d:Document)
                WITH e, r, d
                LIMIT $doc_limit
                RETURN e, collect(DISTINCT {
                    doc_id: d.id,
                    doc_title: d.title,
                    doc_text: substring(d.text, 0, 2000),
                    context: r.context
                })[0..3] as documents
            """
            
            result = session.run(cypher_query, 
                               search_term=normalized_query, 
                               result_limit=limit,
                               doc_limit=limit * 3)
            
            entities = []
            for record in result:
                entities.append({
                    'entity': dict(record['e']),
                    'documents': record['documents']
                })
            
            return {'entities': entities}
    
    def get_document(self, doc_id: str) -> Dict:
        """Récupère un document avec texte limité."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document {id: $doc_id})
                OPTIONAL MATCH (e:Entity)-[r:MENTIONED_IN]->(d)
                WITH d, e, r
                LIMIT 50
                RETURN d, collect(DISTINCT {
                    entity: e,
                    context: r.context
                })[0..20] as entities
            """, doc_id=doc_id)
            
            record = result.single()
            if record:
                doc = dict(record['d'])
                if 'text' in doc and len(doc['text']) > 5000:
                    doc['text'] = doc['text'][:5000] + "...[texte tronqué]"
                return {
                    'document': doc,
                    'entities': record['entities']
                }
            return None
    
    def get_document_by_title(self, title: str) -> Dict:
        """Récupère un document par titre avec limites."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Document)
                WHERE d.title CONTAINS $title
                WITH d
                LIMIT 1
                OPTIONAL MATCH (e:Entity)-[r:MENTIONED_IN]->(d)
                WITH d, e, r
                LIMIT 30
                RETURN d, collect(DISTINCT {
                    entity: e,
                    context: r.context
                })[0..15] as entities
            """, title=title)
            
            record = result.single()
            if record:
                doc = dict(record['d'])
                if 'text' in doc and len(doc['text']) > 5000:
                    doc['text'] = doc['text'][:5000] + "...[texte tronqué]"
                return {
                    'document': doc,
                    'entities': record['entities']
                }
            return None