-- =====================================================================
-- Archivo de Control SQL*Loader - II Malackathon 2025
-- Archivo: load_data.ctl
-- Descripción: Configuración para cargar SaludMental_limpio.csv
--              en la tabla staging mediante SQL*Loader
-- =====================================================================
-- Uso:
--   sqlldr userid=admin/<password>@<connection_string> \
--          control=load_data.ctl \
--          log=load_data.log \
--          bad=load_data.bad \
--          discard=load_data.dis
-- =====================================================================

LOAD DATA
CHARACTERSET UTF8
INFILE 'SaludMental_limpio.csv'
BADFILE 'load_data.bad'
DISCARDFILE 'load_data.dis'
APPEND
INTO TABLE staging_salud_mental
FIELDS TERMINATED BY "," OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    numero_registro             CHAR(100),
    categoria                   CHAR(100),
    nombre                      CHAR(200),
    edad_en_ingreso             INTEGER EXTERNAL,
    sexo                        INTEGER EXTERNAL,
    pais_nacimiento             CHAR(20),
    comunidad_autonoma          CHAR(100),
    centro_recodificado         CHAR(100),
    fecha_ingreso               CHAR(50),
    fecha_fin_contacto          CHAR(50),
    mes_ingreso                 CHAR(50),
    diagnostico_principal       CHAR(50),
    diagnostico_2               CHAR(50),
    diagnostico_3               CHAR(50),
    procedimiento_1             CHAR(50),
    procedimiento_2             CHAR(50),
    procedimiento_3             CHAR(50),
    procedimiento_4             CHAR(50),
    procedimiento_5             CHAR(50),
    procedimiento_6             CHAR(50),
    procedimiento_7             CHAR(50),
    procedimiento_8             CHAR(50),
    procedimiento_9             CHAR(50),
    procedimiento_10            CHAR(50),
    procedimiento_11            CHAR(50),
    tipo_alta                   INTEGER EXTERNAL,
    circunstancia_contacto      INTEGER EXTERNAL,
    estancia_dias               DECIMAL EXTERNAL,
    grd_apr                     DECIMAL EXTERNAL,
    cdm_apr                     DECIMAL EXTERNAL,
    nivel_severidad_apr         INTEGER EXTERNAL,
    riesgo_mortalidad_apr       INTEGER EXTERNAL,
    peso_espanol_apr            DECIMAL EXTERNAL,
    coste_apr                   DECIMAL EXTERNAL,
    diagnosticos_totales        INTEGER EXTERNAL,
    procedimientos_totales      INTEGER EXTERNAL,
    tiene_procedimiento         CHAR(10),
    diagnostico_f               CHAR(10),
    tiene_comorbilidad          CHAR(10),
    duracion_episodio_calculada INTEGER EXTERNAL,
    grupo_etario                CHAR(20),
    dia_semana_ingreso          CHAR(20),
    mes_nombre_ingreso          CHAR(20),
    estancia_dias_acotada       DECIMAL EXTERNAL
)

