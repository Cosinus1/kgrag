# src/evaluation/test_suite.py

from typing import List, Dict
from .metrics import EvaluationMetrics

class TestSuite:
    """Suite de tests pour évaluer le système."""
    
    def __init__(self):
        self.metrics = EvaluationMetrics()
    
    def test_entity_extraction(self, test_cases: List[Dict]) -> Dict:
        """Teste l'extraction d'entités."""
        results = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': []
        }
        
        for test_case in test_cases:
            true_entities = test_case['true_entities']
            predicted_entities = test_case['predicted_entities']
            
            # Calcul des métriques
            accuracy = self.metrics.entity_extraction_accuracy(true_entities, predicted_entities)
            
            # Pour precision/recall, on considère chaque entité comme un item
            true_ids = list(range(len(true_entities)))
            pred_ids = list(range(len(predicted_entities)))
            
            precision = self.metrics.precision_at_k(true_ids, pred_ids, len(pred_ids))
            recall = self.metrics.recall_at_k(true_ids, pred_ids, len(pred_ids))
            f1 = self.metrics.f1_score(precision, recall)
            
            results['accuracy'].append(accuracy)
            results['precision'].append(precision)
            results['recall'].append(recall)
            results['f1'].append(f1)
        
        # Moyennes
        return {
            'accuracy': sum(results['accuracy']) / len(results['accuracy']) if results['accuracy'] else 0,
            'precision': sum(results['precision']) / len(results['precision']) if results['precision'] else 0,
            'recall': sum(results['recall']) / len(results['recall']) if results['recall'] else 0,
            'f1': sum(results['f1']) / len(results['f1']) if results['f1'] else 0
        }
    
    def test_retrieval(self, test_cases: List[Dict]) -> Dict:
        """Teste la récupération d'information."""
        results = {
            'precision_at_5': [],
            'precision_at_10': [],
            'recall_at_10': [],
            'map': []
        }
        
        for test_case in test_cases:
            relevant_items = test_case['relevant_items']
            retrieved_items = test_case['retrieved_items']
            
            p_at_5 = self.metrics.precision_at_k(relevant_items, retrieved_items, 5)
            p_at_10 = self.metrics.precision_at_k(relevant_items, retrieved_items, 10)
            r_at_10 = self.metrics.recall_at_k(relevant_items, retrieved_items, 10)
            map_score = self.metrics.mean_average_precision(relevant_items, retrieved_items)
            
            results['precision_at_5'].append(p_at_5)
            results['precision_at_10'].append(p_at_10)
            results['recall_at_10'].append(r_at_10)
            results['map'].append(map_score)
        
        # Moyennes
        return {
            'precision_at_5': sum(results['precision_at_5']) / len(results['precision_at_5']) if results['precision_at_5'] else 0,
            'precision_at_10': sum(results['precision_at_10']) / len(results['precision_at_10']) if results['precision_at_10'] else 0,
            'recall_at_10': sum(results['recall_at_10']) / len(results['recall_at_10']) if results['recall_at_10'] else 0,
            'map': sum(results['map']) / len(results['map']) if results['map'] else 0
        }
    
    def run_complete_suite(self, extraction_cases: List[Dict], retrieval_cases: List[Dict]) -> Dict:
        """Exécute la suite complète de tests."""
        extraction_results = self.test_entity_extraction(extraction_cases)
        retrieval_results = self.test_retrieval(retrieval_cases)
        
        return {
            'entity_extraction': extraction_results,
            'retrieval': retrieval_results,
            'overall_score': (extraction_results['f1'] + retrieval_results['map']) / 2
        }
