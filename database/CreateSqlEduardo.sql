-- #####################################################################
-- ## Script para la creación de la Base de Datos de Salud Mental    ##
-- ## Convertido a MySQL 8.0+ (Basado en EduardoScript)              ##
-- ## Versión: 2.0 MySQL                                             ##
-- #####################################################################

-- =====================================================================
-- LIMPIEZA: Hacer el script re-ejecutable
-- =====================================================================
-- IMPORTANTE: Ejecutar TODO el script completo, no línea por línea

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE='ALLOW_INVALID_DATES';

-- Eliminar vistas primero
DROP VIEW IF EXISTS VISTA_MUY_INTERESANTE;

-- Eliminar triggers
DROP TRIGGER IF EXISTS trg_ingreso_diag_insert;
DROP TRIGGER IF EXISTS trg_ingreso_diag_delete;
DROP TRIGGER IF EXISTS trg_ingreso_proc_insert;
DROP TRIGGER IF EXISTS trg_ingreso_proc_delete;
DROP TRIGGER IF EXISTS trg_ingresos_pk;
DROP TRIGGER IF EXISTS trg_ingreso_diag_pk;
DROP TRIGGER IF EXISTS trg_ingreso_proc_pk;

-- Eliminar tablas en orden correcto (dependencias primero)
DROP TABLE IF EXISTS Ingreso_Procedimientos;
DROP TABLE IF EXISTS Ingreso_Diagnosticos;
DROP TABLE IF EXISTS Ingresos;
DROP TABLE IF EXISTS Pacientes;
DROP TABLE IF EXISTS GRD_APR;
DROP TABLE IF EXISTS Procedimientos;
DROP TABLE IF EXISTS Diagnosticos;

SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- 1. CREACIÓN DE TABLAS DE DIMENSIONES
-- =====================================================================

-- Tabla para Diagnósticos
CREATE TABLE Diagnosticos (
    ID_Diagnostico          VARCHAR(20) NOT NULL,
    Categoria               VARCHAR(255),
    CONSTRAINT pk_diagnosticos PRIMARY KEY (ID_Diagnostico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de diagnósticos CIE-10';

-- Tabla para Procedimientos
CREATE TABLE Procedimientos (
    ID_Procedimiento        VARCHAR(20) NOT NULL,
    CONSTRAINT pk_procedimientos PRIMARY KEY (ID_Procedimiento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de procedimientos médicos';

-- Tabla para GRD (Grupo Relacionado por el Diagnóstico)
CREATE TABLE GRD_APR (
    ID_GRD_APR              VARCHAR(10) NOT NULL,
    CDM_APR                 INT,
    Nivel_Severidad_APR     TINYINT,
    Riesgo_Mortalidad_APR   TINYINT,
    Tipo_GRD_APR            VARCHAR(5),
    CONSTRAINT pk_grd_apr PRIMARY KEY (ID_GRD_APR)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Clasificación APR-DRG';

-- =====================================================================
-- 2. CREACIÓN DE TABLAS PRINCIPALES
-- =====================================================================

-- Tabla para Pacientes
-- Se han reemplazado los FKs por campos de texto directos
CREATE TABLE Pacientes (
    UUID_Paciente           VARCHAR(36) NOT NULL,
    CIP_SNS_Recodificado    VARCHAR(50),
    Fecha_de_nacimiento     DATE,
    Sexo                    TINYINT,
    Grupo_Etario            VARCHAR(20),
    Comunidad_Autonoma      VARCHAR(100),
    Pais_Nacimiento         VARCHAR(100),
    Pais_Residencia         VARCHAR(100),
    CONSTRAINT pk_pacientes PRIMARY KEY (UUID_Paciente),
    INDEX idx_paciente_sexo (Sexo),
    INDEX idx_paciente_grupo_etario (Grupo_Etario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Información demográfica de pacientes (anonimizada)';

-- Tabla para Ingresos (Tabla de Hechos)
-- Se ha reemplazado el FK a Centros por un campo numérico directo
CREATE TABLE Ingresos (
    ID_Ingreso              INT NOT NULL AUTO_INCREMENT,
    UUID_Paciente           VARCHAR(36) NOT NULL,
    Centro_Recodificado     INT NOT NULL,
    ID_GRD_APR              VARCHAR(10),
    Numero_de_registro_anual VARCHAR(50),
    Fecha_de_Ingreso        DATE,
    Fecha_de_Fin_Contacto   DATE,
    Fecha_de_Inicio_contacto DATE,
    Circunstancia_de_Contacto TINYINT,
    Tipo_Alta               TINYINT,
    Servicio                VARCHAR(10),
    Regimen_Financiacion    TINYINT,
    Procedencia             TINYINT,
    Continuidad_Asistencial TINYINT,
    Estancia_Dias           SMALLINT,
    Estancia_Dias_Acotada   SMALLINT,
    Duracion_Episodio_Calculada SMALLINT,
    Edad                    TINYINT,
    Edad_en_Ingreso         TINYINT,
    Mes_de_Ingreso          TINYINT,
    Mes_Nombre_Ingreso      VARCHAR(20),
    Dia_Semana_Ingreso      VARCHAR(20),
    Coste_APR               DECIMAL(12, 2),
    Peso_Español_APR        DECIMAL(10, 6),
    Ingreso_en_UCI          CHAR(1) DEFAULT 'N' CHECK (Ingreso_en_UCI IN ('S', 'N')),
    Diagnosticos_totales    SMALLINT DEFAULT 0,
    Procedimientos_totales  SMALLINT DEFAULT 0,
    Tiene_procedimiento     CHAR(1) DEFAULT 'N' CHECK (Tiene_procedimiento IN ('S', 'N')),
    Diagnostico_F           CHAR(1) DEFAULT 'N' CHECK (Diagnostico_F IN ('S', 'N')),
    Tiene_Comorbilidad      CHAR(1) DEFAULT 'N' CHECK (Tiene_Comorbilidad IN ('S', 'N')),
    CONSTRAINT pk_ingresos PRIMARY KEY (ID_Ingreso),
    CONSTRAINT fk_ingresos_paciente FOREIGN KEY (UUID_Paciente) 
        REFERENCES Pacientes(UUID_Paciente) ON DELETE CASCADE,
    CONSTRAINT fk_ingresos_grd FOREIGN KEY (ID_GRD_APR) 
        REFERENCES GRD_APR(ID_GRD_APR),
    CONSTRAINT chk_fechas CHECK (Fecha_de_Fin_Contacto IS NULL OR Fecha_de_Fin_Contacto >= Fecha_de_Ingreso),
    INDEX idx_ingreso_fecha (Fecha_de_Ingreso),
    INDEX idx_ingreso_centro (Centro_Recodificado),
    INDEX idx_ingreso_tipo_alta (Tipo_Alta),
    INDEX idx_ingreso_grd (ID_GRD_APR)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabla de hechos de ingresos hospitalarios';

-- =====================================================================
-- 3. CREACIÓN DE TABLAS DE RELACIÓN
-- =====================================================================

-- Tabla que relaciona Ingresos con Diagnósticos
CREATE TABLE Ingreso_Diagnosticos (
    ID_Ingreso_Diagnostico  INT NOT NULL AUTO_INCREMENT,
    ID_Ingreso              INT NOT NULL,
    ID_Diagnostico          VARCHAR(20) NOT NULL,
    Orden_Diagnostico       TINYINT NOT NULL,
    POA                     CHAR(1) CHECK (POA IN ('S', 'N', 'U', 'W', 'Y')),
    CONSTRAINT pk_ingreso_diagnosticos PRIMARY KEY (ID_Ingreso_Diagnostico),
    CONSTRAINT fk_ingdiag_ingreso FOREIGN KEY (ID_Ingreso) 
        REFERENCES Ingresos(ID_Ingreso) ON DELETE CASCADE,
    CONSTRAINT fk_ingdiag_diagnostico FOREIGN KEY (ID_Diagnostico) 
        REFERENCES Diagnosticos(ID_Diagnostico),
    UNIQUE KEY uk_ingreso_diag_orden (ID_Ingreso, Orden_Diagnostico),
    INDEX idx_ingdiag_diagnostico (ID_Diagnostico),
    INDEX idx_ingdiag_orden (Orden_Diagnostico)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Relación entre ingresos y diagnósticos';

-- Tabla que relaciona Ingresos con Procedimientos
CREATE TABLE Ingreso_Procedimientos (
    ID_Ingreso_Procedimiento INT NOT NULL AUTO_INCREMENT,
    ID_Ingreso               INT NOT NULL,
    ID_Procedimiento         VARCHAR(20) NOT NULL,
    Orden_Procedimiento      TINYINT NOT NULL,
    CONSTRAINT pk_ingreso_procedimientos PRIMARY KEY (ID_Ingreso_Procedimiento),
    CONSTRAINT fk_ingproc_ingreso FOREIGN KEY (ID_Ingreso) 
        REFERENCES Ingresos(ID_Ingreso) ON DELETE CASCADE,
    CONSTRAINT fk_ingproc_procedimiento FOREIGN KEY (ID_Procedimiento) 
        REFERENCES Procedimientos(ID_Procedimiento),
    UNIQUE KEY uk_ingreso_proc_orden (ID_Ingreso, Orden_Procedimiento),
    INDEX idx_ingproc_procedimiento (ID_Procedimiento),
    INDEX idx_ingproc_orden (Orden_Procedimiento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Relación entre ingresos y procedimientos';

-- =====================================================================
-- 4. TRIGGERS PARA ACTUALIZACIÓN AUTOMÁTICA DE CONTADORES
-- =====================================================================

DELIMITER $$

-- Trigger: Actualizar contadores al insertar diagnóstico
CREATE TRIGGER trg_ingreso_diag_insert
AFTER INSERT ON Ingreso_Diagnosticos
FOR EACH ROW
BEGIN
    UPDATE Ingresos
    SET Diagnosticos_totales = Diagnosticos_totales + 1,
        Tiene_Comorbilidad = CASE WHEN Diagnosticos_totales + 1 > 1 THEN 'S' ELSE 'N' END,
        Diagnostico_F = CASE 
            WHEN NEW.ID_Diagnostico LIKE 'F%' THEN 'S' 
            WHEN Diagnostico_F = 'S' THEN 'S'
            ELSE 'N' 
        END
    WHERE ID_Ingreso = NEW.ID_Ingreso;
END$$

-- Trigger: Actualizar contadores al eliminar diagnóstico
CREATE TRIGGER trg_ingreso_diag_delete
AFTER DELETE ON Ingreso_Diagnosticos
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    DECLARE v_tiene_f CHAR(1);
    
    SELECT COUNT(*) INTO v_count
    FROM Ingreso_Diagnosticos
    WHERE ID_Ingreso = OLD.ID_Ingreso;
    
    -- Verificar si hay algún diagnóstico F restante
    SELECT CASE WHEN COUNT(*) > 0 THEN 'S' ELSE 'N' END INTO v_tiene_f
    FROM Ingreso_Diagnosticos
    WHERE ID_Ingreso = OLD.ID_Ingreso AND ID_Diagnostico LIKE 'F%';
    
    UPDATE Ingresos
    SET Diagnosticos_totales = v_count,
        Tiene_Comorbilidad = CASE WHEN v_count > 1 THEN 'S' ELSE 'N' END,
        Diagnostico_F = v_tiene_f
    WHERE ID_Ingreso = OLD.ID_Ingreso;
END$$

-- Trigger: Actualizar contadores al insertar procedimiento
CREATE TRIGGER trg_ingreso_proc_insert
AFTER INSERT ON Ingreso_Procedimientos
FOR EACH ROW
BEGIN
    UPDATE Ingresos
    SET Procedimientos_totales = Procedimientos_totales + 1,
        Tiene_procedimiento = 'S'
    WHERE ID_Ingreso = NEW.ID_Ingreso;
END$$

-- Trigger: Actualizar contadores al eliminar procedimiento
CREATE TRIGGER trg_ingreso_proc_delete
AFTER DELETE ON Ingreso_Procedimientos
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    
    SELECT COUNT(*) INTO v_count
    FROM Ingreso_Procedimientos
    WHERE ID_Ingreso = OLD.ID_Ingreso;
    
    UPDATE Ingresos
    SET Procedimientos_totales = v_count,
        Tiene_procedimiento = CASE WHEN v_count > 0 THEN 'S' ELSE 'N' END
    WHERE ID_Ingreso = OLD.ID_Ingreso;
END$$

DELIMITER ;

-- =====================================================================
-- 5. VISTA PRINCIPAL: VISTA_MUY_INTERESANTE
-- =====================================================================

DROP VIEW IF EXISTS VISTA_MUY_INTERESANTE;

CREATE VIEW VISTA_MUY_INTERESANTE AS
SELECT
    -- Identificadores
    i.ID_Ingreso,
    i.UUID_Paciente,
    i.Numero_de_registro_anual,
    
    -- Información del paciente
    p.CIP_SNS_Recodificado,
    p.Fecha_de_nacimiento,
    CASE p.Sexo
        WHEN 0 THEN 'No especificado'
        WHEN 1 THEN 'Hombre'
        WHEN 2 THEN 'Mujer'
        ELSE 'Otro'
    END AS Sexo_Descripcion,
    p.Grupo_Etario,
    p.Comunidad_Autonoma,
    p.Pais_Nacimiento,
    p.Pais_Residencia,
    
    -- Información del ingreso
    i.Centro_Recodificado,
    i.Fecha_de_Ingreso,
    i.Fecha_de_Fin_Contacto,
    i.Fecha_de_Inicio_contacto,
    i.Estancia_Dias,
    i.Estancia_Dias_Acotada,
    i.Duracion_Episodio_Calculada,
    
    -- Información temporal
    i.Mes_de_Ingreso,
    i.Mes_Nombre_Ingreso,
    i.Dia_Semana_Ingreso,
    
    -- Información clínica
    CASE i.Tipo_Alta
        WHEN 1 THEN 'Domicilio'
        WHEN 2 THEN 'Traslado a otro hospital'
        WHEN 3 THEN 'Alta voluntaria'
        WHEN 4 THEN 'Éxitus'
        WHEN 5 THEN 'Traslado a centro sociosanitario'
        ELSE 'Otros'
    END AS Tipo_Alta_Descripcion,
    i.Circunstancia_de_Contacto,
    i.Servicio,
    i.Regimen_Financiacion,
    i.Procedencia,
    i.Continuidad_Asistencial,
    
    -- Edad
    i.Edad,
    i.Edad_en_Ingreso,
    
    -- Clasificación GRD
    i.ID_GRD_APR,
    g.CDM_APR,
    g.Nivel_Severidad_APR,
    CASE g.Nivel_Severidad_APR
        WHEN 1 THEN 'Menor'
        WHEN 2 THEN 'Moderado'
        WHEN 3 THEN 'Mayor'
        WHEN 4 THEN 'Extremo'
        ELSE 'No especificado'
    END AS Severidad_Descripcion,
    g.Riesgo_Mortalidad_APR,
    CASE g.Riesgo_Mortalidad_APR
        WHEN 1 THEN 'Menor'
        WHEN 2 THEN 'Moderado'
        WHEN 3 THEN 'Mayor'
        WHEN 4 THEN 'Extremo'
        ELSE 'No especificado'
    END AS Riesgo_Descripcion,
    g.Tipo_GRD_APR,
    
    -- Información financiera
    i.Coste_APR,
    i.Peso_Español_APR,
    
    -- Indicadores
    CASE i.Ingreso_en_UCI WHEN 'S' THEN 'Sí' ELSE 'No' END AS Ingreso_UCI,
    i.Diagnosticos_totales,
    i.Procedimientos_totales,
    CASE i.Tiene_procedimiento WHEN 'S' THEN 'Sí' ELSE 'No' END AS Tiene_Procedimiento,
    CASE i.Diagnostico_F WHEN 'S' THEN 'Sí' ELSE 'No' END AS Diagnostico_Mental,
    CASE i.Tiene_Comorbilidad WHEN 'S' THEN 'Sí' ELSE 'No' END AS Tiene_Comorbilidad,
    
    -- Diagnóstico principal (el primero en orden)
    (SELECT d.ID_Diagnostico 
     FROM Ingreso_Diagnosticos id 
     JOIN Diagnosticos d ON id.ID_Diagnostico = d.ID_Diagnostico
     WHERE id.ID_Ingreso = i.ID_Ingreso 
     ORDER BY id.Orden_Diagnostico 
     LIMIT 1) AS Diagnostico_Principal,
    
    (SELECT d.Categoria 
     FROM Ingreso_Diagnosticos id 
     JOIN Diagnosticos d ON id.ID_Diagnostico = d.ID_Diagnostico
     WHERE id.ID_Ingreso = i.ID_Ingreso 
     ORDER BY id.Orden_Diagnostico 
     LIMIT 1) AS Categoria_Diagnostico_Principal

FROM 
    Ingresos i
    INNER JOIN Pacientes p ON i.UUID_Paciente = p.UUID_Paciente
    LEFT JOIN GRD_APR g ON i.ID_GRD_APR = g.ID_GRD_APR
ORDER BY 
    i.Fecha_de_Ingreso DESC, i.ID_Ingreso;

-- =====================================================================
-- FIN DEL SCRIPT DE CREACIÓN
-- =====================================================================

-- Verificación del esquema creado
SELECT 'Esquema creado exitosamente para MySQL' AS Status;

-- Mostrar tablas creadas
SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN (
    'Diagnosticos', 'Procedimientos', 'GRD_APR',
    'Pacientes', 'Ingresos',
    'Ingreso_Diagnosticos', 'Ingreso_Procedimientos'
)
ORDER BY TABLE_NAME;

-- Mostrar vistas creadas
SELECT TABLE_NAME AS VIEW_NAME
FROM information_schema.VIEWS
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME;

