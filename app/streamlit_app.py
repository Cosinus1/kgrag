# app/streamlit_app.py

import streamlit as st
import sys
sys.path.append('.')

from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment first
load_dotenv()

# Import after loading env
from src.graph.graph_queries import GraphQueries
from src.embeddings.vector_store import VectorStore
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

# Initialisation de la session
@st.cache_resource
def init_components():
    """Initialize all components once."""
    try:
        # Check if ChromaDB directory exists (should be in project root)
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
            'entity_extractor': EntityExtractor()
        }
        
        # Verify vector store has data
        try:
            count = components['vector_store'].count()
            if count == 0:
                st.warning(f"⚠️ Vector store existe mais est vide (0 entités)")
                st.info("Exécutez: python scripts/04_generate_embeddings.py")
            else:
                st.success(f"✓ Vector store chargé: {count:,} entités")
        except:
            pass  # count() might not work on all versions
        
        return components
        
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.info("Assurez-vous que:")
        st.info("- Neo4j est démarré")
        st.info("- Les données sont générées (scripts 01-04)")
        st.info("- La clé API LLM est configurée dans .env")
        return None

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize components
components = init_components()

if components is None:
    st.stop()

# Main UI
st.title("🧠 Knowledge Graph RAG")
st.markdown("Posez des questions sur votre corpus de documents")

# Sidebar with parameters
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    max_depth = st.slider("Profondeur de parcours du graphe", 1, 3, 2)
    top_k = st.slider("Nombre de résultats vectoriels", 5, 20, 10)
    
    st.markdown("---")
    st.header("📊 Statistiques")
    
    # Display stats
    if st.button("Rafraîchir les stats"):
        with st.spinner("Calcul des statistiques..."):
            try:
                # Count entities by type
                entity_types = {}
                for etype in ['PERSON', 'ORG', 'GPE', 'DATE', 'EVENT', 'PRODUCT']:
                    entities = components['graph_queries'].search_entities_by_type(etype, limit=1000)
                    if entities:
                        entity_types[etype] = len(entities)
                
                if entity_types:
                    st.write("**Entités par type:**")
                    for etype, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
                        st.write(f"- {etype}: {count}")
                else:
                    st.info("Aucune statistique disponible. Vérifiez que le graphe est construit.")
                    
            except Exception as e:
                st.error(f"Erreur: {e}")
                st.info("Assurez-vous que Neo4j est démarré et le graphe construit.")

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

# Chat input
if prompt := st.chat_input("Posez votre question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Recherche dans le graphe..."):
                # 1. Extract entities from question
                entities_in_question = components['entity_extractor'].extract_entities(prompt)
                entity_names = [e['text'] for e in entities_in_question]
                
                if not entity_names:
                    st.warning("⚠️ Aucune entité détectée dans votre question.")
                    st.info("Essayez de reformuler avec des noms propres (personnes, lieux, organisations).")
                    st.stop()
                
                # 2. Vector search
                vector_results = components['vector_store'].search(prompt, top_k=top_k)
                
                # 3. Graph traversal
                traverser = GraphTraverser(components['graph_queries'])
                graph_context = traverser.traverse_from_entities(entity_names, max_depth=max_depth)
                
                # Check if we found anything
                if not graph_context.get('entities'):
                    st.warning("⚠️ Aucune information trouvée dans le graphe pour ces entités.")
                    st.info(f"Entités recherchées: {', '.join(entity_names)}")
                    st.info("Le corpus peut ne pas contenir d'information sur ce sujet.")
                    st.stop()
                
                # 4. Build context
                builder = ContextBuilder()
                context = builder.build_context(vector_results, graph_context)
                
                # 5. Generate answer
                result = components['llm'].answer_question(prompt, context)
                
                # Display answer
                st.markdown(result['answer'])
                
                # Display sources
                sources = builder.format_sources(graph_context)
                if sources:
                    with st.expander("📚 Sources"):
                        for source in sources:
                            st.write(f"- {source}")
                
                # Display context (debug)
                with st.expander("🔍 Contexte utilisé (debug)"):
                    st.text(context)
                
                # Display entities found
                with st.expander("🏷️ Entités trouvées"):
                    st.write(f"**Dans la question:** {', '.join(entity_names)}")
                    st.write(f"**Dans le graphe:** {len(graph_context.get('entities', []))} entités")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération de la réponse: {e}")
            st.info("Vérifiez que:")
            st.info("- Neo4j est démarré")
            st.info("- Le graphe est construit (python scripts/03_build_graph.py)")
            st.info("- Les embeddings sont générés (python scripts/04_generate_embeddings.py)")
            st.info("- ANTHROPIC_API_KEY ou DEEPSEEK_API_KEY est défini dans .env")
            result = {'answer': "Désolé, je n'ai pas pu générer de réponse."}
            sources = []
    
    # Save response
    st.session_state.messages.append({
        "role": "assistant",
        "content": result.get('answer', 'Erreur'),
        "sources": sources if 'sources' in locals() else []
    })

# Footer
st.markdown("---")
st.markdown("*Propulsé par Claude/DeepSeek, Neo4j et Sentence Transformers*")