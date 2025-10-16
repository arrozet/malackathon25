-- #####################################################################
-- ## Script para la creación de la Base de Datos de Salud Mental      ##
-- ## Diseñado para Oracle Database (Versión simplificada)            ##
-- ## Versión: 2.0                                                    ##
-- #####################################################################

-- =====================================================================
-- 1. CREACIÓN DE TABLAS DE DIMENSIONES RESTANTES
-- =====================================================================

-- Tabla para Diagnósticos
CREATE TABLE Diagnosticos (
    ID_Diagnostico          VARCHAR2(20) NOT NULL, -- Ej: 'F60.3'
    Categoria               VARCHAR2(255),
    CONSTRAINT pk_diagnosticos PRIMARY KEY (ID_Diagnostico)
);

-- Tabla para Procedimientos
CREATE TABLE Procedimientos (
    ID_Procedimiento        VARCHAR2(20) NOT NULL,
    CONSTRAINT pk_procedimientos PRIMARY KEY (ID_Procedimiento)
);

-- Tabla para GRD (Grupo Relacionado por el Diagnóstico)
CREATE TABLE GRD_APR (
    ID_GRD_APR              VARCHAR2(10) NOT NULL,
    CDM_APR                 NUMBER(5),
    Nivel_Severidad_APR     NUMBER(2),
    Riesgo_Mortalidad_APR   NUMBER(2),
    Tipo_GRD_APR            VARCHAR2(5),
    CONSTRAINT pk_grd_apr   PRIMARY KEY (ID_GRD_APR)
);


-- =====================================================================
-- 2. CREACIÓN DE TABLAS PRINCIPALES (MODIFICADAS)
-- =====================================================================

-- Tabla para Pacientes
-- Se han reemplazado los FKs por campos de texto directos
CREATE TABLE Pacientes (
    UUID_Paciente           VARCHAR2(36) NOT NULL,
    CIP_SNS_Recodificado    VARCHAR2(50),
    Fecha_de_nacimiento     DATE,
    Sexo                    NUMBER(1),
    Grupo_Etario            VARCHAR2(20),
    Comunidad_Autonoma      VARCHAR2(100), -- Valor directo en lugar de FK
    Pais_Nacimiento         VARCHAR2(100), -- Valor directo en lugar de FK
    Pais_Residencia         VARCHAR2(100), -- Valor directo en lugar de FK
    CONSTRAINT pk_pacientes PRIMARY KEY (UUID_Paciente)
);

-- Tabla para Ingresos (Tabla de Hechos)
-- Se ha reemplazado el FK a Centros por un campo numérico directo
CREATE TABLE Ingresos (
    ID_Ingreso              NUMBER(10) NOT NULL,
    UUID_Paciente           VARCHAR2(36) NOT NULL,
    Centro_Recodificado     NUMBER(10) NOT NULL, -- Valor directo en lugar de FK
    ID_GRD_APR              VARCHAR2(10),
    Numero_de_registro_anual VARCHAR2(50),
    Fecha_de_Ingreso        DATE,
    Fecha_de_Fin_Contacto   DATE,
    Fecha_de_Inicio_contacto DATE,
    Circunstancia_de_Contacto NUMBER(2),
    Tipo_Alta               NUMBER(2),
    Servicio                VARCHAR2(10),
    Regimen_Financiacion    NUMBER(2),
    Procedencia             NUMBER(2),
    Continuidad_Asistencial NUMBER(2),
    Estancia_Dias           NUMBER(5),
    Estancia_Dias_Acotada   NUMBER(5),
    Duracion_Episodio_Calculada NUMBER(5),
    Edad                    NUMBER(3),
    Edad_en_Ingreso         NUMBER(3),
    Mes_de_Ingreso          NUMBER(2),
    Mes_Nombre_Ingreso      VARCHAR2(20),
    Dia_Semana_Ingreso      VARCHAR2(20),
    Coste_APR               NUMBER(12, 2),
    Peso_Español_APR        NUMBER(10, 6),
    Ingreso_en_UCI          CHAR(1), -- 'S' o 'N'
    Diagnosticos_totales    NUMBER(3),
    Procedimientos_totales  NUMBER(3),
    Tiene_procedimiento     CHAR(1),
    Diagnostico_F           CHAR(1),
    Tiene_Comorbilidad      CHAR(1),
    CONSTRAINT pk_ingresos PRIMARY KEY (ID_Ingreso),
    CONSTRAINT fk_ingresos_paciente FOREIGN KEY (UUID_Paciente) REFERENCES Pacientes(UUID_Paciente),
    CONSTRAINT fk_ingresos_grd FOREIGN KEY (ID_GRD_APR) REFERENCES GRD_APR(ID_GRD_APR)
);


-- =====================================================================
-- 3. CREACIÓN DE TABLAS DE RELACIÓN (SIN CAMBIOS)
-- =====================================================================

-- Tabla que relaciona Ingresos con Diagnósticos
CREATE TABLE Ingreso_Diagnosticos (
    ID_Ingreso_Diagnostico  NUMBER(10) NOT NULL,
    ID_Ingreso              NUMBER(10) NOT NULL,
    ID_Diagnostico          VARCHAR2(20) NOT NULL,
    Orden_Diagnostico       NUMBER(2) NOT NULL,
    POA                     CHAR(1),
    CONSTRAINT pk_ingreso_diagnosticos PRIMARY KEY (ID_Ingreso_Diagnostico),
    CONSTRAINT fk_ingdiag_ingreso FOREIGN KEY (ID_Ingreso) REFERENCES Ingresos(ID_Ingreso),
    CONSTRAINT fk_ingdiag_diagnostico FOREIGN KEY (ID_Diagnostico) REFERENCES Diagnosticos(ID_Diagnostico)
);

-- Tabla que relaciona Ingresos con Procedimientos
CREATE TABLE Ingreso_Procedimientos (
    ID_Ingreso_Procedimiento NUMBER(10) NOT NULL,
    ID_Ingreso               NUMBER(10) NOT NULL,
    ID_Procedimiento         VARCHAR2(20) NOT NULL,
    Orden_Procedimiento      NUMBER(2) NOT NULL,
    CONSTRAINT pk_ingreso_procedimientos PRIMARY KEY (ID_Ingreso_Procedimiento),
    CONSTRAINT fk_ingproc_ingreso FOREIGN KEY (ID_Ingreso) REFERENCES Ingresos(ID_Ingreso),
    CONSTRAINT fk_ingproc_procedimiento FOREIGN KEY (ID_Procedimiento) REFERENCES Procedimientos(ID_Procedimiento)
);


-- =====================================================================
-- 4. CREACIÓN DE SECUENCIAS Y TRIGGERS PARA IDs AUTOMÁTICOS (SIN CAMBIOS)
-- =====================================================================

-- Para la tabla Ingresos
CREATE SEQUENCE seq_ingresos START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_ingresos_pk
BEFORE INSERT ON Ingresos
FOR EACH ROW
BEGIN
    SELECT seq_ingresos.NEXTVAL
    INTO :new.ID_Ingreso
    FROM dual;
END;
/

-- Para la tabla Ingreso_Diagnosticos
CREATE SEQUENCE seq_ingreso_diagnosticos START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_ingreso_diag_pk
BEFORE INSERT ON Ingreso_Diagnosticos
FOR EACH ROW
BEGIN
    SELECT seq_ingreso_diagnosticos.NEXTVAL
    INTO :new.ID_Ingreso_Diagnostico
    FROM dual;
END;
/

-- Para la tabla Ingreso_Procedimientos
CREATE SEQUENCE seq_ingreso_procedimientos START WITH 1 INCREMENT BY 1;
CREATE OR REPLACE TRIGGER trg_ingreso_proc_pk
BEFORE INSERT ON Ingreso_Procedimientos
FOR EACH ROW
BEGIN
    SELECT seq_ingreso_procedimientos.NEXTVAL
    INTO :new.ID_Ingreso_Procedimiento
    FROM dual;
END;
/

-- Finalización del script
COMMIT;