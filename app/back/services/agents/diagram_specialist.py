"""
Diagram Specialist Agent.

This agent specializes in generating Mermaid diagrams to visualize concepts,
relationships, and processes related to mental health data analysis.
"""

from typing import Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.back.config import config
from app.back.services.tools.mermaid_tool import MermaidTool

logger = logging.getLogger(__name__)


class DiagramSpecialistAgent:
    """
    Specialist agent for diagram generation.
    
    This agent:
    1. Interprets user's request for visualization
    2. Generates appropriate Mermaid diagram specification using LLM
    3. Returns the diagram code with a natural language description
    4. Focuses on clarity and educational value
    """
    
    def __init__(self):
        """
        Initializes the Diagram Specialist Agent.
        
        Side Effects:
            Initializes the LLM for diagram generation.
        
        Raises:
            ValueError: If XAI_API_KEY is not configured.
        """
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY required for Diagram Specialist Agent")
        
        # LLM for diagram generation and description
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            model="grok-4-fast-reasoning",
            temperature=0.4,  # Balanced for creative but accurate diagrams
            max_tokens=1200,
        )
        
        logger.info("Diagram Specialist Agent initialized")
    
    def execute(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a Mermaid diagram and description.
        
        Args:
            query (str): User's request for a diagram.
            state (Dict[str, Any]): Current agent state (from LangGraph).
        
        Returns:
            Dict[str, Any]: State update with diagram and description.
        """
        try:
            logger.info(f"Diagram Specialist executing query: {query}")
            
            # Step 1: Generate Mermaid diagram using LLM
            mermaid_code = self._generate_mermaid_diagram(query)
            
            logger.debug(f"Generated Mermaid code:\n{mermaid_code[:200]}...")
            
            # Step 2: Generate natural language description
            description = self._generate_diagram_description(query, mermaid_code)
            
            logger.info(f"Diagram Specialist description generated: {description[:100]}...")
            
            # Step 3: Return diagram + description
            summary = f"{description}\n\n{mermaid_code}"
            
            return {
                "specialist_summaries": [{
                    "specialist": "diagram_visualization",
                    "summary": summary,
                    "tool_used": "mermaid_diagram",
                    "has_code": True  # Flag to indicate diagram code is included
                }]
            }
            
        except Exception as e:
            error_msg = f"No se pudo generar el diagrama: {str(e)}"
            logger.error(f"Diagram Specialist error: {error_msg}")
            
            return {
                "specialist_summaries": [{
                    "specialist": "diagram_visualization",
                    "summary": error_msg,
                    "tool_used": "mermaid_diagram",
                    "error": True
                }]
            }
    
    def _generate_mermaid_diagram(self, query: str) -> str:
        """
        Generates Mermaid diagram syntax using LLM.
        
        This method uses the LLM to create contextually appropriate diagrams
        instead of relying on hardcoded templates.
        
        Args:
            query (str): User's diagram request.
        
        Returns:
            str: Mermaid diagram code.
        """
        system_prompt = """Eres un experto en visualización de datos y diagramas Mermaid.

Genera diagramas Mermaid de alta calidad basados en solicitudes de usuarios.

TIPOS DE DIAGRAMAS DISPONIBLES:
- flowchart: Diagramas de flujo (procesos, decisiones)
- sequenceDiagram: Diagramas de secuencia (interacciones temporales)
- classDiagram: Diagramas de clases (estructuras, relaciones)
- stateDiagram-v2: Diagramas de estados (transiciones)
- erDiagram: Diagramas entidad-relación (base de datos)
- gantt: Gráficos de Gantt (cronogramas)
- pie: Gráficos circulares (proporciones)
- journey: Mapas de viaje (experiencias de usuario)
- graph: Grafos genéricos (relaciones)

INSTRUCCIONES:
1. Elige el tipo de diagrama más apropiado para la solicitud
2. Genera sintaxis Mermaid válida y completa
3. Usa etiquetas claras y descriptivas en español
4. Aplica estilos cuando sea apropiado (colores, formas)
5. Para datos de salud mental, usa colores suaves y profesionales
6. Incluye suficiente detalle sin saturar el diagrama

ESTILOS RECOMENDADOS (Brain theme):
- Primary: #7C3AED (purple)
- Secondary: #A855F7
- Accent: #C4B5FD
- Dark: #0D0C1D
- Success: #10B981
- Warning: #F59E0B
- Error: #EF4444

Genera SOLO el código Mermaid, SIN markdown code blocks (```), sin explicaciones."""

        user_prompt = f"""Solicitud de diagrama: {query}

Genera el código Mermaid apropiado para visualizar esto."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        mermaid_code = response.content.strip()
        
        # Clean markdown code blocks if present
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
        
        # Wrap in code block for frontend rendering
        return f"```mermaid\n{mermaid_code}\n```"
    
    def _generate_diagram_description(self, query: str, mermaid_code: str) -> str:
        """
        Generates a natural language description of the diagram.
        
        Args:
            query (str): Original user request.
            mermaid_code (str): Generated Mermaid code.
        
        Returns:
            str: Natural language description (2-3 sentences).
        """
        system_prompt = """Eres un experto en explicar visualizaciones de datos.

Tu tarea es describir brevemente qué representa un diagrama Mermaid.

REGLAS:
- Explica QUÉ muestra el diagrama (no cómo está codificado)
- Sé conciso: 2-3 oraciones
- Usa lenguaje claro y profesional
- Destaca el valor o insight que aporta la visualización
- NO incluyas código Mermaid ni detalles técnicos

Ejemplo de BUENA descripción:
"Este diagrama de flujo ilustra el proceso de admisión hospitalaria, desde la llegada del paciente hasta el cierre del episodio. Muestra las etapas clave de evaluación, diagnóstico, tratamiento y alta, incluyendo puntos de decisión críticos."

Ejemplo de MALA descripción:
"El código Mermaid genera un flowchart TD con nodos A, B, C conectados..."

Describe el diagrama de forma clara y útil."""

        user_prompt = f"""Solicitud del usuario: {query}

Diagrama generado:
{mermaid_code}

Describe brevemente qué representa este diagrama."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            description = response.content.strip()
            
            logger.info(f"Diagram description generated: {len(description)} chars")
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating diagram description: {e}")
            # Fallback: simple description
            return "Diagrama generado para visualizar la información solicitada."

