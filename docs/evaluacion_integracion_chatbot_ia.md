# Evaluación: Integración de Chatbot IA con RAG en Brain

**Fecha:** 2025-10-15  
**Proyecto:** Brain - Malackathon 2025  
**Objetivo:** Evaluar la complejidad de integrar un chatbot conversacional con capacidades RAG, herramientas y acceso a la base de datos Oracle.

---

## 📊 Resumen Ejecutivo

**Veredicto:** **Complejidad MEDIA-ALTA** (6-8 días de desarrollo full-time)

La integración de un chatbot con IA en Brain es **totalmente viable** dentro del contexto del hackathon, pero requiere decisiones arquitectónicas claras y una implementación metódica. Las principales ventajas son:

- ✅ Backend FastAPI ya establecido con conexión estable a Oracle
- ✅ Frontend React modular que puede extenderse con componente chat
- ✅ Infraestructura Docker lista para nuevos servicios
- ✅ Múltiples opciones de LLM providers con diferentes trade-offs

**Puntos críticos de riesgo:**
- ⚠️ Latencia de consultas Oracle en contexto conversacional
- ⚠️ Gestión de costes de APIs externas (OpenAI, OpenRouter)
- ⚠️ Complejidad de implementar tool calling robusto
- ⚠️ Embedding y vectorización de esquema de BD grande

---

## 🏗️ Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TS)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Componente ChatInterface                            │   │
│  │  - Input conversacional                              │   │
│  │  - Historial de mensajes                             │   │
│  │  - Visualización de insights en tiempo real          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /chat/message endpoint                              │   │
│  │  /chat/history endpoint                              │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Orquestador de IA                                   │   │
│  │  - Gestión de contexto conversacional                │   │
│  │  - Decisión de uso de herramientas (tool calling)    │   │
│  │  - Prompt engineering para análisis sanitario        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Motor RAG                                           │   │
│  │  - Embedding de esquema Oracle (columnas, tablas)    │   │
│  │  - Búsqueda semántica en metadatos                   │   │
│  │  - Generación de consultas SQL desde lenguaje natural│   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Herramientas Disponibles (Tools)                    │   │
│  │  1. query_oracle_tool()                              │   │
│  │  2. calculate_statistics_tool()                      │   │
│  │  3. search_internet_tool() [opcional]                │   │
│  │  4. export_data_tool()                               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐      ┌──────────────┐      ┌────────────┐
    │  Oracle │      │ LLM Provider │      │ Vector DB  │
    │   ADB   │      │ (OpenAI/etc) │      │ (opcional) │
    └─────────┘      └──────────────┘      └────────────┘
```

---

## 🤖 Opciones de LLM Provider

### Opción 1: OpenAI GPT-4 / GPT-4o
**Complejidad:** ⭐⭐ (BAJA)

**Pros:**
- API extremadamente estable y documentada
- Excelente capacidad de function calling nativa
- Soporte robusto de system prompts para contexto médico
- Latencia predecible (~1-3s por request)

**Contras:**
- Coste más alto (~$0.03-0.06 por 1K tokens en GPT-4o)
- Requiere API key con billing configurado
- Dependencia de infraestructura externa

**Implementación:**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

tools = [
    {
        "type": "function",
        "function": {
            "name": "query_oracle",
            "description": "Ejecuta una consulta SQL en la base de datos de admisiones de salud mental",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "Consulta SQL parametrizada y segura"
                    }
                },
                "required": ["sql_query"]
            }
        }
    }
]

response = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": MEDICAL_CONTEXT_PROMPT},
        {"role": "user", "content": user_message}
    ],
    tools=tools,
    tool_choice="auto"
)
```

**Estimación de esfuerzo:** 2-3 días

---

### Opción 2: OpenRouter (Agregador Multi-Modelo)
**Complejidad:** ⭐⭐ (BAJA-MEDIA)

**Pros:**
- Acceso a múltiples modelos (Claude, GPT-4, Gemini, Llama) con una API
- Precios competitivos y transparentes
- Fallback automático entre modelos
- Compatible con SDK de OpenAI

**Contras:**
- Capa adicional de abstracción
- Soporte de function calling varía según modelo subyacente
- Menor control sobre infraestructura

**Implementación:**
```python
from openai import AsyncOpenAI

# OpenRouter usa la misma API que OpenAI
client = AsyncOpenAI(
    api_key=config.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

response = await client.chat.completions.create(
    model="anthropic/claude-3.5-sonnet",  # O cualquier otro modelo
    messages=messages,
    extra_headers={
        "HTTP-Referer": "https://brain.malackathon.es",
        "X-Title": "Brain Assistant"
    }
)
```

**Estimación de esfuerzo:** 2-3 días

---

### Opción 3: xAI Grok
**Complejidad:** ⭐⭐ (BAJA)

**Pros:**
- Modelo reciente y competitivo
- Pricing agresivo
- API compatible con OpenAI SDK

**Contras:**
- Menos maduro que OpenAI/Anthropic
- Documentación menos exhaustiva
- Ecosistema de herramientas más limitado

**Implementación:**
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=config.XAI_API_KEY,
    base_url="https://api.x.ai/v1"
)

response = await client.chat.completions.create(
    model="grok-beta",
    messages=messages
)
```

**Estimación de esfuerzo:** 2-3 días

---

### Opción 4: Oracle Cloud Infrastructure Gen AI (Nativo)
**Complejidad:** ⭐⭐⭐⭐ (ALTA)

**Pros:**
- Integración nativa con Oracle Cloud
- Sin latencia de red externa
- Potencial de costes reducidos (misma facturación OCI)
- Cumplimiento normativo healthcare

**Contras:**
- Documentación menos madura
- Requiere configuración adicional de OCI
- Ecosistema de herramientas limitado
- Mayor curva de aprendizaje

**Implementación:**
```python
import oci

config_oci = oci.config.from_file()
generative_ai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(config_oci)

chat_request = oci.generative_ai_inference.models.CohereChatRequest(
    message=user_message,
    chat_history=conversation_history
)

response = generative_ai_client.chat(chat_request)
```

**Estimación de esfuerzo:** 5-7 días (por complejidad de setup)

---

## 🧠 Implementación de RAG sobre Oracle

### Componentes Necesarios

#### 1. Embedding del Esquema de Base de Datos
**Complejidad:** ⭐⭐⭐ (MEDIA)

Necesitas vectorizar:
- Nombres de tablas y sus propósitos
- Nombres de columnas y tipos de datos
- Relaciones entre tablas
- Valores categóricos comunes (ej: códigos de diagnóstico)

**Código de ejemplo:**
```python
from openai import AsyncOpenAI
import numpy as np

async def embed_database_schema():
    """Genera embeddings del esquema Oracle para búsqueda semántica."""
    
    schema_docs = [
        {
            "id": "table_saludmental",
            "text": "Tabla SALUDMENTAL: Contiene registros de admisiones hospitalarias en unidades de salud mental. Columnas: CIP_SNS_RECODIFICADO (identificador paciente), FECHA_DE_INGRESO, SEXO (1=Hombre, 2=Mujer), EDAD, Estancia Días, REINGRESO (S/N), Categoría (diagnóstico primario), INGRESO_EN_UCI (S/N)"
        },
        {
            "id": "vista_muy_interesante",
            "text": "Vista VISTA_MUY_INTERESANTE: Agregación de métricas clave por categoría diagnóstica y grupo etario"
        }
    ]
    
    embeddings = []
    for doc in schema_docs:
        response = await client.embeddings.create(
            model="text-embedding-3-small",  # Más barato que ada-002
            input=doc["text"]
        )
        embeddings.append({
            "id": doc["id"],
            "text": doc["text"],
            "embedding": response.data[0].embedding
        })
    
    return embeddings

# Almacena en memoria o Vector DB
schema_embeddings = await embed_database_schema()
```

**Storage de vectores:**
- **Opción simple:** In-memory con NumPy/FAISS (suficiente para hackathon)
- **Opción robusta:** Qdrant, Weaviate, Pinecone (overkill para hackathon)

#### 2. Búsqueda Semántica de Contexto Relevante
```python
async def find_relevant_context(user_query: str, top_k: int = 3):
    """Encuentra las tablas/columnas más relevantes para la query del usuario."""
    
    # Generar embedding de la pregunta
    query_response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=user_query
    )
    query_embedding = query_response.data[0].embedding
    
    # Calcular similitud coseno
    similarities = []
    for doc in schema_embeddings:
        similarity = np.dot(query_embedding, doc["embedding"]) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc["embedding"])
        )
        similarities.append((doc, similarity))
    
    # Retornar top-k más relevantes
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in similarities[:top_k]]
```

#### 3. Generación de SQL desde Lenguaje Natural
**Complejidad:** ⭐⭐⭐⭐ (ALTA - ÁREA DE MAYOR RIESGO)

**Desafío:** Convertir "¿cuántas mujeres menores de 30 años han reingresado?" en:
```sql
SELECT COUNT(*) 
FROM SALUDMENTAL 
WHERE SEXO = 2 
  AND EDAD < 30 
  AND REINGRESO = 'S'
```

**Estrategia:**
```python
async def generate_sql_from_natural_language(user_query: str):
    """Genera SQL seguro desde lenguaje natural con validación."""
    
    # 1. Recuperar contexto relevante
    relevant_context = await find_relevant_context(user_query)
    
    # 2. Construir prompt con ejemplos few-shot
    system_prompt = f"""Eres un experto en SQL y análisis de datos de salud mental.
    
Esquema de base de datos:
{chr(10).join([doc['text'] for doc, _ in relevant_context])}

Genera consultas SQL válidas para Oracle Database 23ai.
IMPORTANTE:
- Usa comillas dobles para columnas con espacios: "Estancia Días"
- SEXO: 1=Hombre, 2=Mujer
- REINGRESO: 'S'/'N'
- Siempre incluye WHERE para filtros
- NUNCA uses DELETE, DROP, TRUNCATE, UPDATE, INSERT

Ejemplos:
Usuario: "Cuántos pacientes tienen más de 60 años"
SQL: SELECT COUNT(*) FROM SALUDMENTAL WHERE EDAD > 60

Usuario: "Edad promedio de mujeres"
SQL: SELECT AVG(EDAD) FROM SALUDMENTAL WHERE SEXO = 2

Ahora genera SQL para:"""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0  # Determinismo máximo para SQL
    )
    
    sql_query = response.choices[0].message.content.strip()
    
    # 3. Validación de seguridad
    forbidden_keywords = ["DELETE", "DROP", "TRUNCATE", "UPDATE", "INSERT", "ALTER", "CREATE"]
    if any(keyword in sql_query.upper() for keyword in forbidden_keywords):
        raise SecurityError("SQL query contains forbidden operations")
    
    return sql_query
```

**Estimación de esfuerzo:** 3-4 días (incluyendo testing exhaustivo)

---

## 🛠️ Implementación de Tool Calling

### Herramientas Básicas Recomendadas

#### Tool 1: Consultar Base de Datos Oracle
```python
async def query_oracle_tool(sql_query: str, max_rows: int = 100):
    """
    Ejecuta una consulta SQL de solo lectura en Oracle ADB.
    
    Args:
        sql_query: Consulta SQL validada
        max_rows: Límite de filas a retornar
    
    Returns:
        dict con resultados formateados
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            
            # Obtener nombres de columnas
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch con límite
            rows = cursor.fetchmany(max_rows)
            
            # Formatear resultados
            results = [dict(zip(columns, row)) for row in rows]
            
            return {
                "success": True,
                "rows_returned": len(results),
                "columns": columns,
                "data": results
            }
    except Exception as e:
        logger.error(f"Error ejecutando SQL: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

#### Tool 2: Calcular Estadísticas Agregadas
```python
async def calculate_statistics_tool(table: str, column: str, filters: dict = None):
    """
    Calcula estadísticas descriptivas sobre una columna numérica.
    
    Args:
        table: Nombre de la tabla
        column: Columna numérica a analizar
        filters: Filtros WHERE opcionales
    
    Returns:
        dict con mean, median, std, min, max, percentiles
    """
    # Construir SQL dinámico de forma segura
    sql = f'''
        SELECT 
            AVG("{column}") as mean,
            MEDIAN("{column}") as median,
            STDDEV("{column}") as std,
            MIN("{column}") as min,
            MAX("{column}") as max,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "{column}") as q25,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "{column}") as q75
        FROM {table}
    '''
    
    if filters:
        where_clauses = []
        for key, value in filters.items():
            if isinstance(value, str):
                where_clauses.append(f"{key} = '{value}'")
            else:
                where_clauses.append(f"{key} = {value}")
        sql += " WHERE " + " AND ".join(where_clauses)
    
    result = await query_oracle_tool(sql)
    return result
```

#### Tool 3: Búsqueda en Internet (Opcional - MCP)
**Solo si es necesario** para contexto adicional sobre diagnósticos:

```python
import httpx

async def search_medical_context_tool(query: str):
    """
    Busca información médica contextual en fuentes confiables.
    CUIDADO: Solo usar para definiciones generales, no diagnóstico.
    """
    # Ejemplo con API de PubMed o fuente similar
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.example.com/medical-search",
            params={"q": query, "limit": 3}
        )
        return response.json()
```

---

## 🔌 Integración MCP (Model Context Protocol)

**Complejidad:** ⭐⭐⭐⭐⭐ (MUY ALTA - NO RECOMENDADO PARA HACKATHON)

MCP es un protocolo emergente de Anthropic para contexto dinámico, pero:
- Documentación limitada
- Soporte de librerías inmaduro
- Mayor overhead de desarrollo
- Beneficio marginal vs tool calling tradicional

**Recomendación:** Usar function calling estándar de OpenAI/Anthropic por ahora.

---

## 💻 Implementación Frontend

### Componente ChatInterface.tsx
```typescript
import { useState, useEffect, useRef } from 'react'
import type { Message } from '../types/chat'

interface ChatInterfaceProps {
  onInsightGenerated?: (insight: any) => void
}

export function ChatInterface({ onInsightGenerated }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          conversation_id: sessionStorage.getItem('conversation_id')
        })
      })

      const data = await response.json()

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        tool_calls: data.tool_calls,
        data_insights: data.data_insights
      }

      setMessages(prev => [...prev, assistantMessage])

      // Notificar insights al componente padre
      if (data.data_insights && onInsightGenerated) {
        onInsightGenerated(data.data_insights)
      }

      // Guardar conversation_id
      if (data.conversation_id) {
        sessionStorage.setItem('conversation_id', data.conversation_id)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Lo siento, hubo un error procesando tu solicitud.',
        timestamp: new Date(),
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message message--${msg.role}`}>
            <div className="message__content">
              {msg.content}
            </div>
            {msg.tool_calls && (
              <div className="message__tools">
                <span className="tool-badge">🔧 Herramientas usadas: {msg.tool_calls.join(', ')}</span>
              </div>
            )}
            {msg.data_insights && (
              <div className="message__insights">
                <InsightCard data={msg.data_insights} />
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message message--loading">Brain está pensando...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Pregúntame sobre los datos de salud mental..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Enviar
        </button>
      </div>
    </div>
  )
}
```

---

## 📋 Plan de Implementación Recomendado

### Fase 1: Setup Básico (Día 1-2)
- [ ] Instalar dependencias: `openai`, `numpy`, `tiktoken`
- [ ] Configurar API keys en `.env`
- [ ] Crear endpoint `/api/chat/message` en FastAPI
- [ ] Implementar gestión básica de conversación (historial en memoria)
- [ ] Probar conexión con LLM provider elegido

### Fase 2: RAG sobre Esquema Oracle (Día 2-3)
- [ ] Documentar esquema completo de SALUDMENTAL
- [ ] Generar embeddings del esquema
- [ ] Implementar búsqueda semántica de contexto
- [ ] Testear recuperación de información relevante

### Fase 3: Tool Calling (Día 3-5)
- [ ] Implementar `query_oracle_tool` con validación de seguridad
- [ ] Implementar `calculate_statistics_tool`
- [ ] Configurar function calling en LLM provider
- [ ] Testing exhaustivo de generación SQL
- [ ] Implementar fallbacks para queries erróneas

### Fase 4: Frontend Integration (Día 5-6)
- [ ] Crear componente `ChatInterface.tsx`
- [ ] Integrar con backend FastAPI
- [ ] Añadir visualización de resultados inline
- [ ] Styling coherente con diseño Brain existente

### Fase 5: Testing & Refinamiento (Día 6-7)
- [ ] Testing end-to-end de flujos conversacionales
- [ ] Optimización de prompts para contexto médico
- [ ] Manejo de errores y edge cases
- [ ] Documentación de capacidades del chatbot

### Fase 6: Deployment (Día 7-8)
- [ ] Actualizar Docker Compose con variables nuevas
- [ ] Testing en entorno productivo
- [ ] Configurar rate limiting
- [ ] Documentar uso para evaluadores

---

## 💰 Estimación de Costes

### OpenAI GPT-4o (Modelo recomendado)
- **Input:** $2.50 / 1M tokens
- **Output:** $10.00 / 1M tokens
- **Embeddings (text-embedding-3-small):** $0.02 / 1M tokens

**Ejemplo de conversación típica:**
- Pregunta usuario: ~50 tokens
- Contexto RAG: ~500 tokens
- Respuesta modelo: ~300 tokens
- **Total por interacción:** ~850 tokens ≈ **$0.01**

**Presupuesto hackathon estimado:**
- 1000 interacciones de prueba: ~$10
- 5000 interacciones demo: ~$50
- **Total:** $60-100 USD suficientes

### OpenRouter (Alternativa económica)
- Claude 3.5 Sonnet: ~$3/$15 por 1M tokens (input/output)
- GPT-4o via OpenRouter: Similar a OpenAI
- Llama 3.1 70B: Gratis o muy barato

---

## 🎯 Recomendación Final

### Para Malackathon (8 días disponibles):

**Arquitectura recomendada:**
1. **LLM Provider:** OpenAI GPT-4o (estabilidad y documentación)
2. **RAG:** In-memory embeddings con NumPy/FAISS (simplicidad)
3. **Tools:** 2-3 herramientas básicas (query Oracle, stats, export)
4. **Frontend:** Componente chat integrado en página existente

**Alternativa si presupuesto es crítico:**
1. **LLM Provider:** OpenRouter con Claude 3.5 Sonnet
2. Mismo stack técnico que opción principal
3. Coste ~30% menor

**NO recomendado para hackathon:**
- ❌ Oracle Gen AI (demasiado complejo, poca documentación)
- ❌ MCP (protocolo inmaduro, overhead innecesario)
- ❌ Vector DB dedicada (FAISS in-memory es suficiente)
- ❌ Fine-tuning de modelo (tiempo y coste prohibitivos)

---

## 🔒 Consideraciones de Seguridad

### Críticas para datos de salud:
1. **SQL Injection Prevention:**
   - Validación estricta de SQL generado
   - Whitelist de operaciones permitidas
   - Parametrización de queries

2. **Data Anonymization:**
   - NUNCA exponer CIP_SNS_RECODIFICADO completo en respuestas
   - Agregar datos antes de mostrar
   - Logging de todas las queries ejecutadas

3. **Rate Limiting:**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/chat/message")
   @limiter.limit("30/minute")  # 30 mensajes por minuto
   async def chat_endpoint(request: Request):
       ...
   ```

4. **Audit Trail:**
   - Log de todas las interacciones con timestamp
   - Almacenar queries ejecutadas para revisión
   - Monitoreo de patrones anómalos

---

## 📚 Recursos y Referencias

### Documentación Clave:
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [LangChain SQL Agent](https://python.langchain.com/docs/use_cases/sql/)
- [Oracle AI Vector Search](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/)

### Librerías Útiles:
```txt
# Añadir a requirements.txt
openai==1.35.0
anthropic==0.31.0  # Si usas Claude
tiktoken==0.7.0  # Token counting
numpy==1.26.0
faiss-cpu==1.8.0  # Vector search (opcional)
slowapi==0.1.9  # Rate limiting
```

---

## ✅ Checklist de Decisión

Antes de comenzar implementación, confirmar:
- [ ] LLM provider elegido y API key disponible
- [ ] Presupuesto de API aprobado (~$100 USD)
- [ ] Esquema Oracle completamente documentado
- [ ] Equipo tiene conocimientos básicos de async Python
- [ ] Frontend React puede extenderse con nuevo componente
- [ ] Estrategia de testing definida

---

**Preparado por:** Agente IA - Cursor  
**Para revisión por:** Equipo DAJER - Malackathon 2025  
**Próximo paso:** Decisión de arquitectura y kick-off de implementación
