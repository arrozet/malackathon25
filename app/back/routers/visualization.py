"""
Visualization Router - API endpoints for data visualization microservice.

This module exposes RESTful endpoints for retrieving aggregated
visualization data with filtering capabilities.
"""

from fastapi import APIRouter, HTTPException
import logging

from app.back.schemas import DataVisualization, DataFilters
from app.back.services.visualization_service import get_visualization_data

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/data",
    tags=["visualization"],
)


@router.get("/visualization", response_model=DataVisualization)
async def get_data_visualization(
    start_date: str | None = None,
    end_date: str | None = None,
    gender: int | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    category: str | None = None,
    readmission: bool | None = None,
) -> DataVisualization:
    """
    Get aggregated data for visualization with optional filters.
    
    This endpoint returns data structured for multiple chart types,
    including category distributions, age groups, time series, and more.
    Delegates to the visualization microservice for data processing.
    
    Args:
        start_date (str, optional): Start date filter (YYYY-MM-DD).
        end_date (str, optional): End date filter (YYYY-MM-DD).
        gender (int, optional): Gender filter (1=male, 2=female).
        age_min (int, optional): Minimum age filter.
        age_max (int, optional): Maximum age filter.
        category (str, optional): Diagnostic category filter.
        readmission (bool, optional): Readmission status filter.
    
    Returns:
        DataVisualization: Complete visualization data with all distributions.
    
    Raises:
        HTTPException: If database connection fails or query errors occur.
    """
    # Build filters object
    filters = DataFilters(
        start_date=start_date,
        end_date=end_date,
        gender=gender,
        age_min=age_min,
        age_max=age_max,
        category=category,
        readmission=readmission,
    )
    
    try:
        return get_visualization_data(filters)
    except Exception as e:
        logger.error(f"Failed to retrieve visualization data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve visualization data: {str(e)}"
        )

