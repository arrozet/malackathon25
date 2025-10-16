"""
Configuration module for the FastAPI application.

This module loads environment variables from .env file and provides
configuration settings for Oracle Cloud Autonomous Database connection.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_wallet_path() -> str:
    """
    Automatically detects the correct wallet path.
    
    Returns the wallet path based on whether running in Docker or locally.
    - In Docker: /app/oracle_wallet
    - Locally: ./app/oracle_wallet (relative to project root)
    
    Returns:
        str: Absolute path to the wallet directory.
    """
    env_tns_admin = os.getenv("TNS_ADMIN", "")
    
    # If TNS_ADMIN is set and exists, use it
    if env_tns_admin and os.path.exists(env_tns_admin):
        return env_tns_admin
    
    # Check if we're in Docker (TNS_ADMIN points to /app/oracle_wallet)
    if env_tns_admin.startswith("/app/"):
        docker_path = env_tns_admin
        if os.path.exists(docker_path):
            return docker_path
    
    # Local development: find wallet relative to project root
    # Try multiple possible locations
    possible_paths = [
        os.path.join(os.getcwd(), "app", "oracle_wallet"),  # From project root
        os.path.join(os.path.dirname(__file__), "oracle_wallet"),  # Relative to config.py
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "oracle_wallet")),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # If nothing found, return the env variable or default
    return env_tns_admin or "/app/oracle_wallet"


class Config:
    """
    Configuration class for application settings.
    
    Loads all necessary environment variables for Oracle Cloud connection
    and application configuration.
    """
    
    # Oracle Database Connection Settings
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "fagfefcg84y83s1a_medium")
    ORACLE_USER: str = os.getenv("ORACLE_USER", "DAJER_ADMIN")
    ORACLE_PASSWORD: str = os.getenv("ORACLE_PASSWORD", "")
    
    # Oracle Wallet Configuration - Auto-detect path
    TNS_ADMIN: str = _get_wallet_path()
    ORACLE_WALLET_PASSWORD: str = os.getenv("ORACLE_WALLET_PASSWORD", "")
    
    # Application Settings
    APP_ENV: str = os.getenv("APP_ENV", "prod")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Improved CORS configuration for production
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://158.179.212.221,http://158.179.212.221:80,http://158.179.212.221:3000,https://dr-artificial.com,https://www.dr-artificial.com,http://dr-artificial.com",
    )
    
    # AI Service Configuration
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validates that all required configuration parameters are present.
        
        Raises:
            ValueError: If any required configuration parameter is missing.
        """
        required_vars = {
            "ORACLE_DSN": cls.ORACLE_DSN,
            "ORACLE_USER": cls.ORACLE_USER,
            "ORACLE_PASSWORD": cls.ORACLE_PASSWORD,
            "ORACLE_WALLET_PASSWORD": cls.ORACLE_WALLET_PASSWORD,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
    
    @classmethod
    def get_connection_string(cls) -> str:
        """
        Constructs the Oracle database connection string.
        
        Returns:
            str: Connection string for Oracle database.
        """
        return f"{cls.ORACLE_USER}/{cls.ORACLE_PASSWORD}@{cls.ORACLE_DSN}"
    
    @classmethod
    def display_config(cls) -> dict:
        """
        Returns a safe version of configuration for logging/debugging.
        Masks sensitive information like passwords.
        
        Returns:
            dict: Dictionary with configuration values (passwords masked).
        """
        return {
            "ORACLE_DSN": cls.ORACLE_DSN,
            "ORACLE_USER": cls.ORACLE_USER,
            "ORACLE_PASSWORD": "***" if cls.ORACLE_PASSWORD else "NOT SET",
            "TNS_ADMIN": cls.TNS_ADMIN,
            "ORACLE_WALLET_PASSWORD": "***" if cls.ORACLE_WALLET_PASSWORD else "NOT SET",
            "APP_ENV": cls.APP_ENV,
            "DEBUG": cls.DEBUG,
            "CORS_ORIGINS": cls.CORS_ORIGINS,
            "XAI_API_KEY": "***" if cls.XAI_API_KEY else "NOT SET",
            "TAVILY_API_KEY": "***" if cls.TAVILY_API_KEY else "NOT SET",
        }

    @classmethod
    def get_cors_origins(cls) -> list[str]:
        """
        Parses the configured CORS origins into a list.
        
        Returns:
            list[str]: Origins allowed to access the API via CORS.
        """

        return [origin.strip() for origin in cls.CORS_ORIGINS.split(",") if origin.strip()]


# Create a global config instance
config = Config()
