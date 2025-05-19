import os
import json
import logging
from config import PROJECT_ROOT, DATA_DIR, DEFAULT_ENDPOINTS_PATH


# logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def save_raw_data(data: dict, symbols: list, requests: list, save_to: str, timestamp: bool = False) -> None:
    """
    Save fetched data to data/raw as JSON file.
    """

    # Create output directory
    output_dir = os.path.join(DATA_DIR, "raw", save_to)
    os.makedirs(output_dir, exist_ok=True)        


    # For each symbol
    for symbol in symbols:

        # Create symbol directory inside the chosen save folder.
        symbol_dir = os.path.join(output_dir, symbol)
        os.makedirs(symbol_dir, exist_ok=True)

        # For each requested data field
        for request in requests:

            # Get requested data for symbol and check it isn't empty
            symbol_data = data.get(request, {}).get(symbol)
            if symbol_data:
                
                # Save data. Use timestamp if specified.
                if timestamp:
                    filename = os.path.join(symbol_dir, f"{symbol}_{request}_{timestamp}.json")
                else:
                    filename = os.path.join(symbol_dir, f"{symbol}_{request}.json")
                with open(filename, 'w') as f:
                    json.dump(symbol_data, f, indent=2)
                logging.info(f"Saved {symbol} {request} to {filename}")


def load_raw_data(symbols: list, documents: list, folder: str, timestamp=False):
    raw_data_path = os.path.join(DATA_DIR, 'raw', folder)
    financial_data = {}

    # Create empty list for each document type (eg. stock, cashflow, etc)
    for document in documents:
        financial_data[document]= []

        # Append document data for each symbol if said data exists
        for symbol in symbols:
                if timestamp:
                    input_path = os.path.join(raw_data_path, symbol, f"{symbol}_{document}_{timestamp}.json")
                else:
                    input_path = os.path.join(raw_data_path, symbol, f"{symbol}_{document}.json")
                if not os.path.exists(input_path):
                    logging.warning(f"File not found: {input_path}")
                    continue
                with open(input_path, 'r') as f:
                    data = json.load(f)
                if data:
                    financial_data[document].append(data)
                else:
                    logging.warning(f"Could not find {document} for {symbol}")
        
        # If no data exists for this document type, remove it from finanical data
        if financial_data[document] == []:
            logging.warning(f"No {document} info found for any symbols. Skipping {document}s")
            del financial_data[document]

    return financial_data

def save_to_excel(save_to, dfs) -> None:
    """
    Save processed data to data/processed as JSON file.
    """

    # Create output directory
    output_dir = os.path.join(DATA_DIR, "processed", save_to)
    os.makedirs(output_dir, exist_ok=True)

    # Save dataframes to 
    for statement, dataframe in dfs.items():
        dataframe.to_excel(os.path.join(output_dir, f"{statement}.xlsx"), index=False)