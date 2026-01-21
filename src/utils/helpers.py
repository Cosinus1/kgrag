# src/utils/helpers.py

from typing import List, Dict, Any
import hashlib
import json

def generate_id(text: str) -> str:
    """Génère un ID unique à partir d'un texte."""
    return hashlib.md5(text.encode()).hexdigest()[:16]

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Divise une liste en chunks de taille donnée."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def deduplicate_entities(entities: List[Dict]) -> List[Dict]:
    """Déduplique les entités par leur texte normalisé."""
    seen = set()
    unique = []
    
    for entity in entities:
        normalized = entity['text'].lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(entity)
    
    return unique

def merge_dictionaries(dict1: Dict, dict2: Dict) -> Dict:
    """Fusionne deux dictionnaires récursivement."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dictionaries(result[key], value)
        else:
            result[key] = value
    
    return result

def pretty_print_json(data: Any):
    """Affiche du JSON de manière lisible."""
    print(json.dumps(data, indent=2, ensure_ascii=False))
