"""
Health Router - API endpoints for health monitoring microservice.

This module exposes RESTful endpoints for system health checks
and connection pool monitoring.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
import logging

from app.back.services.health_service import check_health, get_pool_status_detailed

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["health"],
)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Tests the database connection and returns the health status of
    the application by delegating to the health microservice.
    
    Returns:
        dict: Health status including database connectivity and pool status.
    
    Raises:
        HTTPException: If health check fails (500 Internal Server Error).
    """
    try:
        return check_health()
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/db/pool-status")
async def get_db_pool_status() -> Dict[str, Any]:
    """
    Get database connection pool status endpoint.
    
    Returns detailed information about the current state of the
    database connection pool by delegating to the health microservice.
    
    Returns:
        dict: Connection pool statistics and status.
    
    Raises:
        HTTPException: If unable to retrieve pool status (500 Internal Server Error).
    """
    try:
        return get_pool_status_detailed()
    except Exception as e:
        logger.error(f"Failed to get pool status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pool status: {str(e)}"
        )

