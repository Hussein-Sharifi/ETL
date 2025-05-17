import pandas as pd
import logging
from utils import parse_to_dataframes, melt_statements
from FA_io import load_raw_data
from parser import get_parser_args, load_config, parse_inputs
from sql_utils import connect_to_postgresql, create_table

# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main(symbols: list, documents: list, load_from: str):

    
    # Load data
    logging.info("Loading data...")
    data = load_raw_data(symbols=symbols, documents=documents, folder=load_from)

    # Parse data to DataFrames
    logging.info("Parsing data to DataFrames...")
    dfs = parse_to_dataframes(data)
    stocks = dfs.pop('stock')

    # Melt statement dataframes for easier analysis
    logging.info("Melting statement DataFrames...")
    tidy_statements = melt_statements(dfs)

    # Computing indicators with SQL
    logging.info("Computing indicators with SQL...")
    "sql_processing(dfs['stock'], tidy_statements)"

    # Save statements to Excel
    logging.info("Saving statements to Excel...")
    dfs.to_csv('data.csv', index=False)
    logging.info("Data saved successfully.")



if __name__ == "__main__":

    # Retrieve CLI arguments from parser
    args = get_parser_args()

    # If arguments were passed through a yaml file
    if args.config:
        config = load_config(args.config)
        symbols, documents, queries, load_from = parse_inputs(**config)

    # If arguments were passed through CLI
    if args.manual:
        symbols, documents, queries, load_from = parse_inputs(args.symbols, args.requests, args.queries, args.save_to)

    main(symbols=symbols, documents=documents, queries=queries, load_from=load_from)