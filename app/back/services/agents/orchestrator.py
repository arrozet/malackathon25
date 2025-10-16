"""
Orchestrator Agent.

This agent analyzes user queries and intelligently routes them to the appropriate
specialist agents. It can invoke multiple specialists when needed.
"""

from typing import Dict, Any, List
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.back.config import config

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrator agent for intelligent routing.
    
    This agent:
    1. Analyzes the user's query
    2. Determines which specialist agents to invoke
    3. Can invoke multiple specialists for complex queries
    4. Returns routing decisions for LangGraph to execute
    """
    
    def __init__(self):
        """
        Initializes the Orchestrator Agent.
        
        Side Effects:
            Initializes the LLM for query analysis.
        
        Raises:
            ValueError: If XAI_API_KEY is not configured.
        """
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY required for Orchestrator Agent")
        
        # LLM for query understanding and routing
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            model="grok-4-fast-reasoning",  
            temperature=0,  # Deterministic routing
            max_tokens=200,
        )
        
        logger.info("Orchestrator Agent initialized")
    
    def route(self, query: str, state: Dict[str, Any]) -> List[str]:
        """
        Analyzes query and determines which specialist(s) to invoke.
        
        Args:
            query (str): User's query.
            state (Dict[str, Any]): Current agent state (from LangGraph).
        
        Returns:
            List[str]: List of specialist agent names to invoke.
        """
        try:
            logger.info(f"Orchestrator analyzing query: {query}")
            
            # Use LLM to determine routing
            routing_decision = self._analyze_query(query)
            
            logger.info(f"Orchestrator routing to: {routing_decision}")
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            # Fallback: route to database specialist (most common)
            return ["sql_specialist"]
    
    def _analyze_query(self, query: str) -> List[str]:
        """
        Analyzes query using LLM to determine appropriate specialists.
        
        Args:
            query (str): User's query.
        
        Returns:
            List[str]: List of specialist names to invoke.
        """
        system_prompt = """Eres un agente experto en enrutamiento de consultas.

Tu tarea es analizar consultas de usuarios y determinar qué especialistas deben responderlas.

ESPECIALISTAS DISPONIBLES:
1. sql_specialist: Consultas sobre datos en la base de datos (estadísticas, conteos, tendencias, filtros)
2. search_specialist: Búsquedas de información médica/científica externa
3. python_specialist: Análisis estadísticos complejos, cálculos, correlaciones
4. diagram_specialist: Solicitudes de diagramas, visualizaciones, esquemas

REGLAS DE ENRUTAMIENTO:
- Puedes invocar MÚLTIPLES especialistas si la consulta es compleja
- sql_specialist: Palabras clave → cuántos, estadísticas, promedio, total, filtrar, episodios, pacientes, datos
- search_specialist: Palabras clave → busca, investiga, información sobre, qué es, últimas investigaciones
- python_specialist: Palabras clave → calcula, correlación, análisis estadístico, regresión, test
- diagram_specialist: Palabras clave → diagrama, gráfico, visualiza, esquema, flujo, proceso, muéstrame

FORMATO DE RESPUESTA:
Devuelve SOLO una lista separada por comas de los especialistas a invocar.

Ejemplos:
- "¿Cuántos pacientes hay?" → sql_specialist
- "Calcula la correlación entre edad y estancia" → sql_specialist,python_specialist
- "Busca información sobre esquizofrenia" → search_specialist
- "Muéstrame un diagrama del proceso de admisión" → diagram_specialist
- "¿Cuál es la prevalencia de depresión y qué dicen los estudios recientes?" → sql_specialist,search_specialist

Analiza la consulta y devuelve solo los nombres de los especialistas, separados por comas."""

        user_prompt = f"""Consulta del usuario: {query}

¿Qué especialistas deben manejar esta consulta?"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        routing_text = response.content.strip()
        
        # Parse response into list of specialist names
        specialists = [s.strip() for s in routing_text.split(",")]
        
        # Validate specialist names
        valid_specialists = ["sql_specialist", "search_specialist", "python_specialist", "diagram_specialist"]
        specialists = [s for s in specialists if s in valid_specialists]
        
        # Fallback if no valid specialists
        if not specialists:
            logger.warning(f"No valid specialists identified for query, defaulting to sql_specialist")
            specialists = ["sql_specialist"]
        
        return specialists

