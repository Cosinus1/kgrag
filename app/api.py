# app/api.py

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

graph_queries = GraphQueries(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)
vector_store = VectorStore()
llm = LLMInterface()
entity_extractor = EntityExtractor()

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
    num_documents: int = 0

class EntitySearchRequest(BaseModel):
    entity_name: str

@app.get("/")
def read_root():
    return {
        "message": "Knowledge Graph RAG API", 
        "version": "1.0.0",
        "llm_provider": "DeepSeek/Claude"
    }

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """Endpoint principal pour poser une question."""
    try:
        entities_in_question = entity_extractor.extract_entities(request.question)
        entity_names = [e['text'] for e in entities_in_question]
        
        if not entity_names:
            search_result = graph_queries.search_by_query(request.question, limit=10)
            if search_result.get('entities'):
                entity_names = [e['entity']['name'] for e in search_result['entities'][:5]]
        
        if not entity_names:
            raise HTTPException(status_code=404, detail="No entities found in question")
        
        vector_results = vector_store.search(request.question, top_k=request.top_k)
        
        traverser = GraphTraverser(graph_queries)
        graph_context = traverser.traverse_from_entities(entity_names, max_depth=request.max_depth)
        
        builder = ContextBuilder(max_context_length=12000)
        context = builder.build_full_context(graph_context)
        
        result = llm.answer_question(request.question, context)
        
        sources = builder.format_sources(graph_context)
        
        return AnswerResponse(
            answer=result['answer'],
            entities=entities_in_question,
            sources=sources,
            context=context,
            usage=result.get('usage'),
            num_documents=len(graph_context.get('documents', {}))
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/entity/search")
def search_entity(request: EntitySearchRequest):
    """Recherche une entité spécifique avec ses documents."""
    entity_data = graph_queries.get_entity_with_documents(request.entity_name)
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity_data

@app.get("/entity/{entity_name}/neighbors")
def get_entity_neighbors(entity_name: str, max_depth: int = 1):
    """Récupère les voisins d'une entité."""
    neighbors = graph_queries.get_neighbors(entity_name, max_depth)
    return {"entity": entity_name, "neighbors": neighbors}

@app.get("/document/{doc_id}")
def get_document(doc_id: str):
    """Récupère un document complet avec ses entités."""
    doc_data = graph_queries.get_document(doc_id)
    if not doc_data:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc_data

@app.get("/stats")
def get_statistics():
    """Statistiques du graphe."""
    try:
        stats = {
            'entities': 0,
            'relationships': 0,
            'documents': 0
        }
        
        for etype in ['PERSON', 'ORG', 'GPE', 'DATE', 'EVENT', 'PRODUCT', 'LOC']:
            entities = graph_queries.search_entities_by_type(etype, limit=1000)
            stats['entities'] += len(entities) if entities else 0
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)