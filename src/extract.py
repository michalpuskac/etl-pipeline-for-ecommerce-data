"""Module provide function for fetching data from API and save them to JSON file"""

import json
import logging
import os
import time

import requests

import config

logger = logging.getLogger(__name__)
RAW_DATA_DIR = config.DATA_DIR

API_ENDPOINTS_TEST = {
    "users": "https://dummyjson.com/users?limit=10",
    "products": "https://dummyjson.com/products?limit=10",
    "carts": "https://dummyjson.com/cart?limit=10",
}


# -- Extraction Function (Fetch) --
def fetch_from_api(url, max_retries=3, delay=2) -> list | dict:
    """Fetch data from API endpoint with retry logic"""

    for attempt in range(max_retries):
        try:
            logger.info(
                "Attempt %d/%d: Data extraction form %s", attempt + 1, max_retries, url
            )
            response = requests.get(url, timeout=10)  # Add timeout for request
            response.raise_for_status()  # Check (4xx,5xx) Errors

            logger.info(
                "Successfully downloaded data from  %s (Status: %d).",
                url,
                response.status_code,
            )

            # JSON Decoding
            data = response.json()
            logger.info("JSON successfully decoded %s", url)
            return data  # Success --> return data and end function

        except requests.exceptions.HTTPError as e:
            logger.warning(
                "Attempt %d/%d: HTTP Error for %s: %s", attempt + 1, max_retries, url, e
            )
        except requests.exceptions.ConnectionError as e:
            logger.warning(
                "Attempt %d/%d: Connection Error for %s: %s",
                attempt + 1,
                max_retries,
                url,
                e,
            )
        except requests.exceptions.Timeout as e:
            logger.warning(
                "Attempt %d/%d: Timeout for %s: %s",
                attempt + 1,
                max_retries,
                url,
                e,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(
                "Attempt %d/%d: Request Error for %s: %s",
                attempt + 1,
                max_retries,
                url,
                e,
            )
        except json.JSONDecodeError:
            logger.warning(
                "Attempt %d/%d: Response data for %s are not valid JSON.",
                attempt + 1,
                max_retries,
                url,
            )
            logger.debug("Response content: %s...", response.text[:200])

        # Waiting for another response if we are not in last attempt
        if attempt < max_retries - 1:
            logger.info("Waiting %f s before another attempt.", delay)
            time.sleep(delay)
        else:
            logger.error("Downloading data was unsuccessful")
            return None  # All attempt failure


# -- Saving Function --
def save_to_json(data, filename, directory) -> json:
    """Save python data (dict/list) to JSON file."""

    if data is None:
        logger.warning("No data to save to %s.", filename)
        return

    file_path = os.path.join(directory, filename)
    logger.info("Saving data to JSON file %s", file_path)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info("Data successfully saved to %s.\n", file_path)

    except IOError as e:
        logger.error("Error during writing to file %s: %s", file_path, e)
    except TypeError as e:
        logger.error("Error during data serialization to JSON for %s: %s", file_path, e)


if __name__ == "__main__":
    # basic logging for separate module testing
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    )

    # Working on each defined endpoint
    for name, url in API_ENDPOINTS_TEST.items():
        # 1. Extraction
        extracted_data = fetch_from_api(url)

        # Skipping current endpoing if extraction failed
        if extracted_data is None:
            logger.warning(
                "Skipping another steps for %s due to error durin extraction.", name
            )
            continue

        # File name is derived from endpoint name
        json_filename = f"{name}_data.json"

        # 2. Saving to JSON File
        save_to_json(extracted_data, json_filename, config.DATA_DIR)
