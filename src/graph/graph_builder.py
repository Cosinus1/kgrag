# src/graph/graph_builder.py

from neo4j import GraphDatabase
from typing import List, Dict
from tqdm import tqdm

class GraphBuilder:
    """Construit le graphe de connaissances dans Neo4j."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Efface toute la base de données."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def create_entity(self, session, entity: Dict):
        """Crée un nœud entité."""
        query = """
        MERGE (e:Entity {name: $name})
        SET e.type = $type,
            e.normalized_name = $normalized_name
        RETURN e
        """
        session.run(query, 
                   name=entity['text'],
                   type=entity['label'],
                   normalized_name=entity['text'].lower())
    
    def create_relation(self, session, relation: Dict):
        """Crée une relation entre deux entités."""
        query = """
        MATCH (a:Entity {name: $subject})
        MATCH (b:Entity {name: $object})
        MERGE (a)-[r:RELATES_TO {type: $predicate}]->(b)
        SET r.method = $method
        RETURN r
        """
        session.run(query,
                   subject=relation['subject'],
                   object=relation['object'],
                   predicate=relation['predicate'],
                   method=relation.get('method', 'unknown'))
    
    def create_document_node(self, session, document: Dict):
        """Crée un nœud document."""
        query = """
        MERGE (d:Document {id: $id})
        SET d.filename = $filename,
            d.path = $path
        RETURN d
        """
        session.run(query,
                   id=document['filename'],
                   filename=document['filename'],
                   path=document['path'])
    
    def link_entity_to_document(self, session, entity_name: str, document_id: str):
        """Lie une entité à un document."""
        query = """
        MATCH (e:Entity {name: $entity_name})
        MATCH (d:Document {id: $document_id})
        MERGE (e)-[:MENTIONED_IN]->(d)
        """
        session.run(query, entity_name=entity_name, document_id=document_id)
    
    def build_graph(self, entities: List[Dict], relations: List[Dict], documents: List[Dict]):
        """Construit le graphe complet."""
        with self.driver.session() as session:
            # Créer les documents
            print("Création des documents...")
            for doc in tqdm(documents):
                self.create_document_node(session, doc)
            
            # Créer les entités
            print("Création des entités...")
            for entity_data in tqdm(entities):
                doc_id = entity_data['document_id']
                for entity in entity_data['entities']:
                    self.create_entity(session, entity)
                    self.link_entity_to_document(session, entity['text'], doc_id)
            
            # Créer les relations
            print("Création des relations...")
            for relation in tqdm(relations):
                self.create_relation(session, relation)
