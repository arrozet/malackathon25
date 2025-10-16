"""
Insights Service - Microservice for generating analytical insights.

This service handles all logic related to computing and delivering
insight summaries for the Brain application.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
import logging

from app.back.db import get_connection, test_connection
from app.back.schemas import InsightSummary

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


def _format_number(value: float, decimals: int = 0) -> str:
    """
    Format numbers using Spanish thousands/decimal separators.
    
    Args:
        value (float): Number to format.
        decimals (int): Number of decimal places. Default is 0.
    
    Returns:
        str: Formatted number string.
    """
    if decimals == 0:
        formatted = format(int(round(value)), ",d") if value else "0"
        return formatted.replace(",", ".")
    formatted = format(value, f",.{decimals}f")
    integer_part, decimal_part = formatted.split(".")
    integer_part = integer_part.replace(",", ".")
    return f"{integer_part},{decimal_part}"


def _format_percentage(ratio: float, decimals: int = 1) -> str:
    """
    Format a ratio (0-1) as percentage string.
    
    Args:
        ratio (float): Ratio value between 0 and 1.
        decimals (int): Number of decimal places. Default is 1.
    
    Returns:
        str: Formatted percentage string.
    """
    value = max(ratio, 0.0) * 100
    return f"{_format_number(value, decimals)}%"


def _build_sample_period(start: Optional[datetime], end: Optional[datetime]) -> str:
    """
    Create a compact label for the analysed period.
    
    Args:
        start (datetime, optional): Start date of the period.
        end (datetime, optional): End date of the period.
    
    Returns:
        str: Formatted period string.
    """
    if not start or not end:
        return "Periodo no disponible"
    start_label = f"{start.year}-{start.month:02d}"
    end_label = f"{end.year}-{end.month:02d}"
    if start_label == end_label:
        return start_label
    return f"{start_label} a {end_label}"


def build_insight_summary() -> InsightSummary:
    """
    Generate comprehensive insight summary by querying Oracle Autonomous Database.
    
    This method orchestrates all analytical queries and produces a structured
    summary of mental health admission insights for the Brain dashboard.
    
    Returns:
        InsightSummary: Complete insight payload with metrics and highlights.
    
    Raises:
        Exception: If database queries fail.
    """
    generated_at = datetime.now(timezone.utc)
    database_connected = test_connection()

    if not database_connected:
        logger.warning("Database not available, returning fallback insights")
        return _get_fallback_insights(generated_at)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # Query: Total admissions, average stay, readmissions
            cursor.execute(
                '''
                SELECT 
                    COUNT(*) AS total_admissions,
                    AVG("Estancia Días") AS avg_stay,
                    SUM(CASE WHEN REINGRESO = 'S' THEN 1 ELSE 0 END) AS readmissions
                FROM SALUDMENTAL
                '''
            )
            total_admissions_raw, avg_stay_raw, readmissions_raw = cursor.fetchone()
            total_admissions = _to_int(total_admissions_raw)
            avg_stay = _to_float(avg_stay_raw)
            readmissions = _to_int(readmissions_raw)

            # Query: Date range
            cursor.execute(
                '''
                SELECT MIN(FECHA_DE_INGRESO), MAX(FECHA_DE_INGRESO)
                FROM SALUDMENTAL
                WHERE FECHA_DE_INGRESO IS NOT NULL
                '''
            )
            period_start, period_end = cursor.fetchone()
            sample_period = _build_sample_period(period_start, period_end)

            # Query: Unique patients
            cursor.execute(
                '''
                SELECT COUNT(DISTINCT "CIP_SNS_RECODIFICADO")
                FROM SALUDMENTAL
                WHERE "CIP_SNS_RECODIFICADO" IS NOT NULL
                '''
            )
            unique_patients = _to_int(cursor.fetchone()[0])

            # Query: Top category
            cursor.execute(
                '''
                SELECT "Categoría", COUNT(*)
                FROM SALUDMENTAL
                WHERE "Categoría" IS NOT NULL
                GROUP BY "Categoría"
                ORDER BY COUNT(*) DESC
                FETCH FIRST 1 ROWS ONLY
                '''
            )
            top_category_row = cursor.fetchone()
            top_category = top_category_row[0] if top_category_row else None
            top_category_count = _to_int(top_category_row[1]) if top_category_row else 0

            # Query: Female young adults
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM SALUDMENTAL
                WHERE SEXO = 2 AND EDAD BETWEEN 18 AND 29
                """
            )
            female_young = _to_int(cursor.fetchone()[0])

            # Query: Male seniors
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM SALUDMENTAL
                WHERE SEXO = 1 AND EDAD >= 60
                """
            )
            male_senior = _to_int(cursor.fetchone()[0])

            # Query: Average age
            cursor.execute(
                """
                SELECT AVG(EDAD)
                FROM SALUDMENTAL
                WHERE EDAD IS NOT NULL
                """
            )
            avg_age = _to_float(cursor.fetchone()[0])

            # Query: ICU admissions
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM SALUDMENTAL
                WHERE INGRESO_EN_UCI = 'S'
                """
            )
            icu_admissions = _to_int(cursor.fetchone()[0])

            # Query: Average stay for readmissions
            cursor.execute(
                '''
                SELECT AVG("Estancia Días")
                FROM SALUDMENTAL
                WHERE REINGRESO = 'S' AND "Estancia Días" IS NOT NULL
                '''
            )
            avg_stay_readmissions = _to_float(cursor.fetchone()[0])

            cursor.close()

        # Calculate derived metrics
        female_share = (female_young / total_admissions) if total_admissions else 0.0
        male_senior_share = (male_senior / total_admissions) if total_admissions else 0.0
        readmission_rate = (readmissions / total_admissions) if total_admissions else 0.0
        top_category_share = (
            (top_category_count / total_admissions)
            if total_admissions and top_category_count
            else 0.0
        )

        # Build highlight phrases
        if total_admissions == 0:
            highlight_phrases = [
                "Sin registros disponibles en la tabla SALUDMENTAL.",
            ]
        else:
            highlight_phrases = [
                f"{_format_number(total_admissions)} admisiones registradas entre {sample_period}",
                (
                    f"{top_category} concentra {_format_percentage(top_category_share)} de los diagnósticos"
                    if top_category
                    else f"{_format_percentage(readmission_rate)} de los casos termina en reingreso"
                ),
                f"{_format_percentage(female_share)} de los ingresos corresponde a mujeres de 18-29 años",
            ]

        # Build metric sections
        metric_sections = [
            {
                "title": "Panorama general",
                "metrics": [
                    {
                        "title": "Admisiones totales",
                        "value": _format_number(total_admissions),
                        "description": (
                            f"Periodo analizado: {sample_period}. "
                            f"Principal categoría: {top_category or 'sin datos'}."
                        ),
                    },
                    {
                        "title": "Estancia media",
                        "value": f"{_format_number(avg_stay, 1)} días",
                        "description": "Promedio calculado sobre ingresos con estancia registrada.",
                    },
                    {
                        "title": "Pacientes únicos",
                        "value": _format_number(unique_patients),
                        "description": "Identificadores sanitarios distintos presentes en el periodo.",
                    },
                ],
            },
            {
                "title": "Perspectiva por género y edad",
                "metrics": [
                    {
                        "title": "Mujeres 18-29 años",
                        "value": _format_number(female_young),
                        "description": (
                            f"Equivalen a {_format_percentage(female_share)} del total de admisiones."
                        ),
                    },
                    {
                        "title": "Varones ≥60 años",
                        "value": _format_number(male_senior),
                        "description": (
                            f"Representan {_format_percentage(male_senior_share)} de los ingresos."
                        ),
                    },
                    {
                        "title": "Edad media al ingreso",
                        "value": f"{_format_number(avg_age, 1)} años",
                        "description": "Edad promedio considerando registros con dato disponible.",
                    },
                ],
            },
            {
                "title": "Factores de riesgo a vigilar",
                "metrics": [
                    {
                        "title": "Readmisiones registradas",
                        "value": _format_number(readmissions),
                        "description": (
                            f"Impactan a {_format_percentage(readmission_rate)} del total de ingresos."
                        ),
                    },
                    {
                        "title": "Ingresos en UCI",
                        "value": _format_number(icu_admissions),
                        "description": "Casos que requirieron cuidados intensivos durante el contacto.",
                    },
                    {
                        "title": "Estancia media reingresados",
                        "value": (
                            f"{_format_number(avg_stay_readmissions, 1)} días"
                            if readmissions
                            else "–"
                        ),
                        "description": (
                            "Promedio de estancia para quienes reingresaron."
                            if readmissions
                            else "Sin reingresos registrados con estancia disponible."
                        ),
                    },
                ],
            },
        ]

        return InsightSummary(
            generated_at=generated_at,
            sample_period=sample_period,
            highlight_phrases=highlight_phrases,
            metric_sections=metric_sections,
            database_connected=True,
        )

    except Exception as exc:
        logger.error("Failed to build insight summary from Oracle: %s", exc)
        return _get_fallback_insights(generated_at)


def _get_fallback_insights(generated_at: datetime) -> InsightSummary:
    """
    Generate fallback insights when database is unavailable.
    
    Args:
        generated_at (datetime): Timestamp for the insight generation.
    
    Returns:
        InsightSummary: Fallback insight payload.
    """
    return InsightSummary(
        generated_at=generated_at,
        sample_period="Datos no disponibles",
        highlight_phrases=[
            "No se pudo consultar la base de datos en este momento.",
            "Mostrando cifras estáticas para mantener la experiencia demo.",
        ],
        metric_sections=[
            {
                "title": "Servicio temporal",
                "metrics": [
                    {
                        "title": "Backend en modo degradado",
                        "value": "–",
                        "description": "Verifica credenciales, wallet y conectividad con Oracle Autonomous Database.",
                    },
                    {
                        "title": "Paso siguiente",
                        "value": "Reintentar",
                        "description": "Reinicia el backend tras corregir la configuración o vuelve a cargar la página en unos segundos.",
                    },
                    {
                        "title": "Soporte",
                        "value": "Equipo Malackathon",
                        "description": "Reporta el incidente en el canal del equipo para recibir ayuda rápida.",
                    },
                ],
            }
        ],
        database_connected=False,
    )

