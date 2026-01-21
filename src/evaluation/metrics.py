# src/evaluation/metrics.py

from typing import List, Dict
import numpy as np

class EvaluationMetrics:
    """Métriques d'évaluation pour le système RAG."""
    
    @staticmethod
    def precision_at_k(relevant_items: List[int], retrieved_items: List[int], k: int) -> float:
        """Précision@k."""
        if not retrieved_items:
            return 0.0
        
        retrieved_k = retrieved_items[:k]
        relevant_retrieved = len([item for item in retrieved_k if item in relevant_items])
        return relevant_retrieved / len(retrieved_k)
    
    @staticmethod
    def recall_at_k(relevant_items: List[int], retrieved_items: List[int], k: int) -> float:
        """Rappel@k."""
        if not relevant_items:
            return 0.0
        
        retrieved_k = retrieved_items[:k]
        relevant_retrieved = len([item for item in retrieved_k if item in relevant_items])
        return relevant_retrieved / len(relevant_items)
    
    @staticmethod
    def mean_average_precision(relevant_items: List[int], retrieved_items: List[int]) -> float:
        """Mean Average Precision (MAP)."""
        if not relevant_items:
            return 0.0
        
        average_precisions = []
        relevant_count = 0
        
        for i, item in enumerate(retrieved_items, 1):
            if item in relevant_items:
                relevant_count += 1
                precision_at_i = relevant_count / i
                average_precisions.append(precision_at_i)
        
        if not average_precisions:
            return 0.0
        
        return sum(average_precisions) / len(relevant_items)
    
    @staticmethod
    def f1_score(precision: float, recall: float) -> float:
        """Score F1."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def entity_extraction_accuracy(true_entities: List[Dict], predicted_entities: List[Dict]) -> float:
        """Précision de l'extraction d'entités."""
        if not true_entities:
            return 0.0 if predicted_entities else 1.0
        
        true_set = set((e['text'], e.get('label', '')) for e in true_entities)
        pred_set = set((e['text'], e.get('label', '')) for e in predicted_entities)
        
        correct = len(true_set.intersection(pred_set))
        total = len(true_set)
        
        return correct / total if total > 0 else 0.0
