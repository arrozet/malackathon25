# 🚀 Brain AI Service - Instrucciones de Setup

## ⚠️ IMPORTANTE: xAI vs Groq

**Aclaración sobre las tecnologías:**

- **xAI** = Empresa de Elon Musk que desarrolla el modelo **Grok**
- **Grok-4 Fast Reasoning** = Modelo de IA que usamos (de xAI)
- **Groq** (con 'q') = Proveedor diferente de inferencia (NO es lo que usamos)

## 📋 Configuración Rápida

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `langchain-openai` (para conectar con xAI)
- `langchain` y `langchain-core`
- `tavily-python` (búsqueda internet - opcional)
- `pandas`, `numpy`, `matplotlib` (análisis de datos)

### 2. Obtener API Key de xAI

1. Ve a **https://console.x.ai/**
2. Crea una cuenta o inicia sesión
3. Navega a la sección **API Keys**
4. Crea una nueva API key
5. Copia la key (empieza con `xai-...`)

### 3. Configurar variables de entorno

Edita `app/back/.env` y añade:

```bash
# REQUERIDO - API Key de xAI para Grok-4 Fast Reasoning
XAI_API_KEY=xai_tu_key_aqui

# OPCIONAL - Solo si quieres usar búsqueda en internet
TAVILY_API_KEY=tvly_tu_key_aqui
```

### 4. Verificar configuración

Revisa que el archivo `.env` tenga:

```bash
# Oracle Database (ya configurado)
ORACLE_USER=tu_usuario
ORACLE_PASSWORD=tu_password
ORACLE_DSN=tu_dsn
TNS_ADMIN=./app/oracle_wallet

# xAI para Grok-4 Fast Reasoning (NUEVO - AÑADIR)
XAI_API_KEY=xai_tu_key_aqui

# Tavily para búsqueda en internet (OPCIONAL)
TAVILY_API_KEY=tvly_tu_key_aqui
```

## 🧪 Probar el servicio

### Opción 1: Test directo (Python)

```bash
# Probar todas las herramientas
python scripts/test_ai_service.py --mode all

# Solo probar herramientas individuales
python scripts/test_ai_service.py --mode tools

# Solo probar el servicio de IA
python scripts/test_ai_service.py --mode service

# Modo chat interactivo
python scripts/test_ai_service.py --mode interactive
```

### Opción 2: Test via API REST

**Terminal 1** - Iniciar servidor:
```bash
cd app/back
python main.py
```

**Terminal 2** - Probar endpoints:
```bash
python scripts/test_ai_endpoints.py --test all
```

### Opción 3: Test manual con cURL

```bash
# Health check
curl http://localhost:8000/ai/health

# Chat
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuántos episodios hay en total?"}'

# Análisis
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Analiza la distribución por severidad"}'

# Diagrama
curl -X POST http://localhost:8000/ai/visualize \
  -H "Content-Type: application/json" \
  -d '{"description": "esquema de base de datos"}'
```

## 🎯 Modelo Utilizado

- **Proveedor**: xAI (https://x.ai/)
- **Modelo**: `grok-4-fast-reasoning`
- **Características**:
  - Ventana de contexto: 2M tokens
  - Razonamiento paso a paso
  - Soporte para tool calling
  - Optimizado para velocidad y coste

## 🛠️ Herramientas Disponibles

1. **Oracle RAG** - Consulta BD con lenguaje natural
2. **Internet Search** - Búsqueda médica actualizada (Tavily)
3. **Python Executor** - Análisis estadístico con Python
4. **Mermaid Generator** - Diagramas de flujo/ER/etc.

## ❗ Troubleshooting

### Error: "XAI_API_KEY no configurada"
✅ **Solución**: Añade `XAI_API_KEY=xai_...` en `app/back/.env`
📍 **Obtener key**: https://console.x.ai/

### Error: "Connection pool not initialized"
✅ **Solución**: Verifica que Oracle esté configurado correctamente

### Error: Import error de langchain_openai
✅ **Solución**: Ejecuta `pip install -r requirements.txt`

### El modelo no responde
✅ **Solución**: 
- Verifica que la API key sea válida
- Prueba con: `curl https://api.x.ai/v1/models -H "Authorization: Bearer $XAI_API_KEY"`

## 📊 Ejemplo de Uso

```python
from app.back.services.ai_service import get_ai_service

# Inicializar servicio
ai = get_ai_service()

# Chat simple
result = ai.chat("¿Cuántos episodios hay en 2023?")
print(result['response'])

# Con historial
history = [
    {"role": "user", "content": "¿Cuántos episodios hay?"},
    {"role": "assistant", "content": "Hay 150,000 episodios"}
]
result = ai.chat("¿Y cuál es la distribución por sexo?", chat_history=history)
print(result['response'])
```

## 📁 Estructura de Archivos

```
app/back/
├── services/
│   ├── ai_service.py              # Servicio principal (Grok-4)
│   └── tools/                     # Herramientas
│       ├── oracle_rag_tool.py     # RAG Oracle
│       ├── internet_search_tool.py # Búsqueda Tavily
│       ├── python_executor_tool.py # Python seguro
│       └── mermaid_tool.py        # Diagramas Mermaid
├── routers/
│   └── ai.py                      # Endpoints REST
└── schemas.py                     # Modelos Pydantic

scripts/
├── test_ai_service.py             # Tests Python directo
└── test_ai_endpoints.py           # Tests HTTP
```

## 🎓 Detalles Técnicos

### Integración con xAI

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",  # xAI API endpoint
    model="grok-4-fast-reasoning",    # Grok-4 Fast Reasoning
    temperature=0.3,                   # Razonamiento enfocado
    max_tokens=8000,
)
```

### Arquitectura

Sigue el patrón **Microservices + Clean Architecture**:
- **Tools Layer**: Herramientas especializadas
- **Services Layer**: Lógica de negocio (ai_service.py)
- **Routers Layer**: Adaptadores HTTP (ai.py)
- **API Gateway**: Orquestación (main.py)

---

**Desarrollado para Malackathon 2025**  
**Modelo: Grok-4 Fast Reasoning (xAI)**  
**Framework: LangChain**

