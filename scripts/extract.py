from typing import Dict, List
from config import fetch_api_key
from utils import build_urls
from FA_io import save_raw_data
from fmp_client import fetch_endpoint_data, fetch_data
from parser import get_parser_args, load_config, parse_inputs


def main(symbols: List[str], requests: List[str], queries: dict = {}, save_to: str = None, timestamp = False):
    """
    Main function for fetching financial data from FMI API and saving it to JSON files.
    
    requests: list of endpoint names to fetch from the API ("stock", "income_statement", "cashflow", and/or "balance_sheet")
    symbols:  list of ticker symbols for requested endpoints.
    queries:  query parameters. For stocks, use from="yyyy-mm-dd" and to="yyyy-mm-dd"\n\
              For the rest, use period=("quarter" or "annual") limit=N\
              For all, include all query parameters.
    save_to:  Save JSON data to data/raw/<folder_name>.
    """

    # Fetch API key from .env file
    FMP_API_KEY = fetch_api_key("FMP_API_KEY")

    # Fetch data from the Financial Modeling Prep API
    urls = build_urls(api_key=FMP_API_KEY, requests=requests, symbols=symbols, **queries)
    data = fetch_data(urls)

    if save_to.lower() != "none":
        save_raw_data(data, symbols=symbols, requests=requests, save_to=save_to, timestamp=timestamp)
    
    return data


if __name__ == "__main__":

    # Retrieve CLI arguments from parser
    args = get_parser_args()

    # If arguments were passed through a yaml file
    if args.config:
        config = load_config(args.config)
        symbols, requests, queries, save_to, timestamp = parse_inputs(**config)

    # If arguments were passed through CLI
    if args.manual:
        symbols, requests, queries, save_to, timestamp = parse_inputs(args.symbols, args.requests, args.queries, args.save_to, args.timestamp)
    
    
    ''' Example usage: 
    Pass CLI arguments through yaml file:
    python extract.py --config <yaml_abs_path>

    Pass CLI arguments manually:
    python extract.py --manual --symbols AAPL MSFT GOOGL --requests all --queries "from=2022-05-01" "to=2023-05-01" "period=quarter" "limit=4" --save_to timestamp
    '''
    
    data = main(symbols=symbols, requests=requests, queries=queries, save_to=save_to, timestamp=timestamp)
    print("Data fetched successfully.")