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
        print(f"CHYBA: Nepodařilo se nastavit logování - {e}")
        # You can use the basic basicConfig here as an emergency solution
        logging.basicConfig(level=logging.WARNING) 
        logging.error("Logování nebylo správně nakonfigurováno!", exc_info=True)


# Vysvětlení logging_setup.py:

# Importuje potřebné moduly a hlavně config.
# Funkce setup_logging():
# Zajistí existenci adresáře pro logy (logs/).
# Zavolá logging.config.dictConfig() a předá jí slovník LOGGING_CONFIG z config.py. Tím se aplikuje celé nastavení (formáty, handlery, úrovně).
# Přidá jednoduchou zprávu, že logování bylo nastaveno.
# Obsahuje základní try...except pro případ, že by konfigurace selhala.