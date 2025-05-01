import logging # No need for call logging.config, if setup function is called
import config
from src.logging_setup import setup_logging # Import setup function

setup_logging() 

# Logger for main.py
logger = logging.getLogger(__name__)

# Import modules and functions
from src.extract import fetch_from_api, save_to_json
from src.transform import (convert_list_to_dataframe,
                        transform_users,
                        transform_products,
                        transform_carts
)
# from src.load import load_to_sql # Později
import json
import os

# --- 2. Additional configuration load ---
API_ENDPOINTS = config.API_ENDPOINTS
RAW_DATA_DIR = config.DATA_DIR 
BASE_DIR = config.BASE_DIR

# --- 3. Main Pipeline Function ---
def run_pipeline():
    logger.info("="*20 + " S T A R T   E T L   P I P E L I N E " + "="*20)

    # === PART 1: EXTRACT ===
    logger.info("- - -  E X T R A C T I O N  - - -\n")
    extracted_files = {} # Dictionary for saving paths to created files
    for name, url in API_ENDPOINTS.items():
        # Calling function from extract.py
        raw_data = fetch_from_api(url) 
        if raw_data:
            json_filename = f"{name}_data.json"
            file_path = os.path.join(RAW_DATA_DIR, json_filename)
            # Calling function from extract.py
            save_to_json(raw_data, json_filename, RAW_DATA_DIR) 
            extracted_files[name] = file_path # Save path for next step
        else:
            logger.warning(f"Extraction of {name} failed,  skipping current endpoint.")
            extracted_files[name] = None


    # === PART 2: TRANSFORM ===
    logger.info("- - -  T R A N S F O R M A T I O N  - - -\n")
    cleaned_dataframes = {} # Dictionary for saving DataFrames
    for name, file_path in extracted_files.items():
        if file_path is None:
            logger.warning(f"Skipping transformation of {name} (Extraction failed).")
            continue

        logger.info(f"Data tranformation of {name} from file {file_path}")
        try:
            # Loading data from JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                full_data = json.load(f)

            # Getting relevant list od data (specific for dummyjson)
            # Using endpoint name as key (users, products, carts)
            data_list = full_data.get(name, [])
            if not data_list:
                logger.warning(f"In file {file_path} data not found under key '{name}'.")
                continue

            # Conversion to DataFrame (function from transform.py)
            df_raw = convert_list_to_dataframe(data_list, name)
            if df_raw is None:
                logger.error(f"Data conversion of {name} to DataFrame failed.")
                continue

            # Aplication of specific transformation (function from transform.py)
            df_cleaned = None
            if name == "users":
                df_cleaned = transform_users(df_raw) 
                if df_cleaned is not None:
                    cleaned_dataframes['users'] = df_cleaned # Save result
                    logger.info(f"Transformation of 'users' finished. Shape: {df_cleaned.shape}\n")
            elif name == "products":
                df_cleaned = transform_products(df_raw) 
                if df_cleaned is not None:
                    cleaned_dataframes['products'] = df_cleaned
                    logger.info(f"Transformation of 'products' finished. Shape: {df_cleaned.shape}\n")
            elif name == "carts":
                carts_df, items_df = transform_carts(df_raw) 
                if carts_df is not None:
                    cleaned_dataframes['carts'] = carts_df # Uložíme oba výsledky
                    logger.info(f"Transformation of 'carts' finished. Shape: {carts_df.shape}")
                if items_df is not None:
                    cleaned_dataframes['cart_items'] = items_df # Použijeme jiný klíč
                    logger.info(f"Transformation of 'cart_items' finished. Shape: {items_df.shape}")
            else:
                logger.warning(f"Pro {name} Specific transform function is not defined.")

        except Exception as e:
            # Detailed log with traceback
            logger.error(f"Unexpected error during transformation for {name}: {e}", exc_info=True) 
    logger.info(f"Transformation finneshed. DataFrames ready: {list(cleaned_dataframes.keys())}\n")

    
    
    
    # === PART 3: LOAD ===
    logger.info("- - -   L o a d  (Placeholder)  - - -\n")






    # logger.info("="*20 + " E N D   E T L   P I P E L I N E " + "="*20)


# --- Run the pipeline ---
if __name__ == "__main__":
    run_pipeline()