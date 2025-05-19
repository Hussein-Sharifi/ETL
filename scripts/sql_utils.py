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
            logging.info("Connection successful")
        return engine
    except Exception as e:
        logging.warning(f"Connection failed: {e}")
        raise


def create_indicators(engine, wide: pd.DataFrame, folder_name: str, timestamp = False):
    """
    Create or update indicator tables in PostgreSQL.
    If timestamp, append to existing tables. Otherwise, create new ones.
    """
    
    profitability = text(f"""
    DROP TABLE IF EXISTS {folder_name}_profitability;
    CREATE TABLE {folder_name}_profitability AS (
        SELECT
            date,
            symbol,
            ("netIncome" * 1.0)/"totalEquity" AS return_on_equity,
            ("netIncome" * 1.0)/"totalAssets" AS return_on_assets,
            (("netIncome" - "dividendsPaid") * 1.0) / ("totalDebt" + "totalEquity") AS simplified_roic,
            ("grossProfit" * 1.0)/revenue AS gross_profit_margin,
            ("operatingIncome" * 1.0)/revenue AS operating_margin,
            ("netIncome" * 1.0)/revenue AS net_profit_margin
        FROM {folder_name}_statements
    );
    """)

    leverage = text(f"""
    DROP TABLE IF EXISTS {folder_name}_leverage;
    CREATE TABLE {folder_name}_leverage AS (
        SELECT
            date,
            symbol,
            ("totalDebt" * 1.0)/"totalEquity" AS debt_to_equity,
            ("totalEquity" * 1.0)/"totalAssets" AS equity_ratio,
            ("totalDebt" * 1.0)/"totalAssets" AS debt_ratio,
            ("totalDebt" * 1.0)/NULLIF(("totalDebt" + "totalEquity"), 0) AS debt_to_capital
        FROM {folder_name}_statements
    );
    """)

    liquidity = text(f"""
    DROP TABLE IF EXISTS {folder_name}_liquidity;
    CREATE TABLE {folder_name}_liquidity AS (
    SELECT
        date,
        symbol,
        ("totalCurrentAssets" * 1.0)/"totalCurrentLiabilities" AS current_ratio,
        (("cashAndCashEquivalents" + "shortTermInvestments" + "accountsReceivables") * 1.0)/"totalCurrentLiabilities" AS quick_ratio,
        ("cashAndCashEquivalents" * 1.0)/"totalCurrentLiabilities" AS cash_ratio,
        ABS("operatingCashFlow" * 1.0)/NULLIF("capitalExpenditure", 0) AS capex_to_operating_cash_ratio,
        ("operatingCashFlow" * 1.0)/NULLIF("totalCurrentLiabilities", 0) AS operating_cash_flow_ratio
    FROM {folder_name}_statements
    );
    """)

    for indicators, name in [(profitability, 'profitability'), (leverage, 'leverage'), (liquidity, 'liquidity')]:
        try:
            with engine.connect() as conn:
                conn.execute(indicators)
                conn.commit()
            logging.info(f"{folder_name}_{name} table created successfully.")
        except Exception as e:
            logging.warning(f"Failed to create {folder_name}_{name} table: {e}")