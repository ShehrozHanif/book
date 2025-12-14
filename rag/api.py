"""
RAG API Server for AI-Native Physical AI & Humanoid Robotics Textbook

This module provides a FastAPI-based REST API for the RAG chatbot.

Endpoints:
- GET /health - Health check
- POST /ask - Ask a question and get an answer
- GET /chapters - List indexed chapters
- GET /stats - Get index statistics

Run with: uvicorn api:app --reload --port 8000
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from retriever import Retriever, RetrievalResult
from responder import Responder, Response, ResponseType

# Initialize FastAPI app
app = FastAPI(
    title="Physical AI Textbook RAG API",
    description="RAG-powered Q&A API for the AI-Native Physical AI & Humanoid Robotics Textbook",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG components (lazy loading)
_retriever: Optional[Retriever] = None
_responder: Optional[Responder] = None


def get_retriever() -> Retriever:
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        try:
            _retriever = Retriever()
        except FileNotFoundError:
            raise HTTPException(
                status_code=503,
                detail="Index not found. Run indexer.py first to create the index."
            )
    return _retriever


def get_responder() -> Responder:
    """Get or create responder instance."""
    global _responder
    if _responder is None:
        _responder = Responder(get_retriever())
    return _responder


# ----- Request/Response Models -----

class QuestionRequest(BaseModel):
    """Request model for asking a question."""
    question: str = Field(..., min_length=3, max_length=500, description="The question to ask")
    chapter_filter: Optional[str] = Field(None, description="Optional filter for specific chapter")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the perception-action loop?",
                "chapter_filter": None
            }
        }


class Citation(BaseModel):
    """Citation model for source references."""
    chapter: str
    section: str


class AnswerResponse(BaseModel):
    """Response model for answers."""
    success: bool
    response_type: str
    answer: str
    citations: List[Citation]
    confidence: float
    warning: Optional[str] = None
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "response_type": "success",
                "answer": "The perception-action loop is the continuous cycle...",
                "citations": [{"chapter": "Chapter 1", "section": "The Perception-Action Loop"}],
                "confidence": 0.85,
                "warning": None,
                "timestamp": "2025-12-13T10:30:00Z"
            }
        }


class ChapterInfo(BaseModel):
    """Information about an indexed chapter."""
    name: str
    chunk_count: int


class StatsResponse(BaseModel):
    """Response model for index statistics."""
    total_chunks: int
    chapters: List[str]
    tags: List[str]
    index_version: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    index_loaded: bool
    chunk_count: int
    timestamp: str


# ----- API Endpoints -----

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to docs."""
    return {"message": "Physical AI Textbook RAG API", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Check API health and index status.

    Returns the current status of the API and whether the index is loaded.
    """
    try:
        retriever = get_retriever()
        return HealthResponse(
            status="healthy",
            index_loaded=True,
            chunk_count=len(retriever.chunks),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    except HTTPException:
        return HealthResponse(
            status="degraded",
            index_loaded=False,
            chunk_count=0,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )


@app.post("/ask", response_model=AnswerResponse, tags=["Q&A"])
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the textbook content.

    The RAG system will:
    1. Check for unsafe or out-of-scope queries
    2. Retrieve relevant content from the textbook
    3. Generate an answer with citations
    4. Apply confidence thresholds

    Returns an answer with source citations, or an appropriate refusal message.
    """
    responder = get_responder()

    response = responder.generate_response(request.question)

    return AnswerResponse(
        success=response.response_type == ResponseType.SUCCESS,
        response_type=response.response_type.value,
        answer=response.answer,
        citations=[Citation(**c) for c in response.citations],
        confidence=response.confidence,
        warning=response.warning,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/chapters", response_model=List[str], tags=["Content"])
async def list_chapters():
    """
    List all indexed chapters.

    Returns a list of chapter names that are available for querying.
    """
    retriever = get_retriever()
    return retriever.get_all_chapters()


@app.get("/tags", response_model=List[str], tags=["Content"])
async def list_tags():
    """
    List all content tags.

    Returns a list of tags used to categorize content chunks.
    """
    retriever = get_retriever()
    return retriever.get_all_tags()


@app.get("/stats", response_model=StatsResponse, tags=["System"])
async def get_stats():
    """
    Get index statistics.

    Returns information about the indexed content including
    total chunks, chapters, and available tags.
    """
    retriever = get_retriever()
    return StatsResponse(
        total_chunks=len(retriever.chunks),
        chapters=retriever.get_all_chapters(),
        tags=retriever.get_all_tags(),
        index_version=retriever.metadata.get("index_version", "unknown")
    )


# ----- Startup/Shutdown Events -----

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    print("=" * 60)
    print("Physical AI Textbook RAG API")
    print("=" * 60)
    try:
        retriever = get_retriever()
        print(f"Index loaded: {len(retriever.chunks)} chunks")
        print(f"Chapters: {retriever.get_all_chapters()}")
    except HTTPException as e:
        print(f"Warning: {e.detail}")
        print("API will start but /ask endpoint will return 503")
    print("=" * 60)
    print("API ready at http://localhost:8000")
    print("Documentation at http://localhost:8000/docs")
    print("=" * 60)


# ----- Main Entry Point -----

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

















# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from datetime import datetime

# from retriever import Retriever
# from responder import Responder, ResponseType

# app = FastAPI(title="Physical AI RAG API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# retriever = Retriever()
# responder = Responder(retriever)


# class QuestionRequest(BaseModel):
#     question: str


# class Citation(BaseModel):
#     chapter: str
#     section: str


# class AnswerResponse(BaseModel):
#     success: bool
#     response_type: str
#     answer: str
#     citations: list[Citation]
#     confidence: float
#     warning: str | None = None
#     timestamp: str


# @app.get("/health")
# def health():
#     return {
#         "status": "healthy",
#         "index_loaded": True,
#         "chunk_count": len(retriever.chunks),
#         "timestamp": datetime.utcnow().isoformat() + "Z",
#     }


# @app.post("/ask", response_model=AnswerResponse)
# def ask(req: QuestionRequest):
#     r = responder.generate_response(req.question)
#     return AnswerResponse(
#         success=r.response_type == ResponseType.SUCCESS,
#         response_type=r.response_type.value,
#         answer=r.answer,
#         citations=[Citation(**c) for c in r.citations],
#         confidence=r.confidence,
#         warning=r.warning,
#         timestamp=datetime.utcnow().isoformat() + "Z",
#     )


# @app.get("/chapters")
# def chapters():
#     return retriever.get_all_chapters()
