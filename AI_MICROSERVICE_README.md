# 🧠 Brain AI Microservice - Quick Start

Microservicio de IA para el hackathon Malackathon 2025 que integra LangChain + **Grok-4 Fast Reasoning** (xAI) con 4 herramientas especializadas.

## 🚀 Instalación Rápida

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar API Keys

Edita `app/back/.env` y añade:

```bash
# REQUERIDO - Obtener en https://console.groq.com/
GROQ_API_KEY=gsk_your_api_key_here

# OPCIONAL - Para búsqueda en internet (https://tavily.com/)
TAVILY_API_KEY=tvly_your_api_key_here
```

**Obtener Groq API Key:**
1. Visita https://console.groq.com/
2. Crea una cuenta
3. Ve a "API Keys" → "Create API Key"
4. Copia la key y pégala en `.env`

### 3. Probar desde terminal

```bash
# Probar herramientas individuales
python scripts/test_ai_service.py --mode tools

# Probar servicio completo
python scripts/test_ai_service.py --mode service

# Modo chat interactivo
python scripts/test_ai_service.py --mode interactive
```

### 4. Iniciar servidor FastAPI

```bash
cd app/back
python main.py
```

El servidor estará en `http://localhost:8000`

### 5. Probar endpoints REST

```bash
# En otra terminal
python scripts/test_ai_endpoints.py --test all
```

## 📡 Endpoints Disponibles

### Chat con IA
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos episodios hay en 2023?"}'
```

### Análisis de datos
```bash
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Analiza la distribución por severidad"}'
```

### Generar diagrama Mermaid
```bash
curl -X POST http://localhost:8000/ai/visualize \
  -H "Content-Type: application/json" \
  -d '{"description": "flujo de admisión hospitalaria"}'
```

### Health check
```bash
curl http://localhost:8000/ai/health
```

## 🛠️ Herramientas Implementadas

### 1. Oracle RAG Tool
- Consulta la base de datos Oracle con lenguaje natural
- Traduce preguntas a SQL automáticamente
- Retorna resultados formateados

### 2. Internet Search Tool
- Busca información médica actualizada
- Usa Tavily API para búsqueda semántica
- Opcional (requiere TAVILY_API_KEY)

### 3. Python Executor Tool
- Ejecuta código Python de forma segura
- Librerías: numpy, pandas, matplotlib, statistics
- Útil para análisis estadístico complejo

### 4. Mermaid Diagram Tool
- Genera diagramas Mermaid
- Tipos: flowchart, ER, sequence, etc.
- Plantillas predefinidas para casos comunes

## 🎯 Ejemplos de Uso

### Desde Python
```python
from app.back.services.ai_service import get_ai_service

ai = get_ai_service()
result = ai.chat("¿Cuál es la estancia promedio?")
print(result['response'])
```

### Desde cURL
```bash
# Chat básico
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cuántos episodios hay en total?",
    "chat_history": []
  }'

# Con historial de conversación
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Y cuál es la distribución por sexo?",
    "chat_history": [
      {"role": "user", "content": "¿Cuántos episodios hay?"},
      {"role": "assistant", "content": "Hay 150,000 episodios"}
    ]
  }'
```

## 📊 Capacidades del Asistente

El asistente puede:
- ✅ Responder preguntas sobre los datos de salud mental
- ✅ Realizar análisis estadísticos complejos
- ✅ Buscar información médica actualizada
- ✅ Generar visualizaciones (diagramas Mermaid)
- ✅ Ejecutar código Python para cálculos personalizados
- ✅ Mantener contexto de conversación

## 🧪 Scripts de Testing

### Test servicio completo
```bash
python scripts/test_ai_service.py --mode all
```

### Test solo herramientas
```bash
python scripts/test_ai_service.py --mode tools
```

### Modo interactivo (chat)
```bash
python scripts/test_ai_service.py --mode interactive
```

### Test endpoints HTTP
```bash
python scripts/test_ai_endpoints.py --test all
```

## 📁 Estructura del Código

```
app/back/
├── services/
│   ├── ai_service.py              # Servicio principal (LangChain + Grok)
│   └── tools/
│       ├── oracle_rag_tool.py     # Herramienta RAG de Oracle
│       ├── internet_search_tool.py # Búsqueda en internet
│       ├── python_executor_tool.py # Ejecutor de Python
│       └── mermaid_tool.py        # Generador de diagramas
├── routers/
│   └── ai.py                      # Endpoints REST
└── schemas.py                     # Modelos Pydantic (añadidos)
```

## 🔧 Troubleshooting

### Error: "GROQ_API_KEY no configurada"
➡️ Verifica que tengas `GROQ_API_KEY` en `app/back/.env`

### Error: "Connection pool not initialized"
➡️ Verifica que la base de datos Oracle esté configurada y accesible

### El servidor no arranca
➡️ Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`

### Internet search no funciona
➡️ La herramienta de búsqueda es opcional. Necesitas `TAVILY_API_KEY` en `.env`

## 📚 Documentación Completa

Para documentación detallada, ver: `docs/AI_SERVICE_SETUP.md`

## 🎓 Arquitectura

El microservicio sigue la arquitectura establecida en `AGENTS.md`:

- **Services Layer**: Lógica de negocio (ai_service.py, tools/)
- **Routers Layer**: Adaptadores HTTP (ai.py)
- **Schemas Layer**: Modelos Pydantic (schemas.py)
- **API Gateway**: Orquestación (main.py)

## 🏆 Award 2 - Integration de IA

Este microservicio está diseñado específicamente para cumplir con los criterios del **Award 2**:

✅ **Relevant data selection**: Oracle RAG selecciona datos relevantes de la BD  
✅ **Prompt construction quality**: Sistema de prompts estructurado en ai_service.py  
✅ **AI response quality**: Grok-4 Fast Reasoning con temperatura optimizada  
✅ **Information presentation**: Respuestas formateadas con markdown, tablas y diagramas  

## 🚀 Próximos Pasos

1. ✅ Backend implementado y funcional
2. ⏳ Integración con frontend React (siguiente paso)
3. ⏳ Componente de chat UI
4. ⏳ Visualización de diagramas Mermaid en el frontend
5. ⏳ Cache de respuestas frecuentes

---

**Desarrollado para Malackathon 2025**  
**Equipo Brain - II Malackathon**

