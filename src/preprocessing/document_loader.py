# src/preprocessing/document_loader.py

import os
from pathlib import Path
from typing import List, Dict
import PyPDF2
import pdfplumber
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

class DocumentLoader:
    """Charge et extrait le texte de différents formats de documents."""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.supported_formats = ['.pdf', '.txt', '.html']
    
    def load_pdf(self, file_path: Path) -> str:
        """Extrait le texte d'un PDF."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Erreur lors de la lecture de {file_path}: {e}")
        return text
    
    def load_txt(self, file_path: Path) -> str:
        """Charge un fichier texte."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_html(self, file_path: Path) -> str:
        """Extrait le texte d'un fichier HTML."""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text()
    
    def load_all_documents(self) -> List[Dict]:
        """Charge tous les documents du répertoire."""
        documents = []
        files = list(self.data_dir.rglob('*'))
        
        for file_path in tqdm(files, desc="Chargement des documents"):
            if file_path.suffix.lower() not in self.supported_formats:
                continue
            
            if file_path.suffix == '.pdf':
                text = self.load_pdf(file_path)
            elif file_path.suffix == '.txt':
                text = self.load_txt(file_path)
            elif file_path.suffix == '.html':
                text = self.load_html(file_path)
            else:
                continue
            
            documents.append({
                'filename': file_path.name,
                'path': str(file_path),
                'text': text,
                'metadata': {
                    'format': file_path.suffix,
                    'size': file_path.stat().st_size
                }
            })
        
        return documents
    
    def save_processed(self, documents: List[Dict], output_path: Path):
        """Sauvegarde les documents traités en JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
