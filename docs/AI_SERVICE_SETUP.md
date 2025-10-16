# Brain AI Service - Setup & Usage Guide

## 🎯 Overview

El microservicio de IA de Brain integra LangChain con el modelo **Grok-4 Fast Reasoning** de xAI (empresa de Elon Musk) para proporcionar un asistente inteligente de investigación en salud mental. El servicio incluye 4 herramientas especializadas:

1. **Oracle RAG Tool**: Consulta la base de datos Oracle con lenguaje natural
2. **Internet Search Tool**: Busca información médica actualizada en internet
3. **Python Executor Tool**: Ejecuta código Python para análisis estadístico
4. **Mermaid Tool**: Genera diagramas Mermaid para visualizaciones

## 🏗️ Arquitectura

```
AI Service (Microservice)
├── Services Layer
│   ├── ai_service.py         # Orquestador principal con LangChain
│   └── tools/                # Herramientas especializadas
│       ├── oracle_rag_tool.py
│       ├── internet_search_tool.py
│       ├── python_executor_tool.py
│       └── mermaid_tool.py
├── Routers Layer
│   └── ai.py                 # Endpoints REST
└── Schemas Layer
    └── schemas.py            # Modelos Pydantic
```

## 📦 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `langchain` y `langchain-core`: Framework de IA
- `langchain-groq`: Integración con Groq API
- `tavily-python`: Cliente para búsqueda en internet
- `matplotlib`, `pandas`, `numpy`: Para análisis de datos

### 2. Configurar variables de entorno

Crea o actualiza el archivo `.env` **en la raíz del proyecto** (no en `app/back/`) con las siguientes variables:

```bash
# API Key de xAI (REQUERIDO - para Grok-4 Fast Reasoning)
XAI_API_KEY=xai_your_api_key_here

# API Key de Tavily (OPCIONAL - solo para búsqueda en internet)
TAVILY_API_KEY=tvly_your_api_key_here
```

#### Obtener XAI_API_KEY:
1. Visita https://console.x.ai/
2. Regístrate o inicia sesión
3. Ve a la sección "API Keys"
4. Crea una nueva API key
5. Copia la key y añádela al archivo `.env` en la **raíz del proyecto**

**Notas importantes**: 
- Estamos usando **Grok-4 Fast Reasoning**, el modelo de IA de xAI (empresa de Elon Musk), no confundir con Groq (proveedor de inferencia)
- El archivo `.env` está en la raíz del proyecto, no en `app/back/.env`
- Todas las configuraciones se cargan centralizadamente a través de `config.py`

#### Obtener TAVILY_API_KEY (opcional):
1. Visita https://tavily.com/
2. Regístrate para obtener una cuenta
3. Obtén tu API key del dashboard
4. Copia la key y añádela a tu `.env`

## 🧪 Testing

### Modo 1: Probar herramientas individuales

```bash
python scripts/test_ai_service.py --mode tools
```

Esto probará cada herramienta por separado:
- Oracle RAG: Consulta la base de datos
- Python Executor: Ejecuta código de ejemplo
- Mermaid: Genera un diagrama de ejemplo
- Internet Search: Busca información (requiere TAVILY_API_KEY)

### Modo 2: Probar el servicio completo

```bash
python scripts/test_ai_service.py --mode service
```

Esto ejecutará pruebas del servicio de IA completo:
1. Consulta de base de datos
2. Análisis estadístico
3. Generación de visualizaciones
4. Health check

### Modo 3: Modo interactivo (chat)

```bash
python scripts/test_ai_service.py --mode interactive
```

Esto inicia una sesión de chat interactiva donde puedes hablar con Brain directamente desde la terminal.

Ejemplo:
```
You: ¿Cuántos episodios hay en 2023?
Brain: [Respuesta con datos de la base de datos]

You: Analiza la distribución por severidad
Brain: [Análisis con estadísticas]
```

### Modo 4: Ejecutar todas las pruebas

```bash
python scripts/test_ai_service.py --mode all
```

## 🚀 Uso con FastAPI

### Iniciar el servidor

```bash
cd app/back
python main.py
```

El servidor se ejecutará en `http://localhost:8000`

### Endpoints disponibles

#### 1. Chat con IA

**POST** `/ai/chat`

```json
{
  "message": "¿Cuántos episodios hay en 2023?",
  "chat_history": []
}
```

Respuesta:
```json
{
  "response": "Según los datos de la base de datos...",
  "tool_calls": ["oracle_database_query"],
  "intermediate_steps": [...]
}
```

#### 2. Análisis de datos

**POST** `/ai/analyze`

```json
{
  "query": "Analiza la distribución de episodios por severidad"
}
```

#### 3. Generación de visualizaciones

**POST** `/ai/visualize`

```json
{
  "description": "diagrama de flujo de admisión hospitalaria"
}
```

Respuesta:
```json
{
  "mermaid_code": "```mermaid\nflowchart TD\n...\n```",
  "description": "diagrama de flujo de admisión hospitalaria"
}
```

#### 4. Health check

**GET** `/ai/health`

Respuesta:
```json
{
  "status": "healthy",
  "components": {
    "ai_service": true,
    "llm": true,
    "oracle_tool": true,
    "internet_tool": true,
    "python_tool": true,
    "mermaid_tool": true
  }
}
```

## 🔧 Ejemplos de uso con cURL

### Chat básico
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos episodios hay en total?"}'
```

### Análisis de datos
```bash
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Analiza la estancia promedio por severidad"}'
```

### Generar diagrama
```bash
curl -X POST http://localhost:8000/ai/visualize \
  -H "Content-Type: application/json" \
  -d '{"description": "esquema de base de datos"}'
```

### Health check
```bash
curl http://localhost:8000/ai/health
```

## 📊 Capacidades del AI Assistant

### 1. Consultas a la base de datos
El asistente puede responder preguntas sobre los datos usando lenguaje natural:
- "¿Cuántos episodios hay en 2023?"
- "¿Cuál es la estancia promedio?"
- "Muéstrame los diagnósticos más frecuentes"
- "¿Cuál es la distribución por sexo?"

### 2. Análisis estadístico
Puede ejecutar código Python para análisis complejos:
- Calcular correlaciones
- Generar distribuciones
- Realizar pruebas estadísticas
- Crear gráficos

### 3. Búsqueda en internet
Puede buscar información médica actualizada:
- Investigaciones recientes sobre tratamientos
- Contexto sobre códigos CIE-10
- Políticas de salud pública
- Estudios científicos

### 4. Visualizaciones
Genera diagramas Mermaid para:
- Esquemas de base de datos
- Flujos de proceso
- Relaciones entre entidades
- Mapas de viaje del usuario

## 🐛 Troubleshooting

### Error: "XAI_API_KEY no configurada"
**Solución**: 
- Asegúrate de tener la variable `XAI_API_KEY` en el archivo `.env` de la raíz del proyecto
- Verifica que el archivo `.env` esté en la raíz (no en `app/back/`)
- No confundir con `GROQ_API_KEY` (proveedor diferente)

### Error: "Connection pool not initialized"
**Solución**: Verifica que la base de datos Oracle esté correctamente configurada y accesible

### Error: "TAVILY_API_KEY no configurada"
**Solución**: La búsqueda en internet requiere una API key de Tavily. Puedes:
- Obtener una key en https://tavily.com/
- O simplemente no usar la herramienta de búsqueda (opcional)

### El modelo no responde correctamente
**Solución**: Verifica que:
- Tienes una API key válida de xAI (console.x.ai)
- La API key tiene permisos para usar Grok-4 Fast Reasoning
- El modelo tiene acceso a las herramientas
- La base de datos tiene datos

## 🎓 Arquitectura de Herramientas

### Oracle RAG Tool
- **Propósito**: Traducir preguntas en lenguaje natural a SQL
- **Método**: Heurísticas basadas en patrones comunes
- **Mejora futura**: Integrar modelo NL2SQL especializado

### Internet Search Tool
- **Proveedor**: Tavily API
- **Capacidades**: Búsqueda semántica con resúmenes
- **Límite**: 5 resultados por consulta

### Python Executor Tool
- **Entorno**: Restringido por seguridad
- **Librerías disponibles**: numpy, pandas, matplotlib, statistics, math
- **Límite**: No permite operaciones destructivas

### Mermaid Tool
- **Tipos de diagramas**: Flowchart, ER, Sequence, etc.
- **Plantillas**: Pre-configuradas para casos de uso comunes
- **Output**: Código Mermaid listo para renderizar

## 📝 Próximos pasos

1. **Integración frontend**: Crear componentes React para chat UI
2. **Mejora de NL2SQL**: Integrar modelo especializado
3. **Cache de respuestas**: Implementar cache para consultas frecuentes
4. **Métricas y logging**: Añadir telemetría para análisis de uso
5. **Testing automatizado**: Crear suite de tests unitarios y de integración

## 📚 Referencias

- [xAI Grok Documentation](https://docs.x.ai/)
- [xAI Console](https://console.x.ai/)
- [LangChain Documentation](https://python.langchain.com/docs/)
- [Tavily API Documentation](https://docs.tavily.com/)
- [Mermaid Documentation](https://mermaid.js.org/)

