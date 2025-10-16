"""
Base Tool with LLM-powered result summarization.

This module provides a base class for tools that can automatically summarize
their results using an LLM, creating clean, natural language outputs for
multi-agent architectures.
"""

from typing import Optional
import logging
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.back.config import config

logger = logging.getLogger(__name__)


class BaseSummarizableTool(BaseTool):
    """
    Base class for tools that can summarize their results using an LLM.
    
    This class provides automatic result summarization to support multi-agent
    architectures where the final agent should only see clean, natural language
    summaries instead of raw technical outputs.
    """
    
    def _get_summarizer_llm(self):
        """
        Lazy initialization of LLM for result summarization.
        
        Returns:
            ChatOpenAI or None: LLM instance if API key is configured.
        """
        if not hasattr(self, '_summarizer_llm_instance'):
            if config.XAI_API_KEY:
                self._summarizer_llm_instance = ChatOpenAI(
                    api_key=config.XAI_API_KEY,
                    base_url="https://api.x.ai/v1",
                    model="grok-4-fast-reasoning",
                    temperature=0.3,  # Slightly creative for summaries
                    max_tokens=300,  # Short summaries
                )
            else:
                self._summarizer_llm_instance = None
                logger.warning("XAI_API_KEY not configured - result summarization disabled")
        return self._summarizer_llm_instance
    
    def summarize_result(
        self,
        raw_result: str,
        user_query: str,
        tool_name: str,
        context: Optional[str] = None
    ) -> str:
        """
        Summarizes a tool's raw result into natural language.
        
        This method uses an LLM to convert technical outputs (SQL queries, JSON,
        stack traces, diagram code) into clean, actionable summaries that the
        final agent can understand without seeing implementation details.
        
        Args:
            raw_result (str): The raw output from the tool execution.
            user_query (str): The original user question that triggered the tool.
            tool_name (str): Name of the tool that generated the result.
            context (Optional[str]): Additional context about what the tool did.
        
        Returns:
            str: Natural language summary of the result.
        """
        llm = self._get_summarizer_llm()
        
        if not llm:
            # Fallback: return raw result if LLM not available
            logger.warning(f"Summarization disabled for {tool_name}, returning raw result")
            return raw_result
        
        try:
            # Build context-aware prompt
            context_text = f"\n\nContexto adicional: {context}" if context else ""
            
            system_prompt = f"""Eres un asistente experto en resumir resultados técnicos en lenguaje natural claro y conciso.

Tu tarea es convertir la salida técnica de una herramienta en un resumen comprensible para un investigador.

IMPORTANTE:
- NO incluyas detalles técnicos (queries SQL, código, JSON crudo, rutas de archivos, stack traces)
- Enfócate en QUÉ se encontró o QUÉ se hizo, no en CÓMO
- Sé conciso: 2-3 oraciones máximo
- Usa lenguaje natural y profesional
- Si hubo un error, explica QUÉ falló en términos simples

Herramienta: {tool_name}
Pregunta del usuario: {user_query}{context_text}"""
            
            user_prompt = f"""Resultado técnico de la herramienta:

{raw_result}

Resume este resultado en lenguaje natural, omitiendo detalles técnicos."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = llm.invoke(messages)
            summary = response.content.strip()
            
            logger.info(f"Summarized result for {tool_name}: {len(raw_result)} chars → {len(summary)} chars")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing result for {tool_name}: {e}")
            # Fallback: return raw result
            return raw_result

