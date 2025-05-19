import argparse
import yaml
import logging
from datetime import datetime
from datetime import datetime

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_parser_args():
    parser = argparse.ArgumentParser(description="Fetch data from FMP API.")

    # Mutually exclusive arguments: 
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--config', type=str, help='Path to YAML config file for CLI arguments')
    group.add_argument('--manual', action='store_true', help='Use manual CLI arguments')

    # Add arguments for manual input
    parser.add_argument('--symbols', nargs='+', help='List of ticker symbols')
    parser.add_argument('--requests', nargs='+', help='Choose endpoint to fetch from the API. Options: "stock", "statements", or "all"')
    parser.add_argument('--queries', nargs='+', help='Query parameters like "from=2022-01-01" "to=2022-12-31"')
    parser.add_argument('--save_to', help='Folder name to save data. Uppercase and lowercase letters, numbers, and underscores only. This will also be used as SQL table name prefix.')
    parser.add_argument('--timestamp', action='store_true', help='Adds timestamp to saved file names. Use for scheduled jobs.')

    args = parser.parse_args()

    # If using manual input, enforce following arguments
    if args.manual:
        if not all([args.symbols, args.requests, args.save_to]):
            parser.error("--manual requires --symbols, --requests, and --save_to")
    

    return args


def load_config(path: str):
    '''
    Load parser arguments from yaml config file
    '''

    if not path.endswith(('.yaml', '.yml')):
        logging.warning("Config file does not end with .yaml or .yml. Is this correct?")

    with open(path, 'r') as f:
        config=yaml.safe_load(f)
    
    return config


def parse_queries(queries: list):
    '''
    Parse and validate query arguments
    '''
    
    queries = dict(q.split('=') for q in queries) if queries else {}
    valid = ['from', 'to', 'period', 'limit']
    invalid = [q for q in queries.keys() if q not in valid]
    
    if invalid:
        raise KeyError(f'Did not recognize {invalid} query arguments')
    
    return queries


def parse_inputs(symbols: list, requests: list, queries: list = None, save_to: str = None, timestamp: bool = False):
    '''
    Parse and validate CLI arguments.
    '''
    
    # Enforce symbols and requests
    if not symbols or not requests:
        raise KeyError("Symbols and requests arguments are required to fetch data")
    
    # Recommend and parse queries
    if not queries:
        logging.warning("No query argument passed. Fetching only most recent statements and/or current stock data")
        queries = {}
    else:
        queries = parse_queries(queries)
    
    if timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for request in requests:
        if request == 'all':
            requests = ['stock', 'income_statement', 'cashflow', 'balance_sheet']
            break
        elif request == 'statements':
            requests = ['income_statement', 'cashflow', 'balance_sheet']
            break
        elif request == 'stock':
            requests = ['stock']
            break
        elif request not in ['stock', 'statements', 'all']:
            raise KeyError(f"Did not recognize {request} request argument. Options: 'stock', 'statements', or 'all'")
    
    return symbols, requests, queries, save_to, timestamp