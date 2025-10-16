"""
AI Router - REST endpoints for the AI service.

This router exposes endpoints for interacting with the Brain AI assistant.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging

from app.back.services.ai_service import AIService
from app.back.schemas import (
    AIChatRequest,
    AIChatResponse,
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIVisualizationRequest,
    AIVisualizationResponse,
    AIHealthResponse,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/ai",
    tags=["AI Assistant"],
    responses={
        500: {"description": "Internal server error"},
        503: {"description": "Service unavailable - AI service not initialized"},
    },
)

# Global AI service instance (singleton pattern)
_ai_service_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """
    Get or create the AI service singleton instance.
    
    Returns:
        AIService: The AI service instance.
    
    Raises:
        ValueError: If AI service cannot be initialized.
    """
    global _ai_service_instance
    
    if _ai_service_instance is None:
        logger.info("Initializing AI service singleton...")
        _ai_service_instance = AIService()
        logger.info("AI service singleton initialized successfully")
    
    return _ai_service_instance


@router.post("/chat/stream")
async def chat_stream(request: AIChatRequest):
    """
    Chat with the Brain AI assistant (streaming version with real-time progress).
    
    This endpoint processes natural language queries and streams progress events
    in real-time using Server-Sent Events (SSE). This provides transparency into
    the multi-agent thinking process.
    
    Args:
        request (AIChatRequest): Chat request with message and optional history.
    
    Returns:
        StreamingResponse: SSE stream with progress events and final response.
    
    Raises:
        HTTPException: If AI service is unavailable or processing fails.
    
    Event types streamed:
        - thinking: General thinking/analysis message
        - routing: Specialist routing decision
        - specialist_start: A specialist started working
        - specialist_complete: A specialist completed their task
        - synthesizing: Final synthesis in progress
        - complete: Final response ready (includes full response text)
        - error: An error occurred
    
    Example:
        ```python
        POST /ai/chat/stream
        {
            "message": "¿Cuántos episodios hay en 2023?",
            "chat_history": []
        }
        
        # Response (SSE format):
        data: {"type": "thinking", "message": "Analizando tu pregunta..."}
        
        data: {"type": "routing", "specialists": ["sql_specialist"], "message": "Consultando: Base de Datos"}
        
        data: {"type": "specialist_start", "specialist": "sql_specialist", "message": "🔍 Base de Datos trabajando..."}
        
        data: {"type": "specialist_complete", "specialist": "sql_specialist", "message": "✓ Base de Datos completado"}
        
        data: {"type": "synthesizing", "message": "Integrando toda la información..."}
        
        data: {"type": "complete", "response": "Hay 1,234 episodios...", "tools_used": ["oracle_rag"], "has_errors": false}
        ```
    """
    try:
        logger.info(f"Received streaming chat request: {request.message[:100]}...")
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Create streaming response
        return StreamingResponse(
            ai_service.chat_stream(
                message=request.message,
                chat_history=request.chat_history,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
        
    except ValueError as e:
        # Configuration error
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service not properly configured: {str(e)}"
        )
    except Exception as e:
        # Processing error
        logger.error(f"Error processing streaming chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing streaming chat request: {str(e)}"
        )


@router.post("/chat", response_model=AIChatResponse)
async def chat(request: AIChatRequest) -> AIChatResponse:
    """
    Chat with the Brain AI assistant (non-streaming version).
    
    This endpoint processes natural language queries and returns AI-generated responses
    using the configured tools (database queries, internet search, code execution, diagrams).
    
    For real-time progress updates, use /ai/chat/stream instead.
    
    Args:
        request (AIChatRequest): Chat request with message and optional history.
    
    Returns:
        AIChatResponse: AI response with message, tool calls, and intermediate steps.
    
    Raises:
        HTTPException: If AI service is unavailable or processing fails.
    
    Example:
        ```python
        POST /ai/chat
        {
            "message": "¿Cuántos episodios hay en 2023?",
            "chat_history": []
        }
        ```
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Process chat
        result = ai_service.chat(
            message=request.message,
            chat_history=request.chat_history,
        )
        
        # Return response (multi-agent architecture)
        return AIChatResponse(
            response=result["response"],
            tool_calls=result.get("tools_used", []),
            intermediate_steps=[],  # Multi-agent hides intermediate steps
        )
        
    except ValueError as e:
        # Configuration error
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service not properly configured: {str(e)}"
        )
    except Exception as e:
        # Processing error
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze(request: AIAnalysisRequest) -> AIAnalysisResponse:
    """
    Perform data analysis using AI.
    
    This endpoint is specialized for analytical queries that require database queries
    and statistical analysis.
    
    Args:
        request (AIAnalysisRequest): Analysis request with query.
    
    Returns:
        AIAnalysisResponse: Analysis results with data, statistics, and insights.
    
    Raises:
        HTTPException: If AI service is unavailable or analysis fails.
    
    Example:
        ```python
        POST /ai/analyze
        {
            "query": "Analiza la distribución de episodios por severidad"
        }
        ```
    """
    try:
        logger.info(f"Received analysis request: {request.query[:100]}...")
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Perform analysis (uses chat with multi-agent routing)
        result = ai_service.analyze(query=request.query)
        
        # Return response
        return AIAnalysisResponse(
            response=result["response"],
            tool_calls=result.get("tools_used", []),
            intermediate_steps=[],  # Multi-agent hides intermediate steps
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service not properly configured: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error processing analysis request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing analysis request: {str(e)}"
        )


@router.post("/visualize", response_model=AIVisualizationResponse)
async def visualize(request: AIVisualizationRequest) -> AIVisualizationResponse:
    """
    Generate Mermaid diagram visualization.
    
    This endpoint generates Mermaid diagram syntax based on a description.
    
    Args:
        request (AIVisualizationRequest): Visualization request with description.
    
    Returns:
        AIVisualizationResponse: Mermaid diagram code.
    
    Raises:
        HTTPException: If visualization generation fails.
    
    Example:
        ```python
        POST /ai/visualize
        {
            "description": "diagrama de flujo de admisión hospitalaria"
        }
        ```
    """
    try:
        logger.info(f"Received visualization request: {request.description[:100]}...")
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Generate visualization (uses chat with diagram specialist)
        result = ai_service.visualize(query=request.description)
        
        # Extract mermaid code from response
        response_text = result["response"]
        
        # Mermaid code should be in the response
        return AIVisualizationResponse(
            mermaid_code=response_text,
            description=request.description,
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"AI service not properly configured: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )


@router.get("/health", response_model=AIHealthResponse)
async def health() -> AIHealthResponse:
    """
    Check AI service health.
    
    This endpoint checks the health of the AI service and all its components.
    
    Returns:
        AIHealthResponse: Health status of AI service components.
    
    Example:
        ```python
        GET /ai/health
        ```
    """
    try:
        logger.info("Checking AI service health...")
        
        # Get AI service
        ai_service = get_ai_service()
        
        # Check health
        health_status = ai_service.health_check()
        
        # Extract components status
        status = health_status.get("status", "unknown")
        agents = health_status.get("agents", {})
        
        # Convert agents to components format
        components = {
            "ai_service": status == "healthy",
            "llm": health_status.get("xai_api_key") == "configured",
            "orchestrator": agents.get("orchestrator") == "active",
            "sql_specialist": agents.get("sql_specialist") == "active",
            "search_specialist": agents.get("search_specialist") == "active",
            "python_specialist": agents.get("python_specialist") == "active",
            "diagram_specialist": agents.get("diagram_specialist") == "active",
            "synthesizer": agents.get("synthesizer") == "active",
        }
        
        # Return response
        return AIHealthResponse(
            status=status,
            components=components,
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return AIHealthResponse(
            status="unhealthy",
            components={
                "ai_service": False,
                "llm": False,
                "oracle_tool": False,
                "internet_tool": False,
                "python_tool": False,
                "mermaid_tool": False,
            },
            error=str(e),
        )
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}")
        return AIHealthResponse(
            status="unhealthy",
            components={},
            error=str(e),
        )

