"""
FastAPI application for Oracle Cloud Autonomous Database integration.

This is the main application module that initializes FastAPI and manages
the database connection lifecycle.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from app.back.config import config
from app.back.db import (
    initialize_connection_pool,
    close_connection_pool,
    test_connection,
    get_pool_status,
    execute_query,
)

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


@app.get("/db/test")
async def test_db_query() -> Dict[str, Any]:
    """
    Test database query endpoint.
    
    Executes a simple test query to verify database connectivity
    and query execution capabilities.
    
    Returns:
        dict: Test query results with timestamp from database.
    
    Raises:
        HTTPException: If query execution fails (500 Internal Server Error).
    """
    try:
        # Execute a simple test query
        result = execute_query(
            "SELECT SYSDATE, USER, SYS_CONTEXT('USERENV', 'DB_NAME') as DB_NAME FROM DUAL"
        )
        
        if result:
            row = result[0]
            return {
                "status": "success",
                "query": "Test query executed successfully",
                "result": {
                    "timestamp": str(row[0]),
                    "user": row[1],
                    "database": row[2],
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Query returned no results"
            )
    except Exception as e:
        logger.error(f"Test query failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Test query failed: {str(e)}"
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
