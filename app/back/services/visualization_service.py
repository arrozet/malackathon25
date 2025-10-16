"""
Visualization Service - Microservice for data visualization and filtering.

This service handles all logic related to generating aggregated data
for charts and visualizations with optional filtering capabilities.
"""

from decimal import Decimal
from typing import Any, Optional
import logging

from app.back.db import get_connection, test_connection
from app.back.schemas import (
    DataVisualization,
    CategoryDistribution,
    AgeDistribution,
    TimeSeriesData,
    GenderDistribution,
    StayDistribution,
    DataFilters,
)

logger = logging.getLogger(__name__)


def _to_float(value: Optional[Any]) -> float:
    """
    Convert database numeric outputs into float numbers.
    
    Args:
        value (Any, optional): Value to convert to float.
    
    Returns:
        float: Converted float value or 0.0 if None.
    """
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def _to_int(value: Optional[Any]) -> int:
    """
    Convert database numeric outputs into integers.
    
    Args:
        value (Any, optional): Value to convert to integer.
    
    Returns:
        int: Converted integer value or 0 if None.
    """
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, (int, float)):
        return int(round(value))
    return int(str(value))


def _build_where_clause(filters: DataFilters) -> tuple[str, dict]:
    """
    Build SQL WHERE clause from filter parameters.
    
    This method constructs a parameterized SQL WHERE clause based on
    the provided filter criteria, ensuring SQL injection protection.
    
    Args:
        filters (DataFilters): Filter parameters from the request.
    
    Returns:
        tuple: WHERE clause string and parameters dictionary.
    """
    conditions = []
    params = {}
    
    if filters.start_date:
        conditions.append("FECHA_DE_INGRESO >= TO_DATE(:start_date, 'YYYY-MM-DD')")
        params['start_date'] = filters.start_date
    
    if filters.end_date:
        conditions.append("FECHA_DE_INGRESO <= TO_DATE(:end_date, 'YYYY-MM-DD')")
        params['end_date'] = filters.end_date
    
    if filters.gender is not None:
        conditions.append("SEXO = :gender")
        params['gender'] = filters.gender
    
    if filters.age_min is not None:
        conditions.append("EDAD >= :age_min")
        params['age_min'] = filters.age_min
    
    if filters.age_max is not None:
        conditions.append("EDAD <= :age_max")
        params['age_max'] = filters.age_max
    
    if filters.category:
        conditions.append('"Categoría" = :category')
        params['category'] = filters.category
    
    if filters.readmission is not None:
        conditions.append("REINGRESO = :readmission")
        params['readmission'] = 'S' if filters.readmission else 'N'
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    return where_clause, params


def get_visualization_data(filters: DataFilters) -> DataVisualization:
    """
    Retrieve aggregated data for visualization with optional filters.
    
    This method orchestrates all visualization queries including category
    distributions, age groups, time series, gender distribution, and
    stay distributions.
    
    Args:
        filters (DataFilters): Filter criteria for the data query.
    
    Returns:
        DataVisualization: Complete visualization data with all distributions.
    
    Raises:
        Exception: If database connection fails or queries error.
    """
    # Verify database connectivity
    if not test_connection():
        raise Exception("Database connection unavailable")
    
    where_clause, params = _build_where_clause(filters)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Total records matching filters
        query = f"SELECT COUNT(*) FROM SALUDMENTAL WHERE {where_clause}"
        cursor.execute(query, params)
        total_records = _to_int(cursor.fetchone()[0])
        
        # Category distribution
        query = f'''
            SELECT "Categoría", COUNT(*) as cnt
            FROM SALUDMENTAL
            WHERE {where_clause} AND "Categoría" IS NOT NULL
            GROUP BY "Categoría"
            ORDER BY cnt DESC
        '''
        cursor.execute(query, params)
        categories = []
        for row in cursor.fetchall():
            cat_name, count = row
            categories.append(CategoryDistribution(
                category=cat_name,
                count=_to_int(count),
                percentage=round((_to_int(count) / total_records * 100), 2) if total_records > 0 else 0
            ))
        
        # Age distribution
        query = f'''
            SELECT 
                CASE 
                    WHEN EDAD < 18 THEN '< 18'
                    WHEN EDAD BETWEEN 18 AND 29 THEN '18-29'
                    WHEN EDAD BETWEEN 30 AND 39 THEN '30-39'
                    WHEN EDAD BETWEEN 40 AND 49 THEN '40-49'
                    WHEN EDAD BETWEEN 50 AND 59 THEN '50-59'
                    WHEN EDAD BETWEEN 60 AND 69 THEN '60-69'
                    WHEN EDAD >= 70 THEN '70+'
                    ELSE 'Desconocido'
                END as age_group,
                CASE 
                    WHEN EDAD < 18 THEN 1
                    WHEN EDAD BETWEEN 18 AND 29 THEN 2
                    WHEN EDAD BETWEEN 30 AND 39 THEN 3
                    WHEN EDAD BETWEEN 40 AND 49 THEN 4
                    WHEN EDAD BETWEEN 50 AND 59 THEN 5
                    WHEN EDAD BETWEEN 60 AND 69 THEN 6
                    WHEN EDAD >= 70 THEN 7
                    ELSE 999
                END as sort_order,
                COUNT(*) as cnt
            FROM SALUDMENTAL
            WHERE {where_clause}
            GROUP BY 
                CASE 
                    WHEN EDAD < 18 THEN '< 18'
                    WHEN EDAD BETWEEN 18 AND 29 THEN '18-29'
                    WHEN EDAD BETWEEN 30 AND 39 THEN '30-39'
                    WHEN EDAD BETWEEN 40 AND 49 THEN '40-49'
                    WHEN EDAD BETWEEN 50 AND 59 THEN '50-59'
                    WHEN EDAD BETWEEN 60 AND 69 THEN '60-69'
                    WHEN EDAD >= 70 THEN '70+'
                    ELSE 'Desconocido'
                END,
                CASE 
                    WHEN EDAD < 18 THEN 1
                    WHEN EDAD BETWEEN 18 AND 29 THEN 2
                    WHEN EDAD BETWEEN 30 AND 39 THEN 3
                    WHEN EDAD BETWEEN 40 AND 49 THEN 4
                    WHEN EDAD BETWEEN 50 AND 59 THEN 5
                    WHEN EDAD BETWEEN 60 AND 69 THEN 6
                    WHEN EDAD >= 70 THEN 7
                    ELSE 999
                END
            ORDER BY sort_order
        '''
        cursor.execute(query, params)
        age_groups = []
        for row in cursor.fetchall():
            age_group, sort_order, count = row
            age_groups.append(AgeDistribution(
                age_group=age_group,
                count=_to_int(count),
                percentage=round((_to_int(count) / total_records * 100), 2) if total_records > 0 else 0
            ))
        
        # Time series (by month)
        query = f'''
            SELECT 
                TO_CHAR(FECHA_DE_INGRESO, 'YYYY-MM') as period,
                COUNT(*) as cnt
            FROM SALUDMENTAL
            WHERE {where_clause} AND FECHA_DE_INGRESO IS NOT NULL
            GROUP BY TO_CHAR(FECHA_DE_INGRESO, 'YYYY-MM')
            ORDER BY period
        '''
        cursor.execute(query, params)
        time_series = []
        for row in cursor.fetchall():
            period, count = row
            time_series.append(TimeSeriesData(
                period=period,
                count=_to_int(count)
            ))
        
        # Gender distribution
        query = f'''
            SELECT 
                CASE 
                    WHEN SEXO = 1 THEN 'Hombre'
                    WHEN SEXO = 2 THEN 'Mujer'
                    ELSE 'Desconocido'
                END as gender_label,
                COUNT(*) as cnt
            FROM SALUDMENTAL
            WHERE {where_clause}
            GROUP BY SEXO
            ORDER BY SEXO
        '''
        cursor.execute(query, params)
        gender_distribution = []
        for row in cursor.fetchall():
            gender_label, count = row
            gender_distribution.append(GenderDistribution(
                gender=gender_label,
                count=_to_int(count),
                percentage=round((_to_int(count) / total_records * 100), 2) if total_records > 0 else 0
            ))
        
        # Stay distribution
        query = f'''
            SELECT 
                CASE 
                    WHEN "Estancia Días" < 3 THEN '< 3 días'
                    WHEN "Estancia Días" BETWEEN 3 AND 7 THEN '3-7 días'
                    WHEN "Estancia Días" BETWEEN 8 AND 14 THEN '8-14 días'
                    WHEN "Estancia Días" BETWEEN 15 AND 30 THEN '15-30 días'
                    WHEN "Estancia Días" > 30 THEN '> 30 días'
                    ELSE 'Desconocido'
                END as stay_range,
                CASE 
                    WHEN "Estancia Días" < 3 THEN 1
                    WHEN "Estancia Días" BETWEEN 3 AND 7 THEN 2
                    WHEN "Estancia Días" BETWEEN 8 AND 14 THEN 3
                    WHEN "Estancia Días" BETWEEN 15 AND 30 THEN 4
                    WHEN "Estancia Días" > 30 THEN 5
                    ELSE 999
                END as sort_order,
                COUNT(*) as cnt
            FROM SALUDMENTAL
            WHERE {where_clause}
            GROUP BY 
                CASE 
                    WHEN "Estancia Días" < 3 THEN '< 3 días'
                    WHEN "Estancia Días" BETWEEN 3 AND 7 THEN '3-7 días'
                    WHEN "Estancia Días" BETWEEN 8 AND 14 THEN '8-14 días'
                    WHEN "Estancia Días" BETWEEN 15 AND 30 THEN '15-30 días'
                    WHEN "Estancia Días" > 30 THEN '> 30 días'
                    ELSE 'Desconocido'
                END,
                CASE 
                    WHEN "Estancia Días" < 3 THEN 1
                    WHEN "Estancia Días" BETWEEN 3 AND 7 THEN 2
                    WHEN "Estancia Días" BETWEEN 8 AND 14 THEN 3
                    WHEN "Estancia Días" BETWEEN 15 AND 30 THEN 4
                    WHEN "Estancia Días" > 30 THEN 5
                    ELSE 999
                END
            ORDER BY sort_order
        '''
        cursor.execute(query, params)
        stay_distribution = []
        for row in cursor.fetchall():
            stay_range, sort_order, count = row
            stay_distribution.append(StayDistribution(
                stay_range=stay_range,
                count=_to_int(count),
                percentage=round((_to_int(count) / total_records * 100), 2) if total_records > 0 else 0
            ))
        
        cursor.close()
        
        return DataVisualization(
            total_records=total_records,
            categories=categories,
            age_groups=age_groups,
            time_series=time_series,
            gender_distribution=gender_distribution,
            stay_distribution=stay_distribution,
            filters_applied=filters,
        )

