# docker/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle spaCy
RUN python -m spacy download fr_core_news_lg

# Copier le code source
COPY . .

# Exposer le port pour Streamlit
EXPOSE 8501

# Exposer le port pour l'API FastAPI
EXPOSE 8000

# Commande par défaut
CMD ["streamlit", "run", "app/streamlit_app.py"]
