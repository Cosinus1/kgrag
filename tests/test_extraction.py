# tests/test_extraction.py

import unittest
import sys
sys.path.append('.')

from src.extraction.entity_extractor import EntityExtractor
from src.extraction.relation_extractor import RelationExtractor

class TestEntityExtraction(unittest.TestCase):
    
    def setUp(self):
        self.extractor = EntityExtractor()
    
    def test_extract_entities(self):
        """Test l'extraction d'entités basique."""
        text = "Emmanuel Macron est président de la France depuis 2017."
        entities = self.extractor.extract_entities(text)
        
        self.assertGreater(len(entities), 0)
        
        # Vérifier qu'on trouve au moins une personne et un lieu
        labels = [e['label'] for e in entities]
        self.assertIn('PERSON', labels)
        self.assertIn('GPE', labels)
    
    def test_normalize_entities(self):
        """Test la normalisation des entités."""
        text = "Paris est la capitale de la France. Paris a été fondée il y a longtemps."
        normalized = self.extractor.extract_and_normalize(text)
        
        # "Paris" devrait apparaître normalisé
        self.assertIn('GPE', normalized)

class TestRelationExtraction(unittest.TestCase):
    
    def setUp(self):
        self.extractor = RelationExtractor(use_llm=False)  # Sans LLM pour les tests
    
    def test_extract_dependencies(self):
        """Test l'extraction de relations via dépendances."""
        text = "Marie dirige l'entreprise."
        relations = self.extractor.extract_with_dependencies(text)
        
        # On devrait avoir au moins une relation
        self.assertGreater(len(relations), 0)

if __name__ == '__main__':
    unittest.run()
