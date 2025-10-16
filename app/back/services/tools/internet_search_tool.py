"""
Internet Search Tool using Tavily API.

This tool enables the AI to search the internet for up-to-date information
about mental health topics, medical research, and healthcare trends.
"""

from typing import Optional
import logging
from langchain_core.tools import BaseTool
from pydantic import Field

from app.back.config import config

logger = logging.getLogger(__name__)


class InternetSearchTool(BaseTool):
    """
    Tool for searching the internet using Tavily API.
    
    This tool allows the AI to retrieve current information about mental health,
    medical research, healthcare policies, and related topics.
    """
    
    name: str = "internet_search"
    description: str = """
    Busca información actualizada en internet sobre temas de salud mental, investigación médica,
    políticas de salud, y temas relacionados.
    
    Input: Una consulta de búsqueda en lenguaje natural (ej: "últimas investigaciones sobre depresión")
    Output: Resultados de búsqueda con títulos, snippets y URLs.
    
    Útil para:
    - Obtener información actualizada sobre tratamientos
    - Buscar estudios científicos recientes
    - Consultar políticas de salud pública
    - Obtener contexto sobre diagnósticos CIE-10
    """
    
    def _run(self, query: str) -> str:
        """
        Executes an internet search using Tavily API.
        
        Args:
            query (str): Search query in natural language.
        
        Returns:
            str: Formatted search results with titles, snippets, and URLs.
        
        Side Effects:
            Makes API call to Tavily search service.
        """
        try:
            # Import here to avoid dependency issues if Tavily not configured
            from tavily import TavilyClient
            
            # Get API key from centralized config
            if not config.TAVILY_API_KEY:
                return "Error: TAVILY_API_KEY no configurada. Añade TAVILY_API_KEY=tu_key en el archivo .env para usar búsqueda en internet."
            
            # Initialize client
            client = TavilyClient(api_key=config.TAVILY_API_KEY)
            
            logger.info(f"Searching internet for: {query}")
            
            # Execute search
            results = client.search(
                query=query,
                search_depth="basic",  # "basic" or "advanced"
                max_results=5,
                include_answer=True,
                include_raw_content=False,
            )
            
            # Format results
            output = []
            
            # Add summary answer if available
            if results.get("answer"):
                output.append(f"**Resumen:**\n{results['answer']}\n")
            
            # Add search results
            output.append("**Resultados de búsqueda:**\n")
            
            for idx, result in enumerate(results.get("results", []), 1):
                title = result.get("title", "Sin título")
                url = result.get("url", "")
                content = result.get("content", "")
                
                output.append(f"{idx}. **{title}**")
                output.append(f"   URL: {url}")
                output.append(f"   {content[:300]}...")
                output.append("")
            
            formatted_output = "\n".join(output)
            logger.info(f"Internet search returned {len(results.get('results', []))} results")
            
            return formatted_output
            
        except ImportError:
            error_msg = "Error: Tavily no está instalado. Ejecuta: pip install tavily-python"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error ejecutando búsqueda en internet: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, query: str) -> str:
        """
        Async version of _run (delegates to sync version).
        
        Args:
            query (str): Search query in natural language.
        
        Returns:
            str: Formatted search results.
        """
        return self._run(query)

