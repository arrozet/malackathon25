-- =====================================================================
-- Script de Creación de Base de Datos - II Malackathon 2025
-- Base de Datos: Oracle Autonomous Database 23ai
-- Tema: Análisis de Datos de Salud Mental - Hospitalizaciones
-- =====================================================================
-- Autor: Brain - AI Research Companion
-- Descripción: Esquema normalizado para almacenar datos de episodios
--              de hospitalización en salud mental, con normalización
--              a 3FN y anonimización mediante sustitución.
-- =====================================================================

-- =====================================================================
-- PASO 1: LIMPIEZA DE ESQUEMA (solo para desarrollo)
-- =====================================================================
-- Advertencia: Descomentar solo en desarrollo, NUNCA en producción

/*
BEGIN
   FOR rec IN (SELECT table_name FROM user_tables) LOOP
      EXECUTE IMMEDIATE 'DROP TABLE ' || rec.table_name || ' CASCADE CONSTRAINTS';
   END LOOP;
   
   FOR rec IN (SELECT sequence_name FROM user_sequences) LOOP
      EXECUTE IMMEDIATE 'DROP SEQUENCE ' || rec.sequence_name;
   END LOOP;
   
   FOR rec IN (SELECT view_name FROM user_views) LOOP
      EXECUTE IMMEDIATE 'DROP VIEW ' || rec.view_name;
   END LOOP;
END;
/
*/

-- =====================================================================
-- PASO 2: CREACIÓN DE SECUENCIAS
-- =====================================================================

CREATE SEQUENCE seq_paciente_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE seq_episodio_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE seq_centro_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE seq_diagnostico_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE seq_procedimiento_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE seq_comunidad_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

CREATE SEQUENCE seq_pais_id
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- =====================================================================
-- PASO 3: TABLAS DE CATÁLOGOS Y DIMENSIONES
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: COMUNIDADES_AUTONOMAS
-- Descripción: Catálogo de comunidades autónomas de España
-- ---------------------------------------------------------------------
CREATE TABLE comunidades_autonomas (
    comunidad_id        NUMBER          PRIMARY KEY,
    codigo_comunidad    VARCHAR2(10)    NOT NULL UNIQUE,
    nombre_comunidad    VARCHAR2(100)   NOT NULL,
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE comunidades_autonomas IS 'Catálogo de comunidades autónomas de España';
COMMENT ON COLUMN comunidades_autonomas.comunidad_id IS 'Identificador único de la comunidad autónoma';
COMMENT ON COLUMN comunidades_autonomas.codigo_comunidad IS 'Código ISO de la comunidad autónoma';
COMMENT ON COLUMN comunidades_autonomas.nombre_comunidad IS 'Nombre completo de la comunidad autónoma';

-- ---------------------------------------------------------------------
-- Tabla: PAISES
-- Descripción: Catálogo de países (códigos ISO)
-- ---------------------------------------------------------------------
CREATE TABLE paises (
    pais_id             NUMBER          PRIMARY KEY,
    codigo_pais         VARCHAR2(10)    NOT NULL UNIQUE,
    nombre_pais         VARCHAR2(100),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE paises IS 'Catálogo de países según códigos ISO';
COMMENT ON COLUMN paises.pais_id IS 'Identificador único del país';
COMMENT ON COLUMN paises.codigo_pais IS 'Código ISO del país (ej: 724 para España)';
COMMENT ON COLUMN paises.nombre_pais IS 'Nombre completo del país';

-- ---------------------------------------------------------------------
-- Tabla: CENTROS_HOSPITALARIOS
-- Descripción: Catálogo de centros hospitalarios
-- ---------------------------------------------------------------------
CREATE TABLE centros_hospitalarios (
    centro_id           NUMBER          PRIMARY KEY,
    codigo_centro       VARCHAR2(50)    NOT NULL UNIQUE,
    nombre_centro       VARCHAR2(200),
    comunidad_id        NUMBER          NOT NULL,
    activo              CHAR(1)         DEFAULT 'S' CHECK (activo IN ('S', 'N')),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_centro_comunidad FOREIGN KEY (comunidad_id)
        REFERENCES comunidades_autonomas(comunidad_id)
);

COMMENT ON TABLE centros_hospitalarios IS 'Catálogo de centros hospitalarios';
COMMENT ON COLUMN centros_hospitalarios.centro_id IS 'Identificador único del centro';
COMMENT ON COLUMN centros_hospitalarios.codigo_centro IS 'Código recodificado del centro hospitalario';
COMMENT ON COLUMN centros_hospitalarios.comunidad_id IS 'Comunidad autónoma donde se ubica el centro';
COMMENT ON COLUMN centros_hospitalarios.activo IS 'Indicador de centro activo (S/N)';

-- ---------------------------------------------------------------------
-- Tabla: DIAGNOSTICOS_CIE
-- Descripción: Catálogo de códigos diagnósticos CIE-10
-- ---------------------------------------------------------------------
CREATE TABLE diagnosticos_cie (
    diagnostico_id      NUMBER          PRIMARY KEY,
    codigo_cie          VARCHAR2(20)    NOT NULL UNIQUE,
    descripcion         VARCHAR2(500),
    capitulo_cie        VARCHAR2(10),
    es_mental           CHAR(1)         DEFAULT 'N' CHECK (es_mental IN ('S', 'N')),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE diagnosticos_cie IS 'Catálogo de códigos diagnósticos CIE-10';
COMMENT ON COLUMN diagnosticos_cie.diagnostico_id IS 'Identificador único del diagnóstico';
COMMENT ON COLUMN diagnosticos_cie.codigo_cie IS 'Código CIE-10 del diagnóstico';
COMMENT ON COLUMN diagnosticos_cie.capitulo_cie IS 'Capítulo CIE al que pertenece (ej: F para trastornos mentales)';
COMMENT ON COLUMN diagnosticos_cie.es_mental IS 'Indicador de trastorno mental (capítulo F)';

-- ---------------------------------------------------------------------
-- Tabla: PROCEDIMIENTOS
-- Descripción: Catálogo de procedimientos clínicos
-- ---------------------------------------------------------------------
CREATE TABLE procedimientos (
    procedimiento_id    NUMBER          PRIMARY KEY,
    codigo_proc         VARCHAR2(20)    NOT NULL UNIQUE,
    descripcion         VARCHAR2(500),
    categoria           VARCHAR2(100),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE procedimientos IS 'Catálogo de procedimientos clínicos';
COMMENT ON COLUMN procedimientos.procedimiento_id IS 'Identificador único del procedimiento';
COMMENT ON COLUMN procedimientos.codigo_proc IS 'Código del procedimiento';
COMMENT ON COLUMN procedimientos.descripcion IS 'Descripción del procedimiento';

-- =====================================================================
-- PASO 4: TABLA DE PACIENTES (ANONIMIZADA)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: PACIENTES
-- Descripción: Información demográfica anonimizada de pacientes
-- Nota: Los nombres han sido sustituidos por identificadores anónimos
-- ---------------------------------------------------------------------
CREATE TABLE pacientes (
    paciente_id         NUMBER          PRIMARY KEY,
    identificador_anonimo VARCHAR2(100) NOT NULL UNIQUE,
    edad_ingreso        NUMBER(3),
    sexo                CHAR(1)         CHECK (sexo IN ('M', 'F', 'X', 'N')),
    pais_nacimiento_id  NUMBER,
    comunidad_residencia_id NUMBER,
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paciente_pais FOREIGN KEY (pais_nacimiento_id)
        REFERENCES paises(pais_id),
    CONSTRAINT fk_paciente_comunidad FOREIGN KEY (comunidad_residencia_id)
        REFERENCES comunidades_autonomas(comunidad_id)
);

COMMENT ON TABLE pacientes IS 'Información demográfica anonimizada de pacientes';
COMMENT ON COLUMN pacientes.paciente_id IS 'Identificador único del paciente (generado)';
COMMENT ON COLUMN pacientes.identificador_anonimo IS 'Identificador anonimizado del paciente';
COMMENT ON COLUMN pacientes.edad_ingreso IS 'Edad del paciente en el primer ingreso registrado';
COMMENT ON COLUMN pacientes.sexo IS 'Sexo del paciente: M=Masculino, F=Femenino, X=No especificado, N=No disponible';
COMMENT ON COLUMN pacientes.pais_nacimiento_id IS 'País de nacimiento del paciente';

-- =====================================================================
-- PASO 5: TABLA DE EPISODIOS (CORE)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: EPISODIOS
-- Descripción: Episodios de hospitalización en salud mental
-- ---------------------------------------------------------------------
CREATE TABLE episodios (
    episodio_id         NUMBER          PRIMARY KEY,
    paciente_id         NUMBER          NOT NULL,
    centro_id           NUMBER          NOT NULL,
    numero_registro     VARCHAR2(50),
    categoria           VARCHAR2(100),
    fecha_ingreso       DATE            NOT NULL,
    fecha_fin_contacto  DATE,
    mes_ingreso         DATE,
    estancia_dias       NUMBER(5),
    tipo_alta           NUMBER(2),
    circunstancia_contacto NUMBER(2),
    -- Campos calculados/derivados
    duracion_episodio_calc NUMBER(5),
    dia_semana_ingreso  VARCHAR2(20),
    mes_nombre_ingreso  VARCHAR2(20),
    grupo_etario        VARCHAR2(10),
    -- Clasificación APR-DRG
    grd_apr             NUMBER(10),
    cdm_apr             NUMBER(10),
    nivel_severidad_apr NUMBER(2),
    riesgo_mortalidad_apr NUMBER(2),
    peso_espanol_apr    NUMBER(10,4),
    coste_apr           NUMBER(12,2),
    -- Métricas agregadas
    diagnosticos_totales NUMBER(3)      DEFAULT 0,
    procedimientos_totales NUMBER(3)    DEFAULT 0,
    tiene_procedimiento CHAR(1)         DEFAULT 'N' CHECK (tiene_procedimiento IN ('S', 'N')),
    tiene_comorbilidad  CHAR(1)         DEFAULT 'N' CHECK (tiene_comorbilidad IN ('S', 'N')),
    -- Auditoría
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT fk_episodio_paciente FOREIGN KEY (paciente_id)
        REFERENCES pacientes(paciente_id),
    CONSTRAINT fk_episodio_centro FOREIGN KEY (centro_id)
        REFERENCES centros_hospitalarios(centro_id),
    CONSTRAINT chk_fechas CHECK (fecha_fin_contacto IS NULL OR fecha_fin_contacto >= fecha_ingreso),
    CONSTRAINT chk_estancia CHECK (estancia_dias IS NULL OR estancia_dias >= 0)
);

COMMENT ON TABLE episodios IS 'Episodios de hospitalización en salud mental';
COMMENT ON COLUMN episodios.episodio_id IS 'Identificador único del episodio';
COMMENT ON COLUMN episodios.paciente_id IS 'Referencia al paciente';
COMMENT ON COLUMN episodios.centro_id IS 'Centro hospitalario del episodio';
COMMENT ON COLUMN episodios.numero_registro IS 'Número de registro anual del episodio';
COMMENT ON COLUMN episodios.fecha_ingreso IS 'Fecha de ingreso del paciente';
COMMENT ON COLUMN episodios.fecha_fin_contacto IS 'Fecha de fin del contacto/alta';
COMMENT ON COLUMN episodios.estancia_dias IS 'Duración de la estancia en días';
COMMENT ON COLUMN episodios.tipo_alta IS 'Tipo de alta médica';
COMMENT ON COLUMN episodios.grd_apr IS 'Grupo Relacionado por el Diagnóstico APR';
COMMENT ON COLUMN episodios.nivel_severidad_apr IS 'Nivel de severidad APR (1-4)';
COMMENT ON COLUMN episodios.riesgo_mortalidad_apr IS 'Nivel de riesgo de mortalidad APR (1-4)';
COMMENT ON COLUMN episodios.peso_espanol_apr IS 'Peso español APR para cálculo de costes';
COMMENT ON COLUMN episodios.coste_apr IS 'Coste estimado APR del episodio';
COMMENT ON COLUMN episodios.diagnosticos_totales IS 'Número total de diagnósticos registrados';
COMMENT ON COLUMN episodios.procedimientos_totales IS 'Número total de procedimientos realizados';

-- =====================================================================
-- PASO 6: TABLAS DE RELACIÓN (MUCHOS A MUCHOS)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: EPISODIOS_DIAGNOSTICOS
-- Descripción: Relación entre episodios y diagnósticos (incluye orden)
-- ---------------------------------------------------------------------
CREATE TABLE episodios_diagnosticos (
    episodio_id         NUMBER          NOT NULL,
    diagnostico_id      NUMBER          NOT NULL,
    orden_diagnostico   NUMBER(2)       NOT NULL,
    es_principal        CHAR(1)         DEFAULT 'N' CHECK (es_principal IN ('S', 'N')),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (episodio_id, diagnostico_id, orden_diagnostico),
    CONSTRAINT fk_epidiag_episodio FOREIGN KEY (episodio_id)
        REFERENCES episodios(episodio_id) ON DELETE CASCADE,
    CONSTRAINT fk_epidiag_diagnostico FOREIGN KEY (diagnostico_id)
        REFERENCES diagnosticos_cie(diagnostico_id)
);

COMMENT ON TABLE episodios_diagnosticos IS 'Relación entre episodios y diagnósticos';
COMMENT ON COLUMN episodios_diagnosticos.orden_diagnostico IS 'Orden del diagnóstico (1=principal, 2+=secundarios)';
COMMENT ON COLUMN episodios_diagnosticos.es_principal IS 'Indicador de diagnóstico principal';

-- ---------------------------------------------------------------------
-- Tabla: EPISODIOS_PROCEDIMIENTOS
-- Descripción: Relación entre episodios y procedimientos (incluye orden)
-- ---------------------------------------------------------------------
CREATE TABLE episodios_procedimientos (
    episodio_id         NUMBER          NOT NULL,
    procedimiento_id    NUMBER          NOT NULL,
    orden_procedimiento NUMBER(2)       NOT NULL,
    fecha_realizacion   DATE,
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (episodio_id, procedimiento_id, orden_procedimiento),
    CONSTRAINT fk_epiproc_episodio FOREIGN KEY (episodio_id)
        REFERENCES episodios(episodio_id) ON DELETE CASCADE,
    CONSTRAINT fk_epiproc_procedimiento FOREIGN KEY (procedimiento_id)
        REFERENCES procedimientos(procedimiento_id)
);

COMMENT ON TABLE episodios_procedimientos IS 'Relación entre episodios y procedimientos realizados';
COMMENT ON COLUMN episodios_procedimientos.orden_procedimiento IS 'Orden del procedimiento (1=primero, 2+=subsiguientes)';
COMMENT ON COLUMN episodios_procedimientos.fecha_realizacion IS 'Fecha en que se realizó el procedimiento';

-- =====================================================================
-- PASO 7: ÍNDICES PARA OPTIMIZACIÓN DE CONSULTAS
-- =====================================================================

-- Índices en tabla PACIENTES
CREATE INDEX idx_paciente_sexo ON pacientes(sexo);
CREATE INDEX idx_paciente_pais ON pacientes(pais_nacimiento_id);
CREATE INDEX idx_paciente_edad ON pacientes(edad_ingreso);

-- Índices en tabla EPISODIOS
CREATE INDEX idx_episodio_paciente ON episodios(paciente_id);
CREATE INDEX idx_episodio_centro ON episodios(centro_id);
CREATE INDEX idx_episodio_fecha_ingreso ON episodios(fecha_ingreso);
CREATE INDEX idx_episodio_fecha_fin ON episodios(fecha_fin_contacto);
CREATE INDEX idx_episodio_tipo_alta ON episodios(tipo_alta);
CREATE INDEX idx_episodio_severidad ON episodios(nivel_severidad_apr);
CREATE INDEX idx_episodio_riesgo ON episodios(riesgo_mortalidad_apr);
CREATE INDEX idx_episodio_grd ON episodios(grd_apr);
CREATE INDEX idx_episodio_estancia ON episodios(estancia_dias);
CREATE INDEX idx_episodio_coste ON episodios(coste_apr);

-- Índices en tabla DIAGNOSTICOS_CIE
CREATE INDEX idx_diagnostico_capitulo ON diagnosticos_cie(capitulo_cie);
CREATE INDEX idx_diagnostico_mental ON diagnosticos_cie(es_mental);

-- Índices en tabla CENTROS_HOSPITALARIOS
CREATE INDEX idx_centro_comunidad ON centros_hospitalarios(comunidad_id);
CREATE INDEX idx_centro_activo ON centros_hospitalarios(activo);

-- Índices en tablas de relación
CREATE INDEX idx_epidiag_diagnostico ON episodios_diagnosticos(diagnostico_id);
CREATE INDEX idx_epidiag_principal ON episodios_diagnosticos(es_principal);
CREATE INDEX idx_epiproc_procedimiento ON episodios_procedimientos(procedimiento_id);

-- =====================================================================
-- PASO 8: VISTA PRINCIPAL PARA EL USUARIO MALACKATHON
-- =====================================================================

-- ---------------------------------------------------------------------
-- Vista: VISTA_MUY_INTERESANTE
-- Descripción: Vista desnormalizada que combina información de episodios,
--              pacientes, diagnósticos principales y centros para facilitar
--              el análisis exploratorio y la generación de insights.
--              Esta vista es la interfaz principal para la aplicación Brain.
-- Propósito: Proporcionar una vista consolidada y optimizada para:
--            1. Análisis descriptivo de episodios de salud mental
--            2. Visualizaciones en la aplicación web Brain
--            3. Exploración de patrones de estancia, costes y severidad
--            4. Identificación de tendencias por diagnóstico y demografía
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW vista_muy_interesante AS
SELECT
    -- Identificadores
    e.episodio_id,
    e.paciente_id,
    p.identificador_anonimo,
    e.numero_registro,
    -- Información demográfica
    p.edad_ingreso,
    CASE p.sexo
        WHEN 'M' THEN 'Hombre'
        WHEN 'F' THEN 'Mujer'
        WHEN 'X' THEN 'No especificado'
        ELSE 'No disponible'
    END AS sexo,
    pa.codigo_pais,
    pa.nombre_pais AS pais_nacimiento,
    -- Información del centro
    c.codigo_centro,
    c.nombre_centro,
    ca.nombre_comunidad AS comunidad_autonoma,
    -- Información temporal
    e.fecha_ingreso,
    e.fecha_fin_contacto,
    e.mes_ingreso,
    e.estancia_dias,
    e.duracion_episodio_calc,
    e.dia_semana_ingreso,
    e.mes_nombre_ingreso,
    e.grupo_etario,
    -- Información clínica
    e.categoria,
    dc.codigo_cie AS diagnostico_principal,
    dc.descripcion AS diagnostico_descripcion,
    dc.capitulo_cie,
    e.diagnosticos_totales,
    e.procedimientos_totales,
    CASE e.tiene_procedimiento
        WHEN 'S' THEN 'Sí'
        ELSE 'No'
    END AS tiene_procedimiento,
    CASE e.tiene_comorbilidad
        WHEN 'S' THEN 'Sí'
        ELSE 'No'
    END AS tiene_comorbilidad,
    -- Información de alta
    CASE e.tipo_alta
        WHEN 1 THEN 'Domicilio'
        WHEN 2 THEN 'Traslado a otro hospital'
        WHEN 3 THEN 'Alta voluntaria'
        WHEN 4 THEN 'Éxitus'
        WHEN 5 THEN 'Traslado a centro sociosanitario'
        ELSE 'Otros'
    END AS tipo_alta,
    e.circunstancia_contacto,
    -- Clasificación APR-DRG
    e.grd_apr,
    e.cdm_apr,
    e.nivel_severidad_apr,
    CASE e.nivel_severidad_apr
        WHEN 1 THEN 'Menor'
        WHEN 2 THEN 'Moderado'
        WHEN 3 THEN 'Mayor'
        WHEN 4 THEN 'Extremo'
        ELSE 'No especificado'
    END AS severidad_descripcion,
    e.riesgo_mortalidad_apr,
    CASE e.riesgo_mortalidad_apr
        WHEN 1 THEN 'Menor'
        WHEN 2 THEN 'Moderado'
        WHEN 3 THEN 'Mayor'
        WHEN 4 THEN 'Extremo'
        ELSE 'No especificado'
    END AS riesgo_descripcion,
    e.peso_espanol_apr,
    e.coste_apr,
    -- Metadatos
    e.fecha_creacion,
    e.fecha_modificacion
FROM
    episodios e
    INNER JOIN pacientes p ON e.paciente_id = p.paciente_id
    LEFT JOIN centros_hospitalarios c ON e.centro_id = c.centro_id
    LEFT JOIN comunidades_autonomas ca ON c.comunidad_id = ca.comunidad_id
    LEFT JOIN paises pa ON p.pais_nacimiento_id = pa.pais_id
    LEFT JOIN episodios_diagnosticos ed ON e.episodio_id = ed.episodio_id AND ed.es_principal = 'S'
    LEFT JOIN diagnosticos_cie dc ON ed.diagnostico_id = dc.diagnostico_id
ORDER BY
    e.fecha_ingreso DESC, e.episodio_id;

COMMENT ON TABLE vista_muy_interesante IS 
'Vista desnormalizada para análisis exploratorio de episodios de salud mental. ' ||
'Combina información de pacientes, episodios, diagnósticos principales, centros y clasificaciones APR. ' ||
'Propósito: Facilitar visualizaciones y análisis en la aplicación Brain, proporcionando una interfaz ' ||
'simplificada para investigadores sin conocimientos profundos de SQL. ' ||
'Incluye descripciones legibles de códigos categóricos y métricas calculadas.';

-- =====================================================================
-- PASO 9: VISTAS ADICIONALES PARA ANÁLISIS
-- =====================================================================

-- ---------------------------------------------------------------------
-- Vista: RESUMEN_DIAGNOSTICOS_PRINCIPALES
-- Descripción: Estadísticas agregadas por diagnóstico principal
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW resumen_diagnosticos_principales AS
SELECT
    dc.codigo_cie,
    dc.descripcion,
    dc.capitulo_cie,
    COUNT(DISTINCT e.episodio_id) AS total_episodios,
    COUNT(DISTINCT e.paciente_id) AS total_pacientes,
    ROUND(AVG(e.estancia_dias), 2) AS estancia_promedio,
    ROUND(MEDIAN(e.estancia_dias), 2) AS estancia_mediana,
    ROUND(AVG(e.coste_apr), 2) AS coste_promedio,
    ROUND(MEDIAN(e.coste_apr), 2) AS coste_mediano,
    ROUND(AVG(p.edad_ingreso), 2) AS edad_promedio,
    COUNT(CASE WHEN p.sexo = 'M' THEN 1 END) AS casos_masculinos,
    COUNT(CASE WHEN p.sexo = 'F' THEN 1 END) AS casos_femeninos
FROM
    diagnosticos_cie dc
    INNER JOIN episodios_diagnosticos ed ON dc.diagnostico_id = ed.diagnostico_id AND ed.es_principal = 'S'
    INNER JOIN episodios e ON ed.episodio_id = e.episodio_id
    INNER JOIN pacientes p ON e.paciente_id = p.paciente_id
GROUP BY
    dc.codigo_cie, dc.descripcion, dc.capitulo_cie
ORDER BY
    total_episodios DESC;

COMMENT ON TABLE resumen_diagnosticos_principales IS 'Estadísticas agregadas por diagnóstico principal';

-- ---------------------------------------------------------------------
-- Vista: RESUMEN_CENTROS
-- Descripción: Estadísticas agregadas por centro hospitalario
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW resumen_centros AS
SELECT
    c.codigo_centro,
    c.nombre_centro,
    ca.nombre_comunidad,
    COUNT(DISTINCT e.episodio_id) AS total_episodios,
    COUNT(DISTINCT e.paciente_id) AS total_pacientes,
    ROUND(AVG(e.estancia_dias), 2) AS estancia_promedio,
    ROUND(AVG(e.coste_apr), 2) AS coste_promedio,
    ROUND(AVG(e.nivel_severidad_apr), 2) AS severidad_promedio,
    COUNT(CASE WHEN e.tipo_alta = 4 THEN 1 END) AS total_exitus
FROM
    centros_hospitalarios c
    INNER JOIN episodios e ON c.centro_id = e.centro_id
    INNER JOIN comunidades_autonomas ca ON c.comunidad_id = ca.comunidad_id
GROUP BY
    c.codigo_centro, c.nombre_centro, ca.nombre_comunidad
ORDER BY
    total_episodios DESC;

COMMENT ON TABLE resumen_centros IS 'Estadísticas agregadas por centro hospitalario';

-- ---------------------------------------------------------------------
-- Vista: RESUMEN_TEMPORAL
-- Descripción: Evolución temporal de episodios por mes
-- ---------------------------------------------------------------------
CREATE OR REPLACE VIEW resumen_temporal AS
SELECT
    TO_CHAR(e.fecha_ingreso, 'YYYY') AS anio,
    TO_CHAR(e.fecha_ingreso, 'MM') AS mes_numero,
    TO_CHAR(e.fecha_ingreso, 'Month', 'NLS_DATE_LANGUAGE=SPANISH') AS mes_nombre,
    TO_CHAR(e.fecha_ingreso, 'YYYY-MM') AS periodo,
    COUNT(DISTINCT e.episodio_id) AS total_episodios,
    COUNT(DISTINCT e.paciente_id) AS total_pacientes,
    ROUND(AVG(e.estancia_dias), 2) AS estancia_promedio,
    ROUND(AVG(e.coste_apr), 2) AS coste_promedio
FROM
    episodios e
WHERE
    e.fecha_ingreso IS NOT NULL
GROUP BY
    TO_CHAR(e.fecha_ingreso, 'YYYY'),
    TO_CHAR(e.fecha_ingreso, 'MM'),
    TO_CHAR(e.fecha_ingreso, 'Month', 'NLS_DATE_LANGUAGE=SPANISH'),
    TO_CHAR(e.fecha_ingreso, 'YYYY-MM')
ORDER BY
    anio, mes_numero;

COMMENT ON TABLE resumen_temporal IS 'Evolución temporal de episodios por mes y año';

-- =====================================================================
-- PASO 10: CREACIÓN DE USUARIO MALACKATHON CON PERMISOS DE LECTURA
-- =====================================================================

-- NOTA: Ejecutar esta sección con usuario ADMIN de la base de datos
-- La contraseña debe ser proporcionada por los organizadores del hackathon

/*
-- Crear usuario malackathon
CREATE USER malackathon IDENTIFIED BY "<PASSWORD_PROPORCIONADA_POR_ORGANIZADORES>";

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

-- Crear sinónimos para facilitar el acceso
CREATE PUBLIC SYNONYM vista_muy_interesante FOR <SCHEMA_OWNER>.vista_muy_interesante;
CREATE PUBLIC SYNONYM resumen_diagnosticos_principales FOR <SCHEMA_OWNER>.resumen_diagnosticos_principales;
CREATE PUBLIC SYNONYM resumen_centros FOR <SCHEMA_OWNER>.resumen_centros;
CREATE PUBLIC SYNONYM resumen_temporal FOR <SCHEMA_OWNER>.resumen_temporal;
*/

-- =====================================================================
-- PASO 11: TRIGGERS PARA AUDITORÍA Y VALIDACIÓN
-- =====================================================================

-- ---------------------------------------------------------------------
-- Trigger: Actualizar fecha_modificacion en EPISODIOS
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_episodios_update
BEFORE UPDATE ON episodios
FOR EACH ROW
BEGIN
    :NEW.fecha_modificacion := CURRENT_TIMESTAMP;
END;
/

-- ---------------------------------------------------------------------
-- Trigger: Validar y calcular campos derivados en EPISODIOS
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_episodios_calc
BEFORE INSERT OR UPDATE ON episodios
FOR EACH ROW
BEGIN
    -- Calcular duración del episodio si hay fechas
    IF :NEW.fecha_fin_contacto IS NOT NULL AND :NEW.fecha_ingreso IS NOT NULL THEN
        :NEW.duracion_episodio_calc := :NEW.fecha_fin_contacto - :NEW.fecha_ingreso;
    END IF;
    
    -- Determinar grupo etario basado en edad del paciente
    IF :NEW.paciente_id IS NOT NULL THEN
        DECLARE
            v_edad NUMBER;
        BEGIN
            SELECT edad_ingreso INTO v_edad
            FROM pacientes
            WHERE paciente_id = :NEW.paciente_id;
            
            :NEW.grupo_etario := CASE
                WHEN v_edad < 18 THEN '0-17'
                WHEN v_edad BETWEEN 18 AND 35 THEN '18-35'
                WHEN v_edad BETWEEN 36 AND 64 THEN '36-64'
                WHEN v_edad >= 65 THEN '65+'
                ELSE NULL
            END;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                NULL;
        END;
    END IF;
    
    -- Determinar día de la semana y mes del ingreso
    IF :NEW.fecha_ingreso IS NOT NULL THEN
        :NEW.dia_semana_ingreso := TO_CHAR(:NEW.fecha_ingreso, 'Day', 'NLS_DATE_LANGUAGE=SPANISH');
        :NEW.mes_nombre_ingreso := TO_CHAR(:NEW.fecha_ingreso, 'Month', 'NLS_DATE_LANGUAGE=SPANISH');
    END IF;
    
    -- Actualizar timestamp de modificación
    :NEW.fecha_modificacion := CURRENT_TIMESTAMP;
END;
/

-- ---------------------------------------------------------------------
-- Trigger: Actualizar contadores en EPISODIOS tras insertar diagnósticos
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_episodio_diag_count
AFTER INSERT OR DELETE ON episodios_diagnosticos
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    IF INSERTING THEN
        -- Incrementar contador de diagnósticos
        UPDATE episodios
        SET diagnosticos_totales = diagnosticos_totales + 1,
            tiene_comorbilidad = CASE WHEN diagnosticos_totales + 1 > 1 THEN 'S' ELSE 'N' END
        WHERE episodio_id = :NEW.episodio_id;
    ELSIF DELETING THEN
        -- Decrementar contador de diagnósticos
        SELECT COUNT(*) INTO v_count
        FROM episodios_diagnosticos
        WHERE episodio_id = :OLD.episodio_id;
        
        UPDATE episodios
        SET diagnosticos_totales = v_count,
            tiene_comorbilidad = CASE WHEN v_count > 1 THEN 'S' ELSE 'N' END
        WHERE episodio_id = :OLD.episodio_id;
    END IF;
END;
/

-- ---------------------------------------------------------------------
-- Trigger: Actualizar contadores en EPISODIOS tras insertar procedimientos
-- ---------------------------------------------------------------------
CREATE OR REPLACE TRIGGER trg_episodio_proc_count
AFTER INSERT OR DELETE ON episodios_procedimientos
FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    IF INSERTING THEN
        -- Incrementar contador de procedimientos
        UPDATE episodios
        SET procedimientos_totales = procedimientos_totales + 1,
            tiene_procedimiento = 'S'
        WHERE episodio_id = :NEW.episodio_id;
    ELSIF DELETING THEN
        -- Decrementar contador de procedimientos
        SELECT COUNT(*) INTO v_count
        FROM episodios_procedimientos
        WHERE episodio_id = :OLD.episodio_id;
        
        UPDATE episodios
        SET procedimientos_totales = v_count,
            tiene_procedimiento = CASE WHEN v_count > 0 THEN 'S' ELSE 'N' END
        WHERE episodio_id = :OLD.episodio_id;
    END IF;
END;
/

-- =====================================================================
-- PASO 12: DATOS DE PRUEBA (OPCIONAL - solo para testing)
-- =====================================================================

-- Los datos reales se cargarán mediante script de importación ETL
-- desde el archivo SaludMental_limpio.xlsx

-- =====================================================================
-- FIN DEL SCRIPT DE CREACIÓN
-- =====================================================================

-- Para verificar la creación exitosa:
SELECT 'Esquema creado exitosamente' AS status FROM dual;

-- Listado de tablas creadas
SELECT table_name, num_rows 
FROM user_tables 
WHERE table_name IN (
    'COMUNIDADES_AUTONOMAS', 'PAISES', 'CENTROS_HOSPITALARIOS',
    'DIAGNOSTICOS_CIE', 'PROCEDIMIENTOS', 'PACIENTES',
    'EPISODIOS', 'EPISODIOS_DIAGNOSTICOS', 'EPISODIOS_PROCEDIMIENTOS'
)
ORDER BY table_name;

-- Listado de vistas creadas
SELECT view_name 
FROM user_views 
WHERE view_name IN (
    'VISTA_MUY_INTERESANTE', 'RESUMEN_DIAGNOSTICOS_PRINCIPALES',
    'RESUMEN_CENTROS', 'RESUMEN_TEMPORAL'
)
ORDER BY view_name;

-- Listado de índices creados
SELECT index_name, table_name, uniqueness
FROM user_indexes
WHERE table_name IN (
    'PACIENTES', 'EPISODIOS', 'DIAGNOSTICOS_CIE', 
    'CENTROS_HOSPITALARIOS', 'EPISODIOS_DIAGNOSTICOS', 'EPISODIOS_PROCEDIMIENTOS'
)
ORDER BY table_name, index_name;

