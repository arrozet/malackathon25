# Malackathon 2025

The winner takes it all.

## 📋 Descripción

Aplicación FastAPI dockerizada con integración a Oracle Autonomous Database en Oracle Cloud. Esta aplicación proporciona una API REST con conexión segura mediante Oracle Wallet.

## 🏗️ Arquitectura

- **Framework**: FastAPI 0.111.0
- **Base de Datos**: Oracle Autonomous Database (Oracle Cloud)
- **Driver**: python-oracledb 2.2.0 (thin mode)
- **Autenticación**: Oracle Wallet encriptado
- **Contenedorización**: Docker + Docker Compose

## 📁 Estructura del Proyecto

```
malackathon25/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuración y variables de entorno
│   ├── db.py              # Gestión de conexiones a Oracle
│   ├── main.py            # Aplicación FastAPI principal
│   └── oracle_wallet/     # Wallet de Oracle Cloud (encriptado)
├── scripts/
│   └── test_connection.py # Script de prueba de conexión
├── docker/
│   ├── Dockerfile         # Imagen Docker de la aplicación
│   └── docker-compose.yml # Orquestación de servicios
├── .env                   # Variables de entorno (NO SUBIR A GIT)
├── requirements.txt       # Dependencias Python
└── README.md
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose instalados
- Archivo `.env` configurado con credenciales de Oracle Cloud
- Oracle Wallet en `app/oracle_wallet/`

### Configuración

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd malackathon25
```

2. **Verificar el archivo `.env`**:
```env
ORACLE_DSN=fagfefcg84y83s1a_medium
ORACLE_USER=DAJER_ADMIN
ORACLE_PASSWORD=tu_password
TNS_ADMIN=/app/oracle_wallet
ORACLE_WALLET_PASSWORD=tu_wallet_password
APP_ENV=prod
DEBUG=false
```

3. **Verificar el Oracle Wallet**:
Asegúrate de que el directorio `app/oracle_wallet/` contiene:
- `cwallet.sso`
- `tnsnames.ora`
- `sqlnet.ora`
- Otros archivos del wallet

### Ejecución con Docker

#### Opción 1: Docker Compose (Recomendado)

```bash
# Construir y levantar servicios
docker-compose -f docker/docker-compose.yml up --build

# En modo detached (background)
docker-compose -f docker/docker-compose.yml up -d --build

# Ver logs
docker-compose -f docker/docker-compose.yml logs -f api

# Detener servicios
docker-compose -f docker/docker-compose.yml down
```

#### Opción 2: Docker directo

```bash
# Construir imagen
docker build -f docker/Dockerfile -t malackathon-api:latest .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env malackathon-api:latest
```

#### Opción 3: Scripts de utilidad

```bash
# Linux/Mac
chmod +x docker.sh
./docker.sh

# Windows PowerShell
.\docker.ps1

# Windows CMD
docker.bat
```

### Ejecución Local (Sin Docker)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Pruebas

### Probar conexión a la base de datos

```bash
# Dentro del contenedor
docker exec -it malackathon-api python scripts/test_connection.py

# Local
python scripts/test_connection.py
```

### Endpoints Disponibles

Una vez que la aplicación esté corriendo, puedes acceder a:

- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc
- **Root endpoint**: http://localhost:8000/
- **Health check**: http://localhost:8000/health
- **Test DB query**: http://localhost:8000/db/test
- **Pool status**: http://localhost:8000/db/pool-status

### Ejemplo de respuestas

#### GET /health
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "dsn": "fagfefcg84y83s1a_medium",
    "pool": {
      "opened": 2,
      "busy": 0,
      "max": 10,
      "min": 2
    }
  }
}
```

#### GET /db/test
```json
{
  "status": "success",
  "query": "Test query executed successfully",
  "result": {
    "timestamp": "2025-10-14 10:30:45",
    "user": "DAJER_ADMIN",
    "database": "FAGFEFCG84Y83S1A"
  }
}
```

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `ORACLE_DSN` | Nombre del servicio en tnsnames.ora | `fagfefcg84y83s1a_medium` |
| `ORACLE_USER` | Usuario de la base de datos | `DAJER_ADMIN` |
| `ORACLE_PASSWORD` | Contraseña del usuario | *(requerido)* |
| `TNS_ADMIN` | Ruta al directorio del wallet | `/app/oracle_wallet` |
| `ORACLE_WALLET_PASSWORD` | Contraseña del wallet encriptado | *(requerido)* |
| `APP_ENV` | Entorno de la aplicación | `prod` |
| `DEBUG` | Modo debug | `false` |

### Connection Pool

Configuración del pool de conexiones en `app/main.py`:

```python
initialize_connection_pool(
    min_connections=2,    # Conexiones mínimas en el pool
    max_connections=10,   # Conexiones máximas en el pool
    increment=2           # Incremento al crecer el pool
)
```

## 📚 Módulos Principales

### `app/config.py`
Gestiona la carga de variables de entorno y proporciona una interfaz centralizada para la configuración.

### `app/db.py`
Maneja el pool de conexiones a Oracle, proporciona funciones de utilidad para:
- Inicialización y cierre del pool
- Ejecución de queries (SELECT)
- Ejecución de DML (INSERT, UPDATE, DELETE)
- Context managers para gestión segura de conexiones

### `app/main.py`
Aplicación FastAPI principal con:
- Gestión del ciclo de vida (startup/shutdown)
- Endpoints de health check
- Endpoints de prueba de BD
- Manejadores de excepciones globales

## 🐛 Troubleshooting

### Error: "DPI-1047: Cannot locate a 64-bit Oracle Client library"
- **Solución**: Usa el modo thin de oracledb (ya configurado). No requiere Oracle Instant Client.

### Error: "ORA-12170: TNS:Connect timeout occurred"
- Verifica que el wallet esté en la ubicación correcta
- Confirma que `TNS_ADMIN` apunta al directorio correcto
- Revisa que el `ORACLE_DSN` coincida con un servicio en `tnsnames.ora`

### Error: "ORA-01017: invalid username/password"
- Verifica las credenciales en `.env`
- Confirma que el usuario tiene permisos en la base de datos

### Error: "DPI-1010: not connected"
- Verifica la contraseña del wallet (`ORACLE_WALLET_PASSWORD`)
- Confirma que los archivos del wallet no estén corruptos

### Logs del contenedor
```bash
# Ver logs en tiempo real
docker logs -f malackathon-api

# Ver últimas 100 líneas
docker logs --tail 100 malackathon-api
```

## 🔒 Seguridad

- ⚠️ **NUNCA** subas el archivo `.env` al repositorio
- ⚠️ **NUNCA** subas el wallet sin encriptar
- ✅ Usa variables de entorno para todas las credenciales
- ✅ El wallet debe estar encriptado con contraseña
- ✅ Usa HTTPS en producción
- ✅ Implementa rate limiting y autenticación según necesidades

## 🛠️ Desarrollo

### Añadir nuevos endpoints

Edita `app/main.py` y añade tus rutas:

```python
@app.get("/mi-endpoint")
async def mi_funcion():
    # Tu lógica aquí
    result = execute_query("SELECT * FROM mi_tabla")
    return {"data": result}
```

### Ejecutar en modo desarrollo

```python
# En app/main.py o desde terminal
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 TODO

- [ ] Implementar autenticación y autorización
- [ ] Añadir más endpoints de negocio
- [ ] Implementar caché (Redis)
- [ ] Añadir tests unitarios y de integración
- [ ] Configurar CI/CD
- [ ] Añadir monitoring y métricas (Prometheus)
- [ ] Implementar rate limiting
- [ ] Documentar APIs adicionales

## 📄 Licencia

Ver archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

Malackathon 2025 - DAJER Team

---

**¡Buena suerte en el hackathon! 🚀**
