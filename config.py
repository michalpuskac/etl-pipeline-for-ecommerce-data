"""Module providing configuration for project.
Ssuch as dir route, API configuration, logging configuration and database configuration
"""

import os

from dotenv import load_dotenv

# --- Load variables from .env file
PROJECT_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DOTENV_PATH = os.path.join(PROJECT_ROOT_DIR, ".env")

if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
    print(f"INFO: Variables from .env successfully loaded {DOTENV_PATH}")
else:
    print(
        f"INFO: .env file could not be found, {DOTENV_PATH}."
        "Default values or system environment variables are used."
    )

# --- Base project Configuration ---
BASE_DIR = PROJECT_ROOT_DIR
# route to folder for data saving
DATA_DIR = os.path.join(BASE_DIR, "data")
# route to folder for log files
LOG_DIR = os.path.join(BASE_DIR, "logs")
# create folder "data" if not exists
os.makedirs(DATA_DIR, exist_ok=True)

# -- API configuration --
API_ENDPOINTS = {
    "users": "https://dummyjson.com/users?limit=1000",
    "products": "https://dummyjson.com/products?limit=1000",
    "carts": "https://dummyjson.com/cart?limit=1000",
}

# --- Logging Configuration ---
LOG_FILE_PATH = os.path.join(LOG_DIR, "etl_pipeline.log")
LOGGING_CONFIG = {
    "version": 1,  # Version of schema config
    "disable_existing_loggers": False,  # Keep existing loggers
    # Format of logs
    "formatters": {
        "standard": {
            # basic format for console
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            # Detailed format for file
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(module)s - "
            "%(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    # Handlers (where logs should be send)
    "handlers": {
        "console": {  # dict for console handler
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {  # dict for file handler
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "detailed",
        },
    },
    # Root logger (setting for all loggers, in case of tey has not own setting)
    "root": {
        "level": "DEBUG",  # Lowest level which we want to catch
        "handlers": ["console", "file"],  # Sending logs to both handlers
    },
}

# --- Database Configuration ---
DB_TYPE = os.getenv("ETL_DB_TYPE", "sqlite").lower()
DB_CONNECTION_STRING = None

print(f"INFO: Chosen database type (ETL_DB_TYPE): {DB_TYPE}")

if DB_TYPE == "sqlite":
    # For SQLite database,  file name is used from .env or default
    sqlite_filename = os.getenv("SQLITE_DB_FILENAME", "ecommerce_pipeline_default.db")
    db_path = os.path.join(DATA_DIR, sqlite_filename)
    DB_CONNECTION_STRING = f"sqlite:///{db_path}"
    print(f"INFO: SQLite databáze in: {db_path}")

elif DB_TYPE == "postgresql":
    db_user = os.getenv("PG_DB_USER")
    db_password = os.getenv("PG_DB_PASSWORD")
    db_host = os.getenv("PG_DB_HOST", "localhost")
    db_port = os.getenv("PG_DB_PORT", "5432")
    db_name = os.getenv("PG_DB_NAME")

    if not all([db_user, db_password, db_name]):
        print(
            "WARNING: All necessary environment variables (EPG_DB_USER, PG_DB_PASSWORD,"
            "PG_DB_NAME) are not set for PostgreSQL in .env file."
            "Pipeline may not work properly."
        )
        DB_CONNECTION_STRING = None
    else:
        DB_CONNECTION_STRING = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        print(
            f"INFO: Connectiong to PostgreSQL: user={db_user}, host={db_host},"
            "port={db_port}, dbname={db_name}"
        )

elif DB_TYPE == "mssql":
    db_user = os.getenv("MSSQL_DB_USER")
    db_password = os.getenv("MSSQL_DB_PASSWORD")
    db_host = os.getenv("MSSQL_DB_HOST")
    db_port = os.getenv("MSSQL_DB_PORT", "1433")
    db_name = os.getenv("MSSQL_DB_NAME")
    odbc_driver = os.getenv(
        "MSSQL_DB_ODBC_DRIVER", "ODBC Driver 17 for SQL Server"
    ).replace(" ", "+")

    if not all([db_user, db_password, db_host, db_name]):
        print(
            "WARNING: All necessary environment variables (MSSQL_DB_USER, MSSQL_DB_PASSWORD,"
            "MSSQL_DB_HOST, MSSQL_DB_NAME) are not set for MSSQL in .env file."
            "Pipeline may not work properly."
        )
        DB_CONNECTION_STRING = None
    else:
        DB_CONNECTION_STRING = f"mssql+pyodbc://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?driver={odbc_driver}"
        print(
            f"INFO: Connecting to MSSQL: user={db_user}, host={db_host},"
            "port={db_port}, dbname={db_name}, driver={odbc_driver.replace('+', ' ')}"
        )
else:
    print(
        f"Error: Unknown DB_TYPE '{DB_TYPE}' set in ETL_DB_TYPE."
        "Pipeline can not continue in database configuration."
    )
    # Fallback to sqlite in case of Unknown database
    print("INFO: Setting default fallback SQLite configuration.")
    sqlite_filename_fallback = "ecommerce_pipeline_fallback.db"
    db_path_fallback = os.path.join(DATA_DIR, sqlite_filename_fallback)
    DB_CONNECTION_STRING = f"sqlite:///{db_path_fallback}"
    DB_TYPE = "sqlite"

if DB_CONNECTION_STRING:
    # Short print of connection string for log,(hide password)
    safe_conn_str_display = DB_CONNECTION_STRING
    if "@" in safe_conn_str_display and ":" in safe_conn_str_display.split("@")[0]:
        user_pass, rest = safe_conn_str_display.split("://")[1].split("@", 1)
        user = user_pass.split(":")[0]
        safe_conn_str_display = (
            f"{safe_conn_str_display.split('://')[0]}://{user}:********@{rest}"
        )

    print(
        f"INFO: Final DB_CONNECTION_STRING (safety shortened): {safe_conn_str_display}"
    )
else:
    print(
        f"Error: DB_CONNECTION_STRING can not be successfully created for DB_TYPE: {DB_TYPE}."
        "Check the configuration and environment variables."
    )
