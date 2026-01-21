# src/extraction/entity_linker.py

from typing import List, Dict

class EntityLinker:
    """Lie les entités à des bases de connaissances externes."""
    
    def __init__(self):
        pass
    
    def link_to_wikidata(self, entity: Dict) -> Dict:
        """Tente de lier une entité à Wikidata."""
        # Implémentation basique - à améliorer
        return {
            'entity': entity,
            'wikidata_id': None,
            'confidence': 0.0
        }
    
    def link_entities(self, entities: List[Dict]) -> List[Dict]:
        """Lie une liste d'entités à des bases de connaissances."""
        linked_entities = []
        
        for entity in entities:
            linked = self.link_to_wikidata(entity)
            linked_entities.append(linked)
        
        return linked_entities
    
    def disambiguate(self, entity_name: str, candidates: List[Dict]) -> Dict:
        """Désambiguïse une entité parmi plusieurs candidats."""
        if not candidates:
            return None
        
        # Pour l'instant, retourne le premier candidat
        return candidates[0]
