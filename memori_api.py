"""
BOTFUSIONS - MEMORI API
FastAPI REST API for Memori service
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import logging
from dotenv import load_dotenv

from memori_service import get_memori_service

# Load environment
load_dotenv()

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Botfusions Memori API",
    description="AI Memory API powered by Memori SDK",
    version="1.0.0",
    contact={
        "name": "Botfusions",
        "email": "info@botfusions.com",
        "url": "https://botfusions.com"
    }
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1, max_length=5000)
    user_id: Optional[str] = Field(None, description="User ID for multi-user isolation")
    namespace: Optional[str] = Field("default", description="Memory namespace")
    model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt")


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


class MemoryStatsResponse(BaseModel):
    """Memory statistics response"""
    namespace: str
    database: str
    status: str


# ============================================
# ENDPOINTS
# ============================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "online",
        "service": "Botfusions Memori API",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Botfusions Memori API",
        "version": "1.0.0"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with memory

    Example:
```json
    {
        "message": "Merhaba! Ben Cenk, Botfusions'ta çalışıyorum.",
        "user_id": "customer_123",
        "namespace": "botfusions_production"
    }
```
    """
    try:
        # Get service
        service = get_memori_service(
            namespace=request.namespace,
            user_id=request.user_id
        )

        # Chat
        result = service.chat(
            message=request.message,
            user_id=request.user_id,
            model=request.model,
            system_prompt=request.system_prompt
        )

        if result["success"]:
            return ChatResponse(
                success=True,
                response=result["response"],
                metadata={
                    "model": result["model"],
                    "namespace": result["namespace"],
                    "usage": result["usage"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/stats", response_model=MemoryStatsResponse)
async def memory_stats(
    namespace: str = "default",
    user_id: Optional[str] = None
):
    """
    Get memory statistics

    Query params:
    - namespace: Memory namespace (default: "default")
    - user_id: Optional user ID
    """
    try:
        service = get_memori_service(namespace=namespace, user_id=user_id)
        stats = service.get_memory_stats()
        return stats

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/namespaces")
async def list_namespaces():
    """List all active namespaces"""
    from memori_service import _services

    return {
        "namespaces": list(_services.keys()),
        "count": len(_services)
    }


# ============================================
# STARTUP/SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Botfusions Memori API starting...")
    logger.info(f"📡 Database: {os.getenv('MEMORI_DATABASE__CONNECTION_STRING', 'Not configured')[:50]}...")
    logger.info(f"🔑 OpenAI: {'Configured' if os.getenv('OPENAI_API_KEY') else 'Not configured'}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Botfusions Memori API shutting down...")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "memori_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
