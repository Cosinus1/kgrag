# src/graph/graph_builder.py

from neo4j import GraphDatabase
from typing import List, Dict
from tqdm import tqdm

class GraphBuilder:
    """Construit le graphe de connaissances dans Neo4j."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._create_constraints()
    
    def close(self):
        self.driver.close()
    
    def _create_constraints(self):
        """Crée les contraintes et index pour optimiser les requêtes."""
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
                session.run("CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
                session.run("CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)")
                session.run("CREATE INDEX entity_normalized IF NOT EXISTS FOR (e:Entity) ON (e.normalized_name)")
            except:
                pass
    
    def clear_database(self):
        """Efface toute la base de données."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def extract_title_from_text(self, text: str, filename: str) -> str:
        """Extrait le titre depuis la première ligne du document."""
        lines = text.split('\n')
        
        for line in lines[:5]:
            line = line.strip()
            if line.startswith('# ') and len(line) > 2:
                return line[2:].strip()
        
        if filename.startswith('wiki_') and filename.endswith('.txt'):
            return filename[5:-4].replace('_', ' ').title()
        
        return filename.replace('.txt', '').replace('_', ' ')
    
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
        """
        
        params = {
            'subject': relation['subject'],
            'object': relation['object'],
            'predicate': relation['predicate'],
            'method': relation.get('method', 'unknown')
        }
        
        if 'common_docs' in relation:
            params['common_docs'] = relation['common_docs']
            params['strength'] = relation.get('strength', 1)
            query += ", r.common_docs = $common_docs, r.strength = $strength"
        
        if 'distance' in relation:
            params['distance'] = relation['distance']
            query += ", r.distance = $distance"
        
        query += " RETURN r"
        session.run(query, **params)
    
    def create_document_node(self, session, document: Dict):
        """Crée un nœud document avec titre extrait."""
        title = self.extract_title_from_text(document['text'], document['filename'])
        
        query = """
        MERGE (d:Document {id: $id})
        SET d.filename = $filename,
            d.title = $title,
            d.path = $path,
            d.text = $text,
            d.num_chars = $num_chars
        RETURN d
        """
        session.run(query,
                   id=document['filename'],
                   filename=document['filename'],
                   title=title,
                   path=document['path'],
                   text=document['text'],
                   num_chars=len(document['text']))
    
    def link_entity_to_document(self, session, entity_name: str, document_id: str, context: str = None):
        """Lie une entité à un document avec contexte."""
        query = """
        MATCH (e:Entity {name: $entity_name})
        MATCH (d:Document {id: $document_id})
        MERGE (e)-[r:MENTIONED_IN]->(d)
        """
        
        params = {
            'entity_name': entity_name,
            'document_id': document_id
        }
        
        if context:
            query += "SET r.context = $context"
            params['context'] = context
        
        session.run(query, **params)
    
    def extract_context(self, text: str, entity: Dict, window: int = 200) -> str:
        """Extrait le contexte autour d'une entité."""
        start = max(0, entity['start'] - window)
        end = min(len(text), entity['end'] + window)
        return text[start:end]
    
    def build_graph(self, entities_data: List[Dict], relations: List[Dict], documents: List[Dict]):
        """Construit le graphe complet."""
        with self.driver.session() as session:
            print("Création des documents...")
            for doc in tqdm(documents):
                self.create_document_node(session, doc)
            
            print("Création des entités...")
            entity_contexts = {}
            for entity_data in tqdm(entities_data):
                doc_id = entity_data['document_id']
                doc_text = entity_data.get('text', '')
                
                for entity in entity_data['entities']:
                    self.create_entity(session, entity)
                    
                    context = self.extract_context(doc_text, entity)
                    entity_key = (entity['text'], doc_id)
                    entity_contexts[entity_key] = context
                    
                    self.link_entity_to_document(session, entity['text'], doc_id, context)
            
            print("Création des relations...")
            for relation in tqdm(relations):
                try:
                    self.create_relation(session, relation)
                except:
                    pass
    
    def get_statistics(self) -> Dict:
        """Récupère les statistiques du graphe."""
        with self.driver.session() as session:
            stats = {}
            
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            stats['entities'] = result.single()['count']
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats['relationships'] = result.single()['count']
            
            result = session.run("MATCH (d:Document) RETURN count(d) as count")
            stats['documents'] = result.single()['count']
            
            return stats