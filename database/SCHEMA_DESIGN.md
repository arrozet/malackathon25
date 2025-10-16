# Diseño del Esquema de Base de Datos

## Diagrama Entidad-Relación (Modelo Conceptual)

```
┌─────────────────────────┐
│  COMUNIDADES_AUTONOMAS  │
├─────────────────────────┤
│ PK: comunidad_id        │
│     codigo_comunidad    │
│     nombre_comunidad    │
└─────────────────────────┘
          │
          │ 1:N
          ▼
┌─────────────────────────┐         ┌──────────────────┐
│  CENTROS_HOSPITALARIOS  │         │     PAISES       │
├─────────────────────────┤         ├──────────────────┤
│ PK: centro_id           │         │ PK: pais_id      │
│ FK: comunidad_id        │         │     codigo_pais  │
│     codigo_centro       │         │     nombre_pais  │
│     nombre_centro       │         └──────────────────┘
│     activo              │                  │
└─────────────────────────┘                  │ 1:N
          │                                   │
          │ 1:N                               │
          │                                   ▼
          │                         ┌──────────────────┐
          │                         │    PACIENTES     │
          │                         ├──────────────────┤
          │                         │ PK: paciente_id  │
          │                         │ FK: pais_nacimiento_id
          │                         │ FK: comunidad_residencia_id
          │                         │     identificador_anonimo
          │                         │     edad_ingreso │
          │                         │     sexo         │
          │                         └──────────────────┘
          │                                   │
          │                                   │ 1:N
          │                                   │
          │                                   ▼
          └─────────────────────────────────>┌──────────────────┐
                                              │    EPISODIOS     │
                                              ├──────────────────┤
                                              │ PK: episodio_id  │
                                              │ FK: paciente_id  │
                                              │ FK: centro_id    │
                                              │     numero_registro
                                              │     categoria    │
                                              │     fecha_ingreso│
                                              │     fecha_fin_contacto
                                              │     estancia_dias│
                                              │     tipo_alta    │
                                              │     grd_apr      │
                                              │     nivel_severidad_apr
                                              │     riesgo_mortalidad_apr
                                              │     peso_espanol_apr
                                              │     coste_apr    │
                                              │     diagnosticos_totales
                                              │     procedimientos_totales
                                              └──────────────────┘
                                                      │  │
                                        ┌─────────────┘  └─────────────┐
                                        │ N:M                      N:M  │
                                        ▼                               ▼
                         ┌──────────────────────────┐   ┌──────────────────────────┐
                         │ EPISODIOS_DIAGNOSTICOS   │   │ EPISODIOS_PROCEDIMIENTOS │
                         ├──────────────────────────┤   ├──────────────────────────┤
                         │ PK: (episodio_id,        │   │ PK: (episodio_id,        │
                         │      diagnostico_id,     │   │      procedimiento_id,   │
                         │      orden_diagnostico)  │   │      orden_procedimiento)│
                         │ FK: episodio_id          │   │ FK: episodio_id          │
                         │ FK: diagnostico_id       │   │ FK: procedimiento_id     │
                         │     es_principal         │   │     fecha_realizacion    │
                         └──────────────────────────┘   └──────────────────────────┘
                                        │                               │
                                        │ N:1                      N:1  │
                                        ▼                               ▼
                         ┌──────────────────────┐       ┌──────────────────────┐
                         │  DIAGNOSTICOS_CIE    │       │   PROCEDIMIENTOS     │
                         ├──────────────────────┤       ├──────────────────────┤
                         │ PK: diagnostico_id   │       │ PK: procedimiento_id │
                         │     codigo_cie       │       │     codigo_proc      │
                         │     descripcion      │       │     descripcion      │
                         │     capitulo_cie     │       │     categoria        │
                         │     es_mental        │       └──────────────────────┘
                         └──────────────────────┘
```

## Cardinalidades y Relaciones

### Relaciones Uno a Muchos (1:N)

1. **COMUNIDADES_AUTONOMAS → CENTROS_HOSPITALARIOS**
   - Una comunidad autónoma puede tener muchos centros hospitalarios
   - Un centro hospitalario pertenece a una sola comunidad autónoma
   - Constraint: `fk_centro_comunidad`

2. **CENTROS_HOSPITALARIOS → EPISODIOS**
   - Un centro hospitalario puede tener muchos episodios
   - Un episodio se registra en un solo centro hospitalario
   - Constraint: `fk_episodio_centro`

3. **PAISES → PACIENTES**
   - Un país puede tener muchos pacientes que nacieron allí
   - Un paciente nace en un solo país
   - Constraint: `fk_paciente_pais`

4. **PACIENTES → EPISODIOS**
   - Un paciente puede tener muchos episodios de hospitalización
   - Un episodio pertenece a un solo paciente
   - Constraint: `fk_episodio_paciente`

### Relaciones Muchos a Muchos (N:M)

1. **EPISODIOS ↔ DIAGNOSTICOS_CIE** (a través de EPISODIOS_DIAGNOSTICOS)
   - Un episodio puede tener múltiples diagnósticos (principal + secundarios)
   - Un diagnóstico puede aparecer en múltiples episodios
   - Tabla intermedia: `episodios_diagnosticos`
   - Atributos adicionales: `orden_diagnostico`, `es_principal`
   - Constraints: `fk_epidiag_episodio`, `fk_epidiag_diagnostico`

2. **EPISODIOS ↔ PROCEDIMIENTOS** (a través de EPISODIOS_PROCEDIMIENTOS)
   - Un episodio puede tener múltiples procedimientos realizados
   - Un procedimiento puede realizarse en múltiples episodios
   - Tabla intermedia: `episodios_procedimientos`
   - Atributos adicionales: `orden_procedimiento`, `fecha_realizacion`
   - Constraints: `fk_epiproc_episodio`, `fk_epiproc_procedimiento`

## Normalización

### Primera Forma Normal (1FN)
✓ **Cumplida**
- Todos los atributos son atómicos
- No hay grupos repetidos
- Cada celda contiene un solo valor
- Se eliminaron las columnas repetitivas (`Diagnóstico 1`, `Diagnóstico 2`, ..., `Diagnóstico 20`)

### Segunda Forma Normal (2FN)
✓ **Cumplida**
- Está en 1FN
- Todos los atributos no-clave dependen completamente de la clave primaria
- Se separaron las entidades independientes:
  - Información del paciente → tabla `PACIENTES`
  - Información del centro → tabla `CENTROS_HOSPITALARIOS`
  - Códigos diagnósticos → tabla `DIAGNOSTICOS_CIE`
  - Códigos de procedimientos → tabla `PROCEDIMIENTOS`

### Tercera Forma Normal (3FN)
✓ **Cumplida**
- Está en 2FN
- No hay dependencias transitivas
- Eliminación de redundancias:
  - `Comunidad Autónoma` del centro se extrae a `COMUNIDADES_AUTONOMAS`
  - Nombres de países se separan en tabla `PAISES`
  - Información del diagnóstico (descripción, capítulo CIE) no se repite

### Forma Normal de Boyce-Codd (BCNF)
✓ **Cumplida**
- Está en 3FN
- Toda dependencia funcional tiene una superclave como determinante
- No hay anomalías de actualización, inserción o eliminación

## Decisiones de Diseño

### 1. Anonimización de Pacientes

**Problema:** El dataset original contiene nombres que podrían identificar a pacientes reales.

**Solución:** 
- Campo `Nombre` → `identificador_anonimo` con formato `PACIENTE_XXXXXXXX`
- Hash irreversible del nombre original durante la carga
- Cumplimiento con RGPD y normativas de protección de datos

**Implementación:**
```sql
'PACIENTE_' || LPAD(seq_paciente_id.CURRVAL, 8, '0')
```

### 2. Separación de Diagnósticos y Procedimientos

**Problema:** El dataset original tiene 20 columnas para diagnósticos y 20 para procedimientos.

**Solución:**
- Tablas de relación `episodios_diagnosticos` y `episodios_procedimientos`
- Atributo `orden_diagnostico` / `orden_procedimiento` para mantener secuencia
- Flag `es_principal` para distinguir diagnóstico principal

**Ventajas:**
- Esquema extensible (no limitado a 20 diagnósticos)
- Consultas más eficientes para análisis por diagnóstico
- Eliminación de columnas vacías

### 3. Catálogos Normalizados

**Problema:** Códigos repetidos en múltiples registros (diagnósticos, procedimientos, comunidades).

**Solución:**
- Tablas de catálogo independientes con IDs secuenciales
- Referencias mediante foreign keys
- Facilita actualización de descripciones sin afectar datos históricos

**Tablas de catálogo:**
- `diagnosticos_cie`: Códigos CIE-10 únicos
- `procedimientos`: Códigos de procedimientos únicos
- `comunidades_autonomas`: Comunidades de España
- `paises`: Códigos ISO de países

### 4. Campos Calculados en EPISODIOS

**Problema:** Algunos campos se pueden derivar de otros (ej: duración del episodio).

**Solución:**
- Almacenar campos calculados para optimizar consultas frecuentes
- Usar triggers para mantener consistencia automática
- Evitar recálculo en tiempo de query

**Campos derivados:**
- `duracion_episodio_calc`: Calculado desde fechas
- `grupo_etario`: Derivado de edad
- `dia_semana_ingreso`, `mes_nombre_ingreso`: Extraídos de fecha

**Trade-off:**
- ✓ Queries más rápidas (no calcular en SELECT)
- ✓ Índices sobre campos calculados
- ✗ Ligero aumento de espacio
- ✗ Necesidad de triggers de actualización

### 5. Contadores Desnormalizados

**Problema:** Contar diagnósticos/procedimientos por episodio requiere JOINs costosos.

**Solución:**
- Campos `diagnosticos_totales` y `procedimientos_totales` en `EPISODIOS`
- Mantenidos automáticamente por triggers
- Uso en filtros y ordenamientos

**Justificación:**
- Desnormalización controlada para performance
- Consultas del tipo "episodios con más de 3 diagnósticos" son instantáneas
- Triggers garantizan consistencia

### 6. Índices Estratégicos

**Análisis de queries esperadas:**
1. Filtrado por fecha de ingreso → `idx_episodio_fecha_ingreso`
2. Búsqueda por diagnóstico → `idx_epidiag_diagnostico`
3. Análisis por centro → `idx_episodio_centro`
4. Filtros por severidad/riesgo → `idx_episodio_severidad`, `idx_episodio_riesgo`
5. Análisis de costes → `idx_episodio_coste`
6. Búsqueda por paciente → `idx_episodio_paciente`

**Trade-off:**
- ✓ Queries analíticas 10-100x más rápidas
- ✗ Ligero overhead en INSERT/UPDATE
- ✗ Espacio adicional (~20% del tamaño de la tabla)

## Tipos de Datos

### Estrategia de Tipos Oracle

1. **Identificadores**: `NUMBER` sin decimales
   - Secuencias autoincrementales
   - Rango: hasta 38 dígitos (más que suficiente)

2. **Códigos y Textos**: `VARCHAR2`
   - `VARCHAR2(20)` para códigos (CIE, procedimientos)
   - `VARCHAR2(100)` para nombres cortos
   - `VARCHAR2(500)` para descripciones

3. **Fechas**: `DATE` y `TIMESTAMP`
   - `DATE` para fechas sin hora (fecha_ingreso, fecha_fin_contacto)
   - `TIMESTAMP` para auditoría con hora exacta

4. **Números con Decimales**: `NUMBER(p,s)`
   - `NUMBER(10,4)` para peso_espanol_apr (alta precisión)
   - `NUMBER(12,2)` para coste_apr (euros con céntimos)

5. **Flags Booleanos**: `CHAR(1)` con CHECK constraint
   - Valores: 'S' / 'N'
   - Más eficiente que VARCHAR2 o NUMBER para Oracle

### Validaciones con CHECK Constraints

```sql
CHECK (sexo IN ('M', 'F', 'X', 'N'))
CHECK (activo IN ('S', 'N'))
CHECK (tiene_procedimiento IN ('S', 'N'))
CHECK (tiene_comorbilidad IN ('S', 'N'))
CHECK (es_principal IN ('S', 'N'))
CHECK (es_mental IN ('S', 'N'))
```

## Vista VISTA_MUY_INTERESANTE

### Propósito
Proporcionar una interfaz desnormalizada para análisis exploratorio sin requerir conocimientos profundos de SQL.

### Características

1. **Desnormalización Controlada**
   - JOIN de todas las tablas relevantes
   - Un solo SELECT para obtener información completa de un episodio

2. **Transformación de Códigos**
   ```sql
   CASE p.sexo
       WHEN 'M' THEN 'Hombre'
       WHEN 'F' THEN 'Mujer'
       WHEN 'X' THEN 'No especificado'
       ELSE 'No disponible'
   END AS sexo
   ```

3. **Inclusión de Métricas Calculadas**
   - Campos derivados ya calculados
   - Descripciones legibles de códigos APR
   - Interpretación de tipo de alta

4. **Optimización**
   - LEFT JOIN para datos opcionales
   - INNER JOIN solo para relaciones obligatorias
   - ORDER BY para ordenamiento predecible

### Uso en Aplicación Brain

```python
# Backend FastAPI puede consultar directamente
query = "SELECT * FROM vista_muy_interesante WHERE diagnostico_principal LIKE 'F20%'"
results = await db.fetch_all(query)
```

## Triggers de Negocio

### 1. `trg_episodios_calc`
**Propósito:** Calcular campos derivados antes de INSERT/UPDATE

**Lógica:**
- Calcula `duracion_episodio_calc` desde fechas
- Determina `grupo_etario` consultando edad del paciente
- Extrae `dia_semana_ingreso` y `mes_nombre_ingreso`
- Actualiza `fecha_modificacion`

**Ejecuta:** BEFORE INSERT OR UPDATE

### 2. `trg_episodio_diag_count`
**Propósito:** Mantener contador de diagnósticos sincronizado

**Lógica:**
- En INSERT: Incrementa `diagnosticos_totales`
- En DELETE: Recalcula contando registros restantes
- Actualiza `tiene_comorbilidad` si total > 1

**Ejecuta:** AFTER INSERT OR DELETE en `episodios_diagnosticos`

### 3. `trg_episodio_proc_count`
**Propósito:** Mantener contador de procedimientos sincronizado

**Lógica:**
- En INSERT: Incrementa `procedimientos_totales`, marca `tiene_procedimiento = 'S'`
- En DELETE: Recalcula contador
- Actualiza `tiene_procedimiento` según total

**Ejecuta:** AFTER INSERT OR DELETE en `episodios_procedimientos`

### 4. `trg_episodios_update`
**Propósito:** Auditoría de modificaciones

**Lógica:**
- Actualiza automáticamente `fecha_modificacion` a CURRENT_TIMESTAMP

**Ejecuta:** BEFORE UPDATE en `episodios`

## Seguridad y Permisos

### Modelo de Tres Niveles

1. **Nivel ADMIN (Schema Owner)**
   - Control total: CREATE, ALTER, DROP
   - Ejecución de scripts DDL/DML
   - Gestión de usuarios y permisos

2. **Nivel MALACKATHON (Solo Lectura)**
   - SELECT en todas las tablas y vistas
   - Acceso a vistas agregadas
   - Sin permisos de escritura

3. **Nivel APLICACIÓN (Backend)**
   - SELECT en vistas específicas
   - Conexión mediante usuario de servicio
   - Acceso a través de Oracle Wallet

### Principio de Mínimo Privilegio

```sql
-- Usuario malackathon tiene solo SELECT
GRANT SELECT ON vista_muy_interesante TO malackathon;

-- NO tiene permisos de:
-- INSERT, UPDATE, DELETE, TRUNCATE, DROP
```

## Escalabilidad y Performance

### Estimación de Volumen

**Dataset Actual:**
- ~21,000 episodios
- ~20,000 pacientes únicos
- ~500 diagnósticos únicos
- ~300 procedimientos únicos

**Proyección a 5 años:**
- ~100,000 episodios/año
- ~500,000 episodios totales
- ~450,000 pacientes
- ~2,000 diagnósticos
- ~1,500 procedimientos

### Estrategias de Optimización

1. **Particionamiento (futuro)**
   ```sql
   PARTITION BY RANGE (fecha_ingreso) (
       PARTITION p2020 VALUES LESS THAN (TO_DATE('2021-01-01', 'YYYY-MM-DD')),
       PARTITION p2021 VALUES LESS THAN (TO_DATE('2022-01-01', 'YYYY-MM-DD')),
       ...
   )
   ```

2. **Índices Bitmap** (si selectividad es baja)
   ```sql
   CREATE BITMAP INDEX idx_episodio_severidad_bm ON episodios(nivel_severidad_apr);
   ```

3. **Materialización de Vistas** (para agregaciones pesadas)
   ```sql
   CREATE MATERIALIZED VIEW mv_resumen_mensual
   REFRESH FAST ON COMMIT
   AS SELECT ...;
   ```

4. **Compression** (Oracle Advanced Compression)
   ```sql
   ALTER TABLE episodios COMPRESS FOR OLTP;
   ```

## Referencias y Estándares

### Códigos CIE-10
- **Capítulo F**: Trastornos mentales y del comportamiento
- Rango: F00-F99
- Fuente: [WHO ICD-10](https://www.who.int/standards/classifications/classification-of-diseases)

### Clasificación APR-DRG
- **APR**: All Patient Refined
- **DRG**: Diagnosis Related Groups
- **GRD**: Grupos Relacionados por el Diagnóstico
- **CDM**: Clinical Diagnostic Module
- **Severidad**: 1 (Menor) a 4 (Extremo)
- **Riesgo Mortalidad**: 1 (Menor) a 4 (Extremo)

### Normativas de Datos
- **RGPD**: Reglamento General de Protección de Datos (UE 2016/679)
- **Anonimización**: Técnica de sustitución de identificadores
- **Auditoría**: Campos de fecha de creación/modificación en todas las tablas

---

**Documento de Diseño de Esquema**  
**Versión:** 1.0  
**Fecha:** Octubre 2025  
**Proyecto:** Brain - II Malackathon 2025

