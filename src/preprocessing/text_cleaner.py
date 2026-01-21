# src/preprocessing/text_cleaner.py

import re
from typing import List

class TextCleaner:
    """Nettoie et normalise le texte extrait."""
    
    def __init__(self):
        self.patterns = {
            'multiple_spaces': re.compile(r'\s+'),
            'multiple_newlines': re.compile(r'\n{3,}'),
            'page_numbers': re.compile(r'^\d+\s*$', re.MULTILINE),
            'urls': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        }
    
    def clean(self, text: str) -> str:
        """Nettoie le texte."""
        # Suppression des URLs
        text = self.patterns['urls'].sub('', text)
        
        # Suppression des numéros de page
        text = self.patterns['page_numbers'].sub('', text)
        
        # Normalisation des espaces
        text = self.patterns['multiple_spaces'].sub(' ', text)
        
        # Normalisation des sauts de ligne
        text = self.patterns['multiple_newlines'].sub('\n\n', text)
        
        # Suppression des espaces en début et fin
        text = text.strip()
        
        return text
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """Divise le texte en paragraphes."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
