# Fix de Conexión Oracle en Producción

## Problema Identificado

El backend de producción muestra el error:
```
ERROR:app.back.db:Error acquiring connection (busy: 0/50): DPY-4005: timed out waiting for the connection pool to return a connection
```

**Causa raíz**: El archivo `sqlnet.ora` del wallet tenía un placeholder `?/network/admin` que Oracle no puede resolver correctamente en contenedores Docker.

## Cambios Realizados

### 1. **Corrección de `sqlnet.ora`** (CRÍTICO)
- Cambió `DIRECTORY="?/network/admin"` → `DIRECTORY="/app/oracle_wallet"`
- Añadido `SQLNET.WALLET_OVERRIDE = TRUE` para forzar el uso del wallet

### 2. **Mejoras en `db.py`**
- Pool inicia con `min=0` conexiones para startup más rápido
- Conexiones se establecen gradualmente después del startup
- Timeout aumentado a 60s en producción para compensar latencia de red
- Añadidos parámetros `ping_interval` y `stmtcachesize` para estabilidad
- Mejor manejo de errores con warnings en vez de crashes

### 3. **Mejoras en `main.py`**
- Detección automática de entorno producción
- Timeout de 60s en producción vs 30s en desarrollo
- La app continúa el startup aunque fallen conexiones iniciales
- Mejor logging de estado de conexión

### 4. **Script de Diagnóstico**
- Nuevo script `scripts/diagnose_oracle_connection.py` para debugging

## Pasos para Desplegar el Fix

### Opción A: Despliegue Rápido (Recomendado)

```bash
# 1. Conectar al servidor de producción
ssh usuario@158.179.212.221

# 2. Ir al directorio del proyecto
cd /ruta/a/malackathon25

# 3. Hacer pull de los cambios
git pull origin main

# 4. Reconstruir y reiniciar solo el backend
docker-compose -f docker-compose.prod.yml up -d --build --force-recreate backend

# 5. Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Opción B: Despliegue Completo

```bash
# 1. Conectar al servidor
ssh usuario@158.179.212.221

# 2. Ir al directorio del proyecto
cd /ruta/a/malackathon25

# 3. Hacer pull de los cambios
git pull origin main

# 4. Parar todos los servicios
docker-compose -f docker-compose.prod.yml down

# 5. Reconstruir imágenes
docker-compose -f docker-compose.prod.yml build

# 6. Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

# 7. Verificar estado
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

## Verificación del Fix

### 1. Verificar logs del backend

```bash
docker-compose -f docker-compose.prod.yml logs backend | tail -50
```

**Deberías ver**:
```
✓ Connection pool created successfully
✓ Successfully established connection 1/1
✓ Connection pool ready with 1/1 initial connection(s)
```

**NO deberías ver**:
```
✗ DPY-4005: timed out waiting for the connection pool
```

### 2. Verificar health endpoint

```bash
curl http://localhost/api/health
```

**Respuesta esperada**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "..."
}
```

### 3. Ejecutar diagnóstico completo

```bash
# Dentro del contenedor backend
docker exec -it malackathon-backend python scripts/diagnose_oracle_connection.py
```

Este script verificará:
- ✓ Configuración de entorno
- ✓ Archivos del wallet
- ✓ Conectividad de red a Oracle Cloud
- ✓ Conexión real a la base de datos

## Troubleshooting

### Si sigue sin funcionar después del despliegue:

#### 1. Verificar que el wallet esté montado correctamente

```bash
docker exec -it malackathon-backend ls -la /app/oracle_wallet/
```

Deberías ver:
- `cwallet.sso`
- `tnsnames.ora`
- `sqlnet.ora`
- `truststore.jks`

#### 2. Verificar contenido de sqlnet.ora

```bash
docker exec -it malackathon-backend cat /app/oracle_wallet/sqlnet.ora
```

Debe contener:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="/app/oracle_wallet")))
SSL_SERVER_DN_MATCH=yes
SQLNET.WALLET_OVERRIDE = TRUE
```

#### 3. Verificar variables de entorno

```bash
docker exec -it malackathon-backend env | grep -E "ORACLE|TNS"
```

Debe mostrar:
- `ORACLE_DSN=fagfefcg84y83s1a_medium`
- `ORACLE_USER=DAJER_ADMIN`
- `TNS_ADMIN=/app/oracle_wallet`

#### 4. Probar conectividad de red

```bash
# Desde el contenedor
docker exec -it malackathon-backend ping -c 3 adb.eu-madrid-1.oraclecloud.com

# Probar puerto TCP
docker exec -it malackathon-backend nc -zv adb.eu-madrid-1.oraclecloud.com 1522
```

#### 5. Verificar firewall de Oracle Cloud

Si el problema persiste, puede ser un **firewall en Oracle Cloud**:

1. Acceder a OCI Console → Autonomous Database
2. Ir a **Network** → **Access Control List**
3. Verificar que la IP pública del servidor esté en la whitelist:
   - IP del servidor: `158.179.212.221`
4. O cambiar a **Allow secure access from everywhere** temporalmente

## Posibles Problemas Adicionales

### Problema: "ORA-01017: invalid username/password"

**Solución**: Verificar credenciales en `.env`

```bash
# En el servidor
cat .env | grep ORACLE
```

### Problema: "DPY-6005: cannot connect to database"

**Solución**: Wallet corrupto o incorrecto

1. Re-descargar wallet desde OCI Console
2. Reemplazar archivos en `app/oracle_wallet/`
3. Reconstruir contenedor

### Problema: Timeout persistente

**Solución**: Verificar acceso de red

```bash
# Probar desde el HOST (no el contenedor)
telnet adb.eu-madrid-1.oraclecloud.com 1522
```

Si esto falla, el problema es **firewall** o **routing de red**.

## Contacto de Emergencia

Si nada funciona, verificar:

1. ✓ Oracle Autonomous Database está **RUNNING** en OCI Console
2. ✓ IP del servidor en whitelist de Oracle Cloud
3. ✓ Wallet no ha expirado (tienen fecha de caducidad)
4. ✓ Usuario `DAJER_ADMIN` existe y tiene permisos

## Resumen de Cambios en Git

```bash
# Ver cambios realizados
git diff HEAD~1

# Archivos modificados:
# - app/oracle_wallet/sqlnet.ora (FIX CRÍTICO)
# - app/back/db.py (resilencia)
# - app/back/main.py (timeout producción)
# - scripts/diagnose_oracle_connection.py (nuevo)
```

## Logs a Buscar

**✓ Éxito**:
```
INFO:app.back.db:Connection pool created successfully
INFO:app.back.db:Successfully established connection 1/1
INFO:app.back.main:Database connection pool initialized successfully
```

**✗ Fallo**:
```
ERROR:app.back.db:DPY-4005: timed out
WARNING:app.back.db:No initial connections could be established
```

---

**Fecha**: 2025-10-16  
**Versión**: 2.0.1  
**Prioridad**: CRÍTICA - Bloquea toda funcionalidad que requiere base de datos

