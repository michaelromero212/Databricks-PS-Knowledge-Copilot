"""
FastAPI Backend for Databricks PS Knowledge Copilot

This API serves as the backend for the React frontend, providing:
- /api/query - Ask questions to the knowledge base
- /api/ingest - Ingest documents into the vector store
- /api/health - System health check

Run with: uvicorn app.api.main:app --reload --port 8000
"""

import sys
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.api.models import (
    QueryRequest, QueryResponse, SourceDocument,
    IngestRequest, IngestResponse,
    HealthResponse, ComponentStatus,
    LLMProvider
)
from app.rag.retriever import Retriever
from app.rag.llm_connector import LLMConnector
from app.rag.embedder import Embedder
from app.ingest.document_loader import DocumentLoader
from app.ingest.chunker import TextChunker
from app.vectorstore.chroma_client import ChromaClient


# Global instances (lazy-loaded)
_retriever: Optional[Retriever] = None
_llm_connectors: dict = {}


def get_retriever() -> Retriever:
    """Get or create the retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever(use_databricks=False)
    return _retriever


def get_llm(provider: str) -> LLMConnector:
    """Get or create an LLM connector for the given provider."""
    global _llm_connectors
    if provider not in _llm_connectors:
        _llm_connectors[provider] = LLMConnector(provider=provider)
    return _llm_connectors[provider]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    print("🚀 Starting Databricks PS Knowledge Copilot API...")
    yield
    # Shutdown
    print("👋 Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title="Databricks PS Knowledge Copilot API",
    description="RAG-powered knowledge assistant for Databricks Professional Services",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= API Endpoints =============

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Check the health of all system components.
    
    Returns status of:
    - Vector Store (ChromaDB)
    - LLM (configured provider)
    - Embedding Model
    """
    components = []
    overall_status = "healthy"
    
    # Check Vector Store
    try:
        chroma = ChromaClient()
        count = chroma.collection.count()
        components.append(ComponentStatus(
            name="Vector Store (ChromaDB)",
            status="healthy",
            details=f"{count} documents indexed"
        ))
    except Exception as e:
        components.append(ComponentStatus(
            name="Vector Store (ChromaDB)",
            status="unhealthy",
            details=str(e)
        ))
        overall_status = "degraded"
    
    # Check Embedder
    try:
        embedder = Embedder()
        test_embedding = embedder.generate_embeddings(["test"])
        components.append(ComponentStatus(
            name="Embedding Model",
            status="healthy",
            details="all-MiniLM-L6-v2 loaded"
        ))
    except Exception as e:
        components.append(ComponentStatus(
            name="Embedding Model",
            status="unhealthy",
            details=str(e)
        ))
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        components=components,
        version="1.0.0"
    )


@app.post("/api/query", response_model=QueryResponse, tags=["RAG"])
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base and get an AI-generated answer.
    
    This endpoint:
    1. Retrieves relevant documents from the vector store
    2. Sends context + query to the LLM
    3. Returns the answer with source citations
    """
    start_time = time.time()
    
    try:
        # 1. Retrieve relevant documents
        retriever = get_retriever()
        docs = retriever.retrieve(request.query, k=request.k)
        
        # 2. Generate answer
        if docs:
            llm = get_llm(request.provider.value)
            answer = llm.generate_answer(request.query, docs)
        else:
            answer = "No relevant documents found in the knowledge base. Please try rephrasing your question or ensure documents have been ingested."
        
        # 3. Format sources
        sources = []
        for doc in docs:
            metadata = doc.get('metadata', {})
            sources.append(SourceDocument(
                content=doc['content'][:500],  # Truncate for response
                source=metadata.get('source', doc.get('source', 'Unknown')),
                chunk_index=metadata.get('chunk_index'),
                relevance_score=doc.get('score')
            ))
        
        processing_time = (time.time() - start_time) * 1000
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            query=request.query,
            provider=request.provider,
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/ingest", response_model=IngestResponse, tags=["Admin"])
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents from a directory into the vector store.
    
    This endpoint:
    1. Loads documents from the specified directory
    2. Chunks them for optimal retrieval (if enabled)
    3. Generates embeddings
    4. Stores in ChromaDB
    """
    try:
        # Validate directory exists
        if not os.path.isdir(request.directory):
            raise HTTPException(
                status_code=400, 
                detail=f"Directory not found: {request.directory}"
            )
        
        # Create chunker with custom settings
        chunker = TextChunker(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        # Load documents
        loader = DocumentLoader(request.directory, chunker=chunker)
        documents = loader.load_documents(chunk=request.chunk)
        
        if not documents:
            return IngestResponse(
                success=False,
                documents_processed=0,
                chunks_created=0,
                message="No documents found in the specified directory"
            )
        
        # Prepare for embedding
        texts = [doc['content'] for doc in documents]
        metadatas = [doc.get('metadata', {"source": doc['source']}) for doc in documents]
        
        # Generate unique IDs
        ids = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            chunk_idx = metadata.get('chunk_index', 0)
            source = doc['source']
            ids.append(f"{source}_chunk_{chunk_idx}")
        
        # Generate embeddings
        embedder = Embedder()
        embeddings = embedder.generate_embeddings(texts)
        
        # Store in ChromaDB
        chroma = ChromaClient()
        chroma.upsert_documents(texts, metadatas, ids, embeddings)
        
        # Count unique source files
        unique_sources = len(set(doc['source'] for doc in documents))
        
        return IngestResponse(
            success=True,
            documents_processed=unique_sources,
            chunks_created=len(documents),
            message=f"Successfully ingested {unique_sources} documents ({len(documents)} chunks)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.get("/api/stats", tags=["Admin"])
async def get_stats():
    """Get statistics about the knowledge base."""
    try:
        chroma = ChromaClient()
        count = chroma.collection.count()
        
        return {
            "total_chunks": count,
            "vector_store": "ChromaDB",
            "embedding_model": "all-MiniLM-L6-v2"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Root redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
