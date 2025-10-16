-- insert_normalizacion.sql
-- Script de inserción para poblar el esquema normalizado desde archivos CSV
-- exportados por `data/R/normalizacion.qmd`. Cada bloque usa SQL*Loader externo
-- con soporte de Oracle Autonomous Database 23ai a través de `DBMS_CLOUD.COPY_DATA`.
--
-- Parámetros de ejecución recomendados:
--   1) Subir los CSV al bucket OCI Object Storage o directorio externo vinculado
--      a la credencial `DMK_CRED`.
--   2) Ajustar la variable `PREFIX_URI` al prefijo del bucket (por ejemplo,
--      'https://objectstorage.eu-frankfurt-1.oraclecloud.com/n/.../normalizacion/').

DEFINE PREFIX_URI = 'https://ruta-almacenamiento/normalizacion/';


BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Comunidades_Autonomas',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Comunidades_Autonomas.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Paises',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Paises.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Centros',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Centros.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'GRD_APR',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.GRD_APR.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Diagnosticos',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Diagnosticos.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Procedimientos',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Procedimientos.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Pacientes',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Pacientes.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/


BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Ingresos',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Ingresos.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1,
      'dateformat' VALUE 'YYYY-MM-DD',
      'timestampformat' VALUE 'YYYY-MM-DD"T"HH24:MI:SS'
    )
  );
END;
/


BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Ingreso_Diagnosticos',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Ingreso_Diagnosticos.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/

BEGIN
  DBMS_CLOUD.COPY_DATA(
    table_name      => 'Ingreso_Procedimientos',
    credential_name => 'DMK_CRED',
    file_uri_list   => '&PREFIX_URI.Ingreso_Procedimientos.csv',
    format          => json_object(
      'type'      VALUE 'csv',
      'delimiter' VALUE ',',
      'skipheaders' VALUE 1
    )
  );
END;
/


