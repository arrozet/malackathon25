"""
Python Code Executor Tool.

This tool enables the AI to execute Python code for data analysis, statistical
computations, and generating visualizations.
"""

from typing import Optional
import logging
import sys
import io
import traceback
from langchain_core.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class PythonExecutorTool(BaseTool):
    """
    Tool for executing Python code safely.
    
    This tool allows the AI to run Python code for data analysis, calculations,
    and generating insights. Code is executed in a restricted environment.
    """
    
    name: str = "python_executor"
    description: str = """
    Ejecuta código Python para análisis de datos, cálculos estadísticos, y visualizaciones.
    
    Input: Código Python válido (puede incluir imports de pandas, numpy, matplotlib)
    Output: Resultado de la ejecución (stdout, valores retornados, o errores)
    
    Útil para:
    - Realizar cálculos estadísticos complejos
    - Analizar tendencias en datos
    - Generar gráficos y visualizaciones
    - Transformar y procesar datos
    
    Nota: El código se ejecuta en un entorno restringido por seguridad.
    Librerías disponibles: numpy, pandas, matplotlib, statistics, math
    """
    
    def _run(self, code: str) -> str:
        """
        Executes Python code in a restricted environment.
        
        Args:
            code (str): Python code to execute.
        
        Returns:
            str: Execution output (stdout, return values, or error messages).
        
        Side Effects:
            Executes arbitrary Python code (restricted environment).
        """
        try:
            logger.info("Executing Python code")
            logger.debug(f"Code to execute:\n{code}")
            
            # Check for dangerous operations
            dangerous_keywords = ['eval', 'exec', 'compile', '__import__', 'open', 'file', 'input', 'raw_input']
            for keyword in dangerous_keywords:
                if keyword in code:
                    return f"Error: Operación no permitida '{keyword}' por razones de seguridad."
            
            # Create namespace with pre-imported safe libraries
            namespace = {}
            
            # Pre-import safe libraries
            try:
                import numpy as np
                namespace["np"] = np
            except ImportError:
                pass
            
            try:
                import pandas as pd
                namespace["pd"] = pd
            except ImportError:
                pass
            
            try:
                import matplotlib
                matplotlib.use('Agg')  # Non-interactive backend
                import matplotlib.pyplot as plt
                namespace["plt"] = plt
            except ImportError:
                pass
            
            try:
                import statistics
                namespace["statistics"] = statistics
            except ImportError:
                pass
            
            try:
                import math
                namespace["math"] = math
            except ImportError:
                pass
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                # Execute code
                exec(code, namespace)
                
                # Get output
                output = captured_output.getvalue()
                
                # If no print output, try to get last expression value
                if not output:
                    # Check if there's a result variable
                    if "result" in namespace:
                        output = str(namespace["result"])
                    else:
                        output = "Código ejecutado correctamente (sin output)."
                
                logger.info("Code executed successfully")
                return output
                
            finally:
                # Restore stdout
                sys.stdout = old_stdout
                
        except SyntaxError as e:
            error_msg = f"Error de sintaxis en el código Python:\n{str(e)}\nLínea {e.lineno}: {e.text}"
            logger.error(error_msg)
            return error_msg
            
        except Exception as e:
            error_msg = f"Error ejecutando código Python:\n{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, code: str) -> str:
        """
        Async version of _run (delegates to sync version).
        
        Args:
            code (str): Python code to execute.
        
        Returns:
            str: Execution output.
        """
        return self._run(code)

