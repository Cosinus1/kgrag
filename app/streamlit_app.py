# app/streamlit_app_fixed.py
# Version améliorée avec meilleure gestion des entités et debugging

import streamlit as st
import sys
sys.path.append('.')

from dotenv import load_dotenv
import os
from pathlib import Path
import re

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
        # Check if ChromaDB directory exists
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
            pass
        
        return components
        
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.info("Assurez-vous que:")
        st.info("- Neo4j est démarré")
        st.info("- Les données sont générées (scripts 01-04)")
        st.info("- La clé API LLM est configurée dans .env")
        return None

def extract_keywords_from_question(question: str) -> list:
    """Extrait des mots-clés d'une question si aucune entité n'est détectée."""
    # Mots à ignorer
    stop_words = {
        'qui', 'est', 'quoi', 'où', 'quand', 'comment', 'pourquoi',
        'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du',
        'parle', 'moi', 'sur', 'à', 'dans', 'pour', 'par'
    }
    
    # Extraire les mots
    words = re.findall(r'\b\w+\b', question.lower())
    
    # Filtrer et garder les mots significatifs (> 3 caractères)
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    return keywords[:5]  # Limiter à 5 mots-clés

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

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
    
    # Debug mode
    st.session_state.debug_mode = st.checkbox("Mode Debug", value=st.session_state.debug_mode)
    
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
                    st.info("Aucune statistique disponible.")
                    
            except Exception as e:
                st.error(f"Erreur: {e}")
    
    st.markdown("---")
    
    # Requêtes exemples
    st.header("💡 Exemples")
    
    if st.button("Qui est Napoleon?"):
        st.session_state.example_query = "Qui est Napoleon Bonaparte?"
    if st.button("Qu'est-ce que Paris?"):
        st.session_state.example_query = "Parle-moi de Paris"
    if st.button("Info sur France"):
        st.session_state.example_query = "Qu'est-ce que la France?"

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "debug_info" in message and st.session_state.debug_mode:
            with st.expander("🔍 Debug Info"):
                st.json(message["debug_info"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.write(f"- {source}")

# Use example query if set
if 'example_query' in st.session_state:
    prompt = st.session_state.example_query
    del st.session_state.example_query
else:
    # Chat input
    prompt = st.chat_input("Posez votre question...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        debug_info = {}
        
        try:
            with st.spinner("Recherche dans le graphe..."):
                # 1. Extract entities from question
                entities_in_question = components['entity_extractor'].extract_entities(prompt)
                entity_names = [e['text'] for e in entities_in_question]
                
                debug_info['entities_extracted'] = entity_names
                
                # Debug mode - show extracted entities
                if st.session_state.debug_mode:
                    with st.expander("🔍 Debug: Entités extraites de la question"):
                        if entity_names:
                            st.write(f"✓ Trouvées: {entity_names}")
                        else:
                            st.write("⚠️ Aucune entité extraite par spaCy")
                
                # 2. Vector search (always perform, even without entities)
                vector_results = components['vector_store'].search(prompt, top_k=top_k)
                
                debug_info['vector_results_count'] = len(vector_results)
                
                if st.session_state.debug_mode:
                    with st.expander("🔍 Debug: Résultats de la recherche vectorielle"):
                        if vector_results:
                            st.write(f"✓ Trouvés: {len(vector_results)} résultats")
                            for i, res in enumerate(vector_results[:3], 1):
                                st.write(f"{i}. {res.get('document', 'N/A')}")
                        else:
                            st.write("⚠️ Aucun résultat vectoriel")
                
                # 3. Fallback strategies if no entities detected
                if not entity_names:
                    # Strategy 1: Extract from vector results
                    if vector_results:
                        if st.session_state.debug_mode:
                            st.info("💡 Stratégie 1: Extraction d'entités des résultats vectoriels...")
                        
                        for result in vector_results[:5]:
                            metadata = result.get('metadata', {})
                            if metadata.get('text'):
                                entity_names.append(metadata['text'])
                    
                    # Strategy 2: Extract keywords from question
                    if not entity_names:
                        if st.session_state.debug_mode:
                            st.info("💡 Stratégie 2: Utilisation de mots-clés...")
                        
                        keywords = extract_keywords_from_question(prompt)
                        entity_names = keywords
                        debug_info['fallback_keywords'] = keywords
                
                debug_info['final_entity_names'] = entity_names
                
                # 4. Graph traversal
                traverser = GraphTraverser(components['graph_queries'])
                graph_context = traverser.traverse_from_entities(entity_names, max_depth=max_depth)
                
                debug_info['graph_entities_found'] = len(graph_context.get('entities', []))
                debug_info['graph_relations_found'] = len(graph_context.get('relationships', []))
                
                if st.session_state.debug_mode:
                    with st.expander("🔍 Debug: Contexte du graphe"):
                        st.write(f"Entités trouvées: {len(graph_context.get('entities', []))}")
                        st.write(f"Relations trouvées: {len(graph_context.get('relationships', []))}")
                        if graph_context.get('entities'):
                            st.write("Premières entités:")
                            for ent in graph_context['entities'][:5]:
                                st.write(f"- {ent.get('name', 'N/A')} ({ent.get('type', 'unknown')})")
                
                # 5. Build context (combine vector and graph results)
                builder = ContextBuilder()
                context = builder.build_context(vector_results, graph_context)
                
                debug_info['context_length'] = len(context)
                
                # 6. Check if we have enough context
                if not graph_context.get('entities') and not vector_results:
                    st.warning("⚠️ Aucune information trouvée.")
                    st.info(f"**Recherché:** {', '.join(entity_names)}")
                    st.info("**Suggestions:**")
                    st.info("- Vérifiez que le corpus contient des informations sur ce sujet")
                    st.info("- Essayez une question plus générale")
                    st.info("- Utilisez les exemples dans la barre latérale")
                    
                    answer = "Je n'ai pas trouvé d'information sur ce sujet dans le corpus."
                    sources = []
                else:
                    # 7. Generate answer
                    result = components['llm'].answer_question(prompt, context)
                    answer = result['answer']
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Display sources
                    sources = builder.format_sources(graph_context)
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.write(f"- {source}")
                    
                    # Display context (debug)
                    if st.session_state.debug_mode:
                        with st.expander("📄 Contexte utilisé"):
                            st.text(context[:1000] + "..." if len(context) > 1000 else context)
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération de la réponse: {e}")
            st.info("Vérifiez que:")
            st.info("- Neo4j est démarré")
            st.info("- Le graphe est construit (python scripts/03_build_graph.py)")
            st.info("- Les embeddings sont générés (python scripts/04_generate_embeddings.py)")
            st.info("- ANTHROPIC_API_KEY ou DEEPSEEK_API_KEY est défini dans .env")
            
            if st.session_state.debug_mode:
                import traceback
                st.code(traceback.format_exc())
            
            answer = "Désolé, je n'ai pas pu générer de réponse."
            sources = []
    
    # Save response
    message_data = {
        "role": "assistant",
        "content": answer if 'answer' in locals() else "Erreur",
        "sources": sources if 'sources' in locals() else []
    }
    
    if st.session_state.debug_mode:
        message_data["debug_info"] = debug_info
    
    st.session_state.messages.append(message_data)

# Footer
st.markdown("---")
st.markdown("*Propulsé par Claude/DeepSeek, Neo4j et Sentence Transformers*")