# Arquitectura de Microservicios - Brain Backend

## Resumen Ejecutivo

El backend de Brain ha sido refactorizado desde una arquitectura monolítica hacia una **arquitectura basada en microservicios** para mejorar la escalabilidad, mantenibilidad y separación de responsabilidades. Esta migración establece las bases para un sistema modular y resiliente.

## Estructura de Directorios

```
app/back/
├── __init__.py
├── main.py                    # API Gateway - Punto de entrada único
├── config.py                  # Gestión de configuración
├── db.py                      # Gestión del pool de conexiones Oracle
├── schemas.py                 # Modelos Pydantic para validación
├── services/                  # Capa de Microservicios (Lógica de Negocio)
│   ├── __init__.py
│   ├── insights_service.py    # Servicio de insights y métricas
│   ├── visualization_service.py  # Servicio de visualización de datos
│   ├── health_service.py      # Servicio de monitoreo de salud
│   └── category_service.py    # Servicio de gestión de categorías
└── routers/                   # Capa de Routers (Adaptadores HTTP)
    ├── __init__.py
    ├── insights.py            # Endpoints /insights
    ├── visualization.py       # Endpoints /data/visualization
    ├── health.py              # Endpoints /health y /db/pool-status
    └── categories.py          # Endpoints /data/categories
```

## Capas de la Arquitectura

### 1. API Gateway (`main.py`)

**Responsabilidad**: Punto de entrada único que orquesta todos los microservicios.

**Funcionalidades**:
- Gestión del ciclo de vida de la aplicación (startup/shutdown)
- Configuración de CORS
- Registro de routers de microservicios
- Manejo global de excepciones
- Inicialización del pool de conexiones a base de datos

**Beneficios**:
- Única interfaz externa para todos los servicios
- Configuración centralizada de middleware
- Logging unificado
- Gestión consistente de errores

### 2. Capa de Routers (`routers/`)

**Responsabilidad**: Adaptadores que exponen los microservicios como endpoints HTTP RESTful.

**Routers implementados**:

#### `insights.py`
- **Endpoint**: `GET /insights`
- **Función**: Retrieves analytical insights and metrics
- **Delega a**: `insights_service.build_insight_summary()`

#### `visualization.py`
- **Endpoint**: `GET /data/visualization`
- **Función**: Returns aggregated data for charts with filters
- **Delega a**: `visualization_service.get_visualization_data()`

#### `health.py`
- **Endpoints**: 
  - `GET /health` - System health check
  - `GET /db/pool-status` - Connection pool status
- **Delega a**: `health_service.check_health()`, `health_service.get_pool_status_detailed()`

#### `categories.py`
- **Endpoint**: `GET /data/categories`
- **Función**: Returns list of diagnostic categories
- **Delega a**: `category_service.get_all_categories()`

**Principios**:
- Thin adapters: solo manejo de HTTP
- Validación de entrada con Pydantic
- Manejo de excepciones con HTTPException
- Logging de errores

### 3. Capa de Servicios - Microservicios (`services/`)

**Responsabilidad**: Lógica de negocio encapsulada en servicios independientes.

**Microservicios implementados**:

#### `insights_service.py`
**Función**: Generación de insights analíticos y métricas agregadas.

**Métodos principales**:
- `build_insight_summary()`: Genera resumen completo de insights
- `_build_sample_period()`: Formatea periodo de análisis
- `_get_fallback_insights()`: Proporciona datos de respaldo si la DB falla

**Consultas SQL**:
- Admisiones totales, estancia media, reingresos
- Rango de fechas del dataset
- Pacientes únicos
- Categoría diagnóstica más frecuente
- Distribuciones demográficas (edad, género)
- Admisiones en UCI

#### `visualization_service.py`
**Función**: Agregación de datos para visualizaciones con capacidad de filtrado.

**Métodos principales**:
- `get_visualization_data()`: Orquesta todas las consultas de visualización
- `_build_where_clause()`: Construye cláusulas WHERE dinámicas y seguras

**Datos generados**:
- Distribución por categoría diagnóstica
- Distribución por grupos de edad
- Series temporales (por mes)
- Distribución por género
- Distribución por duración de estancia

**Filtros soportados**:
- Rango de fechas (start_date, end_date)
- Género (1=hombre, 2=mujer)
- Rango de edad (age_min, age_max)
- Categoría diagnóstica
- Estado de reingreso (readmission)

#### `health_service.py`
**Función**: Monitoreo de salud del sistema y recursos.

**Métodos principales**:
- `check_health()`: Verifica conectividad a base de datos y estado general
- `get_pool_status_detailed()`: Retorna estadísticas detalladas del connection pool

**Métricas monitoreadas**:
- Estado de conexión a Oracle ADB
- Conexiones abiertas/ocupadas/disponibles en el pool
- Porcentaje de utilización del pool

#### `category_service.py`
**Función**: Gestión de categorías diagnósticas.

**Métodos principales**:
- `get_all_categories()`: Retorna lista de todas las categorías únicas

**Uso**:
- Poblado de dropdowns de filtros en el frontend
- Análisis de distribución de diagnósticos

### 4. Capa de Acceso a Datos

**Módulos compartidos**:

#### `db.py`
- Gestión del connection pool de Oracle
- Context managers para adquisición segura de conexiones
- Funciones utilitarias para queries y DML

#### `config.py`
- Carga de variables de entorno
- Validación de configuración
- Detección automática de Oracle Wallet path

#### `schemas.py`
- Modelos Pydantic para validación de datos
- Tipos compartidos entre servicios
- Serialización JSON automática

## Patrones de Diseño Aplicados

### 1. **Microservices Architecture**
- Servicios pequeños, independientes y con responsabilidad única
- Cada servicio puede evolucionar y desplegarse independientemente

### 2. **API Gateway Pattern**
- Punto de entrada único que enruta peticiones
- Simplifica la comunicación cliente-servidor
- Facilita cross-cutting concerns (CORS, logging, auth)

### 3. **Service Layer Pattern**
- Lógica de negocio encapsulada en la capa de servicios
- Routers actúan como thin adapters
- Reutilización de servicios desde múltiples endpoints

### 4. **Dependency Injection**
- Servicios reciben dependencias (DB connections) de forma explícita
- Facilita testing con mocks

### 5. **Repository Pattern (implícito)**
- Módulo `db.py` actúa como repository
- Abstrae detalles de acceso a datos

## Beneficios de la Refactorización

### Escalabilidad
- Cada microservicio puede escalarse horizontalmente de forma independiente
- Connection pooling optimizado por servicio si se necesita
- Facilita la migración a contenedores/Kubernetes

### Mantenibilidad
- Código más limpio y organizado
- Responsabilidades claramente delimitadas
- Fácil localización de lógica de negocio
- Reducción de acoplamiento entre componentes

### Testabilidad
- Servicios pueden testearse de forma aislada
- Mocking simplificado de dependencias
- Tests unitarios más enfocados

### Resiliencia
- Fallos en un servicio no afectan a otros
- Posibilidad de implementar circuit breakers
- Degradación elegante con fallbacks

### Desarrollo en Equipo
- Múltiples desarrolladores pueden trabajar en servicios diferentes
- Menos conflictos de merge
- Iteración más rápida

## Compatibilidad con API Existente

La refactorización **mantiene completa compatibilidad** con la API existente. Todos los endpoints siguen funcionando igual:

| Endpoint Original | Estado | Implementación Nueva |
|-------------------|--------|---------------------|
| `GET /` | ✅ Funcional | `main.py` |
| `GET /health` | ✅ Funcional | `routers/health.py` → `health_service.py` |
| `GET /insights` | ✅ Funcional | `routers/insights.py` → `insights_service.py` |
| `GET /data/visualization` | ✅ Funcional | `routers/visualization.py` → `visualization_service.py` |
| `GET /data/categories` | ✅ Funcional | `routers/categories.py` → `category_service.py` |
| `GET /db/pool-status` | ✅ Funcional | `routers/health.py` → `health_service.py` |

**No se requieren cambios en el frontend** - la API es completamente retrocompatible.

## Migración y Despliegue

### Pasos de Migración (Completados)

1. ✅ Crear estructura de directorios `services/` y `routers/`
2. ✅ Extraer lógica de insights a `insights_service.py`
3. ✅ Extraer lógica de visualización a `visualization_service.py`
4. ✅ Extraer lógica de health a `health_service.py`
5. ✅ Extraer lógica de categorías a `category_service.py`
6. ✅ Crear routers que deleguen a servicios
7. ✅ Refactorizar `main.py` como API Gateway
8. ✅ Registrar todos los routers en el gateway
9. ✅ Verificar compatibilidad con API existente
10. ✅ Actualizar documentación y diagrama de arquitectura

### Despliegue

**Docker**: No requiere cambios en el Dockerfile existente, la estructura de microservicios es compatible.

**Comandos**:
```bash
# Desarrollo local
cd app/back
python -m uvicorn main:app --reload

# Docker
docker-compose up --build

# Producción
./deploy.sh
```

## Testing

### Tests Unitarios Recomendados

```python
# Ejemplo: tests/test_insights_service.py
import pytest
from unittest.mock import Mock, patch
from app.back.services.insights_service import build_insight_summary

def test_build_insight_summary_success():
    with patch('app.back.services.insights_service.test_connection', return_value=True):
        with patch('app.back.services.insights_service.get_connection'):
            result = build_insight_summary()
            assert result.database_connected == True
            assert len(result.highlight_phrases) > 0

def test_build_insight_summary_db_failure():
    with patch('app.back.services.insights_service.test_connection', return_value=False):
        result = build_insight_summary()
        assert result.database_connected == False
        assert "no disponible" in result.sample_period.lower()
```

### Tests de Integración

```bash
# Health check
curl http://localhost:8000/health

# Insights
curl http://localhost:8000/insights

# Visualization con filtros
curl "http://localhost:8000/data/visualization?gender=2&age_min=18&age_max=29"

# Categories
curl http://localhost:8000/data/categories
```

## Roadmap Futuro

### Fase 2: Separación Física de Microservicios
- Desplegar cada microservicio en su propio contenedor
- Implementar service discovery (Consul, etcd)
- API Gateway como reverse proxy (Kong, Traefik)

### Fase 3: Observabilidad
- Logging distribuido (ELK stack)
- Tracing distribuido (Jaeger, OpenTelemetry)
- Métricas por servicio (Prometheus, Grafana)

### Fase 4: Resiliencia Avanzada
- Circuit breakers (resilience4py)
- Rate limiting por servicio
- Retry policies con backoff exponencial

### Fase 5: Event-Driven Architecture
- Message broker (RabbitMQ, Kafka)
- Comunicación asíncrona entre servicios
- Event sourcing para auditoría

## Conclusión

La migración a arquitectura de microservicios proporciona una base sólida para el crecimiento futuro de Brain. El sistema ahora es:

- ✅ **Modular**: Servicios independientes con responsabilidades claras
- ✅ **Escalable**: Preparado para crecimiento y alta carga
- ✅ **Mantenible**: Código limpio y organizado
- ✅ **Testeable**: Facilita testing aislado de componentes
- ✅ **Resiliente**: Fallos aislados no afectan todo el sistema
- ✅ **Compatible**: Sin cambios en la API pública
- ✅ **Documentado**: Arquitectura clara y bien documentada

Esta refactorización posiciona a Brain como una plataforma robusta y profesional para investigación en salud mental, lista para impresionar al jurado del Malackathon 2025. 🧠✨

