# src/extraction/coreference_resolver.py

from typing import List, Dict

class CoreferenceResolver:
    """Résout les coréférences dans le texte."""
    
    def __init__(self):
        pass
    
    def resolve(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Résout les coréférences pour les entités."""
        # Implémentation basique - à améliorer
        resolved_entities = []
        
        for entity in entities:
            # Pour l'instant, on retourne les entités telles quelles
            resolved_entities.append(entity)
        
        return resolved_entities
    
    def find_coreferences(self, text: str) -> List[Dict]:
        """Trouve les coréférences dans le texte."""
        # Implémentation basique
        return []
