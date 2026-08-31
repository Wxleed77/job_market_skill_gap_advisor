from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.seed_data import RAW_POSTINGS
from src.normalization import normalize_postings
from src.chunking_embedding import ChunkingStrategy, EmbeddingEngine, QdrantVectorDB
from src.rag_query_engine import RAGQueryEngine
from src.llm_synthesis import OpenRouterLLM

app = FastAPI(title="Job Market Skill Gap Advisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build once at startup
normalized = normalize_postings(RAW_POSTINGS)
chunks = ChunkingStrategy().chunk_postings(normalized)
embedding_engine = EmbeddingEngine()
chunks_with_embeddings = embedding_engine.embed_chunks(chunks)
vector_db = QdrantVectorDB(vector_size=embedding_engine.embedding_dim)
vector_db.store_chunks(chunks_with_embeddings)

try:
    llm = OpenRouterLLM(model="auto")
except ValueError:
    llm = None

rag_engine = RAGQueryEngine(vector_db, embedding_engine, normalized, llm=llm)


class QueryRequest(BaseModel):
    query: str = Field(..., example="What should I learn for backend roles in Karachi?")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/query")
def handle_query(payload: QueryRequest) -> Dict[str, Any]:
    result = rag_engine.query(payload.query)
    return {
        "query": payload.query,
        "query_type": result.get("query_classification") or result.get("classified_as"),
        "filters": result.get("extracted_filters") or result.get("filters", {}),
        "answer": result.get("answer", ""),
        "relevant_postings": result.get("relevant_postings", []),
        "top_skills": result.get("top_skills", []),
        "retrieved_chunks": result.get("retrieved_chunks", []),
        "cited_postings": result.get("cited_postings", []),
    }


@app.get("/demo")
def demo() -> Dict[str, Any]:
    result = rag_engine.query("What should I learn for backend roles?")
    return {
        "query": "What should I learn for backend roles?",
        "query_type": result.get("query_classification") or result.get("classified_as"),
        "answer": result.get("answer", ""),
        "top_skills": result.get("top_skills", []),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
