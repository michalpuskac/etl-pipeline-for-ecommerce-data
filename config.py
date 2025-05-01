import os 
import logging

# --- Base project Configuration ---

# Spolehlivé určení kořenového adresáře projektu
# __file__ is route to this config.py file
# os.path.dirname(__file__) is the directory where config.py is (i.e. the root of the project)
# os.path.abspath will provide an absolute path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# route to folder for data saving 
DATA_DIR = os.path.join(BASE_DIR, "data")
# route to folder for log files
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
# create folder "data" if not exists
os.makedirs(DATA_DIR, exist_ok=True)

# -- API configuration -- 
API_ENDPOINTS = {
    "users": "https://dummyjson.com/users?limit=1000",
    "products": "https://dummyjson.com/products?limit=1000",
    "carts": "https://dummyjson.com/cart?limit=1000"
}

# --- Logging Configuration (for logging.config.dictConfig) ---

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
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    # Handlers (where logs should be send)
    "handlers": {
        "console": {  # Slovník pro console handler
            "level": "INFO",       
            "class": "logging.StreamHandler",
            "formatter": "standard", 
            "stream": "ext://sys.stdout" # Správné umístění streamu
        }, # Uzavírací závorka pro console handler
        "file": {     # Slovník pro file handler
            "level": "DEBUG",      
            "class": "logging.handlers.RotatingFileHandler", 
            "filename": LOG_FILE_PATH, 
            "maxBytes": 1024*1024*5, 
            "backupCount": 3,       
            "encoding": "utf-8",    
            "formatter": "detailed", 
        },
    },

    # Root logger (setting for all loggers, in case of tey has not own setting)
    "root": {
        "level": "DEBUG", # Lowest level which we want to catch
        "handlers": ["console", "file"], # Sending logs to both handlers
    },
    }

# --- Konfigurace Databáze (Placeholder) ---
# DB_CONNECTION_STRING = "sqlite:///path/to/your/database.db" 
# DB_CONNECTION_STRING = "postgresql://user:password@host:port/database"