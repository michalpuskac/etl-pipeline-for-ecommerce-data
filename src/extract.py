import requests
import json
import pandas as pd
import time
import os
import logging
import config

logger = logging.getLogger(__name__)
RAW_DATA_DIR = config.DATA_DIR 

# API_ENDPOINTS_TEST = {
#     "users": "https://dummyjson.com/users?limit=10",
#     "products": "https://dummyjson.com/products?limit=10",
#     "carts": "https://dummyjson.com/cart?limit=10"
# }


# TODO: Implement API fetch with retry logic
# -- Extraction Function (Fetch) --
def fetch_from_api(url, max_retries=3, delay=2) -> list | dict:
    """Fetch data from API endpoint with retry logic"""

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt +1}/{max_retries}: Data extraction form {url}")
            response = requests.get(url, timeout=10) # Add timeout for request
            response.raise_for_status() # Check (4xx,5xx) Errors

            logger.info(f"Successfully downloaded data from  {url} (Status: {response.status_code}).") 

            # JSON Decoding
            data = response.json()
            logger.info(f"JSON successfully decoded {url}")
            return data # Success --> return data and end function
        
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Attempt {attempt +1} / {max_retries}: HTTP Error for {url}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Attempt {attempt +1} / {max_retries}: Connection Error for {url}: {e}")
        except requests.exceptions.Timeout as e:
            logger.warning(f"Attempt {attempt +1} / {max_retries}: Timeout for {url}: {e}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt +1} / {max_retries}: Request Error for {url}: {e}")
        except json.JSONDecodeError:
            logger.warning(f"Attempt {attempt +1} / {max_retries}: Response data for {url} are not valid JSON.")
            logger.debug(f"Response content: {response.text[:200]}...")

        # Waiting for another response if we are not in last attempt
        if attempt < max_retries -1:
            logger.info(f"Waiting {delay}s before another attempt.")
            time.sleep(delay)
        else:
            logger.error(f"Downloading data was unsuccessful")
            return None # All attempt failure


#TODO: Implement saving fetched data
# -- Saving Function --
def save_to_json(data, filename, directory) -> json:
    """Save python data (dict/list) to JSON file."""

    if data is None:
        logger.warning(f"No data to save to {filename}.")
        return
    
    file_path = os.path.join(directory, filename)
    logger.info(f"Saving data to JSON file {file_path}")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Data successfully saved to {file_path}.\n")
    
    except IOError as e:
        logger.error(f"Error during writing to file {file_path}: {e}")
    except TypeError as e:
        logger.error(f"Error during data serialization to JSON for {file_path}: {e}")


# if __name__ == "__main__":
#     # basic logging for separate module testing 
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

#     # Working on each defined endpoint
#     for name, url in API_ENDPOINTS_TEST.items():
#         # 1. Extraction
#         extracted_data = fetch_from_api(url)

#         # Skipping current endpoing if extraction failed
#         if extracted_data is None:
#             logger.warning(f"Skipping another steps for {name} due to error durin extraction.")
#             continue
        
#         #File name is derived from endpoint name
#         json_filename= f"{name}_data.json"

#         # 2. Saving to JSON File
#         save_to_json(extracted_data, json_filename, config.DATA_DIR)


