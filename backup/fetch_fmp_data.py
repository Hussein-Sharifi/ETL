import requests
import pandas as pd
import os
import argparse
import json
import logging
from dotenv import load_dotenv
from typing import Tuple, Dict, List


# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_api_key(key: str, dotenv_path: str) -> str:
    """
    Fetch API key from .env file.
    """

    loaded = load_dotenv(dotenv_path)
    if not loaded:
        logging.error(f"Failed to load .env file from {dotenv_path}.")
        raise FileNotFoundError(f".env file not loaded from path: {dotenv_path}. \nLikely not found or empty.")

    api_key = os.getenv(key)
    if not api_key:
        logging.error(f"{key} not found in environment. Check your .env file.")
        raise ValueError(f"{key} not found in environment. Check your .env file.")

    return api_key


def fetch_endpoint_data(url: str, ticker: str) -> dict:
    """
    Fetch data from a given API endpoint for a given ticker.
    """

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            logging.error("No data returned from API.")
            raise ValueError("No data returned from API.")
        return data
    except Exception as e:
        logging.warning(f"Error fetching data for {ticker}: {e}")
        return None


def fetch_data(tickers: List[str], kind: str, FMP_API_KEY: str) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    """
    Fetch stock or statement data from the Financial Modeling Prep API.
    """

    stocks_data = {}
    statements_data = {}

    # Fetch stock data
    if kind in ("stocks", "both"): 
        for ticker in tickers:
            url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_API_KEY}"
            data = fetch_endpoint_data(url, ticker)
            if data:
                stocks_data[ticker] = data

    # Fetch financial statement data
    if kind in ("statements", "both"):
        for ticker in tickers:
            url = f"https://financialmodelingprep.com/api/v3/financials/income-statement/{ticker}?apikey={FMP_API_KEY}"
            data = fetch_endpoint_data(url, ticker)
            if data:
                statements_data[ticker] = data
    
    return stocks_data, statements_data


def save_data_to_json(
    tickers: List[str], 
    stocks_data: Dict[str, dict]=None, 
    statements_data: Dict[str, dict]=None, 
    project_root: str
  ) -> None:
    """
    Save fetched data to a JSON file.
    """

    output_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    for ticker in tickers:    
        if ticker in stocks_data:
            stock_filename = os.path.join(output_dir, f"{ticker}_stock_data.json")
            with open(stock_filename, 'w') as f:
                json.dump(stocks_data[ticker], f, indent=2)
            logging.info(f"Saved {ticker} stock data to {stock_filename}")

        if ticker in statements_data:
            statement_filename = os.path.join(output_dir, f"{ticker}_statement_data.json")
            with open(statement_filename, 'w') as f:
                json.dump(statements_data[ticker], f, indent=2)
            logging.info(f"Saved {ticker} statement stock data to {statement_filename}")


def main(tickers: List[str], save: bool = False, kind: str = 'both') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function to fetch stock and financial statement data and save it to JSON files.

    tickers: list of ticker symbols
    save: boolean flag to save data to JSON files
    kind: type of data to fetch ('stocks', 'statements', or 'both')
    project_root: path to the project root directory
    """

    # Fetch API key from .env file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, "config", ".env")
    FMP_API_KEY = fetch_api_key("FMP_API_KEY", env_path)

    # Fetch data from the Financial Modeling Prep API
    stocks_data, statements_data = fetch_data(tickers, kind, FMP_API_KEY)
    if not stocks_data and not statements_data:
        logging.warning("No data fetched. Returning None.")
        return None, None

    if save:
        save_data_to_json(tickers, stocks_data, statements_data, project_root)

    return pd.DataFrame(stocks_data), pd.DataFrame(statements_data)


if __name__ == "__main__":
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Fetch stock data from Financial Modeling Prep API')
    parser.add_argument('--tickers', nargs='+', required=True, help='List of ticker symbols e.g. AAPL MSFT GOOGL')
    parser.add_argument('--kind', default='both', help='Type stocks, statements, or both')
    parser.add_argument('--save', action='store_true', help='Save output to JSON')
    
    args = parser.parse_args()

    # Example usage: python fetch_fmp_data.py --tickers AAPL MSFT GOOGL --statements
    stocks_df, statements_df = main(tickers=args.tickers, save=args.save, kind=args.kind)
    
    logging.info(f"Fetched and saved data for {len(args.tickers)} tickers.")