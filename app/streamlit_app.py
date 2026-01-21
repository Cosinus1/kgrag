# app/streamlit_app.py

import streamlit as st
import sys
sys.path.append('.')

from dotenv import load_dotenv
import os
from src.graph.graph_queries import GraphQueries
from src.embeddings.vector_store import VectorStore
from src.rag.retriever import HybridRetriever
from src.rag.graph_traverser import GraphTraverser
from src.rag.context_builder import ContextBuilder
from src.rag.llm_interface import LLMInterface
from src.extraction.entity_extractor import EntityExtractor

# Configuration de la page
st.set_page_config(
    page_title="Knowledge Graph RAG",
    page_icon="🧠",
    layout="wide"
)

# Charger les variables d'environnement
load_dotenv()

# Initialisation de la session
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'graph_queries' not in st.session_state:
    st.session_state.graph_queries = GraphQueries(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )

if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore()

if 'llm' not in st.session_state:
    st.session_state.llm = LLMInterface()

if 'entity_extractor' not in st.session_state:
    st.session_state.entity_extractor = EntityExtractor()

# Interface
st.title("🧠 Knowledge Graph RAG")
st.markdown("Posez des questions sur votre corpus de documents")

# Sidebar avec paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    max_depth = st.slider("Profondeur de parcours du graphe", 1, 3, 2)
    top_k = st.slider("Nombre de résultats vectoriels", 5, 20, 10)
    
    st.markdown("---")
    st.header("📊 Statistiques")
    
    # Afficher quelques stats du graphe
    if st.button("Rafraîchir les stats"):
        with st.spinner("Calcul des statistiques..."):
            # Compter les entités
            st.metric("Entités", "N/A")  # À implémenter avec une requête Neo4j

# Zone de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

# Input utilisateur
if prompt := st.chat_input("Posez votre question..."):
    # Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("Recherche dans le graphe..."):
            # 1. Extraire les entités de la question
            entities_in_question = st.session_state.entity_extractor.extract_entities(prompt)
            entity_names = [e['text'] for e in entities_in_question]
            
            # 2. Recherche vectorielle
            vector_results = st.session_state.vector_store.search(prompt, top_k=top_k)
            
            # 3. Parcours du graphe
            traverser = GraphTraverser(st.session_state.graph_queries)
            graph_context = traverser.traverse_from_entities(entity_names, max_depth=max_depth)
            
            # 4. Construction du contexte
            builder = ContextBuilder()
            context = builder.build_context(vector_results, graph_context)
            
            # 5. Génération de la réponse
            result = st.session_state.llm.answer_question(prompt, context)
            
            # Afficher la réponse
            st.markdown(result['answer'])
            
            # Afficher les sources
            sources = builder.format_sources(graph_context)
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.write(f"- {source}")
            
            # Afficher le contexte utilisé (debug)
            with st.expander("🔍 Contexte utilisé (debug)"):
                st.text(context)
    
    # Sauvegarder la réponse
    st.session_state.messages.append({
        "role": "assistant",
        "content": result['answer'],
        "sources": sources
    })

# Footer
st.markdown("---")
st.markdown("*Propulsé par Claude, Neo4j et Sentence Transformers*")
