# app/streamlit_app.py

import streamlit as st
import sys
sys.path.append('.')

from dotenv import load_dotenv
import os
from pathlib import Path
import traceback

load_dotenv()

from src.graph.graph_queries import GraphQueries
from src.embeddings.vector_store import VectorStore
from src.rag.graph_traverser import GraphTraverser
from src.rag.context_builder import ContextBuilder
from src.rag.context_compactor import ContextCompactor
from src.rag.llm_interface import LLMInterface
from src.extraction.entity_extractor import EntityExtractor

st.set_page_config(
    page_title="Knowledge Graph RAG",
    page_icon="🧠",
    layout="wide"
)

@st.cache_resource
def init_components():
    """Initialize all components once."""
    try:
        chroma_paths = [Path("chroma_db"), Path("./chroma_db"), Path("../chroma_db")]
        chroma_found = any(p.exists() for p in chroma_paths)
        
        if not chroma_found:
            st.error("❌ Vector store (ChromaDB) not found!")
            st.info("Exécutez: python scripts/04_generate_embeddings.py")
            st.stop()
        
        components = {
            'graph_queries': GraphQueries(
                uri=os.getenv("NEO4J_URI"),
                user=os.getenv("NEO4J_USER"),
                password=os.getenv("NEO4J_PASSWORD")
            ),
            'vector_store': VectorStore(),
            'llm': LLMInterface(),
            'entity_extractor': EntityExtractor(),
            'compactor': ContextCompactor(max_tokens=100000)
        }
        
        try:
            count = components['vector_store'].count()
            if count == 0:
                st.warning(f"⚠️ Vector store existe mais est vide (0 entités)")
                st.info("Exécutez: python scripts/04_generate_embeddings.py")
            else:
                st.success(f"✓ Vector store chargé: {count:,} entités")
        except:
            pass
        
        return components
        
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

components = init_components()

if components is None:
    st.stop()

st.title("🧠 Knowledge Graph RAG")
st.markdown("Posez des questions sur votre corpus de documents")

with st.sidebar:
    st.header("⚙️ Paramètres")
    
    max_depth = st.slider("Profondeur de parcours du graphe", 1, 3, 1)
    top_k = st.slider("Nombre de résultats vectoriels", 3, 10, 5)
    
    st.session_state.debug_mode = st.checkbox("Mode Debug", value=False)
    
    st.markdown("---")
    st.header("📊 Statistiques")
    
    if st.button("Rafraîchir les stats"):
        with st.spinner("Calcul des statistiques..."):
            try:
                entity_types = {}
                for etype in ['PERSON', 'ORG', 'GPE', 'DATE', 'EVENT', 'PRODUCT', 'LOC']:
                    entities = components['graph_queries'].search_entities_by_type(etype, limit=100)
                    if entities:
                        entity_types[etype] = len(entities)
                
                if entity_types:
                    st.write("**Entités par type:**")
                    for etype, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- {etype}: {count}")
                else:
                    st.info("Aucune statistique disponible.")
                    
            except Exception as e:
                st.error(f"Erreur: {e}")
                if st.session_state.debug_mode:
                    st.error(f"Traceback: {traceback.format_exc()}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

if prompt := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            if st.session_state.debug_mode:
                st.info(f"🔍 Question: {prompt}")
            
            with st.spinner("Extraction des entités..."):
                entities_in_question = components['entity_extractor'].extract_entities(prompt)
                entity_names = [e['text'] for e in entities_in_question]
                
                if st.session_state.debug_mode:
                    st.info(f"Entités extraites: {entity_names}")
                
                if not entity_names:
                    st.warning("⚠️ Aucune entité détectée. Recherche générale...")
                    
                    try:
                        search_result = components['graph_queries'].search_by_query(prompt, limit=5)
                        
                        if st.session_state.debug_mode:
                            st.info(f"Résultats recherche: {len(search_result.get('entities', []))} entités")
                        
                        if search_result.get('entities'):
                            entity_names = [e['entity']['name'] for e in search_result['entities'][:3]]
                            if st.session_state.debug_mode:
                                st.success(f"✓ Entités trouvées: {entity_names}")
                    except Exception as e:
                        st.error(f"❌ Erreur recherche: {e}")
                        if st.session_state.debug_mode:
                            st.error(f"Traceback: {traceback.format_exc()}")
                        entity_names = []
                
                if not entity_names:
                    st.warning("⚠️ Aucune entité trouvée.")
                    st.info("Essayez de reformuler avec des noms propres.")
                    st.stop()
            
            with st.spinner("Recherche vectorielle..."):
                vector_results = components['vector_store'].search(prompt, top_k=top_k)
                if st.session_state.debug_mode:
                    st.info(f"Résultats vectoriels: {len(vector_results)}")
            
            with st.spinner("Parcours du graphe..."):
                traverser = GraphTraverser(components['graph_queries'])
                graph_context = traverser.traverse_from_entities(entity_names[:3], max_depth=max_depth)
                
                if st.session_state.debug_mode:
                    st.info(f"Contexte brut:")
                    st.info(f"  - Entités: {len(graph_context.get('entities', []))}")
                    st.info(f"  - Relations: {len(graph_context.get('relationships', []))}")
                    st.info(f"  - Documents: {len(graph_context.get('documents', {}))}")
                
                if not graph_context.get('entities') and not graph_context.get('documents'):
                    st.warning("⚠️ Aucune information trouvée.")
                    st.stop()
            
            with st.spinner("Compactage du contexte..."):
                compactor = components['compactor']
                compacted_context = compactor.compact_context(graph_context)
                context = compactor.build_compact_context_string(compacted_context)
                
                estimated_tokens = compactor.estimate_tokens(context)
                
                if st.session_state.debug_mode:
                    st.info(f"Contexte compacté:")
                    st.info(f"  - Longueur: {len(context):,} caractères")
                    st.info(f"  - Tokens estimés: {estimated_tokens:,}")
                    st.info(f"  - Documents compactés: {len(compacted_context.get('documents', {}))}")
            
            with st.spinner("Génération de la réponse..."):
                result = components['llm'].answer_question(prompt, context)
                
                if st.session_state.debug_mode:
                    st.info(f"LLM: {result.get('provider')}")
                    if result.get('usage'):
                        st.info(f"Tokens: {result.get('usage')}")
            
            st.markdown(result['answer'])
            
            builder = ContextBuilder()
            sources = builder.format_sources(compacted_context)
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources[:10]:
                        st.write(f"- {source}")
            
            with st.expander("🔍 Contexte utilisé"):
                st.text(context[:1000] + "..." if len(context) > 1000 else context)
            
            with st.expander("🏷️ Détails"):
                st.write(f"**Entités recherchées:** {', '.join(entity_names[:5])}")
                st.write(f"**Entités trouvées:** {len(compacted_context.get('entities', []))}")
                st.write(f"**Documents:** {len(compacted_context.get('documents', {}))}")
                st.write(f"**Taille contexte:** {len(context):,} chars (~{estimated_tokens:,} tokens)")
        
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
            st.error(f"Traceback: {traceback.format_exc()}")
            result = {'answer': "Désolé, je n'ai pas pu générer de réponse."}
            sources = []
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get('answer', 'Erreur'),
        "sources": sources if 'sources' in locals() else []
    })

st.markdown("---")
st.markdown("*Propulsé par Claude/DeepSeek, Neo4j et Sentence Transformers*")