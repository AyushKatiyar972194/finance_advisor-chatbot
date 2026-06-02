import logging
import time
import urllib.request
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from config.settings import settings
from services.chat_service import ChatService
from workflows.finance_workflow import FinanceWorkflow

# Setup structured logging configuration
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api")

app = FastAPI(
    title="Personal Finance Advisor API",
    description="Local-first, Ollama-powered API ready for n8n/chatbot integrations",
    version="1.0.0"
)

# Instantiate services and workflows
try:
    chat_service = ChatService()
    finance_workflow = FinanceWorkflow()
    logger.info("Core services and workflows successfully initialized.")
except Exception as e:
    logger.critical(f"Startup Failure: Could not initialize core classes: {e}")

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming Request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Request Completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {process_time:.4f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request Failed: {request.method} {request.url.path} "
            f"- Error: {str(e)} - Duration: {process_time:.4f}s"
        )
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal Server Error: {str(e)}"}
        )

# Pydantic Schemas for requests/responses
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique identifier for user session context")
    message: str = Field(..., description="User request message")

class ChatResponse(BaseModel):
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AnalysisRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Optional session context tracking identifier")
    query: str = Field(..., min_length=5, description="Full details of user financial state for CrewAI execution")
    focus: str = Field("all", description="Targeted analysis focus area: all, budget, investment, debt, tax")

class AnalysisResponse(BaseModel):
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Endpoints
@app.get("/health")
def health_check():
    """
    Check system state and local Ollama accessibility directly.
    """
    logger.info("Health check path invoked.")
    try:
        url = f"{settings.OLLAMA_BASE_URL}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=3) as response:
            ollama_connected = (response.status == 200)
    except Exception as e:
        logger.error(f"Error during health check validation: {e}")
        ollama_connected = False
    
    status = "healthy" if ollama_connected else "unhealthy"
    return {
        "status": status,
        "ollama_connected": ollama_connected,
        "model": settings.OLLAMA_MODEL
    }

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """
    Conversational chatbot endpoint maintaining session context in history.
    """
    logger.info(f"Chat request received for session {payload.session_id}.")
    if not payload.message.strip():
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    try:
        response_text = chat_service.chat(payload.session_id, payload.message)
        return ChatResponse(
            response=response_text,
            metadata={"session_id": payload.session_id}
        )
    except Exception as e:
        logger.error(f"Error in POST /chat handler: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama Chat error: {str(e)}")

@app.post("/analysis", response_model=AnalysisResponse)
def analysis_endpoint(payload: AnalysisRequest):
    """
    Deep analysis endpoint triggering the sequential CrewAI financial orchestration workflow.
    """
    logger.info(f"Deep analysis request received with focus: {payload.focus}.")
    valid_focus_areas = ["all", "budget", "investment", "debt", "tax"]
    if payload.focus.lower() not in valid_focus_areas:
        raise HTTPException(
            status_code=422, 
            detail=f"Invalid focus area '{payload.focus}'. Must be one of: {', '.join(valid_focus_areas)}"
        )
    try:
        response_text = finance_workflow.run(payload.query)
        return AnalysisResponse(
            response=response_text,
            metadata={
                "session_id": payload.session_id if payload.session_id else "anonymous",
                "focus": payload.focus
            }
        )
    except ConnectionError as ce:
        logger.error(f"Connection failure in POST /analysis handler: {ce}")
        raise HTTPException(status_code=503, detail=str(ce))
    except Exception as e:
        logger.error(f"Error in POST /analysis handler: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failure: {str(e)}")
