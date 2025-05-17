import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from config import fetch_postgresql_credentials

def connect_to_postgresql():
    """
    Connect to PostgreSQL database using SQLAlchemy engine.
    Returns a SQLAlchemy engine instance.
    """
    sql_credentials = fetch_postgresql_credentials()
    
    try:
        # Unpack credentials directly into URL.create()
        url = URL.create(**sql_credentials)
        engine = create_engine(url)
        
        # Test connection
        with engine.connect() as conn:
            print("Connection successful!")
        return engine
    except Exception as e:
        print(f"Connection failed: {e}")
        raise


def create_table(conn, cur, table_name, dataframe, folder_name):
    """
    Create a table in the PostgreSQL database based on a DataFrame's dtypes.
    """
    pandas_to_postgres = {
        'int64': 'BIGINT',
        'float64': 'DOUBLE PRECISION',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP',
    }

    columns = {}
    # Convert DataFrame dtypes to PostgreSQL types. Default to TEXT for unknown types.
    for col, dtype in dataframe.dtypes.items():
        columns[col] = pandas_to_postgres.get(str(dtype), 'TEXT')

    # Create SQL query to create table
    columns_with_types = ", ".join([f"{col} {sql_type}" for col, sql_type in columns.items()])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {folder_name}_{table_name} ({columns_with_types});"

    # Execute and commit the query
    try:
        cur.execute(create_table_query)
        conn.commit()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Failed to create table {table_name}: {e}")
        conn.rollback()