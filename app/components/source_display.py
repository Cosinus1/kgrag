# app/components/source_display.py

import streamlit as st
from typing import List, Dict

class SourceDisplay:
    """Composant pour afficher les sources des réponses."""
    
    def __init__(self):
        pass
    
    def display_sources(self, sources: List[Dict], title: str = "📚 Sources"):
        """Affiche les sources d'une réponse."""
        if not sources:
            return
        
        with st.expander(title):
            for i, source in enumerate(sources, 1):
                if isinstance(source, dict):
                    self._display_source_dict(source, i)
                else:
                    st.write(f"{i}. {source}")
    
    def _display_source_dict(self, source: Dict, index: int):
        """Affiche une source sous forme de dictionnaire."""
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if 'confidence' in source:
                st.metric(f"Source {index}", f"{source.get('confidence', 0)*100:.1f}%")
        
        with col2:
            if 'title' in source:
                st.write(f"**{source['title']}**")
            if 'content' in source:
                st.write(source['content'][:200] + "..." if len(source['content']) > 200 else source['content'])
            if 'url' in source:
                st.write(f"[Lien]({source['url']})")
    
    def display_document_sources(self, documents: List[Dict]):
        """Affiche les sources documentaires."""
        if not documents:
            st.info("Aucun document source trouvé.")
            return
        
        st.subheader("📄 Documents sources")
        
        for doc in documents:
            with st.expander(f"📄 {doc.get('filename', 'Document')}"):
                if 'path' in doc:
                    st.write(f"**Chemin:** {doc['path']}")
                if 'metadata' in doc:
                    st.write(f"**Format:** {doc['metadata'].get('format', 'N/A')}")
                    st.write(f"**Taille:** {doc['metadata'].get('size', 0)} octets")
                if 'text' in doc and len(doc['text']) > 0:
                    st.write("**Extrait:**")
                    st.text(doc['text'][:500] + "..." if len(doc['text']) > 500 else doc['text'])
