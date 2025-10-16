"""
Categories Router - API endpoints for category microservice.

This module exposes RESTful endpoints for diagnostic category operations.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
import logging

from app.back.services.category_service import get_all_categories

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/data",
    tags=["categories"],
)


@router.get("/categories")
async def get_categories() -> Dict[str, Any]:
    """
    Get list of all available diagnostic categories.
    
    This endpoint returns unique category values for use in filter dropdowns
    by delegating to the category microservice.
    
    Returns:
        dict: List of available categories.
    
    Raises:
        HTTPException: If database connection fails or query errors occur.
    """
    try:
        return get_all_categories()
    except Exception as e:
        logger.error(f"Failed to retrieve categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve categories: {str(e)}"
        )

