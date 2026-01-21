# tests/test_graph.py

import unittest
import sys
sys.path.append('.')

from src.graph.graph_builder import GraphBuilder
from src.graph.graph_queries import GraphQueries
import os
from dotenv import load_dotenv

load_dotenv()

class TestGraphOperations(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Initialise la connexion au graphe de test."""
        cls.builder = GraphBuilder(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        cls.queries = GraphQueries(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"),
            password=os.getenv("NEO4J_PASSWORD")
        )
    
    def test_create_entity(self):
        """Test la création d'une entité."""
        with self.builder.driver.session() as session:
            entity = {
                'text': 'Test Entity',
                'label': 'PERSON'
            }
            self.builder.create_entity(session, entity)
            
            # Vérifier que l'entité existe
            result = self.queries.find_entity('Test Entity')
            self.assertIsNotNone(result)
    
    def test_find_neighbors(self):
        """Test la recherche de voisins."""
        # Ce test nécessite des données préexistantes
        pass
    
    @classmethod
    def tearDownClass(cls):
        """Nettoie après les tests."""
        cls.builder.close()
        cls.queries.close()

if __name__ == '__main__':
    unittest.main()
