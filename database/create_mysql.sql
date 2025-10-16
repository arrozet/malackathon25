-- =====================================================================
-- Script de Creación de Base de Datos - II Malackathon 2025
-- Base de Datos: MySQL 8.0+
-- Tema: Análisis de Datos de Salud Mental - Hospitalizaciones
-- =====================================================================
-- Autor: Brain - AI Research Companion (Convertido a MySQL)
-- Descripción: Esquema normalizado para almacenar datos de episodios
--              de hospitalización en salud mental, con normalización
--              a 3FN y anonimización mediante sustitución.
-- =====================================================================

-- =====================================================================
-- PASO 1: LIMPIEZA DE ESQUEMA (para hacer el script re-ejecutable)
-- =====================================================================
-- Nota: Esta sección elimina vistas y tablas existentes para permitir
--       la re-ejecución del script. Comentar en producción si es necesario.

-- Deshabilitar temporalmente las comprobaciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 0;

-- Eliminar triggers primero
DROP TRIGGER IF EXISTS trg_episodios_calc;
DROP TRIGGER IF EXISTS trg_episodios_calc_update;
DROP TRIGGER IF EXISTS trg_episodio_diag_insert;
DROP TRIGGER IF EXISTS trg_episodio_diag_delete;
DROP TRIGGER IF EXISTS trg_episodio_proc_insert;
DROP TRIGGER IF EXISTS trg_episodio_proc_delete;

-- Eliminar vistas
DROP VIEW IF EXISTS vista_muy_interesante;
DROP VIEW IF EXISTS resumen_diagnosticos_principales;
DROP VIEW IF EXISTS resumen_centros;
DROP VIEW IF EXISTS resumen_temporal;

-- Eliminar tablas en orden correcto (tablas dependientes primero)
DROP TABLE IF EXISTS episodios_procedimientos;
DROP TABLE IF EXISTS episodios_diagnosticos;
DROP TABLE IF EXISTS episodios;
DROP TABLE IF EXISTS pacientes;
DROP TABLE IF EXISTS procedimientos;
DROP TABLE IF EXISTS diagnosticos_cie;
DROP TABLE IF EXISTS centros_hospitalarios;
DROP TABLE IF EXISTS paises;
DROP TABLE IF EXISTS comunidades_autonomas;

-- Rehabilitar las comprobaciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- PASO 2: CREACIÓN DE BASE DE DATOS
-- =====================================================================

-- Nota: Las secuencias de Oracle se reemplazan con AUTO_INCREMENT en MySQL
-- No es necesario crear secuencias por separado

-- =====================================================================
-- PASO 3: TABLAS DE CATÁLOGOS Y DIMENSIONES
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: COMUNIDADES_AUTONOMAS
-- Descripción: Catálogo de comunidades autónomas de España
-- ---------------------------------------------------------------------
CREATE TABLE comunidades_autonomas (
    comunidad_id        INT             AUTO_INCREMENT PRIMARY KEY,
    codigo_comunidad    VARCHAR(10)     NOT NULL UNIQUE,
    nombre_comunidad    VARCHAR(100)    NOT NULL,
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo_comunidad (codigo_comunidad)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de comunidades autónomas de España';

-- ---------------------------------------------------------------------
-- Tabla: PAISES
-- Descripción: Catálogo de países (códigos ISO)
-- ---------------------------------------------------------------------
CREATE TABLE paises (
    pais_id             INT             AUTO_INCREMENT PRIMARY KEY,
    codigo_pais         VARCHAR(10)     NOT NULL UNIQUE,
    nombre_pais         VARCHAR(100),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_codigo_pais (codigo_pais)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de países según códigos ISO';

-- ---------------------------------------------------------------------
-- Tabla: CENTROS_HOSPITALARIOS
-- Descripción: Catálogo de centros hospitalarios
-- ---------------------------------------------------------------------
CREATE TABLE centros_hospitalarios (
    centro_id           INT             AUTO_INCREMENT PRIMARY KEY,
    codigo_centro       VARCHAR(50)     NOT NULL UNIQUE,
    nombre_centro       VARCHAR(200),
    comunidad_id        INT             NOT NULL,
    activo              CHAR(1)         DEFAULT 'S' CHECK (activo IN ('S', 'N')),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_centro_comunidad FOREIGN KEY (comunidad_id)
        REFERENCES comunidades_autonomas(comunidad_id),
    INDEX idx_centro_comunidad (comunidad_id),
    INDEX idx_centro_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de centros hospitalarios';

-- ---------------------------------------------------------------------
-- Tabla: DIAGNOSTICOS_CIE
-- Descripción: Catálogo de códigos diagnósticos CIE-10
-- ---------------------------------------------------------------------
CREATE TABLE diagnosticos_cie (
    diagnostico_id      INT             AUTO_INCREMENT PRIMARY KEY,
    codigo_cie          VARCHAR(20)     NOT NULL UNIQUE,
    descripcion         VARCHAR(500),
    capitulo_cie        VARCHAR(10),
    es_mental           CHAR(1)         DEFAULT 'N' CHECK (es_mental IN ('S', 'N')),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_diagnostico_capitulo (capitulo_cie),
    INDEX idx_diagnostico_mental (es_mental)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de códigos diagnósticos CIE-10';

-- ---------------------------------------------------------------------
-- Tabla: PROCEDIMIENTOS
-- Descripción: Catálogo de procedimientos clínicos
-- ---------------------------------------------------------------------
CREATE TABLE procedimientos (
    procedimiento_id    INT             AUTO_INCREMENT PRIMARY KEY,
    codigo_proc         VARCHAR(20)     NOT NULL UNIQUE,
    descripcion         VARCHAR(500),
    categoria           VARCHAR(100),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de procedimientos clínicos';

-- =====================================================================
-- PASO 4: TABLA DE PACIENTES (ANONIMIZADA)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: PACIENTES
-- Descripción: Información demográfica anonimizada de pacientes
-- Nota: Los nombres han sido sustituidos por identificadores anónimos
-- ---------------------------------------------------------------------
CREATE TABLE pacientes (
    paciente_id         INT             AUTO_INCREMENT PRIMARY KEY,
    identificador_anonimo VARCHAR(100)  NOT NULL UNIQUE,
    edad_ingreso        INT,
    sexo                CHAR(1)         CHECK (sexo IN ('M', 'F', 'X', 'N')),
    pais_nacimiento_id  INT,
    comunidad_residencia_id INT,
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_paciente_pais FOREIGN KEY (pais_nacimiento_id)
        REFERENCES paises(pais_id),
    CONSTRAINT fk_paciente_comunidad FOREIGN KEY (comunidad_residencia_id)
        REFERENCES comunidades_autonomas(comunidad_id),
    INDEX idx_paciente_sexo (sexo),
    INDEX idx_paciente_pais (pais_nacimiento_id),
    INDEX idx_paciente_edad (edad_ingreso)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Información demográfica anonimizada de pacientes';

-- =====================================================================
-- PASO 5: TABLA DE EPISODIOS (CORE)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: EPISODIOS
-- Descripción: Episodios de hospitalización en salud mental
-- ---------------------------------------------------------------------
CREATE TABLE episodios (
    episodio_id         INT             AUTO_INCREMENT PRIMARY KEY,
    paciente_id         INT             NOT NULL,
    centro_id           INT             NOT NULL,
    numero_registro     VARCHAR(50),
    categoria           VARCHAR(100),
    fecha_ingreso       DATE            NOT NULL,
    fecha_fin_contacto  DATE,
    mes_ingreso         DATE,
    estancia_dias       INT,
    tipo_alta           SMALLINT,
    circunstancia_contacto SMALLINT,
    -- Campos calculados/derivados
    duracion_episodio_calc INT,
    dia_semana_ingreso  VARCHAR(20),
    mes_nombre_ingreso  VARCHAR(20),
    grupo_etario        VARCHAR(10),
    -- Clasificación APR-DRG
    grd_apr             BIGINT,
    cdm_apr             BIGINT,
    nivel_severidad_apr SMALLINT,
    riesgo_mortalidad_apr SMALLINT,
    peso_espanol_apr    DECIMAL(10,4),
    coste_apr           DECIMAL(12,2),
    -- Métricas agregadas
    diagnosticos_totales SMALLINT       DEFAULT 0,
    procedimientos_totales SMALLINT     DEFAULT 0,
    tiene_procedimiento CHAR(1)         DEFAULT 'N' CHECK (tiene_procedimiento IN ('S', 'N')),
    tiene_comorbilidad  CHAR(1)         DEFAULT 'N' CHECK (tiene_comorbilidad IN ('S', 'N')),
    -- Auditoría
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Constraints
    CONSTRAINT fk_episodio_paciente FOREIGN KEY (paciente_id)
        REFERENCES pacientes(paciente_id),
    CONSTRAINT fk_episodio_centro FOREIGN KEY (centro_id)
        REFERENCES centros_hospitalarios(centro_id),
    CONSTRAINT chk_fechas CHECK (fecha_fin_contacto IS NULL OR fecha_fin_contacto >= fecha_ingreso),
    CONSTRAINT chk_estancia CHECK (estancia_dias IS NULL OR estancia_dias >= 0),
    INDEX idx_episodio_paciente (paciente_id),
    INDEX idx_episodio_centro (centro_id),
    INDEX idx_episodio_fecha_ingreso (fecha_ingreso),
    INDEX idx_episodio_fecha_fin (fecha_fin_contacto),
    INDEX idx_episodio_tipo_alta (tipo_alta),
    INDEX idx_episodio_severidad (nivel_severidad_apr),
    INDEX idx_episodio_riesgo (riesgo_mortalidad_apr),
    INDEX idx_episodio_grd (grd_apr),
    INDEX idx_episodio_estancia (estancia_dias),
    INDEX idx_episodio_coste (coste_apr)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Episodios de hospitalización en salud mental';

-- =====================================================================
-- PASO 6: TABLAS DE RELACIÓN (MUCHOS A MUCHOS)
-- =====================================================================

-- ---------------------------------------------------------------------
-- Tabla: EPISODIOS_DIAGNOSTICOS
-- Descripción: Relación entre episodios y diagnósticos (incluye orden)
-- ---------------------------------------------------------------------
CREATE TABLE episodios_diagnosticos (
    episodio_id         INT             NOT NULL,
    diagnostico_id      INT             NOT NULL,
    orden_diagnostico   SMALLINT        NOT NULL,
    es_principal        CHAR(1)         DEFAULT 'N' CHECK (es_principal IN ('S', 'N')),
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (episodio_id, diagnostico_id, orden_diagnostico),
    CONSTRAINT fk_epidiag_episodio FOREIGN KEY (episodio_id)
        REFERENCES episodios(episodio_id) ON DELETE CASCADE,
    CONSTRAINT fk_epidiag_diagnostico FOREIGN KEY (diagnostico_id)
        REFERENCES diagnosticos_cie(diagnostico_id),
    INDEX idx_epidiag_diagnostico (diagnostico_id),
    INDEX idx_epidiag_principal (es_principal)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Relación entre episodios y diagnósticos';

-- ---------------------------------------------------------------------
-- Tabla: EPISODIOS_PROCEDIMIENTOS
-- Descripción: Relación entre episodios y procedimientos (incluye orden)
-- ---------------------------------------------------------------------
CREATE TABLE episodios_procedimientos (
    episodio_id         INT             NOT NULL,
    procedimiento_id    INT             NOT NULL,
    orden_procedimiento SMALLINT        NOT NULL,
    fecha_realizacion   DATE,
    fecha_creacion      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (episodio_id, procedimiento_id, orden_procedimiento),
    CONSTRAINT fk_epiproc_episodio FOREIGN KEY (episodio_id)
        REFERENCES episodios(episodio_id) ON DELETE CASCADE,
    CONSTRAINT fk_epiproc_procedimiento FOREIGN KEY (procedimiento_id)
        REFERENCES procedimientos(procedimiento_id),
    INDEX idx_epiproc_procedimiento (procedimiento_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Relación entre episodios y procedimientos realizados';

-- =====================================================================
-- PASO 7: VISTA PRINCIPAL PARA EL USUARIO MALACKATHON
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
CREATE VIEW vista_muy_interesante AS
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

-- =====================================================================
-- PASO 8: VISTAS ADICIONALES PARA ANÁLISIS
-- =====================================================================

-- ---------------------------------------------------------------------
-- Vista: RESUMEN_DIAGNOSTICOS_PRINCIPALES
-- Descripción: Estadísticas agregadas por diagnóstico principal
-- ---------------------------------------------------------------------
CREATE VIEW resumen_diagnosticos_principales AS
SELECT
    dc.codigo_cie,
    dc.descripcion,
    dc.capitulo_cie,
    COUNT(DISTINCT e.episodio_id) AS total_episodios,
    COUNT(DISTINCT e.paciente_id) AS total_pacientes,
    ROUND(AVG(e.estancia_dias), 2) AS estancia_promedio,
    MIN(e.estancia_dias) AS estancia_minima,
    MAX(e.estancia_dias) AS estancia_maxima,
    ROUND(AVG(e.coste_apr), 2) AS coste_promedio,
    MIN(e.coste_apr) AS coste_minimo,
    MAX(e.coste_apr) AS coste_maximo,
    ROUND(AVG(p.edad_ingreso), 2) AS edad_promedio,
    SUM(CASE WHEN p.sexo = 'M' THEN 1 ELSE 0 END) AS casos_masculinos,
    SUM(CASE WHEN p.sexo = 'F' THEN 1 ELSE 0 END) AS casos_femeninos
FROM
    diagnosticos_cie dc
    INNER JOIN episodios_diagnosticos ed ON dc.diagnostico_id = ed.diagnostico_id AND ed.es_principal = 'S'
    INNER JOIN episodios e ON ed.episodio_id = e.episodio_id
    INNER JOIN pacientes p ON e.paciente_id = p.paciente_id
GROUP BY
    dc.diagnostico_id, dc.codigo_cie, dc.descripcion, dc.capitulo_cie
ORDER BY
    total_episodios DESC;

-- ---------------------------------------------------------------------
-- Vista: RESUMEN_CENTROS
-- Descripción: Estadísticas agregadas por centro hospitalario
-- ---------------------------------------------------------------------
CREATE VIEW resumen_centros AS
SELECT
    c.codigo_centro,
    c.nombre_centro,
    ca.nombre_comunidad,
    COUNT(DISTINCT e.episodio_id) AS total_episodios,
    COUNT(DISTINCT e.paciente_id) AS total_pacientes,
    ROUND(AVG(e.estancia_dias), 2) AS estancia_promedio,
    ROUND(AVG(e.coste_apr), 2) AS coste_promedio,
    ROUND(AVG(e.nivel_severidad_apr), 2) AS severidad_promedio,
    SUM(CASE WHEN e.tipo_alta = 4 THEN 1 ELSE 0 END) AS total_exitus
FROM
    centros_hospitalarios c
    INNER JOIN episodios e ON c.centro_id = e.centro_id
    INNER JOIN comunidades_autonomas ca ON c.comunidad_id = ca.comunidad_id
GROUP BY
    c.centro_id, c.codigo_centro, c.nombre_centro, ca.nombre_comunidad
ORDER BY
    total_episodios DESC;

-- ---------------------------------------------------------------------
-- Vista: RESUMEN_TEMPORAL
-- Descripción: Evolución temporal de episodios por mes
-- ---------------------------------------------------------------------
CREATE VIEW resumen_temporal AS
SELECT
    YEAR(e.fecha_ingreso) AS anio,
    LPAD(MONTH(e.fecha_ingreso), 2, '0') AS mes_numero,
    DATE_FORMAT(e.fecha_ingreso, '%M') AS mes_nombre,
    DATE_FORMAT(e.fecha_ingreso, '%Y-%m') AS periodo,
    COUNT(DISTINCT e.episodio_id) AS total_episodios,
    COUNT(DISTINCT e.paciente_id) AS total_pacientes,
    ROUND(AVG(e.estancia_dias), 2) AS estancia_promedio,
    ROUND(AVG(e.coste_apr), 2) AS coste_promedio
FROM
    episodios e
WHERE
    e.fecha_ingreso IS NOT NULL
GROUP BY
    YEAR(e.fecha_ingreso),
    MONTH(e.fecha_ingreso),
    DATE_FORMAT(e.fecha_ingreso, '%M'),
    DATE_FORMAT(e.fecha_ingreso, '%Y-%m')
ORDER BY
    anio, mes_numero;

-- =====================================================================
-- PASO 9: TRIGGERS PARA AUDITORÍA Y VALIDACIÓN
-- =====================================================================

-- ---------------------------------------------------------------------
-- Trigger: Validar y calcular campos derivados en EPISODIOS
-- ---------------------------------------------------------------------
DELIMITER $$

CREATE TRIGGER trg_episodios_calc
BEFORE INSERT ON episodios
FOR EACH ROW
BEGIN
    -- Calcular duración del episodio si hay fechas
    IF NEW.fecha_fin_contacto IS NOT NULL AND NEW.fecha_ingreso IS NOT NULL THEN
        SET NEW.duracion_episodio_calc = DATEDIFF(NEW.fecha_fin_contacto, NEW.fecha_ingreso);
    END IF;
    
    -- Determinar grupo etario basado en edad del paciente
    IF NEW.paciente_id IS NOT NULL THEN
        BEGIN
            DECLARE v_edad INT;
            
            SELECT edad_ingreso INTO v_edad
            FROM pacientes
            WHERE paciente_id = NEW.paciente_id;
            
            SET NEW.grupo_etario = CASE
                WHEN v_edad < 18 THEN '0-17'
                WHEN v_edad BETWEEN 18 AND 35 THEN '18-35'
                WHEN v_edad BETWEEN 36 AND 64 THEN '36-64'
                WHEN v_edad >= 65 THEN '65+'
                ELSE NULL
            END;
        END;
    END IF;
    
    -- Determinar día de la semana y mes del ingreso
    IF NEW.fecha_ingreso IS NOT NULL THEN
        SET NEW.dia_semana_ingreso = DATE_FORMAT(NEW.fecha_ingreso, '%W');
        SET NEW.mes_nombre_ingreso = DATE_FORMAT(NEW.fecha_ingreso, '%M');
    END IF;
END$$

CREATE TRIGGER trg_episodios_calc_update
BEFORE UPDATE ON episodios
FOR EACH ROW
BEGIN
    -- Calcular duración del episodio si hay fechas
    IF NEW.fecha_fin_contacto IS NOT NULL AND NEW.fecha_ingreso IS NOT NULL THEN
        SET NEW.duracion_episodio_calc = DATEDIFF(NEW.fecha_fin_contacto, NEW.fecha_ingreso);
    END IF;
    
    -- Determinar grupo etario basado en edad del paciente
    IF NEW.paciente_id IS NOT NULL THEN
        BEGIN
            DECLARE v_edad INT;
            
            SELECT edad_ingreso INTO v_edad
            FROM pacientes
            WHERE paciente_id = NEW.paciente_id;
            
            SET NEW.grupo_etario = CASE
                WHEN v_edad < 18 THEN '0-17'
                WHEN v_edad BETWEEN 18 AND 35 THEN '18-35'
                WHEN v_edad BETWEEN 36 AND 64 THEN '36-64'
                WHEN v_edad >= 65 THEN '65+'
                ELSE NULL
            END;
        END;
    END IF;
    
    -- Determinar día de la semana y mes del ingreso
    IF NEW.fecha_ingreso IS NOT NULL THEN
        SET NEW.dia_semana_ingreso = DATE_FORMAT(NEW.fecha_ingreso, '%W');
        SET NEW.mes_nombre_ingreso = DATE_FORMAT(NEW.fecha_ingreso, '%M');
    END IF;
END$$

-- ---------------------------------------------------------------------
-- Trigger: Actualizar contadores en EPISODIOS tras insertar diagnósticos
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_episodio_diag_insert
AFTER INSERT ON episodios_diagnosticos
FOR EACH ROW
BEGIN
    UPDATE episodios
    SET diagnosticos_totales = diagnosticos_totales + 1,
        tiene_comorbilidad = CASE WHEN diagnosticos_totales + 1 > 1 THEN 'S' ELSE 'N' END
    WHERE episodio_id = NEW.episodio_id;
END$$

CREATE TRIGGER trg_episodio_diag_delete
AFTER DELETE ON episodios_diagnosticos
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    
    SELECT COUNT(*) INTO v_count
    FROM episodios_diagnosticos
    WHERE episodio_id = OLD.episodio_id;
    
    UPDATE episodios
    SET diagnosticos_totales = v_count,
        tiene_comorbilidad = CASE WHEN v_count > 1 THEN 'S' ELSE 'N' END
    WHERE episodio_id = OLD.episodio_id;
END$$

-- ---------------------------------------------------------------------
-- Trigger: Actualizar contadores en EPISODIOS tras insertar procedimientos
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_episodio_proc_insert
AFTER INSERT ON episodios_procedimientos
FOR EACH ROW
BEGIN
    UPDATE episodios
    SET procedimientos_totales = procedimientos_totales + 1,
        tiene_procedimiento = 'S'
    WHERE episodio_id = NEW.episodio_id;
END$$

CREATE TRIGGER trg_episodio_proc_delete
AFTER DELETE ON episodios_procedimientos
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    
    SELECT COUNT(*) INTO v_count
    FROM episodios_procedimientos
    WHERE episodio_id = OLD.episodio_id;
    
    UPDATE episodios
    SET procedimientos_totales = v_count,
        tiene_procedimiento = CASE WHEN v_count > 0 THEN 'S' ELSE 'N' END
    WHERE episodio_id = OLD.episodio_id;
END$$

DELIMITER ;

-- =====================================================================
-- PASO 10: CREACIÓN DE USUARIO MALACKATHON CON PERMISOS DE LECTURA
-- =====================================================================

-- NOTA: Ejecutar esta sección con usuario ROOT de MySQL
-- La contraseña debe ser proporcionada por los organizadores del hackathon

/*
-- Crear usuario malackathon
CREATE USER IF NOT EXISTS 'malackathon'@'%' IDENTIFIED BY '<PASSWORD_PROPORCIONADA_POR_ORGANIZADORES>';

-- Otorgar permisos de lectura en todas las tablas de la base de datos
GRANT SELECT ON malackathon25.* TO 'malackathon'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;
*/

-- =====================================================================
-- FIN DEL SCRIPT DE CREACIÓN
-- =====================================================================

-- Para verificar la creación exitosa:
SELECT 'Esquema creado exitosamente' AS status;

-- Listado de tablas creadas
SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN (
    'comunidades_autonomas', 'paises', 'centros_hospitalarios',
    'diagnosticos_cie', 'procedimientos', 'pacientes',
    'episodios', 'episodios_diagnosticos', 'episodios_procedimientos'
)
ORDER BY TABLE_NAME;

-- Listado de vistas creadas
SELECT TABLE_NAME AS VIEW_NAME
FROM information_schema.VIEWS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN (
    'vista_muy_interesante', 'resumen_diagnosticos_principales',
    'resumen_centros', 'resumen_temporal'
)
ORDER BY TABLE_NAME;

-- Listado de índices creados
SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN (
    'pacientes', 'episodios', 'diagnosticos_cie', 
    'centros_hospitalarios', 'episodios_diagnosticos', 'episodios_procedimientos'
)
ORDER BY TABLE_NAME, INDEX_NAME;

