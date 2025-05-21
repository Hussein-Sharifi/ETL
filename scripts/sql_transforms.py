from sql_utils import connect_to_postgresql, create_indicators
from sqlalchemy import text
from utils import long_format
import logging
import os
import pandas as pd
from config import DATA_DIR

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(stocks, wide_statements, tidy_statements, folder_name, documents, timestamp = False):
    # Connect to PostgreSQL and return connection instance
    engine = connect_to_postgresql()
    with engine.connect() as conn:
        db_info = conn.execute(text("SELECT current_database(), current_user;")).fetchone()
        logging.info(f"Connected to database: {db_info[0]} as user: {db_info[1]}")
    
    # Determine if the tables should be replaced or appended
    if timestamp:
        if_exists = 'append'
    else:
        if_exists = 'replace'
    # Make directory for processed data
    os.makedirs(f"{DATA_DIR}\\processed\\{folder_name}", exist_ok=True)
    if timestamp:
        append_time = f"_{timestamp}"
    else:
        append_time = ""

    # Upload dataframes to PostgreSQL
    logging.info("Uploading dataframes to PostgreSQL...")
    if not stocks.empty:
        stocks.to_sql(
            f"{folder_name}_stocks", 
            engine, 
            if_exists=if_exists, 
            index=False, 
            method='multi', 
            chunksize=10000
        )
        logging.info(f"Table {folder_name}_stocks successfully created/updated.")
        # Save to csv
        stocks.to_csv(f"{DATA_DIR}\\processed\\{folder_name}\\stocks.csv" + append_time, index=False)
    if not wide_statements.empty:
        wide_statements.to_sql(
            f"{folder_name}_statements", 
            engine, 
            if_exists=if_exists, 
            index=False, 
            method='multi',
            chunksize=10000
        )
        logging.info(f"Table {folder_name}_statements successfully created/updated.")
        logging.info("Computing statement indicators in SQL.")
        # Compute statement indicators in SQL
        create_indicators(engine, wide_statements, folder_name, timestamp)

        # Read indicators from PostgreSQL
        indicators = {}
        for type in ['profitability', 'leverage', 'liquidity']:
            query = f"SELECT * FROM {folder_name}_{type};"
            with engine.connect() as conn:
                indicators[type] = pd.read_sql(query, conn)
        # Convert indicators to long format
        logging.info("Converting indicators to long format...")
        tidy_indicators = long_format(indicators)
        # Save indicators to csv
        tidy_indicators.to_csv(f"{DATA_DIR}\\processed\\{folder_name}\\indicators.csv" + append_time, index=False)


        # Replace wide format statements with long format in PostgreSQL
        # Drop wide format tables
        logging.info("Replacing wide format statements with long format")
        logging.info(f"Uploading long tables...")
        # Upload tidy indicators
        tidy_indicators.to_sql(
            f"{folder_name}_indicators", 
            engine, 
            if_exists=if_exists, 
            index=False, 
            method='multi', 
            chunksize=10000
        )
        logging.info(f"Table {folder_name}_indicators successfully created.")

        # Upload tidy statements
        tidy_statements.to_sql(
            f"{folder_name}_tidy", 
            engine, 
            if_exists=if_exists, 
            index=False, 
            method='multi', 
            chunksize=10000
        )
        logging.info(f"Table {folder_name}_tidy successfully created.")
        # Save statements to csv
        tidy_statements.to_csv(f"{DATA_DIR}\\processed\\{folder_name}\\tidy.csv" + append_time, index=False)
    
        # Drop the original tables
        logging.info("Dropping wide tables...")
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {folder_name}_profitability;"))
            conn.execute(text(f"DROP TABLE IF EXISTS {folder_name}_leverage;"))
            conn.execute(text(f"DROP TABLE IF EXISTS {folder_name}_liquidity;"))
            conn.execute(text(f"DROP TABLE IF EXISTS {folder_name}_statements;"))
    
    logging.info(f"SQL transformations successfully completed. Closing connection to PostgreSQL.")
    engine.dispose()
    