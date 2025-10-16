# 📋 Brain - Referencia de Configuración

## Estructura de Configuración

El proyecto Brain usa un sistema de configuración **centralizado** basado en variables de entorno.

### 📁 Ubicación del archivo .env

```
malackathon25/               ← Raíz del proyecto
├── .env                     ← ✅ ARCHIVO .ENV AQUÍ (copiar de .env.example)
├── .env.example             ← Template de configuración
├── app/
│   ├── back/
│   │   ├── config.py        ← Módulo que carga el .env
│   │   └── ...
│   └── front/
└── ...
```

**⚠️ IMPORTANTE**: 
- El archivo `.env` va en la **raíz del proyecto**, no dentro de `app/back/`
- Todas las variables se gestionan centralizadamente a través de `config.py`

## Variables de Entorno

### 🔐 Oracle Database

```bash
# Conexión a Oracle Autonomous Database
ORACLE_USER=tu_usuario
ORACLE_PASSWORD=tu_password
ORACLE_DSN=tu_servicio_bd
TNS_ADMIN=./app/oracle_wallet
ORACLE_WALLET_PASSWORD=tu_wallet_password
```

### 🤖 AI Service (xAI - Grok-4)

```bash
# API Key de xAI para Grok-4 Fast Reasoning
# Obtener en: https://console.x.ai/
XAI_API_KEY=xai-tu_key_aqui

# OPCIONAL - Tavily API para búsqueda en internet
# Obtener en: https://tavily.com/
TAVILY_API_KEY=tvly-tu_key_aqui
```

### 🌐 Application Settings

```bash
# Entorno de ejecución
APP_ENV=development  # o production

# Modo debug (activa logs detallados)
DEBUG=True  # o False

# Orígenes CORS permitidos (separados por comas)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Cómo funciona config.py

El módulo `app/back/config.py` centraliza toda la configuración:

### 1. Carga automática del .env

```python
from dotenv import load_dotenv
load_dotenv()  # Carga .env desde la raíz del proyecto
```

### 2. Clase Config centralizada

```python
class Config:
    # Oracle Database
    ORACLE_USER: str = os.getenv("ORACLE_USER", "")
    ORACLE_PASSWORD: str = os.getenv("ORACLE_PASSWORD", "")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "")
    
    # AI Service
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Application
    APP_ENV: str = os.getenv("APP_ENV", "prod")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
```

### 3. Uso en los servicios

```python
# Ejemplo en ai_service.py
from app.back.config import config

class AIService:
    def __init__(self):
        # Leer configuración centralizada
        if not config.XAI_API_KEY:
            raise ValueError("XAI_API_KEY no configurada")
        
        self.llm = ChatOpenAI(
            api_key=config.XAI_API_KEY,  # Desde config
            ...
        )
```

## Seguridad

### Variables sensibles enmascaradas

El método `display_config()` enmascara valores sensibles en logs:

```python
config.display_config()
# Output:
# {
#   "ORACLE_PASSWORD": "***",
#   "XAI_API_KEY": "***",
#   "TAVILY_API_KEY": "***",
#   ...
# }
```

### .gitignore

El archivo `.env` está excluido del control de versiones:

```gitignore
.env
*.env
!.env.example
```

## Setup Rápido

### 1. Copiar template

```bash
cp .env.example .env
```

### 2. Editar .env

```bash
# Linux/Mac
nano .env

# Windows
notepad .env
```

### 3. Añadir tus valores

```bash
# Oracle Database (si ya está configurado, dejar como está)
ORACLE_USER=admin
ORACLE_PASSWORD=tu_password_real

# xAI API Key (NUEVO - AÑADIR)
XAI_API_KEY=xai-tu_key_real_de_console_x_ai

# Tavily (opcional)
TAVILY_API_KEY=tvly-tu_key_opcional
```

### 4. Verificar configuración

```python
# Desde Python
from app.back.config import config
print(config.display_config())
```

O desde terminal:

```bash
python -c "from app.back.config import config; print(config.display_config())"
```

## Validación de Configuración

El módulo config incluye validación automática para Oracle:

```python
config.validate()  # Lanza ValueError si faltan vars requeridas
```

Para validar manualmente:

```bash
python -c "from app.back.config import config; config.validate()"
```

## Variables por Servicio

### Backend Principal
- `ORACLE_*` - Conexión a base de datos
- `APP_ENV`, `DEBUG` - Configuración de la app
- `CORS_ORIGINS` - Seguridad CORS

### AI Service
- `XAI_API_KEY` - **Requerido** para Grok-4
- `TAVILY_API_KEY` - Opcional para búsqueda internet

### Frontend (si aplica)
- Se configura desde `app/front/.env` (separado)
- Lee `VITE_API_URL` para conectar al backend

## Troubleshooting

### Error: "XAI_API_KEY no configurada"
✅ **Solución**: Añade `XAI_API_KEY=...` en `.env` de la raíz

### Error: "Missing required environment variables"
✅ **Solución**: Ejecuta `config.validate()` para ver qué falta

### La configuración no se carga
✅ **Verificar**:
1. Archivo `.env` está en la raíz del proyecto
2. El archivo tiene permisos de lectura
3. No hay errores de sintaxis en el .env

### Ver configuración actual

```bash
cd app/back
python -c "from config import config; import json; print(json.dumps(config.display_config(), indent=2))"
```

## Ejemplos de .env

### Desarrollo local

```bash
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

ORACLE_USER=admin
ORACLE_PASSWORD=dev_password
ORACLE_DSN=dev_service

XAI_API_KEY=xai-dev-key-here
```

### Producción

```bash
APP_ENV=production
DEBUG=False
CORS_ORIGINS=https://brain.example.com

ORACLE_USER=brain_user
ORACLE_PASSWORD=secure_prod_password
ORACLE_DSN=prod_service

XAI_API_KEY=xai-prod-key-here
```

---

**Documentación para Malackathon 2025**  
**Sistema de Configuración Centralizado**

