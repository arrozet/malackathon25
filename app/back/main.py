"""
FastAPI API Gateway for Brain Backend Microservices.

This module serves as the main API Gateway that orchestrates and exposes
multiple microservices through a unified interface. It handles application
lifecycle, CORS configuration, and routes requests to appropriate services.
"""

from typing import Dict, Any
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.back.config import config
from app.back.db import (
    initialize_connection_pool,
    close_connection_pool,
)

# Import routers for microservices
from app.back.routers import insights, visualization, health, categories, ai

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    Initializes the database connection pool on startup and closes it on shutdown.
    
    Args:
        app (FastAPI): The FastAPI application instance.
    
    Yields:
        None: Control returns to the application during its lifetime.
    
    Side Effects:
        - On startup: Initializes database connection pool
        - On shutdown: Closes database connection pool
    """
    # Startup
    logger.info("Starting Brain API Gateway...")
    logger.info(f"Environment: {config.APP_ENV}")
    logger.info(f"Configuration: {config.display_config()}")
    
    try:
        # Initialize database connection pool
        # Configured for multi-agent AI workloads + concurrent frontend requests
        # Use different settings based on environment
        is_production = config.APP_ENV in ["prod", "production"]
        
        initialize_connection_pool(
            min_connections=1 if is_production else 2,    # Start with 1 in prod for faster startup
            max_connections=50,   # Oracle ADB supports 25-100+ connections
            increment=5,
            timeout=60 if is_production else 30  # Longer timeout in production for cloud latency
        )
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {str(e)}")
        logger.warning("Application will continue startup. Database operations may fail until connection is established.")
        # Don't raise in production - allow app to start and retry connections
        if not config.APP_ENV in ["prod", "production"]:
            raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Brain API Gateway...")
    try:
        close_connection_pool()
        logger.info("Database connection pool closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection pool: {str(e)}")


# Create FastAPI application instance (API Gateway)
app = FastAPI(
    title="Brain - Malackathon 2025 API Gateway",
    description="Microservices-based API Gateway for Brain mental health research platform",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
allowed_origins = config.get_cors_origins()
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {allowed_origins}")


# Register microservice routers
app.include_router(health.router)
app.include_router(insights.router)
app.include_router(visualization.router)
app.include_router(categories.router)
app.include_router(ai.router)

logger.info("Microservice routers registered successfully")


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint for API Gateway.
    
    Returns basic information about the API Gateway and available microservices.
    
    Returns:
        dict: Welcome message with API Gateway details.
    """
    return {
        "message": "Brain API Gateway - Malackathon 2025",
        "status": "running",
        "version": "2.0.0",
        "architecture": "microservices",
        "environment": config.APP_ENV,
        "services": [
            "health - System health monitoring",
            "insights - Analytical insights generation",
            "visualization - Data visualization and filtering",
            "categories - Diagnostic category management",
            "ai - AI Assistant (Brain) with Oracle RAG, internet search, code execution, and diagrams",
        ]
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for the API Gateway.
    
    Catches unhandled exceptions and returns a consistent error response
    across all microservices.
    
    Args:
        request: The request that caused the exception.
        exc (Exception): The exception that was raised.
    
    Returns:
        JSONResponse: Error response with status code 500.
    """
    logger.error(f"Unhandled exception in API Gateway: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if config.DEBUG else "An error occurred processing your request"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the API Gateway
    logger.info("Starting Brain API Gateway with uvicorn...")
    uvicorn.run(
        "app.back.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info"
    )
