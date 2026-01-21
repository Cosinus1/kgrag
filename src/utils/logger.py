# src/utils/logger.py

import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    """Configure un logger avec sortie fichier et console."""
    
    # Créer le répertoire de logs
    Path(log_dir).mkdir(exist_ok=True)
    
    # Nom du fichier de log avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"{name}_{timestamp}.log"
    
    # Configuration du logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler fichier
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
