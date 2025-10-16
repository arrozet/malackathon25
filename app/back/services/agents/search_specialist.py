"""
Search Specialist Agent.

This agent specializes in searching the internet for medical and mental health
information, filtering results, and summarizing relevant findings.
"""

from typing import Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.back.config import config
from app.back.services.tools.internet_search_tool import InternetSearchTool

logger = logging.getLogger(__name__)


class SearchSpecialistAgent:
    """
    Specialist agent for internet search.
    
    This agent:
    1. Uses InternetSearchTool to search the web
    2. Receives raw search results (URLs, snippets, sources)
    3. Filters and summarizes relevant findings
    4. Returns only the synthesized information (NO URLs, NO raw snippets)
    """
    
    def __init__(self):
        """
        Initializes the Search Specialist Agent.
        
        Side Effects:
            Initializes the LLM and Internet Search tool.
        
        Raises:
            ValueError: If XAI_API_KEY is not configured.
        """
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY required for Search Specialist Agent")
        
        # LLM for summarization
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            model="grok-4-fast-reasoning",
            temperature=0.4,  # Slightly more creative for synthesis
            max_tokens=400,
        )
        
        # Internet search tool
        self.tool = InternetSearchTool()
        
        logger.info("Search Specialist Agent initialized")
    
    def execute(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Searches the internet and returns a natural language summary.
        
        Args:
            query (str): User's search query.
            state (Dict[str, Any]): Current agent state (from LangGraph).
        
        Returns:
            Dict[str, Any]: State update with specialist summary.
        """
        try:
            logger.info(f"Search Specialist executing query: {query}")
            
            # Step 1: Search the internet using the tool
            raw_result = self.tool._run(query)
            
            logger.debug(f"Raw search result: {raw_result[:200]}...")
            
            # Step 2: Filter and summarize relevant findings
            summary = self._summarize_search_result(query, raw_result)
            
            logger.info(f"Search Specialist summary generated: {summary[:100]}...")
            
            # Step 3: Return ONLY the summary
            return {
                "specialist_summaries": [{
                    "specialist": "internet_search",
                    "summary": summary,
                    "tool_used": "internet_search"
                }]
            }
            
        except Exception as e:
            error_msg = f"No se pudo realizar la búsqueda: {str(e)}"
            logger.error(f"Search Specialist error: {error_msg}")
            
            return {
                "specialist_summaries": [{
                    "specialist": "internet_search",
                    "summary": error_msg,
                    "tool_used": "internet_search",
                    "error": True
                }]
            }
    
    def _summarize_search_result(self, query: str, raw_result: str) -> str:
        """
        Summarizes internet search results in natural language.
        
        This method filters raw search results (URLs, snippets, metadata) and
        extracts only the most relevant information, synthesized into clear prose.
        
        Args:
            query (str): Original user question.
            raw_result (str): Raw output from Internet Search tool.
        
        Returns:
            str: Natural language summary (3-4 sentences max).
        """
        system_prompt = """Eres un investigador médico experto en sintetizar información científica.

Tu tarea es resumir resultados de búsquedas de internet en lenguaje profesional y preciso.

REGLAS ESTRICTAS:
- NO incluyas URLs, fuentes, ni referencias técnicas
- NO copies snippets crudos de los resultados
- Sintetiza los HALLAZGOS clave en prosa fluida
- Enfócate en información médica/científica relevante
- Sé conciso: 3-4 oraciones máximo
- Si hay consenso científico, destácalo
- Si hay controversia, menciónalo objetivamente
- Si no hay información útil, dilo claramente

Ejemplo de BUENA respuesta:
"Los estudios recientes indican que la esquizofrenia afecta al 1% de la población mundial, con mayor prevalencia en hombres. El tratamiento de primera línea incluye antipsicóticos atípicos combinados con terapia cognitivo-conductual."

Ejemplo de MALA respuesta:
"Según Wikipedia (https://...), la esquizofrenia es un trastorno... [snippet copiado]"

Sintetiza la información encontrada de forma clara y profesional."""

        user_prompt = f"""Pregunta del usuario: {query}

Resultados de búsqueda:
{raw_result}

Sintetiza la información más relevante en lenguaje natural, omitiendo URLs y detalles técnicos."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            summary = response.content.strip()
            
            # Token savings log
            token_reduction = ((len(raw_result) - len(summary)) / len(raw_result)) * 100
            logger.info(f"Search result summarized: {len(raw_result)} → {len(summary)} chars ({token_reduction:.1f}% reduction)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing search result: {e}")
            # Fallback: return truncated raw result
            return f"Búsqueda completada. Información encontrada: {raw_result[:200]}..."

