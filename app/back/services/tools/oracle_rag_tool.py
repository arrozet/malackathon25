"""
Oracle RAG (Retrieval-Augmented Generation) Tool.

This tool provides semantic search and retrieval capabilities over the Oracle database,
enabling the AI to query mental health admission data and generate insights.
"""

from typing import Optional, Dict, Any, List
import logging
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import Field

from app.back.db import get_connection
from app.back.config import config

logger = logging.getLogger(__name__)


class OracleRAGTool(BaseTool):
    """
    Tool for querying Oracle database with natural language.
    
    This tool uses an LLM to translate natural language queries into SQL dynamically,
    executes them, and returns formatted results for the AI to interpret.
    """
    
    name: str = "oracle_database_query"
    description: str = """
    Consulta la base de datos Oracle de hospitalizaciones de salud mental.
    Útil para obtener estadísticas, tendencias, y métricas sobre episodios.
    
    Input: Una pregunta en lenguaje natural sobre los datos (ej: "¿Cuántos episodios hay en 2023?")
    Output: Resultados de la consulta SQL formateados como texto.
    
    Tabla disponible:
    - SALUDMENTAL: Tabla principal con datos de episodios de hospitalización
    
    Campos principales:
    - FECHA_DE_INGRESO (DATE): Fecha de ingreso del paciente
    - EDAD (NUMBER): Edad del paciente
    - SEXO (NUMBER): Género (1=Hombre, 2=Mujer)
    - "Categoría" (VARCHAR2): Categoría diagnóstica
    - Estancia (NUMBER): Duración de la hospitalización en días
    """
    
    def _get_llm(self):
        """
        Lazy initialization of LLM for SQL generation.
        
        Returns:
            ChatOpenAI or None: LLM instance if API key is configured.
        """
        if not hasattr(self, '_llm_instance'):
            if config.XAI_API_KEY:
                self._llm_instance = ChatOpenAI(
                    api_key=config.XAI_API_KEY,
                    base_url="https://api.x.ai/v1",
                    model="grok-4-fast-reasoning",
                    temperature=0,  # Deterministic SQL generation
                    max_tokens=500,
                )
            else:
                self._llm_instance = None
                logger.warning("XAI_API_KEY not configured - SQL generation will use heuristics")
        return self._llm_instance
    
    def _run(self, query: str) -> str:
        """
        Executes a natural language query against the Oracle database.
        
        Args:
            query (str): Natural language question about the data.
        
        Returns:
            str: Formatted results from the database query.
        
        Side Effects:
            Queries the Oracle database.
        """
        try:
            # Convert natural language to SQL (simple heuristic-based approach)
            sql_query = self._translate_to_sql(query)
            
            logger.info(f"Executing SQL query: {sql_query}")
            
            # Execute query
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_query)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch results
                results = cursor.fetchall()
                cursor.close()
                
                # Format results
                formatted_results = self._format_results(columns, results)
                
                logger.info(f"Query returned {len(results)} rows")
                return formatted_results
                
        except Exception as e:
            error_msg = f"Error ejecutando consulta en la base de datos: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, query: str) -> str:
        """
        Async version of _run (delegates to sync version).
        
        Args:
            query (str): Natural language question about the data.
        
        Returns:
            str: Formatted results from the database query.
        """
        return self._run(query)
    
    def _get_schema_info(self) -> str:
        """
        Gets schema information for the SALUDMENTAL table.
        
        Returns:
            str: Schema description for SQL generation.
        """
        return """
TABLA: SALUDMENTAL

COLUMNAS:
- FECHA_DE_INGRESO (DATE): Fecha de ingreso del paciente
- EDAD (NUMBER): Edad del paciente en años
- SEXO (NUMBER): Género del paciente (1 = Hombre/Masculino, 2 = Mujer/Femenino)
- "Categoría" (VARCHAR2): Categoría diagnóstica (USAR COMILLAS DOBLES en la query)
- Estancia (NUMBER): Duración de la hospitalización en días

NOTAS IMPORTANTES:
- El campo "Categoría" DEBE ir entre comillas dobles: "Categoría"
- Para filtrar por año: EXTRACT(YEAR FROM FECHA_DE_INGRESO) = 2023
- Para agrupar por mes: TO_CHAR(FECHA_DE_INGRESO, 'YYYY-MM')
- SEXO: 1 = Hombre, 2 = Mujer
- Usar FETCH FIRST N ROWS ONLY para limitar resultados (no LIMIT)
"""
    
    def _translate_to_sql(self, query: str) -> str:
        """
        Translates natural language query to SQL using LLM.
        
        Args:
            query (str): Natural language query.
        
        Returns:
            str: SQL query string.
        """
        # If LLM is available, use it for dynamic SQL generation
        llm = self._get_llm()
        if llm:
            try:
                system_prompt = f"""Eres un experto en SQL para Oracle Database.

{self._get_schema_info()}

INSTRUCCIONES:
1. Genera SOLO la query SQL, sin explicaciones
2. NO incluyas punto y coma al final
3. Usa sintaxis Oracle (FETCH FIRST en lugar de LIMIT)
4. Siempre usa comillas dobles para "Categoría"
5. Para agregaciones, usa alias claros
6. La query debe ser segura (no DELETE, DROP, UPDATE, etc.)

Genera la query SQL para la siguiente pregunta:"""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=query)
                ]
                
                response = llm.invoke(messages)
                sql_query = response.content.strip()
                
                # Clean up response (remove markdown, semicolons, etc.)
                sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
                if sql_query.endswith(";"):
                    sql_query = sql_query[:-1].strip()
                
                logger.info(f"Generated SQL using LLM: {sql_query}")
                return sql_query
                
            except Exception as e:
                logger.warning(f"Error generating SQL with LLM: {e}. Falling back to heuristics.")
        
        # Fallback to heuristic-based generation if LLM fails or not available
        query_lower = query.lower()
        
        # Common query patterns for mental health data
        
        # Count episodes by specific gender
        if any(word in query_lower for word in ["hombres", "masculino", "varones", "sexo=1", "sexo 1"]):
            return """
                SELECT COUNT(*) as total_hombres
                FROM SALUDMENTAL
                WHERE SEXO = 1
            """
        
        if any(word in query_lower for word in ["mujeres", "femenino", "sexo=2", "sexo 2"]):
            return """
                SELECT COUNT(*) as total_mujeres
                FROM SALUDMENTAL
                WHERE SEXO = 2
            """
        
        # Count total episodes
        if "cuántos episodios" in query_lower or "total de episodios" in query_lower or "cuántos registros" in query_lower:
            if "2023" in query_lower:
                return """
                    SELECT COUNT(*) as total_episodios
                    FROM SALUDMENTAL
                    WHERE EXTRACT(YEAR FROM FECHA_DE_INGRESO) = 2023
                """
            elif "2024" in query_lower:
                return """
                    SELECT COUNT(*) as total_episodios
                    FROM SALUDMENTAL
                    WHERE EXTRACT(YEAR FROM FECHA_DE_INGRESO) = 2024
                """
            else:
                return "SELECT COUNT(*) as total_episodios FROM SALUDMENTAL"
        
        # Average stay duration
        if "estancia promedio" in query_lower or "duración promedio" in query_lower:
            return """
                SELECT 
                    ROUND(AVG(Estancia), 2) as estancia_promedio_dias,
                    ROUND(MIN(Estancia), 2) as estancia_minima,
                    ROUND(MAX(Estancia), 2) as estancia_maxima
                FROM SALUDMENTAL
                WHERE Estancia IS NOT NULL
            """
        
        # Top categories
        if "categorías más frecuentes" in query_lower or "top categorías" in query_lower:
            return """
                SELECT "Categoría", COUNT(*) as total_episodios
                FROM SALUDMENTAL
                WHERE "Categoría" IS NOT NULL
                GROUP BY "Categoría"
                ORDER BY total_episodios DESC
                FETCH FIRST 10 ROWS ONLY
            """
        
        # Episodes by gender
        if "por sexo" in query_lower or "por género" in query_lower:
            return """
                SELECT 
                    CASE SEXO
                        WHEN 1 THEN 'Hombre'
                        WHEN 2 THEN 'Mujer'
                        ELSE 'Desconocido'
                    END as genero,
                    COUNT(*) as total_episodios,
                    ROUND(AVG(Estancia), 2) as estancia_promedio
                FROM SALUDMENTAL
                WHERE SEXO IS NOT NULL
                GROUP BY SEXO
                ORDER BY total_episodios DESC
            """
        
        # Episodes by age group
        if "por edad" in query_lower or "grupo etario" in query_lower or "distribución edad" in query_lower:
            return """
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
                    END as grupo_edad,
                    COUNT(*) as total_episodios,
                    ROUND(AVG(Estancia), 2) as estancia_promedio
                FROM SALUDMENTAL
                WHERE EDAD IS NOT NULL
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
                    END
                ORDER BY 
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
            """
        
        # Temporal trends
        if "evolución temporal" in query_lower or "tendencia" in query_lower or "por mes" in query_lower:
            return """
                SELECT 
                    TO_CHAR(FECHA_DE_INGRESO, 'YYYY-MM') as periodo,
                    COUNT(*) as total_episodios
                FROM SALUDMENTAL
                WHERE FECHA_DE_INGRESO IS NOT NULL
                GROUP BY TO_CHAR(FECHA_DE_INGRESO, 'YYYY-MM')
                ORDER BY periodo DESC
                FETCH FIRST 12 ROWS ONLY
            """
        
        # Schema information
        if "esquema" in query_lower or "tablas" in query_lower or "estructura" in query_lower or "columnas" in query_lower:
            return """
                SELECT column_name, data_type
                FROM user_tab_columns
                WHERE table_name = 'SALUDMENTAL'
                ORDER BY column_id
            """
        
        # Default: count episodes
        return "SELECT COUNT(*) as total_episodios FROM SALUDMENTAL"
    
    def _format_results(self, columns: List[str], results: List[tuple]) -> str:
        """
        Formats query results as a readable string.
        
        Args:
            columns (List[str]): Column names from the query.
            results (List[tuple]): Query result rows.
        
        Returns:
            str: Formatted results as text.
        """
        if not results:
            return "No se encontraron resultados."
        
        # Create header
        output = []
        output.append(" | ".join(columns))
        output.append("-" * (sum(len(col) for col in columns) + len(columns) * 3))
        
        # Add rows (limit to 50 for readability)
        for row in results[:50]:
            formatted_row = []
            for value in row:
                if value is None:
                    formatted_row.append("NULL")
                elif isinstance(value, float):
                    formatted_row.append(f"{value:.2f}")
                else:
                    formatted_row.append(str(value))
            output.append(" | ".join(formatted_row))
        
        if len(results) > 50:
            output.append(f"\n... ({len(results) - 50} filas más omitidas)")
        
        output.append(f"\nTotal de filas: {len(results)}")
        
        return "\n".join(output)

