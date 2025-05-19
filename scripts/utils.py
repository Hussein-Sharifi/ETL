import pandas as pd
import json
import logging
from typing import Dict, List, Optional
from config import DEFAULT_ENDPOINTS_PATH
from FA_io import load_raw_data


# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def build_urls(api_key: str, requests: List[str], symbols: List[str] = None, **kwargs) -> Dict[str, Dict[str, str]]:
    """
    Build the complete URL for the API request.

    inputs:
    - api_key: API key for authentication
    - requests: list of endpoint names to fetch from the API (e.g., 'stock', 'income-statement')
    - symbols: list of stock symbols to fetch data for
    - kwargs: query parameters for the API request. For stocks, from=yyyy-mm-dd and
      to=yyyy-mm-dd. For statements, period=(quarter or annual) and limit=number
      of records to fetch.
    """
    
    # Load default endpoints from JSON file
    with open(DEFAULT_ENDPOINTS_PATH, 'r') as f:
        default_endpoints = json.load(f)
    if not default_endpoints:
        raise FileNotFoundError(f"Failed to load default endpoints from {DEFAULT_ENDPOINTS_PATH}.")

    # Prepare queries:
    if not kwargs.get('from') or not kwargs.get('to'):
        stock_query = ""
    else:
        stock_query = f"from={kwargs.get('from', '')}&to={kwargs.get('to', '')}&"
    statement_query = f"period={kwargs.get('period', 'annual')}&limit={kwargs.get('limit', 1)}&"

    # Format URLs for each endpoint 
    urls = {}
    for endpoint in requests:

        # Choose template and query based on endpoint type
        template = default_endpoints[endpoint]
        query = stock_query if endpoint == "stock" else statement_query

        urls[endpoint] = {}
        for symbol in symbols:
            try:
                formatted_url = template.format(symbol=symbol, query=query) + f"{api_key}"
                urls[endpoint][symbol] = formatted_url
            except Exception as e:
                logging.error(f"Failed to format URL for {endpoint} and symbol {symbol}: {e}")
                continue

    return urls
               

def parse_to_dataframes(financial_data):
    
    dataframes = {}
    documents = financial_data.keys()

    # For each document type
    for document in documents:

        # Process stocks format
        if document == 'stock':
            # For each symbol
            for symbol_data in financial_data[document]:
                
                # Ensure expected stock format
                if 'historical' not in symbol_data or not isinstance(symbol_data['historical'], list):
                    logging.warning(f"Malformed stock data for {symbol_data.get('symbol', 'UNKNOWN')}; skipping.")
                    continue
                
                # Create dataframe and add symbol column
                df = pd.DataFrame(symbol_data['historical'])
                df['symbol'] = symbol_data['symbol']
                df.insert(1, 'symbol', df.pop('symbol'))

                # Change date column to datetime
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

                # Add data. Create document key if it doesn't exist
                if document not in dataframes:
                    dataframes[document] = df
                else:
                    dataframes[document] = pd.concat([dataframes[document], df])
        
        # Process other documents format
        else:
            # For each symbol
            for symbol_data in financial_data[document]:
                
                # Check for expected format
                if not isinstance(symbol_data, list):
                    logging.warning(f"Expected list of records for {document}, got {type(symbol_data)}; skipping.")
                    continue
                
                # Create dataframe
                df = pd.DataFrame(symbol_data)

                # Change date column to datetime
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

                # Add data. Create document key if it doesn't exist
                if document not in dataframes:
                    dataframes[document] = df
                else:
                    dataframes[document] = pd.concat([dataframes[document], df])

    return dataframes


def wide_format(dfs: dict) -> pd.DataFrame:
    """
    Takes in a dictionary of statements dataframes and converts them to wide format.
    
    dfs: dictionary with keys income_statement, balance_sheet, and cashflow
    """

    # Merge all statements into a single DataFrame
    merged = pd.merge(
        dfs['income_statement'],
        dfs['balance_sheet'],
        on=['date', 'symbol'],
        how='inner',
        suffixes=('', '_bs')
    )

    # Merge with cashflow
    merged = pd.merge(
        merged,
        dfs['cashflow'],
        on=['date', 'symbol'],
        how='inner',
        suffixes=('', '_bs')
    )


    # Remove duplicate columns
    drop_columns = [col for col in merged.columns if col.endswith('_bs')]
    merged = merged.drop(columns=drop_columns)

    return merged


def long_format(dfs: dict) -> pd.DataFrame:
    """
    Takes in a dictionary of statement DataFrames and melts statements into long format.
    """

    # Identify columns to keep as identifiers and columns to drop
    id_vars = ['date', 'symbol']
    drop_columns = ['link', 'finalLink', 'fillingDate', 'acceptedDate', 'calendarYear', 'period']
    
    # Melt each statement DataFrame
    melted_frames = [
    df.drop(columns=[c for c in drop_columns if c in df.columns])
      .melt(id_vars=id_vars, var_name='metric', value_name='value')
      .assign(statement_type=name)
    for name, df in dfs.items() if name != 'stock'
]

    return pd.concat(melted_frames, ignore_index=True)