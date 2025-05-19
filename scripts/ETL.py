import extract, transform
from parser import get_parser_args, parse_inputs, load_config
import argparse

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
    python ETL.py --config tests/test.yaml

    Pass CLI arguments manually:
    python ETL.py --manual --symbols AAPL MSFT GOOGL --requests all --queries "from=2022-05-01" "to=2023-05-01" "period=quarter" "limit=4" --save_to timestamp
    '''
    
    data = extract.main(symbols=symbols, requests=requests, queries=queries, save_to=save_to, timestamp=timestamp)
    transform.main(symbols=symbols, documents=requests, load_from=save_to, timestamp=timestamp)