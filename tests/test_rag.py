# tests/test_rag.py

import unittest
import sys
sys.path.append('.')

from src.rag.context_builder import ContextBuilder

class TestRAGPipeline(unittest.TestCase):
    
    def setUp(self):
        self.builder = ContextBuilder()
    
    def test_build_context(self):
        """Test la construction du contexte."""
        vector_results = []
        graph_results = {
            'entities': [
                {'name': 'Paris', 'type': 'GPE'},
                {'name': 'France', 'type': 'GPE'}
            ],
            'relationships': [
                {'subject': 'Paris', 'type': 'capital_of', 'object': 'France'}
            ]
        }
        
        context = self.builder.build_context(vector_results, graph_results)
        
        self.assertIn('Paris', context)
        self.assertIn('France', context)
        self.assertIn('capital_of', context)
    
    def test_context_truncation(self):
        """Test que le contexte est tronqué si trop long."""
        self.builder.max_context_length = 100
        
        large_graph = {
            'entities': [{'name': f'Entity_{i}', 'type': 'TEST'} for i in range(100)]
        }
        
        context = self.builder.build_context([], large_graph)
        self.assertLessEqual(len(context), 150)  # Avec marge pour le message de troncature

if __name__ == '__main__':
    unittest.main()
