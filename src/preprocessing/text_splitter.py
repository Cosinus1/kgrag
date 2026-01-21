# src/preprocessing/text_splitter.py

from typing import List

class TextSplitter:
    """Divise le texte en chunks pour le traitement."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_text(self, text: str) -> List[str]:
        """Divise le texte en chunks de taille fixe avec overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Si on est à la fin du texte
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Chercher un point de coupure naturel (espace, ponctuation)
            while end > start and text[end] not in (' ', '.', '!', '?', '\n'):
                end -= 1
            
            # Si on n'a pas trouvé de point de coupure, couper à la position exacte
            if end == start:
                end = start + self.chunk_size
            
            chunks.append(text[start:end])
            start = end - self.overlap
        
        return chunks
    
    def split_by_sentences(self, text: str, max_sentences: int = 5) -> List[str]:
        """Divise le texte par phrases."""
        import re
        
        # Séparation basique par ponctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
            
            if len(current_chunk) >= max_sentences:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
