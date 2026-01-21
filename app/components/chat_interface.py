# app/components/chat_interface.py

import streamlit as st
from typing import List, Dict

class ChatInterface:
    """Composant d'interface de chat réutilisable."""
    
    def __init__(self):
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def display_message(self, role: str, content: str, metadata: Dict = None):
        """Affiche un message dans le chat."""
        with st.chat_message(role):
            st.markdown(content)
            
            if metadata:
                if 'entities' in metadata:
                    with st.expander("🏷️ Entités détectées"):
                        for entity in metadata['entities']:
                            st.write(f"- **{entity['text']}** ({entity['label']})")
                
                if 'sources' in metadata:
                    with st.expander("📚 Sources"):
                        for source in metadata['sources']:
                            st.write(f"- {source}")
                
                if 'graph_path' in metadata:
                    with st.expander("🗺️ Chemin dans le graphe"):
                        st.write(" → ".join(metadata['graph_path']))
    
    def display_history(self):
        """Affiche l'historique complet."""
        for message in st.session_state.chat_history:
            self.display_message(
                message['role'],
                message['content'],
                message.get('metadata')
            )
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Ajoute un message à l'historique."""
        st.session_state.chat_history.append({
            'role': role,
            'content': content,
            'metadata': metadata or {}
        })
    
    def clear_history(self):
        """Efface l'historique."""
        st.session_state.chat_history = []
