# logging_setup.py
import logging
import logging.config
import os
import config

def setup_logging():
    """
    Set logging for app with logging configuration from config.py.
    Creates the log directory if it does not exist.
    """
    try:
        # 1. Creating log directory
        log_dir = config.LOG_DIR
        os.makedirs(log_dir, exist_ok=True)
        
        # 2. Load and apply dictionary configuration
        logging.config.dictConfig(config.LOGGING_CONFIG)
        
        # 3. Log message about successful setup
        # We get a logger for this setup module
        logger = logging.getLogger(__name__) 
        logger.info("Logging successfully set.") 
        # You will see this message if the root logger is set to INFO or DEBUG

    except Exception as e:
        # Basic dump if the logging configuration fails
        print(f"Error: Logging could not be setup - {e}")
        # You can use the basic basicConfig here as an emergency solution
        logging.basicConfig(level=logging.WARNING) 
        logging.error("Logging was not configured correctly", exc_info=True)