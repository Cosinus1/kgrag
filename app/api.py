from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
sys.path.append('.')

from dotenv import load_dotenv
import os
from src.graph.graph_queries import GraphQueries
from src.embeddings.vector_store import VectorStore
from src.rag.graph_traverser import GraphTraverser
from src.rag.context_builder import ContextBuilder
from src.rag.llm_interface import LLMInterface
from src.extraction.entity_extractor import EntityExtractor

load_dotenv()

app = FastAPI(title="Knowledge Graph RAG API")

# Initialisation des composants
graph_queries = GraphQueries(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)
vector_store = VectorStore()
llm = LLMInterface()  # Utilise DeepSeek automatiquement
entity_extractor = EntityExtractor()

# Modèles Pydantic
class QuestionRequest(BaseModel):
    question: str
    max_depth: int = 2
    top_k: int = 10

class AnswerResponse(BaseModel):
    answer: str
    entities: List[Dict]
    sources: List[str]
    context: Optional[str] = None
    usage: Optional[Dict] = None

class EntitySearchRequest(BaseModel):
    entity_name: str

@app.get("/")
def read_root():
    return {
        "message": "Knowledge Graph RAG API", 
        "version": "1.0.0",
        "llm_provider": "DeepSeek"
    }

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Endpoint principal pour poser une question."""
    try:
        # Extraire les entités de la question
        entities_in_question = entity_extractor.extract_entities(request.question)
        entity_names = [e['text'] for e in entities_in_question]
        
        # Recherche vectorielle
        vector_results = vector_store.search(request.question, top_k=request.top_k)
        
        # Parcours du graphe
        traverser = GraphTraverser(graph_queries)
        graph_context = traverser.traverse_from_entities(entity_names, max_depth=request.max_depth)
        
        # Construction du contexte
        builder = ContextBuilder()
        context = builder.build_context(vector_results, graph_context)
        
        # Génération de la réponse avec DeepSeek
        result = llm.answer_question(request.question, context)
        
        # Préparer la réponse
        sources = builder.format_sources(graph_context)
        
        return AnswerResponse(
            answer=result['answer'],
            entities=entities_in_question,
            sources=sources,
            context=context,
            usage=result.get('usage')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/entity/search")
def search_entity(request: EntitySearchRequest):
    """Recherche une entité spécifique."""
    entity = graph_queries.find_entity(request.entity_name)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@app.get("/entity/{entity_name}/neighbors")
def get_entity_neighbors(entity_name: str, max_depth: int = 1):
    """Récupère les voisins d'une entité."""
    neighbors = graph_queries.get_neighbors(entity_name, max_depth)
    return {"entity": entity_name, "neighbors": neighbors}

@app.get("/stats")
def get_statistics():
    """Statistiques du graphe."""
    return {
        "entities": "N/A",
        "relationships": "N/A",
        "documents": "N/A",
        "llm_provider": "DeepSeek"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)