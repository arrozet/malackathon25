"""
FastAPI application for Oracle Cloud Autonomous Database integration.

This is the main application module that initializes FastAPI and manages
the database connection lifecycle.
"""

from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from app.back.config import config
from app.back.db import (
    initialize_connection_pool,
    close_connection_pool,
    test_connection,
    get_pool_status,
)
from app.back.schemas import InsightSummary

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
    logger.info("Starting application...")
    logger.info(f"Environment: {config.APP_ENV}")
    logger.info(f"Configuration: {config.display_config()}")
    
    try:
        # Initialize database connection pool
        initialize_connection_pool(
            min_connections=2,
            max_connections=10,
            increment=2
        )
        logger.info("Database connection pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        close_connection_pool()
        logger.info("Database connection pool closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection pool: {str(e)}")


# Create FastAPI application instance
app = FastAPI(
    title="Malackathon 2025 - Oracle Cloud API",
    description="FastAPI application with Oracle Autonomous Database integration",
    version="1.0.0",
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


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint.
    
    Returns a welcome message with basic API information.
    
    Returns:
        dict: Welcome message with API details.
    """
    return {
        "message": "Malackathon 2025 API",
        "status": "running",
        "version": "1.0.0",
        "environment": config.APP_ENV,
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Tests the database connection and returns the health status of the application.
    
    Returns:
        dict: Health status including database connectivity and pool status.
    
    Raises:
        HTTPException: If health check fails (500 Internal Server Error).
    """
    try:
        # Test database connection
        db_healthy = test_connection()
        
        # Get connection pool status
        pool_status = get_pool_status()
        
        return {
            "status": "healthy",
            "database": {
                "connected": db_healthy,
                "dsn": config.ORACLE_DSN,
                "pool": pool_status,
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@app.get("/insights", response_model=InsightSummary)
async def get_prototype_insights() -> InsightSummary:
    """
    Retrieve a curated summary of mock insights for the Brain landing page.
    
    The current implementation returns static values that allow the frontend to
    render a realistic dashboard while the Oracle integration is configured.
    Once the database is available, this handler will transform live query
    results into the same schema.
    
    Returns:
        InsightSummary: Structured insight payload for the frontend.
    """

    database_status = False
    try:
        database_status = test_connection()
    except Exception:
        logger.warning("Oracle database not reachable for prototype insights.")

    generated_at = datetime.now(timezone.utc)

    return InsightSummary(
        generated_at=generated_at,
        sample_period="Q1 2024",
        highlight_phrases=[
            "Admisiones psiquiátricas estables con ligero aumento en mujeres jóvenes",
            "Estancias medias reducidas 1.4 días gracias a intervenciones tempranas",
            "Readmisiones concentradas en trastornos afectivos severos",
        ],
        metric_sections=[
            {
                "title": "Panorama general",
                "metrics": [
                    {
                        "title": "Admisiones totales",
                        "value": "1,842",
                        "description": "Pacientes únicos ingresados en la red hospitalaria durante el periodo analizado.",
                    },
                    {
                        "title": "Estancia media",
                        "value": "7.6 días",
                        "description": "Promedio de días desde ingreso hasta alta, excluyendo hospitalizaciones parciales.",
                    },
                    {
                        "title": "Readmisiones 30 días",
                        "value": "12.4%",
                        "description": "Porcentaje de pacientes reingresados en menos de un mes tras el alta.",
                    },
                ],
            },
            {
                "title": "Perspectiva por género y edad",
                "metrics": [
                    {
                        "title": "Mujeres 18-29 años",
                        "value": "+6.2%",
                        "description": "Variación interanual en admisiones, destacando trastornos de ansiedad severa.",
                    },
                    {
                        "title": "Varones >60 años",
                        "value": "-3.8%",
                        "description": "Descenso en ingresos por episodios depresivos mayores tras programas ambulatorios.",
                    },
                    {
                        "title": "Estancia media U. agudos",
                        "value": "5.1 días",
                        "description": "Segmento con mayor rotación, clave para planificar recursos críticos.",
                    },
                ],
            },
            {
                "title": "Factores de riesgo a vigilar",
                "metrics": [
                    {
                        "title": "Intentos de suicidio previos",
                        "value": "27%",
                        "description": "Proporción de pacientes con historial de intentos, indicador de alerta prioritario.",
                    },
                    {
                        "title": "Tiempo a primera cita",
                        "value": "18 días",
                        "description": "Retrasos en seguimiento ambulatorio post alta, foco de mejora en coordinación.",
                    },
                    {
                        "title": "Cobertura terapias familiares",
                        "value": "41%",
                        "description": "Acceso actual a programas de acompañamiento familiar durante la hospitalización.",
                    },
                ],
            },
        ],
        database_connected=database_status,
    )


@app.get("/db/pool-status")
async def get_db_pool_status() -> Dict[str, Any]:
    """
    Get database connection pool status endpoint.
    
    Returns detailed information about the current state of the
    database connection pool.
    
    Returns:
        dict: Connection pool statistics and status.
    
    Raises:
        HTTPException: If unable to retrieve pool status (500 Internal Server Error).
    """
    try:
        pool_status = get_pool_status()
        return {
            "status": "success",
            "pool": pool_status,
            "utilization_percent": (
                (pool_status["busy"] / pool_status["max"]) * 100 
                if pool_status["max"] > 0 else 0
            )
        }
    except Exception as e:
        logger.error(f"Failed to get pool status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pool status: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.
    
    Catches unhandled exceptions and returns a consistent error response.
    
    Args:
        request: The request that caused the exception.
        exc (Exception): The exception that was raised.
    
    Returns:
        JSONResponse: Error response with status code 500.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if config.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level="debug" if config.DEBUG else "info"
    )
