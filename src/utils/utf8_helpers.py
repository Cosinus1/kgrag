# utils/utf8_helpers.py

"""
Helper functions to ensure UTF-8 encoding is used consistently across the project.
This prevents UnicodeDecodeError on Windows where the default encoding is cp1252.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

def load_json_utf8(filepath: str | Path) -> Any:
    """
    Load a JSON file with UTF-8 encoding.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_utf8(data: Any, filepath: str | Path, indent: int = 2):
    """
    Save data to a JSON file with UTF-8 encoding.
    
    Args:
        data: Data to save (must be JSON serializable)
        filepath: Path to save the file
        indent: Indentation level for pretty printing
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_text_utf8(filepath: str | Path) -> str:
    """
    Load a text file with UTF-8 encoding.
    Tries multiple encodings as fallback.
    
    Args:
        filepath: Path to the text file
        
    Returns:
        File contents as string
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Try multiple encodings
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # Last resort: replace errors
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def save_text_utf8(text: str, filepath: str | Path):
    """
    Save text to a file with UTF-8 encoding.
    
    Args:
        text: Text content to save
        filepath: Path to save the file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)


# Convenience functions for common file operations
def read_documents_json() -> List[Dict]:
    """Load processed documents."""
    return load_json_utf8("data/processed/documents.json")


def read_entities_json() -> List[Dict]:
    """Load extracted entities."""
    return load_json_utf8("data/entities/entities.json")


def read_relations_json() -> List[Dict]:
    """Load extracted relations."""
    return load_json_utf8("data/relations/relations.json")


def save_documents_json(documents: List[Dict]):
    """Save processed documents."""
    save_json_utf8(documents, "data/processed/documents.json")


def save_entities_json(entities: List[Dict]):
    """Save extracted entities."""
    save_json_utf8(entities, "data/entities/entities.json")


def save_relations_json(relations: List[Dict]):
    """Save extracted relations."""
    save_json_utf8(relations, "data/relations/relations.json")