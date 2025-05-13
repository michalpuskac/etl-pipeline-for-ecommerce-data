"""Main orchestration module for other modules of ETL pipeline"""

# Import modules and functions
import json
import logging
import os

import config
from src.extract import fetch_from_api, save_to_json
from src.load import create_db_engine, load_dataframe_to_db
from src.logging_setup import setup_logging  # Import setup function
from src.transform import (convert_list_to_dataframe, transform_carts,
                           transform_products, transform_users)

setup_logging()

# Logger for main.py
logger = logging.getLogger(__name__)


# --- 2. Additional configuration load ---
API_ENDPOINTS = config.API_ENDPOINTS
RAW_DATA_DIR = config.DATA_DIR
BASE_DIR = config.BASE_DIR


# --- 3. Main Pipeline Function ---
def run_pipeline():
    """Run pipeline for extraction tranformation and loading data."""
    logger.info("=" * 20 + " S T A R T   E T L   P I P E L I N E " + "=" * 20)

    # === PART 1: EXTRACT ===
    logger.info("- - -  E X T R A C T I O N  - - -\n")
    extracted_files = {}  # Dictionary for saving paths to created files
    for name, url in API_ENDPOINTS.items():
        # Calling function from extract.py
        raw_data = fetch_from_api(url)
        if raw_data:
            json_filename = f"{name}_data.json"
            file_path = os.path.join(RAW_DATA_DIR, json_filename)
            # Calling function from extract.py
            save_to_json(raw_data, json_filename, RAW_DATA_DIR)
            extracted_files[name] = file_path  # Save path for next step
        else:
            logger.warning("Extraction of %s failed,  skipping current endpoint.", name)
            extracted_files[name] = None

    # === PART 2: TRANSFORM ===
    logger.info("- - -  T R A N S F O R M A T I O N  - - -\n")
    cleaned_dataframes = {}  # Dictionary for saving DataFrames
    for name, file_path in extracted_files.items():
        if file_path is None:
            logger.warning("Skipping transformation of %s (Extraction failed).", name)
            continue

        logger.info("Data tranformation of %s from file %s", name, file_path)
        try:
            # Loading data from JSON file
            with open(file_path, "r", encoding="utf-8") as f:
                full_data = json.load(f)

            # Getting relevant list od data (specific for dummyjson)
            # Using endpoint name as key (users, products, carts)
            data_list = full_data.get(name, [])
            if not data_list:
                logger.warning(
                    "In file %s data not found under key '%s'.", file_path, name
                )
                continue

            # Conversion to DataFrame (function from transform.py)
            df_raw = convert_list_to_dataframe(data_list, name)
            if df_raw is None:
                logger.error("Data conversion of %s to DataFrame failed.", name)
                continue

            # Aplication of specific transformation (function from transform.py)
            df_cleaned = None
            if name == "users":
                df_cleaned = transform_users(df_raw)
                if df_cleaned is not None:
                    cleaned_dataframes["users"] = df_cleaned  # Save result
                    logger.info(
                        "Transformation of 'users' finished. Shape: %s\n",
                        df_cleaned.shape,
                    )
            elif name == "products":
                df_cleaned = transform_products(df_raw)
                if df_cleaned is not None:
                    cleaned_dataframes["products"] = df_cleaned
                    logger.info(
                        "Transformation of 'products' finished. Shape: %s\n",
                        df_cleaned.shape,
                    )
            elif name == "carts":
                carts_df, items_df = transform_carts(df_raw)
                if carts_df is not None:
                    cleaned_dataframes["carts"] = carts_df  # Uložíme oba výsledky
                    logger.info(
                        "Transformation of 'carts' finished. Shape: %s", carts_df.shape
                    )
                if items_df is not None:
                    cleaned_dataframes["cart_items"] = items_df  # Použijeme jiný klíč
                    logger.info(
                        "Transformation of 'cart_items' finished. Shape: %s",
                        items_df.shape,
                    )
            else:
                logger.warning(
                    "Pro %s Specific transform function is not defined.", name
                )

        except Exception as e:
            # Detailed log with traceback
            logger.error(
                "Unexpected error during transformation for %s: %s",
                name,
                e,
                exc_info=True,
            )
    logger.info(
        "Transformation finneshed. DataFrames ready: %s\n",
        list(cleaned_dataframes.keys()),
    )

    # === PART 3: LOAD ===
    logger.info("- - -   L o a d   - - -\n")
    if not cleaned_dataframes:
        logger.warning("No transformed DataFrames for loading. Skipping load...")
    else:
        # Create Database engine
        logger.info("Connecting to database: %s", config.DB_CONNECTION_STRING)
        engine = create_db_engine(config.DB_CONNECTION_STRING)

        if engine:
            load_order = ["users", "products", "carts", "cart_items"]

            for table_key_name in load_order:
                if table_key_name in cleaned_dataframes:
                    df_to_load = cleaned_dataframes[table_key_name]
                    sql_table_name = table_key_name
                    load_dataframe_to_db(
                        df_to_load, sql_table_name, engine, if_exists="replace"
                    )
                else:
                    logger.warning(
                        "DataFrame for key '%s can not be found in cleaned_dataframes.",
                        table_key_name,
                    )
            logger.info("Loading Completed.")
        else:
            logger.error("Database engine not created. Load can not continue.")

    logger.info("=" * 20 + " E N D   E T L   P I P E L I N E " + "=" * 20)


# --- Run the pipeline ---
if __name__ == "__main__":
    run_pipeline()
