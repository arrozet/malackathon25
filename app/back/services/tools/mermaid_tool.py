"""
Mermaid Diagram Tool.

This tool enables the AI to generate Mermaid diagram syntax for visualizing
relationships, workflows, timelines, and data structures.
"""

from typing import Optional
import logging
from langchain_core.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)


class MermaidTool(BaseTool):
    """
    Tool for generating Mermaid diagram syntax.
    
    This tool helps the AI create visual diagrams to explain concepts,
    show relationships, or illustrate workflows related to mental health data.
    """
    
    name: str = "mermaid_diagram"
    description: str = """
    Genera diagramas en sintaxis Mermaid para visualizar relaciones, flujos de trabajo,
    líneas de tiempo, y estructuras de datos.
    
    Input: Descripción del diagrama a crear (ej: "flujo de proceso de admisión hospitalaria")
    Output: Código Mermaid listo para renderizar
    
    Tipos de diagramas disponibles:
    - Flowchart: Diagramas de flujo
    - Sequence: Diagramas de secuencia
    - Class: Diagramas de clases
    - State: Diagramas de estados
    - ER: Diagramas entidad-relación
    - Gantt: Gráficos de Gantt
    - Pie: Gráficos circulares
    - Journey: Mapas de viaje del usuario
    
    Útil para:
    - Visualizar flujos de atención al paciente
    - Mostrar relaciones entre diagnósticos
    - Explicar esquemas de base de datos
    - Ilustrar procesos de análisis
    """
    
    def _run(self, description: str) -> str:
        """
        Generates Mermaid diagram syntax based on description.
        
        Args:
            description (str): Description of the diagram to create.
        
        Returns:
            str: Mermaid diagram syntax code.
        """
        try:
            logger.info(f"Generating Mermaid diagram for: {description}")
            
            description_lower = description.lower()
            
            # Determine diagram type and generate appropriate syntax
            
            # Database schema diagram
            if "esquema" in description_lower or "base de datos" in description_lower or "tablas" in description_lower:
                mermaid_code = self._generate_database_schema()
                
            # Patient admission flow
            elif "flujo" in description_lower and ("admisión" in description_lower or "ingreso" in description_lower):
                mermaid_code = self._generate_admission_flow()
                
            # Diagnosis relationship
            elif "diagnóstico" in description_lower and "relación" in description_lower:
                mermaid_code = self._generate_diagnosis_relationship()
                
            # Analysis process
            elif "proceso" in description_lower and "análisis" in description_lower:
                mermaid_code = self._generate_analysis_process()
                
            # Data journey
            elif "journey" in description_lower or "viaje" in description_lower:
                mermaid_code = self._generate_data_journey()
                
            # Generic flowchart
            else:
                mermaid_code = self._generate_generic_flowchart(description)
            
            logger.info("Mermaid diagram generated successfully")
            return f"```mermaid\n{mermaid_code}\n```"
            
        except Exception as e:
            error_msg = f"Error generando diagrama Mermaid: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _arun(self, description: str) -> str:
        """
        Async version of _run (delegates to sync version).
        
        Args:
            description (str): Description of the diagram to create.
        
        Returns:
            str: Mermaid diagram syntax code.
        """
        return self._run(description)
    
    def _generate_database_schema(self) -> str:
        """Generates ER diagram for the mental health database schema."""
        return """erDiagram
    PACIENTES ||--o{ EPISODIOS : tiene
    CENTROS_HOSPITALARIOS ||--o{ EPISODIOS : atiende
    EPISODIOS ||--o{ EPISODIOS_DIAGNOSTICOS : tiene
    EPISODIOS ||--o{ EPISODIOS_PROCEDIMIENTOS : tiene
    DIAGNOSTICOS_CIE ||--o{ EPISODIOS_DIAGNOSTICOS : clasifica
    PROCEDIMIENTOS ||--o{ EPISODIOS_PROCEDIMIENTOS : realiza
    COMUNIDADES_AUTONOMAS ||--o{ CENTROS_HOSPITALARIOS : ubica
    PAISES ||--o{ PACIENTES : nacimiento
    
    PACIENTES {
        number paciente_id PK
        string identificador_anonimo
        number edad_ingreso
        char sexo
        number pais_nacimiento_id FK
    }
    
    EPISODIOS {
        number episodio_id PK
        number paciente_id FK
        number centro_id FK
        date fecha_ingreso
        date fecha_fin_contacto
        number estancia_dias
        number nivel_severidad_apr
        number coste_apr
    }
    
    DIAGNOSTICOS_CIE {
        number diagnostico_id PK
        string codigo_cie
        string descripcion
        string capitulo_cie
    }"""
    
    def _generate_admission_flow(self) -> str:
        """Generates flowchart for patient admission process."""
        return """flowchart TD
    A[Paciente llega al centro] --> B{¿Requiere admisión?}
    B -->|Sí| C[Registro de episodio]
    B -->|No| D[Alta sin ingreso]
    C --> E[Evaluación clínica]
    E --> F[Asignación de diagnóstico principal]
    F --> G[Diagnósticos secundarios]
    G --> H[Determinar severidad APR]
    H --> I[Inicio de tratamiento]
    I --> J{¿Procedimientos requeridos?}
    J -->|Sí| K[Registro de procedimientos]
    J -->|No| L[Seguimiento]
    K --> L
    L --> M{¿Alta médica?}
    M -->|No| L
    M -->|Sí| N[Cierre de episodio]
    N --> O[Cálculo de costes]
    O --> P[Registro en base de datos]"""
    
    def _generate_diagnosis_relationship(self) -> str:
        """Generates diagram showing diagnosis relationships."""
        return """graph LR
    A[Trastornos Mentales<br/>Capítulo F] --> B[F00-F09<br/>Orgánicos]
    A --> C[F10-F19<br/>Sustancias]
    A --> D[F20-F29<br/>Psicóticos]
    A --> E[F30-F39<br/>Afectivos]
    A --> F[F40-F48<br/>Neuróticos]
    A --> G[F50-F59<br/>Fisiológicos]
    
    E --> E1[F32: Depresión]
    E --> E2[F31: Bipolar]
    D --> D1[F20: Esquizofrenia]
    C --> C1[F10: Alcohol]"""
    
    def _generate_analysis_process(self) -> str:
        """Generates flowchart for data analysis process."""
        return """flowchart TB
    A[Datos crudos Oracle] --> B[Extracción de datos]
    B --> C[Limpieza y validación]
    C --> D[Anonimización]
    D --> E[Feature Engineering]
    E --> F{Tipo de análisis}
    F -->|Descriptivo| G[Estadísticas descriptivas]
    F -->|Inferencial| H[Pruebas estadísticas]
    F -->|Predictivo| I[Modelos ML]
    G --> J[Visualizaciones]
    H --> J
    I --> J
    J --> K[Insights y recomendaciones]
    K --> L[Informe final]"""
    
    def _generate_data_journey(self) -> str:
        """Generates user journey map for researchers."""
        return """journey
    title Viaje del Investigador en Brain
    section Exploración inicial
      Acceder a Brain: 5: Investigador
      Ver dashboard principal: 4: Investigador
      Aplicar filtros básicos: 4: Investigador
    section Análisis profundo
      Consultar IA sobre tendencias: 5: Investigador, IA
      Generar visualizaciones: 5: Investigador, IA
      Ejecutar análisis estadístico: 4: Investigador, IA
    section Generación de insights
      Solicitar explicación de patrones: 5: Investigador, IA
      Crear diagramas explicativos: 4: Investigador, IA
      Exportar resultados: 5: Investigador"""
    
    def _generate_generic_flowchart(self, description: str) -> str:
        """Generates a generic flowchart based on description."""
        return f"""flowchart TD
    A[Inicio: {description}] --> B[Proceso 1]
    B --> C[Proceso 2]
    C --> D{{Decisión}}
    D -->|Opción A| E[Resultado A]
    D -->|Opción B| F[Resultado B]
    E --> G[Fin]
    F --> G
    
    style A fill:#7C3AED,stroke:#5B21B6,color:#fff
    style G fill:#7C3AED,stroke:#5B21B6,color:#fff"""

