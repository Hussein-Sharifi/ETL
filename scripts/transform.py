import pandas as pd
import logging
from utils import parse_to_dataframes, wide_format, long_format
from FA_io import load_raw_data
from parser import get_parser_args, load_config, parse_inputs
import sql_transforms

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(symbols: list, documents: list, load_from: str, timestamp = False):
    """
    Main function for loading and transforming financial data.
    Args:
        symbols (list): List of stock symbols to fetch data for.
        documents (list): List of document types to fetch data for.
        load_from (str): Folder name to load data from.
    """

    # Load data
    logging.info("Loading raw data...")
    data = load_raw_data(symbols=symbols, documents=documents, folder=load_from, timestamp=timestamp)

    # Parse data to DataFrames
    logging.info("Parsing data to DataFrames...")
    dfs = parse_to_dataframes(data)
    if 'stock' in documents:
        stocks = dfs.pop('stock')
    else:
        stocks = pd.DataFrame()
    
    if 'balance_sheet' in documents:
        super_wide = wide_format(dfs)
        tidy_statements = long_format(dfs)
    else:
        super_wide = pd.DataFrame()
        tidy_statements = pd.DataFrame()

    # Load data to PostgreSQL
    # Compute statement indicators with SQL
    # Upload dataframes and long format indicators to PostgreSQL
    sql_transforms.main(stocks=stocks, wide_statements=super_wide, tidy_statements=tidy_statements, folder_name=load_from, documents=documents, timestamp=timestamp)


if __name__ == "__main__":

    # Retrieve CLI arguments from parser
    args = get_parser_args()

    # If arguments were passed through a yaml file
    if args.config:
        config = load_config(args.config)
        symbols, documents, queries, load_from, timestamp = parse_inputs(**config)

    # If arguments were passed through CLI
    if args.manual:
        symbols, documents, queries, load_from, timestamp = parse_inputs(args.symbols, args.requests, args.queries, args.save_to, args.timestamp)

    ''' Example usage: 
    Pass CLI arguments through yaml file:
    python extract.py --config tests/test.yaml

    Pass CLI arguments manually:
    python extract.py --manual --symbols AAPL MSFT GOOGL --requests all --queries "from=2022-05-01" "to=2023-05-01" "period=quarter" "limit=4" --save_to timestamp
    '''

    main(symbols=symbols, documents=documents, load_from=load_from, timestamp=timestamp)
    print("Data transformed successfully.")