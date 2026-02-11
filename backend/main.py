"""
Education Intelligence Dashboard - Backend API
Ministry of Education, Government of India
Technology Partner: Deloitte Touche Tohmatsu
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from api.chat_handler import ChatHandler
from rag.rag_system import RAGSystem
from llm.llm_handler import LLMHandler

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Education Intelligence Dashboard API",
    description="AI-powered backend for Ministry of Education Intelligence Dashboard",
    version="1.0.0"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
cors_origins = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
rag_system = RAGSystem()
llm_handler = LLMHandler()
chat_handler = ChatHandler(rag_system, llm_handler)

# =============================================================================
# Data Models
# =============================================================================

class ChatRequest(BaseModel):
    query: str
    current_month: Optional[str] = None
    include_visualization: bool = True

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[Dict[str, Any]]] = None
    visualization: Optional[Dict[str, Any]] = None
    timestamp: str

class CompareRequest(BaseModel):
    entities: List[str]
    metric: str
    months: Optional[List[str]] = None

class HealthResponse(BaseModel):
    status: str
    llm_connected: bool
    rag_initialized: bool
    timestamp: str

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Education Intelligence Dashboard API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    llm_status = await llm_handler.check_connection()
    rag_status = rag_system.is_initialized()

    return HealthResponse(
        status="healthy" if (llm_status and rag_status) else "degraded",
        llm_connected=llm_status,
        rag_initialized=rag_status,
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/api/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    Main chat endpoint for Education Intelligence Assistant

    Handles:
    - Natural language queries about newsletter data
    - Contextual information retrieval
    - Query-to-visualization mapping
    - Comparative analysis
    """
    try:
        response_data = await chat_handler.process_query(
            query=chat_request.query,
            current_month=chat_request.current_month,
            include_visualization=chat_request.include_visualization
        )

        return ChatResponse(
            response=response_data["response"],
            sources=response_data.get("sources"),
            visualization=response_data.get("visualization"),
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/api/compare")
@limiter.limit("20/minute")
async def compare_entities(request: Request, compare_request: CompareRequest):
    """
    Compare states, metrics, or time periods

    Examples:
    - Compare Kerala and Gujarat attendance rates
    - Compare infrastructure across months
    """
    try:
        comparison_data = await chat_handler.handle_comparison(
            entities=compare_request.entities,
            metric=compare_request.metric,
            months=compare_request.months
        )

        return JSONResponse(content=comparison_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing comparison: {str(e)}")

@app.get("/api/newsletter/months")
async def get_available_months():
    """Get list of available months in the newsletter data"""
    try:
        months = rag_system.get_available_months()
        return {"months": months}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching months: {str(e)}")

@app.get("/api/newsletter/{month}")
async def get_month_data(month: str):
    """Get complete data for a specific month"""
    try:
        data = rag_system.get_month_data(month)
        if not data:
            raise HTTPException(status_code=404, detail=f"Month {month} not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching month data: {str(e)}")

@app.post("/api/search")
@limiter.limit("40/minute")
async def semantic_search(request: Request, query: str, top_k: int = 5):
    """
    Semantic search across newsletter content

    Returns most relevant chunks based on the query
    """
    try:
        results = await rag_system.search(query, top_k=top_k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")

# =============================================================================
# Startup & Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    print("=" * 70)
    print("Education Intelligence Dashboard - Backend API")
    print("Ministry of Education, Government of India")
    print("=" * 70)

    # Initialize RAG system
    print("\n[1/3] Initializing RAG system...")
    await rag_system.initialize()
    print("✓ RAG system initialized")

    # Check LLM connection
    print("\n[2/3] Checking LLM connection...")
    llm_connected = await llm_handler.check_connection()
    if llm_connected:
        print("✓ LLM connected successfully")
    else:
        print("⚠ LLM not connected - check Ollama installation")

    # Initialize chat handler
    print("\n[3/3] Initializing chat handler...")
    await chat_handler.initialize()
    print("✓ Chat handler initialized")

    print("\n" + "=" * 70)
    print("Backend API ready to serve requests")
    print("=" * 70 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down Education Intelligence Dashboard API...")
    await rag_system.cleanup()
    print("Cleanup completed")

# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
