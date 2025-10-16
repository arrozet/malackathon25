"""
Synthesizer Agent.

This agent receives summaries from specialist agents and synthesizes them into
a coherent, professional final response for the user.
"""

from typing import Dict, Any, List
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.back.config import config

logger = logging.getLogger(__name__)


class SynthesizerAgent:
    """
    Synthesizer agent for final response generation.
    
    This agent:
    1. Receives ONLY natural language summaries from specialists
    2. Never sees SQL, JSON, code, or technical details
    3. Integrates multiple summaries into a coherent response
    4. Maintains conversation context and tone
    5. Generates professional, researcher-friendly output
    """
    
    def __init__(self):
        """
        Initializes the Synthesizer Agent.
        
        Side Effects:
            Initializes the LLM for response synthesis.
        
        Raises:
            ValueError: If XAI_API_KEY is not configured.
        """
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY required for Synthesizer Agent")
        
        # LLM for final response synthesis
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            model="grok-4-fast-reasoning",
            temperature=0.5,  # Balanced creativity for natural responses
            max_tokens=1000,
        )
        
        logger.info("Synthesizer Agent initialized")
    
    def synthesize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes specialist summaries into final response.
        
        Args:
            state (Dict[str, Any]): Agent state containing:
                - user_query: Original user question
                - specialist_summaries: List of summaries from specialists
                - chat_history: Previous conversation messages (optional)
        
        Returns:
            Dict[str, Any]: State update with final_response.
        """
        try:
            user_query = state.get("user_query", "")
            summaries = state.get("specialist_summaries", [])
            chat_history = state.get("chat_history", [])
            
            logger.info(f"Synthesizer generating response for: {user_query}")
            logger.info(f"Received {len(summaries)} specialist summaries")
            
            # Generate final response
            final_response = self._generate_response(user_query, summaries, chat_history)
            
            # Extract tool information
            tools_used = [s.get("tool_used") for s in summaries if "tool_used" in s]
            has_errors = any(s.get("error", False) for s in summaries)
            
            logger.info(f"Synthesizer response generated: {len(final_response)} chars")
            
            return {
                "final_response": final_response,
                "tools_used": tools_used,
                "has_errors": has_errors,
                "specialist_count": len(summaries)
            }
            
        except Exception as e:
            error_msg = f"Error al generar la respuesta: {str(e)}"
            logger.error(f"Synthesizer error: {error_msg}")
            
            return {
                "final_response": error_msg,
                "tools_used": [],
                "has_errors": True
            }
    
    def _generate_response(
        self,
        user_query: str,
        summaries: List[Dict[str, Any]],
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Generates the final synthesized response.
        
        Args:
            user_query (str): Original user question.
            summaries (List[Dict]): Summaries from specialist agents.
            chat_history (List[Dict]): Previous conversation messages.
        
        Returns:
            str: Final response to the user.
        """
        # Format specialist summaries
        formatted_summaries = self._format_summaries(summaries)
        
        # Format chat history
        formatted_history = self._format_chat_history(chat_history)
        
        system_prompt = """Eres "Brain", un asistente de IA experto en análisis de datos de salud mental.

Tu objetivo es proporcionar respuestas claras, profesionales, y útiles a investigadores médicos.

PRINCIPIOS:
1. **Claridad**: Usa lenguaje profesional pero accesible
2. **Precisión**: Basa tus respuestas SOLO en la información proporcionada por los especialistas
3. **Contexto**: Integra múltiples fuentes de información de forma coherente
4. **Honestidad**: Si hay errores o limitaciones, comunícalos claramente
5. **Valor**: Destaca insights accionables y patrones relevantes

FORMATO DE RESPUESTA OBLIGATORIO - USA MARKDOWN RICO:

1. **Respuesta directa**: Comienza con un párrafo respondiendo la pregunta principal

2. **Datos clave**: Si hay estadísticas o números, usa **negritas** para destacarlos
   - Ejemplo: "Se encontraron **1,234 episodios** en el periodo analizado"

3. **Listas**: Cuando presentes múltiples puntos, usa listas con viñetas:
   - Punto 1
   - Punto 2
   - Punto 3

4. **Secciones**: Si la respuesta es larga, organiza con subtítulos markdown:
   ### Análisis Principal
   Contenido...
   
   ### Hallazgos Adicionales
   Contenido...

5. **Énfasis**: Usa **negritas** para conceptos importantes y *cursivas* para matices

6. **Referencias**: Si usas información de búsquedas en internet, SIEMPRE incluye una sección al final:
   
   ---
   
   **Referencias:**
   - [Título del artículo](URL)
   - [Otro recurso](URL)

7. **Diagramas**: Si generas código Mermaid, usa bloques de código con el lenguaje especificado:
   
   ```mermaid
   flowchart TD
       A[Inicio] --> B[Fin]
   ```

8. **Tablas**: Si presentas comparaciones, usa tablas markdown:
   
   | Categoría | Valor |
   |-----------|-------|
   | A         | 100   |
   | B         | 200   |

TONO:
- Profesional pero cálido
- Confiado pero no dogmático
- Educativo pero no condescendiente
- Científico pero no excesivamente técnico

NO HAGAS:
- NO inventes información que no esté en los resúmenes
- NO menciones "los especialistas dijeron" o "según el agente SQL"
- NO uses jerga técnica de programación (SQL, JSON, APIs)
- NO seas repetitivo con los resúmenes recibidos
- NO olvides usar markdown para formatear tu respuesta

IMPORTANTE: Tu respuesta DEBE usar markdown. El usuario verá tu respuesta renderizada con formato rico."""

        user_prompt = f"""Pregunta del usuario: {user_query}

{formatted_history}

Información recopilada por especialistas:
{formatted_summaries}

INSTRUCCIONES IMPORTANTES:
1. Genera una respuesta completa e integrada usando MARKDOWN RICO
2. Si la información incluye referencias o fuentes (especialmente de búsquedas en internet), INCLÚYELAS al final de tu respuesta
3. Usa **negritas** para destacar datos clave y estadísticas
4. Organiza con listas y subtítulos cuando sea apropiado
5. Si hay código Mermaid para diagramas, inclúyelo en bloques ```mermaid

Genera tu respuesta ahora."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        final_response = response.content.strip()
        
        # Log token usage for analytics
        total_summary_length = sum(len(s.get("summary", "")) for s in summaries)
        logger.info(f"Synthesized {total_summary_length} chars of summaries into {len(final_response)} chars response")
        
        return final_response
    
    def _format_summaries(self, summaries: List[Dict[str, Any]]) -> str:
        """
        Formats specialist summaries for the synthesis prompt.
        
        Args:
            summaries (List[Dict]): Summaries from specialists.
        
        Returns:
            str: Formatted summaries text.
        """
        if not summaries:
            return "No se recopiló información de los especialistas."
        
        formatted = []
        for i, summary_data in enumerate(summaries, 1):
            specialist = summary_data.get("specialist", "unknown")
            summary = summary_data.get("summary", "Sin información")
            error = summary_data.get("error", False)
            
            # Map specialist names to friendly labels
            specialist_labels = {
                "database": "Análisis de Base de Datos",
                "internet_search": "Búsqueda de Información Externa",
                "python_analysis": "Análisis Estadístico",
                "diagram_visualization": "Visualización"
            }
            
            label = specialist_labels.get(specialist, specialist.replace("_", " ").title())
            
            if error:
                formatted.append(f"**{label}**: ⚠️ {summary}")
            else:
                formatted.append(f"**{label}**: {summary}")
        
        return "\n\n".join(formatted)
    
    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        """
        Formats chat history for context.
        
        Args:
            chat_history (List[Dict]): Previous messages.
        
        Returns:
            str: Formatted history text.
        """
        if not chat_history:
            return ""
        
        formatted = ["Contexto de conversación anterior:"]
        
        # Only include last 3 exchanges to avoid context bloat
        recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
        
        for msg in recent_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                formatted.append(f"Usuario: {content}")
            elif role == "assistant":
                # Truncate long assistant responses
                truncated = content[:200] + "..." if len(content) > 200 else content
                formatted.append(f"Brain: {truncated}")
        
        return "\n".join(formatted) + "\n"

