import requests
import logging
from typing import Dict, List, Optional


def fetch_endpoint_data(url: str) -> Optional[dict]:
    """
    Fetch data from a given url.
    """

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.warning(f"Request error for URL {url}: {e}")
    except ValueError:
        logging.warning(f"Invalid JSON response from URL {url}.")
    return None


def fetch_data(urls: dict):
    data = {}
    # For loop for request types
    for request in urls.keys():
        data[request] = {}
        # For loop for symbols
        for symbol in urls[request].keys():
            symbol_data = fetch_endpoint_data(urls[request][symbol])
            if symbol_data:
                data[request][symbol] = symbol_data
                logging.info(f"Fetched {request} for {symbol}")
            else:
                logging.warning(f"No {request} found for {symbol}.")
                data[request][symbol] = None
    
    if not data:
        logging.warning("No data fetched. Returning None.")
        return None
    
    return data