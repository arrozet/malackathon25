SET DEFINE OFF;

DROP TABLE "Ingreso_Procedimientos" CASCADE CONSTRAINTS;
DROP TABLE "Ingreso_Diagnosticos" CASCADE CONSTRAINTS;
DROP TABLE "Ingresos" CASCADE CONSTRAINTS;
DROP TABLE "Pacientes" CASCADE CONSTRAINTS;
DROP TABLE "GRD_APR" CASCADE CONSTRAINTS;
DROP TABLE "Procedimientos" CASCADE CONSTRAINTS;
DROP TABLE "Diagnosticos" CASCADE CONSTRAINTS;
DROP TABLE "Centros" CASCADE CONSTRAINTS;
DROP TABLE "Paises" CASCADE CONSTRAINTS;
DROP TABLE "Comunidades_Autonomas" CASCADE CONSTRAINTS;


CREATE TABLE comunidades_autonomas (
  id_comunidad_autonoma VARCHAR2(100 CHAR) PRIMARY KEY,
  nombre_comunidad VARCHAR2(150 CHAR) NOT NULL
);

CREATE TABLE paises (
  id_pais VARCHAR2(120 CHAR) PRIMARY KEY
);

CREATE TABLE centros (
  id_centro VARCHAR2(60 CHAR) PRIMARY KEY
);

CREATE TABLE diagnosticos (
  id_diagnostico VARCHAR2(20 CHAR) PRIMARY KEY,
  categoria VARCHAR2(200 CHAR)
);

CREATE TABLE procedimientos (
  id_procedimiento VARCHAR2(30 CHAR) PRIMARY KEY
);

CREATE TABLE grd_apr (
  id_grd_apr VARCHAR2(20 CHAR) PRIMARY KEY,
  cdm_apr VARCHAR2(10 CHAR),
  nivel_severidad_apr VARCHAR2(10 CHAR),
  riesgo_mortalidad_apr VARCHAR2(10 CHAR),
  tipo_grd_apr VARCHAR2(50 CHAR)
);

CREATE TABLE pacientes (
  uuid_paciente VARCHAR2(36 CHAR) PRIMARY KEY,
  cip_sns_recodificado VARCHAR2(40 CHAR),
  fecha_de_nacimiento DATE,
  sexo VARCHAR2(20 CHAR),
  grupo_etario VARCHAR2(20 CHAR),
  id_comunidad_autonoma VARCHAR2(100 CHAR),
  id_pais_nacimiento VARCHAR2(120 CHAR),
  id_pais_residencia VARCHAR2(120 CHAR),
  CONSTRAINT fk_pacientes_comunidades FOREIGN KEY (id_comunidad_autonoma)
    REFERENCES comunidades_autonomas (id_comunidad_autonoma),
  CONSTRAINT fk_pacientes_pais_nac FOREIGN KEY (id_pais_nacimiento)
    REFERENCES paises (id_pais),
  CONSTRAINT fk_pacientes_pais_res FOREIGN KEY (id_pais_residencia)
    REFERENCES paises (id_pais)
);


CREATE TABLE ingresos (
  id_ingreso NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  uuid_paciente VARCHAR2(36 CHAR) NOT NULL,
  id_centro VARCHAR2(60 CHAR),
  id_grd_apr VARCHAR2(20 CHAR),
  numero_de_registro_anual NUMBER(15,2),
  fecha_de_ingreso VARCHAR2(25 CHAR),
  fecha_de_fin_contacto VARCHAR2(25 CHAR),
  fecha_de_inicio_contacto VARCHAR2(25 CHAR),
  circunstancia_de_contacto NUMBER(10),
  tipo_alta NUMBER(10),
  servicio VARCHAR2(120 CHAR),
  regimen_financiacion NUMBER(10,2),
  procedencia NUMBER(10,2),
  continuidad_asistencial NUMBER(10,2),
  estancia_dias NUMBER(5),
  estancia_dias_acotada NUMBER(5),
  duracion_episodio_calculada NUMBER(5),
  edad NUMBER(3),
  edad_en_ingreso NUMBER(3),
  mes_de_ingreso VARCHAR2(25 CHAR),
  mes_nombre_ingreso VARCHAR2(20 CHAR),
  dia_semana_ingreso VARCHAR2(20 CHAR),
  coste_apr NUMBER(14,2),
  peso_español_apr NUMBER(10,4),
  ingreso_en_uci VARCHAR2(5 CHAR),
  diagnosticos_totales NUMBER(2),
  procedimientos_totales NUMBER(2),
  tiene_procedimiento VARCHAR2(5 CHAR),
  diagnostico_f VARCHAR2(5 CHAR),
  tiene_comorbilidad VARCHAR2(5 CHAR),
  CONSTRAINT fk_ingresos_pacientes FOREIGN KEY (uuid_paciente)
    REFERENCES pacientes (uuid_paciente),
  CONSTRAINT fk_ingresos_centros FOREIGN KEY (id_centro)
    REFERENCES centros (id_centro),
  CONSTRAINT fk_ingresos_grd FOREIGN KEY (id_grd_apr)
    REFERENCES grd_apr (id_grd_apr)
);


CREATE TABLE ingreso_diagnosticos (
  id_ingreso_diagnostico NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_ingreso NUMBER NOT NULL,
  id_diagnostico VARCHAR2(20 CHAR) NOT NULL,
  orden_diagnostico NUMBER(2) NOT NULL,
  poa CHAR(1 CHAR),
  CONSTRAINT fk_ingreso_diag_ingreso FOREIGN KEY (id_ingreso)
    REFERENCES ingresos (id_ingreso)
    ON DELETE CASCADE,
  CONSTRAINT fk_ingreso_diag_diag FOREIGN KEY (id_diagnostico)
    REFERENCES diagnosticos (id_diagnostico)
);

CREATE TABLE ingreso_procedimientos (
  id_ingreso_procedimiento NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  id_ingreso NUMBER NOT NULL,
  id_procedimiento VARCHAR2(30 CHAR) NOT NULL,
  orden_procedimiento NUMBER(2) NOT NULL,
  CONSTRAINT fk_ingreso_proc_ingreso FOREIGN KEY (id_ingreso)
    REFERENCES ingresos (id_ingreso)
    ON DELETE CASCADE,
  CONSTRAINT fk_ingreso_proc_proc FOREIGN KEY (id_procedimiento)
    REFERENCES procedimientos (id_procedimiento)
);


CREATE INDEX idx_ingresos_uuid ON ingresos (uuid_paciente);
CREATE INDEX idx_ingresos_centro ON ingresos (id_centro);
CREATE INDEX idx_ingreso_diag_ingreso ON ingreso_diagnosticos (id_ingreso);
CREATE INDEX idx_ingreso_diag_diag ON ingreso_diagnosticos (id_diagnostico);
CREATE INDEX idx_ingreso_proc_ingreso ON ingreso_procedimientos (id_ingreso);
CREATE INDEX idx_ingreso_proc_proc ON ingreso_procedimientos (id_procedimiento);
