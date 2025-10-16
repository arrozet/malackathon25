"""
Database connection module for Oracle Autonomous Database.

This module manages the connection pool to Oracle Cloud Autonomous Database
using the python-oracledb library in thin mode with wallet authentication.
"""

import oracledb
from typing import Optional
from contextlib import contextmanager
import logging

from app.back.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool: Optional[oracledb.ConnectionPool] = None


def initialize_connection_pool(
    min_connections: int = 5,
    max_connections: int = 50,
    increment: int = 5,
    timeout: int = 30,
    getmode: int = oracledb.POOL_GETMODE_TIMEDWAIT
) -> None:
    """
    Initializes the Oracle database connection pool.
    
    This function creates a connection pool that will be reused across the application.
    It uses the wallet configuration for secure connection to Oracle Cloud.
    
    Args:
        min_connections (int): Minimum number of connections in the pool. Default is 5.
        max_connections (int): Maximum number of connections in the pool. Default is 50.
        increment (int): Number of connections to create when pool needs to grow. Default is 5.
        timeout (int): Timeout in seconds when waiting for a connection. Default is 30.
        getmode (int): Mode for acquiring connections from pool. Default is TIMEDWAIT.
    
    Raises:
        oracledb.Error: If connection pool creation fails.
        ValueError: If configuration is invalid.
    
    Side Effects:
        Creates a global connection pool stored in _connection_pool.
    
    Notes:
        Oracle ADB supports 25-100+ concurrent connections depending on tier.
        Pool configured for multi-agent AI workloads with concurrent frontend requests.
    """
    global _connection_pool
    
    try:
        # Validate configuration before attempting connection
        config.validate()
    except ValueError as config_error:
        logger.warning(
            "Skipping Oracle connection pool initialization: %s",
            config_error,
        )
        return

    try:
        logger.info("Initializing Oracle connection pool...")
        logger.info(f"Connecting to DSN: {config.ORACLE_DSN}")
        logger.info(f"Using wallet from: {config.TNS_ADMIN}")
        
        # Create connection pool using thin mode with wallet
        _connection_pool = oracledb.create_pool(
            user=config.ORACLE_USER,
            password=config.ORACLE_PASSWORD,
            dsn=config.ORACLE_DSN,
            min=min_connections,
            max=max_connections,
            increment=increment,
            getmode=getmode,  # TIMEDWAIT: wait for connection with timeout
            timeout=timeout,  # Timeout in seconds when pool is exhausted
            config_dir=config.TNS_ADMIN,  # Path to wallet directory
            wallet_location=config.TNS_ADMIN,  # Same as config_dir for wallet
            wallet_password=config.ORACLE_WALLET_PASSWORD,  # Wallet encryption password
        )
        
        logger.info(
            f"Connection pool created successfully: "
            f"min={min_connections}, max={max_connections}, increment={increment}, "
            f"timeout={timeout}s, getmode={'TIMEDWAIT' if getmode == oracledb.POOL_GETMODE_TIMEDWAIT else 'NOWAIT'}"
        )
        
        # Test the connection (non-blocking - logs warnings but doesn't raise)
        try:
            test_connection()
        except Exception as test_error:
            logger.warning(f"Initial connection test failed, but pool is ready: {str(test_error)}")
            logger.warning("Service will continue startup. Connection issues may resolve themselves.")
        
    except oracledb.Error as e:
        error_obj, = e.args
        logger.error(f"Oracle connection error: {error_obj.message}")
        logger.error(f"Error code: {error_obj.code}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing connection pool: {str(e)}")
        raise


def close_connection_pool() -> None:
    """
    Closes the Oracle database connection pool.
    
    This function should be called during application shutdown to properly
    release all database connections.
    
    Side Effects:
        Closes and removes the global connection pool.
    """
    global _connection_pool
    
    if _connection_pool:
        try:
            logger.info("Closing Oracle connection pool...")
            _connection_pool.close()
            _connection_pool = None
            logger.info("Connection pool closed successfully")
        except oracledb.Error as e:
            logger.error(f"Error closing connection pool: {str(e)}")
            raise


@contextmanager
def get_connection():
    """
    Context manager for obtaining a database connection from the pool.
    
    This function provides a safe way to acquire and release connections,
    ensuring proper resource management even if errors occur.
    
    Yields:
        oracledb.Connection: A database connection from the pool.
    
    Raises:
        RuntimeError: If connection pool has not been initialized.
        oracledb.Error: If connection acquisition fails.
    
    Example:
        ```python
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
        ```
    """
    if not _connection_pool:
        raise RuntimeError(
            "Connection pool not initialized. Call initialize_connection_pool() first."
        )
    
    connection = None
    try:
        # Acquire connection from pool (will wait up to timeout seconds if pool exhausted)
        connection = _connection_pool.acquire()
        logger.debug(f"Connection acquired from pool (busy: {_connection_pool.busy}, open: {_connection_pool.opened})")
        yield connection
    except oracledb.Error as e:
        pool_stats = f"(busy: {_connection_pool.busy}/{_connection_pool.max})" if _connection_pool else ""
        logger.error(f"Error acquiring connection {pool_stats}: {str(e)}")
        raise
    finally:
        # Always release connection back to pool
        if connection:
            try:
                connection.close()  # Returns connection to pool
                logger.debug("Connection released to pool")
            except oracledb.Error as e:
                logger.error(f"Error releasing connection: {str(e)}")


def test_connection() -> bool:
    """
    Tests the database connection by executing a simple query.
    
    Returns:
        bool: True if connection test succeeds, False otherwise.
    
    Raises:
        RuntimeError: If connection pool has not been initialized.
        oracledb.Error: If the test query fails.
    """
    if not _connection_pool:
        logger.info("Connection pool not initialised; returning degraded status.")
        return False

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 'Connection successful' FROM DUAL")
            result = cursor.fetchone()
            logger.info(f"Connection test result: {result[0]}")
            cursor.close()
            return True
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return False


def execute_query(query: str, params: Optional[dict] = None) -> list:
    """
    Executes a SELECT query and returns all results.
    
    Args:
        query (str): The SQL SELECT query to execute.
        params (dict, optional): Parameters for parameterized queries. Default is None.
    
    Returns:
        list: List of tuples containing query results.
    
    Raises:
        RuntimeError: If connection pool has not been initialized.
        oracledb.Error: If query execution fails.
    
    Example:
        ```python
        results = execute_query(
            "SELECT * FROM users WHERE user_id = :id",
            {"id": 123}
        )
        ```
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
    except oracledb.Error as e:
        logger.error(f"Error executing query: {str(e)}")
        logger.error(f"Query: {query}")
        raise


def execute_dml(query: str, params: Optional[dict] = None, commit: bool = True) -> int:
    """
    Executes a DML statement (INSERT, UPDATE, DELETE) and optionally commits.
    
    Args:
        query (str): The SQL DML statement to execute.
        params (dict, optional): Parameters for parameterized queries. Default is None.
        commit (bool): Whether to commit the transaction. Default is True.
    
    Returns:
        int: Number of rows affected by the DML statement.
    
    Raises:
        RuntimeError: If connection pool has not been initialized.
        oracledb.Error: If DML execution fails.
    
    Side Effects:
        Modifies database if commit=True.
    
    Example:
        ```python
        rows_affected = execute_dml(
            "UPDATE users SET status = :status WHERE user_id = :id",
            {"status": "active", "id": 123}
        )
        ```
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            rows_affected = cursor.rowcount
            if commit:
                conn.commit()
            cursor.close()
            return rows_affected
    except oracledb.Error as e:
        logger.error(f"Error executing DML: {str(e)}")
        logger.error(f"Query: {query}")
        raise


def get_pool_stats() -> dict:
    """
    Gets real-time statistics about the connection pool.
    
    Returns:
        dict: Pool statistics including busy/opened/max connections and utilization percentage.
    """
    if not _connection_pool:
        return {
            "status": "not_initialized",
            "busy": 0,
            "opened": 0,
            "max": 0,
            "min": 0,
            "utilization_percent": 0
        }
    
    busy = _connection_pool.busy
    opened = _connection_pool.opened
    max_conn = _connection_pool.max
    min_conn = _connection_pool.min
    
    utilization = (busy / max_conn * 100) if max_conn > 0 else 0
    
    return {
        "status": "active",
        "busy": busy,
        "opened": opened,
        "max": max_conn,
        "min": min_conn,
        "utilization_percent": round(utilization, 2),
        "warning": utilization > 80  # Warn if pool is >80% utilized
    }


def get_pool_status() -> dict:
    """
    Returns the current status of the connection pool.
    
    Returns:
        dict: Dictionary containing pool statistics including:
            - opened: Number of connections currently opened
            - busy: Number of connections currently in use
            - max: Maximum number of connections allowed
            - min: Minimum number of connections maintained
    
    Raises:
        RuntimeError: If connection pool has not been initialized.
    """
    if not _connection_pool:
        raise RuntimeError(
            "Connection pool not initialized. Call initialize_connection_pool() first."
        )
    
    return {
        "opened": _connection_pool.opened,
        "busy": _connection_pool.busy,
        "max": _connection_pool.max,
        "min": _connection_pool.min,
    }
