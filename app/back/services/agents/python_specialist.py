"""
Python Specialist Agent.

This agent specializes in executing Python code for data analysis, interpreting
execution results, and summarizing findings in clear, natural language.
"""

from typing import Dict, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.back.config import config
from app.back.services.tools.python_executor_tool import PythonExecutorTool

logger = logging.getLogger(__name__)


class PythonSpecialistAgent:
    """
    Specialist agent for Python code execution and data analysis.
    
    This agent:
    1. Generates Python code for the user's analytical request
    2. Uses PythonExecutorTool to execute the code safely
    3. Interprets execution results (stdout, errors, values)
    4. Summarizes findings in natural language (NO code, NO stack traces)
    """
    
    def __init__(self):
        """
        Initializes the Python Specialist Agent.
        
        Side Effects:
            Initializes the LLM and Python Executor tool.
        
        Raises:
            ValueError: If XAI_API_KEY is not configured.
        """
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY required for Python Specialist Agent")
        
        # LLM for code generation and summarization
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,
            base_url="https://api.x.ai/v1",
            model="grok-4-fast-reasoning",
            temperature=0.2,  # Lower temperature for code generation
            max_tokens=800,
        )
        
        # Python executor tool
        self.tool = PythonExecutorTool()
        
        logger.info("Python Specialist Agent initialized")
    
    def execute(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates and executes Python code, then summarizes results.
        
        Args:
            query (str): User's analytical request.
            state (Dict[str, Any]): Current agent state (from LangGraph).
        
        Returns:
            Dict[str, Any]: State update with specialist summary.
        """
        try:
            logger.info(f"Python Specialist executing query: {query}")
            
            # Step 1: Generate Python code for the analysis
            python_code = self._generate_python_code(query)
            
            logger.debug(f"Generated Python code:\n{python_code}")
            
            # Step 2: Execute the code using the tool
            raw_result = self.tool._run(python_code)
            
            logger.debug(f"Raw execution result: {raw_result[:200]}...")
            
            # Step 3: Interpret and summarize the result
            summary = self._summarize_python_result(query, python_code, raw_result)
            
            logger.info(f"Python Specialist summary generated: {summary[:100]}...")
            
            # Step 4: Return ONLY the summary
            return {
                "specialist_summaries": [{
                    "specialist": "python_analysis",
                    "summary": summary,
                    "tool_used": "python_executor"
                }]
            }
            
        except Exception as e:
            error_msg = f"No se pudo ejecutar el análisis: {str(e)}"
            logger.error(f"Python Specialist error: {error_msg}")
            
            return {
                "specialist_summaries": [{
                    "specialist": "python_analysis",
                    "summary": error_msg,
                    "tool_used": "python_executor",
                    "error": True
                }]
            }
    
    def _generate_python_code(self, query: str) -> str:
        """
        Generates Python code to answer the user's analytical question.
        
        Args:
            query (str): User's analytical request.
        
        Returns:
            str: Python code to execute.
        """
        system_prompt = """Eres un experto en análisis de datos con Python.

Genera código Python para responder preguntas analíticas.

INSTRUCCIONES:
- Usa SOLO librerías disponibles: numpy, pandas, matplotlib, statistics, math
- El código debe ser autocontenido y ejecutable
- Usa print() para mostrar resultados
- Para cálculos, almacena el resultado en variable 'result'
- NO uses operaciones de archivo (open, file)
- NO uses inputs interactivos
- El código debe ser conciso y eficiente

Librerías pre-importadas:
- np (numpy)
- pd (pandas)
- plt (matplotlib.pyplot)
- statistics
- math

Genera SOLO el código Python, sin explicaciones."""

        user_prompt = f"""Tarea analítica: {query}

Genera el código Python necesario para realizar este análisis."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        code = response.content.strip()
        
        # Clean markdown code blocks if present
        code = code.replace("```python", "").replace("```", "").strip()
        
        return code
    
    def _summarize_python_result(self, query: str, code: str, raw_result: str) -> str:
        """
        Summarizes Python execution results in natural language.
        
        This method interprets execution outputs (stdout, errors, values) and
        converts them into clear, actionable insights.
        
        Args:
            query (str): Original user question.
            code (str): Python code that was executed.
            raw_result (str): Raw output from Python executor.
        
        Returns:
            str: Natural language summary (2-3 sentences).
        """
        system_prompt = """Eres un analista de datos experto en interpretar resultados de código Python.

Tu tarea es resumir resultados de ejecución de código en lenguaje natural claro.

REGLAS ESTRICTAS:
- NO incluyas código Python, imports, ni detalles técnicos
- NO muestres stack traces ni errores técnicos completos
- Enfócate en QUÉ se calculó y QUÉ se encontró
- Interpreta números y estadísticas de forma comprensible
- Sé conciso: 2-3 oraciones máximo
- Si hubo un error, explica QUÉ falló en términos simples (no el traceback completo)

Ejemplo de BUENA respuesta:
"El análisis calculó una correlación de 0.73 entre edad y duración de estancia, indicando una relación positiva moderada-fuerte."

Ejemplo de MALA respuesta:
"El código 'import numpy as np; result = np.corrcoef(...)' retornó: [[1. 0.73][0.73 1.]]"

Resume los hallazgos del análisis de forma clara y profesional."""

        user_prompt = f"""Pregunta del usuario: {query}

Código ejecutado:
{code}

Resultado de la ejecución:
{raw_result}

Resume los hallazgos del análisis en lenguaje natural, omitiendo detalles técnicos del código."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            summary = response.content.strip()
            
            # Token savings log
            combined_length = len(code) + len(raw_result)
            token_reduction = ((combined_length - len(summary)) / combined_length) * 100
            logger.info(f"Python result summarized: {combined_length} → {len(summary)} chars ({token_reduction:.1f}% reduction)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing Python result: {e}")
            # Fallback: return truncated raw result
            return f"Análisis completado. Resultados: {raw_result[:200]}..."

