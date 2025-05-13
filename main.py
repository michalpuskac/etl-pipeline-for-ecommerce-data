"""Main orchestration module for other modules of ETL pipeline"""

# Import modules and functions
import json
import logging
import os

import config
from src.logging_setup import setup_logging
from src.extract import fetch_from_api, save_to_json
from src.transform import (
    convert_list_to_dataframe,
    transform_carts,
    transform_products,
    transform_users,
)
from src.load import create_db_engine, load_dataframe_to_db, apply_ddl_script


setup_logging()
logger = logging.getLogger(__name__)


# --- Main Pipeline Function ---
def run_pipeline():
    """Run pipeline for extraction tranformation and loading data."""
    logger.info("%s S T A R T   E T L   P I P E L I N E %s", "=" * 20, "=" * 20)

    logger.info("=== Database schema setup ===")
    engine = create_db_engine(config.DB_CONNECTION_STRING)

    if not engine:
        logger.critical("Failed to create database engine. Halting pipeline.")
        return

    ddl_file_name = ""
    if config.DB_TYPE == "mssql":
        ddl_file_name = "schema_mssql_ddl.sql"
    elif config.DB_TYPE == "postgresql":
        ddl_file_name = "schema_postgresql_ddl.sql"
    elif config.DB_TYPE == "sqlite":
        ddl_file_name = "schema_sqlite_ddl.sql"

    if ddl_file_name:
        ddl_script_path = os.path.join(config.SQL_DIR, ddl_file_name)

        if not os.path.exists(ddl_script_path):
            logger.error(
                "DDL script file not found at: %s. Halting pipeline.", ddl_script_path
            )
            return

        try:
            apply_ddl_script(engine, ddl_script_path)
            logger.info(
                "Database schema from '%s' applied successfully.", ddl_file_name
            )
        except Exception as e:
            logger.critical(
                "Could not apply DDL schema from '%s'. Halting pipeline. Error: %s",
                ddl_file_name,
                e,
                exc_info=True,
            )
            return
    else:
        logger.warning(
            "No DDL script defined for DB_TYPE: %s."
            "Proceeding without DDL application.",
            config.DB_TYPE,
        )

    # === PART 1: EXTRACT ===
    logger.info("- - -  E X T R A C T I O N  - - -\n")
    extracted_files = {}  # Dictionary for saving paths to created files
    for name, url in config.API_ENDPOINTS.items():
        # Calling function from extract.py
        raw_data = fetch_from_api(url)
        if raw_data:
            json_filename = f"{name}_data.json"
            file_path = os.path.join(config.DATA_DIR, json_filename)
            # Calling function from extract.py
            save_to_json(raw_data, json_filename, config.DATA_DIR)
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
            df_cleaned = None  # Initialize df_cleaned
            if name == "users":
                df_cleaned_users = transform_users(df_raw)
                if df_cleaned_users is not None:
                    cleaned_dataframes["users"] = df_cleaned_users
            elif name == "products":
                df_cleaned_products = transform_products(df_raw)
                if df_cleaned_products is not None:
                    cleaned_dataframes["products"] = df_cleaned_products
            elif name == "carts":
                carts_df, items_df = transform_carts(df_raw)
                if carts_df is not None:
                    cleaned_dataframes["carts"] = carts_df
                if items_df is not None:
                    cleaned_dataframes["cart_items"] = items_df

            # Log shapes after transformations
            if name == "users" and "users" in cleaned_dataframes:
                logger.info(
                    "Transformation of 'users' finished. Shape: %s\n",
                    cleaned_dataframes["users"].shape,
                )
            elif name == "products" and "products" in cleaned_dataframes:
                logger.info(
                    "Transformation of 'products' finished. Shape: %s\n",
                    cleaned_dataframes["products"].shape,
                )
            elif name == "carts":
                if "carts" in cleaned_dataframes:
                    logger.info(
                        "Transformation of 'carts' finished. Shape: %s\n",
                        cleaned_dataframes["carts"].shape,
                    )
                if "cart_items" in cleaned_dataframes:
                    logger.info(
                        "Transformation of 'cart_items' finished. Shape: %s\n",
                        cleaned_dataframes["cart_items"].shape,
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
    elif not engine:  # Check if engine was created
        logger.error("Database engine not available. Skipping load phase.")
    else:
        load_order = ["users", "products", "carts", "cart_items"]
        # schema for SQLite should be none 
        schema_to_load = config.TARGET_DB_SCHEMA if config.DB_TYPE not in ['sqlite'] else None

        for simple_table_name in load_order:
            if simple_table_name in cleaned_dataframes:
                df_to_load = cleaned_dataframes[simple_table_name]

                logger.info(f"Loading DataFrame '{simple_table_name}' into SQL table "
                            f"'{schema_to_load + '.' if schema_to_load else ''}{simple_table_name}'...")

                load_dataframe_to_db(
                    df=df_to_load,
                    table_name=simple_table_name,
                    engine=engine,
                    schema_name=schema_to_load,
                    if_exists="append",
                )
            else:
                logger.warning(
                    "DataFrame for key '%s' not found in cleaned_dataframes. Skipping.",
                    simple_table_name,
                )
        logger.info("Load phase completed.")

    logger.info("%s E N D   E T L   P I P E L I N E %s", "=" * 20, "=" * 20)


# --- Run the pipeline ---
if __name__ == "__main__":
    if not os.path.isdir(config.SQL_DIR):
        logger.warning(
            "SQL directory not found at: %s. DDL scripts might not be loaded."
            "Creating it.",
            config.SQL_DIR,
        )
        try:
            os.makedirs(config.SQL_DIR, exist_ok=True)
        except OSError as e:
            logger.error("Could not create SQL directory %s: %s", config.SQL_DIR, e)

    run_pipeline()
