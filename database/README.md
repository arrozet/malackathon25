# Base de Datos - Oracle Autonomous Database 23ai

## Descripción General

Este directorio contiene los scripts SQL para la creación y carga de la base de datos normalizada del proyecto Brain - II Malackathon 2025. El esquema está diseñado para almacenar y analizar datos de hospitalizaciones en salud mental de manera estructurada, segura y optimizada.

## Arquitectura del Esquema

### Normalización (3FN)

El esquema sigue principios de normalización hasta la Tercera Forma Normal (3FN) para:
- Eliminar redundancia de datos
- Garantizar integridad referencial
- Facilitar mantenimiento y escalabilidad
- Optimizar consultas analíticas

### Tablas Principales

#### 1. **Tablas de Catálogos** (Dimensiones)
- `comunidades_autonomas`: Comunidades autónomas de España
- `paises`: Catálogo de países (códigos ISO)
- `centros_hospitalarios`: Centros hospitalarios
- `diagnosticos_cie`: Códigos diagnósticos CIE-10
- `procedimientos`: Catálogo de procedimientos clínicos

#### 2. **Tabla de Pacientes** (Anonimizada)
- `pacientes`: Información demográfica anonimizada
  - Los nombres originales se sustituyen por identificadores `PACIENTE_XXXXXXXX`
  - Incluye edad, sexo, país de nacimiento, comunidad de residencia

#### 3. **Tabla Central**
- `episodios`: Episodios de hospitalización
  - Información temporal (fechas de ingreso y alta)
  - Clasificación APR-DRG (severidad, riesgo, coste)
  - Métricas derivadas (estancia, diagnósticos totales, etc.)

#### 4. **Tablas de Relación** (Muchos a Muchos)
- `episodios_diagnosticos`: Relación entre episodios y diagnósticos
  - Permite múltiples diagnósticos por episodio
  - Distingue diagnóstico principal de secundarios
- `episodios_procedimientos`: Relación entre episodios y procedimientos
  - Permite múltiples procedimientos por episodio
  - Mantiene el orden de realización

### Vistas Analíticas

#### Vista Principal: `VISTA_MUY_INTERESANTE`
Vista desnormalizada que combina información de todas las tablas para facilitar:
- Análisis exploratorio de datos
- Visualizaciones en la aplicación web Brain
- Consultas sin necesidad de JOINs complejos
- Códigos categóricos con descripciones legibles

**Propósito para el Hackathon:** Esta vista es la interfaz principal para el usuario `malackathon` y permite acceso simplificado a todos los datos relevantes para investigación.

#### Vistas Adicionales
- `resumen_diagnosticos_principales`: Estadísticas agregadas por diagnóstico
- `resumen_centros`: Métricas por centro hospitalario
- `resumen_temporal`: Evolución temporal de episodios

## Archivos del Directorio

### `create.sql`
Script principal de creación del esquema. Incluye:
- Definición de secuencias para IDs autoincrementales
- Creación de todas las tablas con constraints
- Definición de índices para optimización
- Creación de vistas analíticas
- Triggers para auditoría y validación automática
- Instrucciones para crear usuario `malackathon` con permisos de lectura

**Orden de ejecución:** PRIMERO

### `load_data.sql`
Script de carga de datos (ETL) desde `SaludMental_limpio.xlsx`. Incluye:
- Creación de tabla staging temporal
- Instrucciones para importar datos desde Excel
- Transformación y normalización de datos
- Población de tablas de catálogos
- Anonimización de pacientes
- Carga de episodios y relaciones
- Validaciones de integridad
- Estadísticas de carga

**Orden de ejecución:** SEGUNDO (después de `create.sql`)

### `README.md`
Este archivo de documentación.

## Guía de Implementación

### Prerequisitos

1. **Oracle Autonomous Database 23ai** provisionada en OCI
2. Acceso con usuario ADMIN o con privilegios suficientes
3. Cliente SQL (SQL*Plus, SQL Developer, o interfaz web de OCI)
4. Archivo `SaludMental_limpio.xlsx` generado por `data/R/featuresEngineering.qmd`

### Paso 1: Conexión a la Base de Datos

#### Opción A: SQL Developer
```
Host: <autonomous_db_hostname>
Puerto: 1522
Servicio: <service_name>
Usuario: ADMIN
Contraseña: <admin_password>
```

#### Opción B: SQL*Plus
```bash
sqlplus admin/<password>@<connection_string>
```

#### Opción C: OCI Cloud Shell
```bash
sql /nolog
conn admin/<password>@<connection_string>
```

### Paso 2: Ejecutar Script de Creación

```sql
-- Conectar como ADMIN
@create.sql
```

**Tiempo estimado:** 2-5 minutos

**Validación:**
```sql
-- Verificar tablas creadas
SELECT table_name FROM user_tables ORDER BY table_name;

-- Verificar vistas creadas
SELECT view_name FROM user_views ORDER BY view_name;

-- Verificar secuencias
SELECT sequence_name FROM user_sequences ORDER BY sequence_name;
```

### Paso 3: Cargar Datos

#### 3.1 Preparar Archivo de Datos

El archivo `SaludMental_limpio.xlsx` debe convertirse a CSV para facilitar la carga:

**En R:**
```r
library(readxl)
library(readr)

datos <- read_excel("../SaludMental_limpio.xlsx")
write_csv(datos, "../SaludMental_limpio.csv")
```

#### 3.2 Importar a Tabla Staging

**Opción A: SQL Developer Import Wizard**
1. Expandir conexión → Tables
2. Clic derecho en `STAGING_SALUD_MENTAL` → Import Data
3. Seleccionar `SaludMental_limpio.csv`
4. Mapear columnas automáticamente
5. Ejecutar importación

**Opción B: SQL*Loader**
```bash
sqlldr userid=admin/<password>@<connection> \
       control=load_data.ctl \
       log=load_data.log \
       bad=load_data.bad
```

**Opción C: DBMS_CLOUD (si el archivo está en Object Storage)**
```sql
BEGIN
    DBMS_CLOUD.COPY_DATA(
        table_name      => 'STAGING_SALUD_MENTAL',
        credential_name => 'OBJ_STORE_CRED',
        file_uri_list   => 'https://objectstorage.region.oraclecloud.com/.../SaludMental_limpio.csv',
        format          => json_object('type' value 'csv', 'skipheaders' value '1')
    );
END;
/
```

#### 3.3 Ejecutar Transformación y Carga

```sql
@load_data.sql
```

**Tiempo estimado:** 10-20 minutos (depende del tamaño del dataset)

**Validación:**
```sql
-- Ver resumen de registros cargados
SELECT 'Episodios' AS tabla, COUNT(*) AS registros FROM episodios
UNION ALL
SELECT 'Pacientes', COUNT(*) FROM pacientes
UNION ALL
SELECT 'Diagnósticos', COUNT(*) FROM diagnosticos_cie
UNION ALL
SELECT 'Centros', COUNT(*) FROM centros_hospitalarios;

-- Probar vista principal
SELECT * FROM vista_muy_interesante WHERE ROWNUM <= 10;
```

### Paso 4: Crear Usuario Malackathon

```sql
-- Conectar como ADMIN
CREATE USER malackathon IDENTIFIED BY "<PASSWORD_PROPORCIONADA>";

-- Otorgar permisos de conexión
GRANT CREATE SESSION TO malackathon;

-- Otorgar permisos de lectura en todas las tablas
GRANT SELECT ON comunidades_autonomas TO malackathon;
GRANT SELECT ON paises TO malackathon;
GRANT SELECT ON centros_hospitalarios TO malackathon;
GRANT SELECT ON diagnosticos_cie TO malackathon;
GRANT SELECT ON procedimientos TO malackathon;
GRANT SELECT ON pacientes TO malackathon;
GRANT SELECT ON episodios TO malackathon;
GRANT SELECT ON episodios_diagnosticos TO malackathon;
GRANT SELECT ON episodios_procedimientos TO malackathon;

-- Otorgar permisos de lectura en vistas
GRANT SELECT ON vista_muy_interesante TO malackathon;
GRANT SELECT ON resumen_diagnosticos_principales TO malackathon;
GRANT SELECT ON resumen_centros TO malackathon;
GRANT SELECT ON resumen_temporal TO malackathon;

-- Crear sinónimos públicos para facilitar acceso
CREATE PUBLIC SYNONYM vista_muy_interesante FOR admin.vista_muy_interesante;
CREATE PUBLIC SYNONYM resumen_diagnosticos_principales FOR admin.resumen_diagnosticos_principales;
CREATE PUBLIC SYNONYM resumen_centros FOR admin.resumen_centros;
CREATE PUBLIC SYNONYM resumen_temporal FOR admin.resumen_temporal;
```

### Paso 5: Configurar Conexión en Backend

Actualizar `app/back/config.py` con las credenciales:

```python
DB_USER = "malackathon"  # Usuario de solo lectura
DB_PASSWORD = "<PASSWORD_PROPORCIONADA>"
DB_DSN = "<connection_string>"
```

Asegurar que el Oracle Wallet está en `app/oracle_wallet/`.

## Consultas de Ejemplo

### Consulta 1: Top 10 diagnósticos más frecuentes
```sql
SELECT 
    diagnostico_principal,
    diagnostico_descripcion,
    COUNT(*) AS total_casos,
    ROUND(AVG(estancia_dias), 2) AS estancia_promedio,
    ROUND(AVG(coste_apr), 2) AS coste_promedio
FROM vista_muy_interesante
WHERE diagnostico_principal IS NOT NULL
GROUP BY diagnostico_principal, diagnostico_descripcion
ORDER BY total_casos DESC
FETCH FIRST 10 ROWS ONLY;
```

### Consulta 2: Distribución por severidad y sexo
```sql
SELECT 
    sexo,
    severidad_descripcion,
    COUNT(*) AS casos,
    ROUND(AVG(estancia_dias), 2) AS estancia_promedio
FROM vista_muy_interesante
WHERE severidad_descripcion IS NOT NULL
GROUP BY sexo, severidad_descripcion
ORDER BY sexo, severidad_descripcion;
```

### Consulta 3: Evolución temporal de ingresos
```sql
SELECT 
    TO_CHAR(fecha_ingreso, 'YYYY-MM') AS periodo,
    COUNT(*) AS total_ingresos,
    ROUND(AVG(estancia_dias), 2) AS estancia_promedio,
    ROUND(AVG(coste_apr), 2) AS coste_promedio
FROM vista_muy_interesante
GROUP BY TO_CHAR(fecha_ingreso, 'YYYY-MM')
ORDER BY periodo;
```

### Consulta 4: Centros con mayor carga asistencial
```sql
SELECT * FROM resumen_centros
ORDER BY total_episodios DESC
FETCH FIRST 10 ROWS ONLY;
```

## Características Avanzadas

### Triggers Automáticos

El esquema incluye triggers que se ejecutan automáticamente:

1. **`trg_episodios_calc`**: Calcula campos derivados al insertar/actualizar episodios
   - Duración del episodio
   - Grupo etario
   - Día de la semana y mes del ingreso

2. **`trg_episodio_diag_count`**: Actualiza contadores de diagnósticos
   - Incrementa/decrementa `diagnosticos_totales`
   - Actualiza flag `tiene_comorbilidad`

3. **`trg_episodio_proc_count`**: Actualiza contadores de procedimientos
   - Incrementa/decrementa `procedimientos_totales`
   - Actualiza flag `tiene_procedimiento`

4. **`trg_episodios_update`**: Auditoría automática
   - Actualiza `fecha_modificacion` en cada UPDATE

### Índices Optimizados

Se han creado índices específicos para optimizar las consultas más frecuentes:
- Búsquedas por fecha de ingreso
- Filtros por diagnóstico, centro, comunidad
- Agregaciones por severidad y riesgo
- Análisis de costes y estancias

### Constraints de Integridad

- **Foreign Keys**: Garantizan relaciones válidas entre tablas
- **Check Constraints**: Validan rangos y valores permitidos
- **Unique Constraints**: Evitan duplicados en códigos y claves
- **Not Null**: Aseguran que campos críticos tengan valor

## Seguridad y Anonimización

### Anonimización de Datos

El campo `Nombre` del dataset original se transforma en:
```
PACIENTE_00000001
PACIENTE_00000002
...
```

Esto cumple con requisitos de privacidad y RGPD.

### Control de Acceso

- Usuario `ADMIN`: Control total del esquema
- Usuario `malackathon`: Solo lectura (SELECT)
- Vistas: Exponen solo información necesaria

### Auditoría

Todas las tablas incluyen:
- `fecha_creacion`: Timestamp de inserción
- `fecha_modificacion`: Timestamp de última actualización

## Troubleshooting

### Error: "Table does not exist"
**Causa:** No se ejecutó `create.sql` antes de `load_data.sql`  
**Solución:** Ejecutar primero `create.sql`

### Error: "Cannot insert NULL into..."
**Causa:** Datos faltantes en el archivo de origen  
**Solución:** Revisar `SaludMental_limpio.xlsx`, verificar que el feature engineering se completó

### Error: "Unique constraint violated"
**Causa:** Intento de cargar datos duplicados  
**Solución:** 
```sql
-- Limpiar datos existentes
TRUNCATE TABLE episodios_procedimientos;
TRUNCATE TABLE episodios_diagnosticos;
TRUNCATE TABLE episodios;
TRUNCATE TABLE pacientes;
-- Volver a ejecutar load_data.sql
```

### Error: "Parent key not found"
**Causa:** Las tablas de catálogo no se poblaron correctamente  
**Solución:** Verificar que los pasos 4.1 a 4.5 de `load_data.sql` se ejecutaron sin errores

### Performance lenta en vistas
**Causa:** Estadísticas de Oracle desactualizadas  
**Solución:**
```sql
BEGIN
    DBMS_STATS.GATHER_SCHEMA_STATS(USER);
END;
/
```

## Mantenimiento

### Backup
```sql
-- Exportar esquema completo
expdp admin/<password>@<connection> \
     schemas=<schema_name> \
     directory=DATA_PUMP_DIR \
     dumpfile=malackathon_backup_%U.dmp \
     logfile=malackathon_backup.log
```

### Actualización de Datos
Para cargar datos adicionales sin perder los existentes, modificar `load_data.sql` para usar `MERGE` en lugar de `INSERT`.

### Monitoreo de Uso
```sql
-- Ver sesiones activas
SELECT username, machine, program, logon_time
FROM v$session
WHERE username = 'MALACKATHON';

-- Ver tablas más consultadas
SELECT object_name, object_type
FROM v$sql_plan
WHERE object_owner = '<schema_name>'
GROUP BY object_name, object_type
ORDER BY COUNT(*) DESC;
```

## Referencias

- [Oracle Autonomous Database Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
- [SQL Language Reference](https://docs.oracle.com/en/database/oracle/oracle-database/23/sqlrf/)
- [CIE-10 Codes](https://www.who.int/standards/classifications/classification-of-diseases)
- [APR-DRG Methodology](https://www.3m.com/3M/en_US/health-information-systems-us/drive-value-based-care/patient-classification-methodologies/apr-drgs/)

## Contacto y Soporte

Para dudas técnicas sobre el esquema de base de datos:
- Revisar logs de ejecución: `load_data.log`, `load_data.bad`
- Consultar documentación del proyecto en el repositorio principal
- Contactar al equipo de desarrollo del proyecto Brain

---

**Última actualización:** Octubre 2025  
**Versión del esquema:** 1.0  
**Compatible con:** Oracle Autonomous Database 23ai

