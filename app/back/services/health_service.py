"""
Health Service - Microservice for system health monitoring.

This service handles health checks, database connectivity tests,
and connection pool status monitoring.
"""

from typing import Any, Dict
import logging

from app.back.db import test_connection, get_pool_status
from app.back.config import config

logger = logging.getLogger(__name__)


def check_health() -> Dict[str, Any]:
    """
    Perform comprehensive health check of the application.
    
    This method tests database connectivity and retrieves connection
    pool status to provide a complete health assessment.
    
    Returns:
        dict: Health status including database connectivity and pool status.
    
    Raises:
        Exception: If health check encounters critical failures.
    """
    try:
        # Test database connection
        db_healthy = test_connection()
        
        # Get connection pool status
        pool_status = get_pool_status() if db_healthy else None
        
        health_data = {
            "status": "healthy" if db_healthy else "degraded",
            "database": {
                "connected": db_healthy,
                "dsn": config.ORACLE_DSN,
            }
        }
        
        if pool_status:
            health_data["database"]["pool"] = pool_status
        
        return health_data
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise


def get_pool_status_detailed() -> Dict[str, Any]:
    """
    Retrieve detailed connection pool status.
    
    This method provides comprehensive statistics about the database
    connection pool including utilization metrics.
    
    Returns:
        dict: Connection pool statistics and utilization.
    
    Raises:
        Exception: If unable to retrieve pool status.
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
        raise

