import pandas as pd
import logging
from sqlalchemy import create_engine
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


def create_table(engine, table_name, columns_with_types, folder_name):
    """
    Create a table in the PostgreSQL database based on a DataFrame's dtypes.

    Args:
    engine: SQLAlchemy engine instance.
    table_name: Name of the table to create.
    columns: desired columns with their types.
    folder_name: Name of the folder to prefix the table name.
    """

    # Create SQL query to create table
    create_table_query = f"CREATE TABLE IF NOT EXISTS {folder_name}_{table_name} {columns_with_types};"

    # Execute and commit the query
    try:
        with engine.connect() as conn:
            conn.execute(create_table_query)
            conn.commit()
        logging.info(f"Table {table_name} created successfully.")
    except Exception as e:
        logging.warning(f"Failed to create table {table_name}: {e}")
    

def profitability_indicators_table(tables: list, folder_name: str):
    """
    Create a table for profitability indicators in PostgreSQL.
    """

    columns = {
        'date': "DATE",
        'symbol': "VARCHAR(10)",
        ''
    }

    """CREATE TABLE profitability_indicators AS (
        SELECT
            date,
            symbol,
            netIncome/totalEquity AS return_on_equity,
            netIncome/totalAssets AS return_on_assets,
            grossProfit/revenue AS gross_profit_margin,
            operatingIncome/revenue AS operating_margin,
            netIncome/revenue AS net_profit_margin
        FROM
            tidy_statements
    );"""

    if numeric_indicators:
        for indicator in numeric_indicators:
            columns[indicator] = "FLOAT"
    else:
        logging.warning("No numeric indicators provided.")

    # Convert dictionary to SQLAlchemy-compatible string
    columns = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    
    return columns
