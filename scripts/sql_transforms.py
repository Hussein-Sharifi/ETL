from sql_utils import connect_to_postgresql, create_table
from sqlalchemy import text
import pandas as pd


def main(stocks, tidy_statements, folder_name):
    # Connect to PostgreSQL and return connection instance
    engine = connect_to_postgresql()

    # Upload dataframes to PostgreSQL
    stocks.to_sql(
        f"{folder_name}_stocks", 
        engine, 
        if_exists='replace', 
        index=False, 
        method='multi', 
        chunksize=10000
    )
    
    tidy_statements.to_sql(
        f"{folder_name}_tidy", 
        engine, 
        if_exists='replace', 
        index=False, 
        method='multi'
        chunksize=10000
    )

query = "SELECT * FROM overwrite_stocks LIMIT 10;"
with engine.connect() as conn:
    result_df = pd.read_sql(text(query), conn)

    