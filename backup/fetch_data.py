from typing import Dict, List
from config import fetch_api_key
from utils import build_urls, save_data
from fmp_client import fetch_endpoint_data, fetch_data
from parser import get_parser_args, load_config, parse_inputs


def main(symbols: List[str], requests: List[str], queries: dict = {}, save: str = None):
    """
    Main function for fetching financial data and saving it to JSON files.
    
    requests: list of endpoint names to fetch from the API ("stock", "income_statement", "cashflow", "balance_sheet", or "all")
    symbols:  list of ticker symbols for requested endpoints.
    queries:  query parameters. For stocks, use from="yyyy-mm-dd" and to="yyyy-mm-dd"\n\
              For the rest, use period=("quarter" or "annual") limit=N\
              For all, include all query parameters.
    save:     boolean flag for saving data to JSON files in data/raw.
    """

    # Fetch API key from .env file
    FMP_API_KEY = fetch_api_key("FMP_API_KEY")

    # Fetch data from the Financial Modeling Prep API
    urls = build_urls(api_key=FMP_API_KEY, requests=requests, symbols=symbols, **queries)
    data = fetch_data(urls)

    if save:
        save_data(data, symbols=symbols, requests=requests, save=save)
    
    return data


if __name__ == "__main__":

    # Retrieve CLI arguments from parser
    args = get_parser_args()

    # If arguments were passed through a yaml file
    if args.config:
        config = load_config(args.config)
        symbols, requests, queries, save = parse_inputs(**config)

    # If arguments were passed through CLI
    if args.manual:
        symbols, requests, queries, save = parse_inputs(args.symbols, args.requests, args.queries, args.save)
    
    
    ''' Example usage: 
    Pass CLI arguments through yaml file:
    python fetch.py --config tests/fetch_config.yaml

    Pass CLI arguments manually:
    python fetch.py --manual --symbols AAPL MSFT GOOGL --requests stock_statement cashflow --queries "from=2022-05-01" "to=2023-05-01" "period=quarter" "limit=4" --save
    '''
    
    data = main(symbols=symbols, requests=requests, queries=queries, save=save)
    print("Data fetched successfully.")