import pandas as pd
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from config import fetch_postgresql_credentials

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def connect_to_postgresql():
    """
    Connect to PostgreSQL database using SQLAlchemy engine.
    Returns a SQLAlchemy engine instance.
    """
    sql_credentials = fetch_postgresql_credentials()
    
    try:
        logging.info("Connecting to PostgreSQL database...")
        url = URL.create(**sql_credentials)
        engine = create_engine(url)
        
        with engine.connect() as conn:
            logging.info("Connection successful!")
        return engine
    except Exception as e:
        logging.warning(f"Connection failed: {e}")
        raise


def create_table(engine, query: str, table_name: str):
    """
    Create a table in the PostgreSQL database based on a DataFrame's dtypes.

    Args:
    engine: SQLAlchemy engine instance.
    query: SQL query string to create the table.
    """

    # Execute and commit the query
    try:
        with engine.connect() as conn:
            conn.execute(query)
            conn.commit()
        logging.info(f"Table {table_name} created successfully.")
    except Exception as e:
        logging.warning(f"Failed to create {table_name} table: {e}")
    

def create_profitability(engine, wide: pd.DataFrame, folder_name: str, name: str = "profitability_indicators"):
    """
    Create a table for profitability indicators in PostgreSQL.
    """

    table_name = f"{folder_name}_{name}"

    profitability_indicators = text(f"""
    DROP TABLE IF EXISTS {table_name};
    CREATE TABLE {folder_name}_profitability_indicators AS (
        SELECT
            date,
            symbol,
            ("netIncome" * 1.0)/"totalEquity" AS return_on_equity,
            ("netIncome" * 1.0)/"totalAssets" AS return_on_assets,
            ("operatingIncome" * 1.0)/("totalAssets" - "totalLiabilities") AS return_on_invested_capital,
            ("grossProfit" * 1.0)/revenue AS gross_profit_margin,
            ("operatingIncome" * 1.0)/revenue AS operating_margin,
            ("netIncome" * 1.0)/revenue AS net_profit_margin
        FROM
            {folder_name}_merged as m
    );""")

    create_table(engine, profitability_indicators, table_name)
