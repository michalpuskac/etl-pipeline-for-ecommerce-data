"""Module for configuration of logging logic"""

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
        # Creating log directory
        log_dir = config.LOG_DIR
        os.makedirs(log_dir, exist_ok=True)

        # Load and apply dictionary configuration
        logging.config.dictConfig(config.LOGGING_CONFIG)

        # Log message about successful setup
        # We get a logger for this setup module
        logger = logging.getLogger(__name__)
        logger.info("Logging successfully set.")
        # You will see this message if the root logger is set to INFO or DEBUG

    except Exception as e:
        # Fallback in case of any unexpected logging setup failure
        print(f"Error: Logging could not be setup - {e}")
        # use of basic basicConfig here as an emergency solution
        logging.basicConfig(level=logging.WARNING)
        logging.error("Logging was not configured correctly", exc_info=True)
