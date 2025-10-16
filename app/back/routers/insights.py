"""
Insights Router - API endpoints for insights microservice.

This module exposes RESTful endpoints for retrieving analytical insights.
"""

from fastapi import APIRouter, HTTPException
import logging

from app.back.schemas import InsightSummary
from app.back.services.insights_service import build_insight_summary

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/insights",
    tags=["insights"],
)


@router.get("", response_model=InsightSummary)
async def get_insights() -> InsightSummary:
    """
    Retrieve curated summary of insights for the Brain landing page.
    
    The handler delegates to the insights microservice to compute aggregated
    metrics from the Oracle Autonomous Database. If the connection fails,
    a fallback dataset keeps the UI usable.
    
    Returns:
        InsightSummary: Structured insight payload for the frontend.
    """
    try:
        return build_insight_summary()
    except Exception as e:
        logger.error(f"Failed to retrieve insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve insights: {str(e)}"
        )

