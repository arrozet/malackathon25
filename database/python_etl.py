#!/usr/bin/env python3
"""
Script ETL Python para cargar datos en Oracle Autonomous Database 23ai
II Malackathon 2025 - Proyecto Brain

Este script alternativo permite cargar los datos directamente desde Python
sin necesidad de SQL*Loader. Útil para desarrollo y testing.

Uso:
    python python_etl.py --excel ../data/SaludMental_limpio.xlsx
    python python_etl.py --csv ../data/SaludMental_limpio.csv
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import pandas as pd
    import oracledb
except ImportError as e:
    logger.error(f"Dependencias faltantes: {e}")
    logger.error("Instalar con: pip install pandas openpyxl oracledb")
    sys.exit(1)


class OracleETL:
    """
    Clase para gestionar la carga ETL de datos de salud mental a Oracle.
    
    Attributes:
        connection: Conexión activa a Oracle Database
        cursor: Cursor para ejecutar queries
        config: Configuración de conexión
    """
    
    def __init__(self, user: str, password: str, dsn: str, wallet_location: Optional[str] = None):
        """
        Inicializa la conexión a Oracle Autonomous Database.
        
        Args:
            user: Usuario de Oracle
            password: Contraseña del usuario
            dsn: Data Source Name (connection string)
            wallet_location: Ruta al directorio del Oracle Wallet (opcional)
        
        Raises:
            oracledb.DatabaseError: Si no se puede establecer la conexión
        """
        self.config = {
            'user': user,
            'password': password,
            'dsn': dsn
        }
        
        if wallet_location:
            self.config['config_dir'] = wallet_location
            self.config['wallet_location'] = wallet_location
            
        try:
            logger.info("Estableciendo conexión con Oracle Autonomous Database...")
            self.connection = oracledb.connect(**self.config)
            self.cursor = self.connection.cursor()
            logger.info("✓ Conexión establecida exitosamente")
        except oracledb.DatabaseError as e:
            logger.error(f"✗ Error al conectar con Oracle: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión ejecutando una query simple.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            self.cursor.execute("SELECT 'Connection OK' FROM dual")
            result = self.cursor.fetchone()
            logger.info(f"Test de conexión: {result[0]}")
            return True
        except oracledb.DatabaseError as e:
            logger.error(f"Test de conexión falló: {e}")
            return False
    
    def create_staging_table(self):
        """
        Crea la tabla staging_salud_mental si no existe.
        """
        logger.info("Verificando tabla staging...")
        
        drop_sql = "DROP TABLE staging_salud_mental PURGE"
        try:
            self.cursor.execute(drop_sql)
            logger.info("Tabla staging existente eliminada")
        except oracledb.DatabaseError:
            pass  # La tabla no existía
        
        create_sql = """
        CREATE TABLE staging_salud_mental (
            numero_registro VARCHAR2(100),
            categoria VARCHAR2(100),
            nombre VARCHAR2(200),
            edad_en_ingreso NUMBER,
            sexo NUMBER,
            pais_nacimiento VARCHAR2(20),
            comunidad_autonoma VARCHAR2(100),
            centro_recodificado VARCHAR2(100),
            fecha_ingreso VARCHAR2(50),
            fecha_fin_contacto VARCHAR2(50),
            mes_ingreso VARCHAR2(50),
            diagnostico_principal VARCHAR2(50),
            diagnostico_2 VARCHAR2(50),
            diagnostico_3 VARCHAR2(50),
            procedimiento_1 VARCHAR2(50),
            procedimiento_2 VARCHAR2(50),
            procedimiento_3 VARCHAR2(50),
            procedimiento_4 VARCHAR2(50),
            procedimiento_5 VARCHAR2(50),
            procedimiento_6 VARCHAR2(50),
            procedimiento_7 VARCHAR2(50),
            procedimiento_8 VARCHAR2(50),
            procedimiento_9 VARCHAR2(50),
            procedimiento_10 VARCHAR2(50),
            procedimiento_11 VARCHAR2(50),
            tipo_alta NUMBER,
            circunstancia_contacto NUMBER,
            estancia_dias NUMBER,
            grd_apr NUMBER,
            cdm_apr NUMBER,
            nivel_severidad_apr NUMBER,
            riesgo_mortalidad_apr NUMBER,
            peso_espanol_apr NUMBER,
            coste_apr NUMBER,
            diagnosticos_totales NUMBER,
            procedimientos_totales NUMBER,
            tiene_procedimiento VARCHAR2(10),
            diagnostico_f VARCHAR2(10),
            tiene_comorbilidad VARCHAR2(10),
            duracion_episodio_calculada NUMBER,
            grupo_etario VARCHAR2(20),
            dia_semana_ingreso VARCHAR2(20),
            mes_nombre_ingreso VARCHAR2(20),
            estancia_dias_acotada NUMBER
        )
        """
        
        try:
            self.cursor.execute(create_sql)
            self.connection.commit()
            logger.info("✓ Tabla staging creada exitosamente")
        except oracledb.DatabaseError as e:
            logger.error(f"✗ Error al crear tabla staging: {e}")
            raise
    
    def load_data_from_file(self, file_path: str, batch_size: int = 1000):
        """
        Carga datos desde un archivo Excel o CSV a la tabla staging.
        
        Args:
            file_path: Ruta al archivo de datos
            batch_size: Tamaño del lote para inserción (default: 1000)
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato del archivo no es soportado
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        logger.info(f"Leyendo datos desde {file_path}...")
        
        # Leer archivo según extensión
        if file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")
        
        logger.info(f"✓ Datos cargados: {len(df)} registros, {len(df.columns)} columnas")
        
        # Normalizar nombres de columnas (quitar espacios, convertir a minúsculas con guiones bajos)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Mapear nombres de columnas del DataFrame a nombres de columnas de la tabla
        column_mapping = self._get_column_mapping(df.columns)
        df = df.rename(columns=column_mapping)
        
        # Reemplazar NaN con None para Oracle
        df = df.where(pd.notnull(df), None)
        
        # Preparar statement de inserción
        columns = list(df.columns)
        placeholders = ', '.join([f':{i+1}' for i in range(len(columns))])
        insert_sql = f"""
            INSERT INTO staging_salud_mental ({', '.join(columns)})
            VALUES ({placeholders})
        """
        
        logger.info("Insertando datos en staging...")
        
        # Insertar en lotes
        total_rows = len(df)
        inserted = 0
        
        try:
            for start_idx in range(0, total_rows, batch_size):
                end_idx = min(start_idx + batch_size, total_rows)
                batch = df.iloc[start_idx:end_idx]
                
                # Convertir batch a lista de tuplas
                data = [tuple(row) for row in batch.values]
                
                self.cursor.executemany(insert_sql, data)
                self.connection.commit()
                
                inserted += len(batch)
                logger.info(f"  Progreso: {inserted}/{total_rows} registros ({100*inserted/total_rows:.1f}%)")
            
            logger.info(f"✓ Carga completada: {inserted} registros insertados")
            
        except oracledb.DatabaseError as e:
            logger.error(f"✗ Error al insertar datos: {e}")
            self.connection.rollback()
            raise
    
    def _get_column_mapping(self, df_columns: List[str]) -> Dict[str, str]:
        """
        Mapea nombres de columnas del DataFrame a nombres de columnas de Oracle.
        
        Args:
            df_columns: Lista de nombres de columnas del DataFrame
            
        Returns:
            Diccionario de mapeo {nombre_df: nombre_oracle}
        """
        # Mapeo explícito para casos especiales
        mapping = {
            'edad_en_ingreso': 'edad_en_ingreso',
            'edad': 'edad_en_ingreso',
            'número_de_registro_anual': 'numero_registro',
            'comunidad_autónoma': 'comunidad_autonoma',
            'país_nacimiento': 'pais_nacimiento',
            'diagnóstico_principal': 'diagnostico_principal',
            'categoría': 'categoria'
        }
        
        # Para columnas que ya están en el formato correcto
        for col in df_columns:
            if col not in mapping:
                mapping[col] = col
        
        return mapping
    
    def execute_etl_script(self, sql_file: str):
        """
        Ejecuta un script SQL completo (ej: load_data.sql).
        
        Args:
            sql_file: Ruta al archivo SQL
        
        Note:
            Este método ejecuta el script línea por línea.
            Para scripts complejos con PL/SQL, usar SQL*Plus es preferible.
        """
        logger.info(f"Ejecutando script SQL: {sql_file}")
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Dividir por punto y coma (simplificado, no maneja PL/SQL blocks)
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            # Saltar comentarios y líneas vacías
            if statement.startswith('--') or not statement:
                continue
            
            try:
                logger.info(f"Ejecutando statement {i}/{len(statements)}...")
                self.cursor.execute(statement)
                self.connection.commit()
            except oracledb.DatabaseError as e:
                logger.warning(f"Statement {i} falló (puede ser esperado): {e}")
                continue
        
        logger.info("✓ Script SQL ejecutado")
    
    def verify_data_load(self):
        """
        Verifica que los datos se hayan cargado correctamente.
        
        Returns:
            Diccionario con estadísticas de carga
        """
        logger.info("Verificando carga de datos...")
        
        tables = [
            'staging_salud_mental',
            'comunidades_autonomas',
            'paises',
            'centros_hospitalarios',
            'diagnosticos_cie',
            'procedimientos',
            'pacientes',
            'episodios',
            'episodios_diagnosticos',
            'episodios_procedimientos'
        ]
        
        stats = {}
        
        for table in tables:
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                stats[table] = count
                logger.info(f"  {table}: {count:,} registros")
            except oracledb.DatabaseError as e:
                stats[table] = f"Error: {e}"
                logger.warning(f"  {table}: No accesible o no existe")
        
        return stats
    
    def close(self):
        """
        Cierra la conexión a la base de datos.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("Conexión cerrada")


def main():
    """
    Función principal del script ETL.
    """
    parser = argparse.ArgumentParser(
        description='ETL para cargar datos de salud mental en Oracle Autonomous Database'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Ruta al archivo de datos (Excel o CSV)'
    )
    parser.add_argument(
        '--user',
        type=str,
        default=os.getenv('DB_USER', 'admin'),
        help='Usuario de Oracle (default: admin)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default=os.getenv('DB_PASSWORD'),
        help='Contraseña de Oracle (o usar variable DB_PASSWORD)'
    )
    parser.add_argument(
        '--dsn',
        type=str,
        default=os.getenv('DB_DSN'),
        help='Connection string de Oracle (o usar variable DB_DSN)'
    )
    parser.add_argument(
        '--wallet',
        type=str,
        default='../app/oracle_wallet',
        help='Ruta al Oracle Wallet (default: ../app/oracle_wallet)'
    )
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Solo probar conexión sin cargar datos'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verificar datos cargados'
    )
    
    args = parser.parse_args()
    
    # Validar credenciales
    if not args.password:
        logger.error("Contraseña no proporcionada. Usar --password o variable DB_PASSWORD")
        sys.exit(1)
    
    if not args.dsn:
        logger.error("DSN no proporcionado. Usar --dsn o variable DB_DSN")
        sys.exit(1)
    
    # Inicializar ETL
    try:
        etl = OracleETL(
            user=args.user,
            password=args.password,
            dsn=args.dsn,
            wallet_location=args.wallet
        )
        
        # Test de conexión
        if not etl.test_connection():
            logger.error("Test de conexión falló. Abortando.")
            sys.exit(1)
        
        if args.test_only:
            logger.info("✓ Test completado exitosamente")
            return
        
        # Verificar datos existentes
        if args.verify:
            stats = etl.verify_data_load()
            logger.info("✓ Verificación completada")
            return
        
        # Cargar datos
        if args.file:
            etl.create_staging_table()
            etl.load_data_from_file(args.file)
            
            logger.info("\n" + "="*60)
            logger.info("SIGUIENTE PASO:")
            logger.info("Ejecutar el script load_data.sql para completar el ETL:")
            logger.info("  sqlplus admin/<password>@<connection> @load_data.sql")
            logger.info("="*60)
        else:
            logger.warning("No se especificó archivo de datos. Usar --file")
        
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)
    finally:
        if 'etl' in locals():
            etl.close()


if __name__ == '__main__':
    main()

