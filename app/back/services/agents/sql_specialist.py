"""
SQL Specialist Agent.

This agent specializes in translating natural language to SQL, executing queries
against the Oracle database, and summarizing results in clear, natural language.
"""

from typing import Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.back.config import config
from app.back.services.tools.oracle_rag_tool import OracleRAGTool

logger = logging.getLogger(__name__)


class SQLSpecialistAgent:
    """
    Specialist agent for database queries.
    
    This agent:
    1. Uses OracleRAGTool to query the database
    2. Receives raw SQL results
    3. Summarizes findings in natural language (NO SQL, NO JSON)
    4. Returns only the summary to the synthesizer agent
    """
    
    def __init__(self):
        """
        Initializes the SQL Specialist Agent.
        
        Side Effects:
            Initializes the LLM and Oracle RAG tool.
        
        Raises:
            ValueError: If XAI_API_KEY is not configured.
        """
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY required for SQL Specialist Agent")
        
        # LLM for summarization
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            model="grok-4-fast-reasoning",
            temperature=0.3,
            max_tokens=400,
        )
        
        # Oracle RAG tool for database access
        self.tool = OracleRAGTool()
        
        logger.info("SQL Specialist Agent initialized")
    
    def execute(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a database query and returns a natural language summary.
        
        Args:
            query (str): User's natural language query.
            state (Dict[str, Any]): Current agent state (from LangGraph).
        
        Returns:
            Dict[str, Any]: State update with specialist summary.
        """
        try:
            logger.info(f"SQL Specialist executing query: {query}")
            
            # Step 1: Execute database query using the tool
            raw_result = self.tool._run(query)
            
            logger.debug(f"Raw database result: {raw_result[:200]}...")
            
            # Step 2: Summarize result using LLM
            summary = self._summarize_database_result(query, raw_result)
            
            logger.info(f"SQL Specialist summary generated: {summary[:100]}...")
            
            # Step 3: Return ONLY the summary
            return {
                "specialist_summaries": [{
                    "specialist": "database",
                    "summary": summary,
                    "tool_used": "oracle_database_query"
                }]
            }
            
        except Exception as e:
            error_msg = f"No se pudo consultar la base de datos: {str(e)}"
            logger.error(f"SQL Specialist error: {error_msg}")
            
            return {
                "specialist_summaries": [{
                    "specialist": "database",
                    "summary": error_msg,
                    "tool_used": "oracle_database_query",
                    "error": True
                }]
            }
    
    def _summarize_database_result(self, query: str, raw_result: str) -> str:
        """
        Summarizes database query results in natural language.
        
        This method converts technical outputs (SQL, JSON, tables) into
        clean, actionable summaries that focus on WHAT was found, not HOW.
        
        Args:
            query (str): Original user question.
            raw_result (str): Raw output from Oracle RAG tool.
        
        Returns:
            str: Natural language summary (2-3 sentences).
        """
        system_prompt = """Eres un analista de datos experto en salud mental.

Tu tarea es resumir resultados de consultas de base de datos en lenguaje natural claro y profesional.

REGLAS ESTRICTAS:
- NO menciones SQL, queries, ni detalles técnicos
- NO incluyas JSON, tablas formateadas, ni código
- Enfócate en QUÉ se encontró (números, tendencias, patrones)
- Usa lenguaje natural y estadístico apropiado
- Sé conciso: 2-3 oraciones máximo
- Si hay números, redondéalos apropiadamente
- Si es un error, explica qué falló en términos simples

Ejemplo de BUENA respuesta:
"Se encontraron 15,234 pacientes masculinos en la base de datos, representando el 48.2% del total de episodios."

Ejemplo de MALA respuesta:
"La query SQL 'SELECT COUNT(*) FROM...' retornó [{'COUNT(*)': 15234}]"

Resume los hallazgos de forma clara y profesional."""

        user_prompt = f"""Pregunta del usuario: {query}

Resultado de la consulta:
{raw_result}

Resume estos hallazgos en lenguaje natural, omitiendo todo detalle técnico."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            summary = response.content.strip()
            
            # Token savings log
            token_reduction = ((len(raw_result) - len(summary)) / len(raw_result)) * 100
            logger.info(f"Database result summarized: {len(raw_result)} → {len(summary)} chars ({token_reduction:.1f}% reduction)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing database result: {e}")
            # Fallback: return truncated raw result
            return f"Consulta ejecutada. Resultados: {raw_result[:200]}..."

