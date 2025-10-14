"""
Test script for Oracle Autonomous Database connection.

This script tests the connection to Oracle Cloud Autonomous Database
using the configured wallet and credentials. It can be run standalone
to verify connectivity before running the full application.

Usage:
    python scripts/test_connection.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import config
from app.db import initialize_connection_pool, close_connection_pool, execute_query
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to test database connection.
    
    Tests the following:
    1. Configuration validation
    2. Connection pool initialization
    3. Basic query execution
    4. Connection pool closure
    
    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    logger.info("=" * 60)
    logger.info("Oracle Autonomous Database Connection Test")
    logger.info("=" * 60)
    
    try:
        # Display configuration (with masked passwords)
        logger.info("\nConfiguration:")
        for key, value in config.display_config().items():
            logger.info(f"  {key}: {value}")
        
        # Validate configuration
        logger.info("\nValidating configuration...")
        config.validate()
        logger.info("✓ Configuration is valid")
        
        # Initialize connection pool
        logger.info("\nInitializing connection pool...")
        initialize_connection_pool(
            min_connections=1,
            max_connections=5,
            increment=1
        )
        logger.info("✓ Connection pool initialized successfully")
        
        # Test simple query
        logger.info("\nExecuting test query...")
        result = execute_query("SELECT 'Hello from Oracle!' as message FROM DUAL")
        if result:
            logger.info(f"✓ Query result: {result[0][0]}")
        
        # Test database information query
        logger.info("\nRetrieving database information...")
        db_info = execute_query(
            """
            SELECT 
                SYSDATE as current_time,
                USER as current_user,
                SYS_CONTEXT('USERENV', 'DB_NAME') as database_name,
                SYS_CONTEXT('USERENV', 'SERVICE_NAME') as service_name
            FROM DUAL
            """
        )
        
        if db_info:
            row = db_info[0]
            logger.info("✓ Database Information:")
            logger.info(f"  Current Time: {row[0]}")
            logger.info(f"  Current User: {row[1]}")
            logger.info(f"  Database Name: {row[2]}")
            logger.info(f"  Service Name: {row[3]}")
        
        # Test table listing (requires appropriate permissions)
        try:
            logger.info("\nListing user tables...")
            tables = execute_query(
                """
                SELECT table_name 
                FROM user_tables 
                ORDER BY table_name
                """
            )
            if tables:
                logger.info(f"✓ Found {len(tables)} tables:")
                for table in tables[:10]:  # Show first 10 tables
                    logger.info(f"  - {table[0]}")
                if len(tables) > 10:
                    logger.info(f"  ... and {len(tables) - 10} more")
            else:
                logger.info("✓ No tables found (this is normal for a new database)")
        except Exception as e:
            logger.warning(f"Could not list tables (might lack permissions): {str(e)}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS PASSED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error("\n" + "=" * 60)
        logger.error("✗ TEST FAILED!")
        logger.error("=" * 60)
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1
        
    finally:
        # Always try to close the connection pool
        try:
            logger.info("\nClosing connection pool...")
            close_connection_pool()
            logger.info("✓ Connection pool closed")
        except Exception as e:
            logger.error(f"Error closing connection pool: {str(e)}")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
