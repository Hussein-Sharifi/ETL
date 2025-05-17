import os
import logging
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv


# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Configure pathing
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(PROJECT_ROOT, "config", ".env")
DEFAULT_ENDPOINTS_PATH = os.path.join(PROJECT_ROOT, "config", "default_endpoints.json")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")


# Load environment variables
loaded = load_dotenv(ENV_PATH)
if not loaded:
    logging.error(f"Failed to load .env file from {ENV_PATH}.")
    raise FileNotFoundError(f"Failed to load .env file from {ENV_PATH}.")


def fetch_api_key(key: str = "FMP_API_KEY") -> str:
    """
    Fetch API key from .env file.
    """
        
    api_key = os.getenv(key)
    if not api_key:
        raise ValueError(f"{key} not found in environment. Check your .env file at {ENV_PATH}")
    return api_key


def fetch_postgresql_credentials() -> dict:
    """
    Fetch SQL credentials from .env file.
    """
    
    sql_credentials = POSTGRESQL_CONFIG = {
    "drivername": "postgresql+psycopg2",
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
    }
    
    if not sql_credentials:
        raise ValueError(f"sql credentials not found in environment. Check your .env file at {ENV_PATH}")
    
    return sql_credentials