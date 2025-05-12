"""Module for loading data to sql database using SQLAlchemu DB engine"""

import logging

import pandas as pd
from sqlalchemy import create_engine, exc, text

logger = logging.getLogger(__name__)


def create_db_engine(connection_string: str):
    """Create and return SQLAlchemy database engine"""
    try:
        engine = create_engine(connection_string)
        # test connection
        with engine.connect() as connection:
            logger.info(
                "Database engine and test connection successfully created: %s.",
                {
                    (
                        connection_string.split("@")[-1]
                        if "@" in connection_string
                        else connection_string
                    )
                },
            )
            return engine
    except exc.SQLAlchemyError as e:
        logger.error(
            "Error, creation of database engine or connection failed: %s",
            e,
            exc_info=True,
        )
        return None
    except Exception as e:
        logger.error(
            "Unexpected error, creation of database engine or connection failed: %d",
            e,
            exc_info=True,
        )
        return None


def load_dataframe_to_db(
    df: pd.DataFrame,
    table_name: str,
    engine,
    if_exists: str = "replace",
    chunksize: int = 1000,
):
    """Load pandas DataFrame to sql table"""
    if df is None or df.empty:
        logger.warning(
            "DataFrame for table '%s' is empty or None. Loading skipped.", table_name
        )
        return
    try:
        logger.info(
            "Loading to table '%s' (if_exists='%s'). DataFrame shape: %s",
            table_name,
            if_exists,
            df.shape,
        )
        df.to_sql(
            table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=chunksize,
        )
        logger.info(
            "Data successfully loaded to table '%s'. Number of loaded rows: %d",
            table_name,
            len(df),
        )
    except exc.SQLAlchemyError as e:
        logger.error(
            "SQLAlchemy error when uploading data to the table  '%s': %s",
            table_name,
            e,
            exc_info=True,
        )
    except Exception as e:
        logger.error(
            "Unexpected error when uploading data to the table '%s': %s",
            table_name,
            e,
            exc_info=True,
        )
