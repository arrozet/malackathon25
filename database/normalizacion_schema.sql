-- normalizacion_schema.sql
-- Esquema relacional para Oracle Autonomous Database 23ai basado en la normalización
-- del dataset SaludMental_limpio_anon. El script crea tablas de dimensiones, hechos
-- y relaciones respetando los nombres originales de columnas proporcionados por el equipo EDA.

PROMPT Creando tablas de dimensiones...

CREATE TABLE "Comunidades_Autonomas" (
  "ID_Comunidad_Autonoma" VARCHAR2(100 CHAR) PRIMARY KEY,
  "Nombre_Comunidad" VARCHAR2(150 CHAR) NOT NULL
);

CREATE TABLE "Paises" (
  "ID_Pais" VARCHAR2(120 CHAR) PRIMARY KEY
);

CREATE TABLE "Centros" (
  "ID_Centro" VARCHAR2(60 CHAR) PRIMARY KEY
);

CREATE TABLE "Diagnosticos" (
  "ID_Diagnostico" VARCHAR2(20 CHAR) PRIMARY KEY,
  "Categoria" VARCHAR2(200 CHAR)
);

CREATE TABLE "Procedimientos" (
  "ID_Procedimiento" VARCHAR2(30 CHAR) PRIMARY KEY
);

CREATE TABLE "GRD_APR" (
  "ID_GRD_APR" VARCHAR2(20 CHAR) PRIMARY KEY,
  "CDM_APR" VARCHAR2(10 CHAR),
  "Nivel_Severidad_APR" VARCHAR2(10 CHAR),
  "Riesgo_Mortalidad_APR" VARCHAR2(10 CHAR),
  "Tipo_GRD_APR" VARCHAR2(50 CHAR)
);

CREATE TABLE "Pacientes" (
  "UUID_Paciente" VARCHAR2(36 CHAR) PRIMARY KEY,
  "CIP_SNS_Recodificado" VARCHAR2(40 CHAR),
  "Fecha_de_nacimiento" DATE,
  "Sexo" VARCHAR2(20 CHAR),
  "Grupo_Etario" VARCHAR2(20 CHAR),
  "ID_Comunidad_Autonoma" VARCHAR2(100 CHAR),
  "ID_Pais_Nacimiento" VARCHAR2(120 CHAR),
  "ID_Pais_Residencia" VARCHAR2(120 CHAR),
  CONSTRAINT "FK_Pacientes_Comunidades" FOREIGN KEY ("ID_Comunidad_Autonoma")
    REFERENCES "Comunidades_Autonomas" ("ID_Comunidad_Autonoma"),
  CONSTRAINT "FK_Pacientes_Pais_Nac" FOREIGN KEY ("ID_Pais_Nacimiento")
    REFERENCES "Paises" ("ID_Pais"),
  CONSTRAINT "FK_Pacientes_Pais_Res" FOREIGN KEY ("ID_Pais_Residencia")
    REFERENCES "Paises" ("ID_Pais")
);

PROMPT Creando tabla de hechos...

CREATE TABLE "Ingresos" (
  "ID_Ingreso" NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "UUID_Paciente" VARCHAR2(36 CHAR) NOT NULL,
  "ID_Centro" VARCHAR2(60 CHAR),
  "ID_GRD_APR" VARCHAR2(20 CHAR),
  "Numero_de_registro_anual" NUMBER(10),
  "Fecha_de_Ingreso" DATE,
  "Fecha_de_Fin_Contacto" DATE,
  "Fecha_de_Inicio_contacto" TIMESTAMP,
  "Circunstancia_de_Contacto" VARCHAR2(120 CHAR),
  "Tipo_Alta" VARCHAR2(120 CHAR),
  "Servicio" VARCHAR2(120 CHAR),
  "Regimen_Financiacion" VARCHAR2(120 CHAR),
  "Procedencia" VARCHAR2(120 CHAR),
  "Continuidad_Asistencial" VARCHAR2(120 CHAR),
  "Estancia_Dias" NUMBER(5),
  "Estancia_Dias_Acotada" NUMBER(5),
  "Duracion_Episodio_Calculada" NUMBER(5),
  "Edad" NUMBER(3),
  "Edad_en_Ingreso" NUMBER(3),
  "Mes_de_Ingreso" DATE,
  "Mes_Nombre_Ingreso" VARCHAR2(20 CHAR),
  "Dia_Semana_Ingreso" VARCHAR2(20 CHAR),
  "Coste_APR" NUMBER(14,2),
  "Peso_Español_APR" NUMBER(10,4),
  "Ingreso_en_UCI" CHAR(1 CHAR),
  "Diagnosticos_totales" NUMBER(2),
  "Procedimientos_totales" NUMBER(2),
  "Tiene_procedimiento" CHAR(1 CHAR),
  "Diagnostico_F" CHAR(1 CHAR),
  "Tiene_Comorbilidad" CHAR(1 CHAR),
  CONSTRAINT "FK_Ingresos_Pacientes" FOREIGN KEY ("UUID_Paciente")
    REFERENCES "Pacientes" ("UUID_Paciente"),
  CONSTRAINT "FK_Ingresos_Centros" FOREIGN KEY ("ID_Centro")
    REFERENCES "Centros" ("ID_Centro"),
  CONSTRAINT "FK_Ingresos_GRD" FOREIGN KEY ("ID_GRD_APR")
    REFERENCES "GRD_APR" ("ID_GRD_APR")
);

PROMPT Creando tablas de relación...

CREATE TABLE "Ingreso_Diagnosticos" (
  "ID_Ingreso_Diagnostico" NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "ID_Ingreso" NUMBER NOT NULL,
  "ID_Diagnostico" VARCHAR2(20 CHAR) NOT NULL,
  "Orden_Diagnostico" NUMBER(2) NOT NULL,
  "POA" CHAR(1 CHAR),
  CONSTRAINT "FK_Ingreso_Diag_Ingreso" FOREIGN KEY ("ID_Ingreso")
    REFERENCES "Ingresos" ("ID_Ingreso")
    ON DELETE CASCADE,
  CONSTRAINT "FK_Ingreso_Diag_Diag" FOREIGN KEY ("ID_Diagnostico")
    REFERENCES "Diagnosticos" ("ID_Diagnostico")
);

CREATE TABLE "Ingreso_Procedimientos" (
  "ID_Ingreso_Procedimiento" NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "ID_Ingreso" NUMBER NOT NULL,
  "ID_Procedimiento" VARCHAR2(30 CHAR) NOT NULL,
  "Orden_Procedimiento" NUMBER(2) NOT NULL,
  CONSTRAINT "FK_Ingreso_Proc_Ingreso" FOREIGN KEY ("ID_Ingreso")
    REFERENCES "Ingresos" ("ID_Ingreso")
    ON DELETE CASCADE,
  CONSTRAINT "FK_Ingreso_Proc_Proc" FOREIGN KEY ("ID_Procedimiento")
    REFERENCES "Procedimientos" ("ID_Procedimiento")
);

PROMPT Creando índices auxiliares...

CREATE INDEX "IDX_Ingresos_UUID" ON "Ingresos" ("UUID_Paciente");
CREATE INDEX "IDX_Ingresos_Centro" ON "Ingresos" ("ID_Centro");
CREATE INDEX "IDX_Ingreso_Diag_Ingreso" ON "Ingreso_Diagnosticos" ("ID_Ingreso");
CREATE INDEX "IDX_Ingreso_Diag_Diag" ON "Ingreso_Diagnosticos" ("ID_Diagnostico");
CREATE INDEX "IDX_Ingreso_Proc_Ingreso" ON "Ingreso_Procedimientos" ("ID_Ingreso");
CREATE INDEX "IDX_Ingreso_Proc_Proc" ON "Ingreso_Procedimientos" ("ID_Procedimiento");

PROMPT Esquema normalizado creado correctamente.

