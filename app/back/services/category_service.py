"""
Category Service - Microservice for diagnostic category management.

This service handles operations related to diagnostic categories
including retrieval and filtering.
"""

from typing import Any, Dict
import logging

from app.back.db import get_connection, test_connection

logger = logging.getLogger(__name__)


def get_all_categories() -> Dict[str, Any]:
    """
    Retrieve all unique diagnostic categories from the database.
    
    This method queries the database to return a list of all available
    diagnostic categories for use in filter dropdowns and analytics.
    
    Returns:
        dict: List of available categories and total count.
    
    Raises:
        Exception: If database connection fails or query errors occur.
    """
    # Verify database connectivity
    if not test_connection():
        raise Exception("Database connection unavailable")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        query = '''
            SELECT DISTINCT "Categoría"
            FROM SALUDMENTAL
            WHERE "Categoría" IS NOT NULL
            ORDER BY "Categoría"
        '''
        cursor.execute(query)
        
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        return {
            "categories": categories,
            "total": len(categories)
        }

