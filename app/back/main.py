"""
FastAPI application for Oracle Cloud Autonomous Database integration.

This is the main application module that initializes FastAPI and manages
the database connection lifecycle.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.back.config import config
from app.back.db import (
    initialize_connection_pool,
    close_connection_pool,
    test_connection,
    get_pool_status,
    get_connection,
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


def _to_float(value: Optional[Any]) -> float:
    """Convert database numeric outputs into float numbers."""

    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def _to_int(value: Optional[Any]) -> int:
    """Convert database numeric outputs into integers."""

    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, (int, float)):
        return int(round(value))
    return int(str(value))


def _format_number(value: float, decimals: int = 0) -> str:
    """Format numbers using Spanish thousands/decimal separators."""

    if decimals == 0:
        formatted = format(int(round(value)), ",d") if value else "0"
        return formatted.replace(",", ".")
    formatted = format(value, f",.{decimals}f")
    integer_part, decimal_part = formatted.split(".")
    integer_part = integer_part.replace(",", ".")
    return f"{integer_part},{decimal_part}"


def _format_percentage(ratio: float, decimals: int = 1) -> str:
    """Format a ratio (0-1) as percentage string."""

    value = max(ratio, 0.0) * 100
    return f"{_format_number(value, decimals)}%"


def _build_sample_period(start: Optional[datetime], end: Optional[datetime]) -> str:
    """Create a compact label for the analysed period."""

    if not start or not end:
        return "Periodo no disponible"
    start_label = f"{start.year}-{start.month:02d}"
    end_label = f"{end.year}-{end.month:02d}"
    if start_label == end_label:
        return start_label
    return f"{start_label} a {end_label}"


def _build_insight_summary(database_connected: bool) -> InsightSummary:
    """Generate the insight summary by querying Oracle Autonomous Database."""

    generated_at = datetime.now(timezone.utc)

    with get_connection() as conn:
        cursor = conn.cursor()

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

        cursor.execute(
            '''
            SELECT MIN(FECHA_DE_INGRESO), MAX(FECHA_DE_INGRESO)
            FROM SALUDMENTAL
            WHERE FECHA_DE_INGRESO IS NOT NULL
            '''
        )
        period_start, period_end = cursor.fetchone()
        sample_period = _build_sample_period(period_start, period_end)

        cursor.execute(
            '''
            SELECT COUNT(DISTINCT "CIP_SNS_RECODIFICADO")
            FROM SALUDMENTAL
            WHERE "CIP_SNS_RECODIFICADO" IS NOT NULL
            '''
        )
        unique_patients = _to_int(cursor.fetchone()[0])

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

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM SALUDMENTAL
            WHERE SEXO = 2 AND EDAD BETWEEN 18 AND 29
            """
        )
        female_young = _to_int(cursor.fetchone()[0])

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM SALUDMENTAL
            WHERE SEXO = 1 AND EDAD >= 60
            """
        )
        male_senior = _to_int(cursor.fetchone()[0])

        cursor.execute(
            """
            SELECT AVG(EDAD)
            FROM SALUDMENTAL
            WHERE EDAD IS NOT NULL
            """
        )
        avg_age = _to_float(cursor.fetchone()[0])

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM SALUDMENTAL
            WHERE INGRESO_EN_UCI = 'S'
            """
        )
        icu_admissions = _to_int(cursor.fetchone()[0])

        cursor.execute(
            '''
            SELECT AVG("Estancia Días")
            FROM SALUDMENTAL
            WHERE REINGRESO = 'S' AND "Estancia Días" IS NOT NULL
            '''
        )
        avg_stay_readmissions = _to_float(cursor.fetchone()[0])

        cursor.close()

    female_share = (female_young / total_admissions) if total_admissions else 0.0
    male_senior_share = (male_senior / total_admissions) if total_admissions else 0.0
    readmission_rate = (readmissions / total_admissions) if total_admissions else 0.0
    top_category_share = (
        (top_category_count / total_admissions)
        if total_admissions and top_category_count
        else 0.0
    )

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
        database_connected=database_connected,
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
    Retrieve a curated summary of insights for the Brain landing page.
    
    The handler queries the Oracle Autonomous Database to compute aggregated
    metrics. If the connection fails, a fallback dataset keeps the UI usable.
    
    Returns:
        InsightSummary: Structured insight payload for the frontend.
    """

    database_status = False
    try:
        database_status = test_connection()
    except Exception:
        logger.warning("Oracle database not reachable for insights endpoint.")

    if database_status:
        try:
            return _build_insight_summary(database_status)
        except Exception as exc:
            logger.error("Failed to build insight summary from Oracle: %s", exc)

    logger.info("Serving fallback insight payload due to unavailable database.")
    generated_at = datetime.now(timezone.utc)
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
