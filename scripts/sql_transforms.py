from sql_utils import connect_to_postgresql, create_table, create_profitability
from sqlalchemy import text
import pandas as pd


def main(stocks, merged_statements, folder_name):
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
    
    merged_statements.to_sql(
        f"{folder_name}_merged", 
        engine, 
        if_exists='replace', 
        index=False, 
        method='multi',
        chunksize=10000
    )

    # Create indicators tables
    if statements:
        profitability_indicators = create_profitability(engine, merged_statements, folder_name)
        efficiency_indicators = create_efficiency(engine, merged_statements, folder_name)
        liquidity_indicators = create_liquidity(engine, merged_statements, folder_name)
        leverage_indicators = create_leverage(engine, merged_statements, folder_name)
        valuation_indicators = create_valuation(engine, merged_statements, folder_name)
        solvency_indicators = create_solvency(engine, merged_statements, folder_name)

    if stocks:
        stock_indicators = create_stock_indicators(engine, stocks, folder_name)

query = "SELECT * FROM overwrite_tidy LIMIT 10;"
with engine.connect() as conn:
    result_df = pd.read_sql(text(query), conn)

    