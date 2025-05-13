"""Module for loading data to sql database using SQLAlchemu DB engine"""

import logging
import pandas as pd
from sqlalchemy import create_engine, exc, text
import re

logger = logging.getLogger(__name__)


def apply_ddl_script(engine, ddl_file_path: str):
    """
    Reads a DDL script from a file and executes its statements against the database.
    Handles MSSQL 'GO' statements by splitting the script.
    Args:
        engine: SQLAlchemy engine instance.
        ddl_file_path (str): Absolute path to the .sql DDL script file.
    """
    logger.info("Applying DDL script from: %s", ddl_file_path)
    try:
        with open(ddl_file_path, "r", encoding="utf-8") as f:
            full_script = f.read()

        db_dialect_name = engine.dialect.name
        logger.info("Detected DB dialect: %s",db_dialect_name)

        sql_commands = []
        if db_dialect_name == "mssql":
            batches = re.split(r'^\s*GO\s*$', full_script, flags=re.MULTILINE | re.IGNORECASE)
            for batch in batches:
                batch = batch.strip()
                if batch:
                    sql_commands.append(batch)

        else:  # For PostgreSQL and SQLite
            commands_with_comments_removed = []
            # Remove block comments
            script_no_block_comments = re.sub(r'/\*.*?\*/', '', full_script, flags=re.MULTILINE | re.IGNORECASE)
            # Remove full-line comments
            lines_no_full_comments = []
            for line in script_no_block_comments.splitlines():
                stripped_line = line.split("--", 1)[0].strip()
                if stripped_line:
                    lines_no_full_comments.append(stripped_line) 

            # Filter out empty strings, handling multiline statements
            script_for_splitting = " ".join(lines_no_full_comments)
            # Split by semicolon
            sql_commands = [
                cmd.strip()
                for cmd in "".join(script_for_splitting).split(";")
                if cmd.strip()
            ]

        if not sql_commands:
            logger.warning("No SQL commands found in DDL file: %s", ddl_file_path)
            return

        with engine.connect() as connection:
            for command_index, command in enumerate(sql_commands):
                if command:
                    try:
                        logger.debug(
                            "Executing DDL command #%s: %s}...",
                            command_index + 1,
                            command[:200],
                        )
                        connection.execute(text(command))
                        logger.info("Successfully executed DDL command #%s.", command_index + 1)
                    except Exception as cmd_exc:
                        logger.error(
                            "Error executing DDL command #%s: %s... Error: %s",
                            command_index + 1,
                            command[:200],
                            cmd_exc,
                            exc_info=True,
                        )
                        raise

            try:
                connection.commit()
                logger.info(
                    "DDL script '%s' applied successfully and transaction committed.",
                    ddl_file_path,
                )
            except Exception as cmd_exc:
                logger.error(
                    "Error committing DDL transaction for '%s': %s",
                    ddl_file_path,
                    cmd_exc,
                    exc_info=True,
                )
                raise

    except FileNotFoundError:
        logger.error("DDL script file not found: %s", ddl_file_path)
        raise
    except Exception as e:
        logger.error(
            "Failed to apply DDL script from %s: %s", ddl_file_path, e, exc_info=True
        )
        raise


def create_db_engine(connection_string: str):
    """Create and return SQLAlchemy database engine"""
    if not connection_string:
        logger.error(
            "Database connection string is not provided. Cannot create engine."
        )
        return None
    try:
        engine = create_engine(connection_string)
        # Test connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            db_identifier = (
                connection_string.split("@")[-1]
                if "@" in connection_string
                else connection_string.split("///")[-1]
            )
            logger.info(
                "Database engine successfully created and test connection established to: %s",
                db_identifier,
            )
            return engine

    except exc.SQLAlchemyError as e:
        logger.error(
            "SQLAlchemy error during database engine creation or connection test for '%s...': %s",
            connection_string[:30],
            e,
            exc_info=True,
        )
        return None
    except Exception as e:
        logger.error(
            "Unexpected error during database engine creation for '%s...': %s",
            connection_string[:30],
            e,
            exc_info=True,
        )
        return None


def load_dataframe_to_db(
    df: pd.DataFrame,
    table_name: str,
    engine,
    schema_name: str = None,
    if_exists: str = "append",
    chunksize: int = 1000,
):
    """Load pandas DataFrame to sql table"""
    if engine is None:
        logger.error(
            "Database engine is not available. Cannot load data to table '%s'.",
            table_name,
        )
        return
    if df is None or df.empty:
        logger.warning(
            "DataFrame for table '%s%s' is empty or None.",
            schema_name + "." if schema_name else "",
            table_name,
        )
        return

    full_table_name_for_log = f"{schema_name + '.' if schema_name else ''}{table_name}"
    qualified_table_name_for_mssql = f"{schema_name}.{table_name}" if schema_name else table_name

    try:
        logger.info(
            "Loading data into table '%s' (if_exists='%s'). DataFrame shape: %s",
            full_table_name_for_log,
            if_exists,
            df.shape,
        )
        # MSSQL specific: Handle IDENTITY_INSERT
        is_mssql = engine.dialect.name == "mssql"
        # Tables where the DataFrame provides the ID that is an IDENTITY column in MSSQL DDL
        tables_requiring_identity_insert_on = ["users", "products", "carts"] 

        if is_mssql and table_name in tables_requiring_identity_insert_on:
            with engine.connect() as connection:
                try:
                    logger.debug("Attempting to SET IDENTITY_INSERT %s ON",
                                qualified_table_name_for_mssql
                    )
                    sql_identity_on = f"SET IDENTITY_INSERT {qualified_table_name_for_mssql} ON;"
                    connection.execute(text(sql_identity_on))
                    connection.commit() # Commit this SET statement

                    df.to_sql(
                        name=table_name,
                        con=connection, 
                        schema=schema_name,
                        if_exists=if_exists,
                        index=False,
                        chunksize=chunksize,
                    )

                    logger.debug("Attempting to SET IDENTITY_INSERT %s OFF",
                                qualified_table_name_for_mssql
                    )
                    sql_identity_off = f"SET IDENTITY_INSERT {qualified_table_name_for_mssql} OFF;"
                    connection.execute(text(sql_identity_off))
                    connection.commit() # Commit this SET statement

                except Exception as e_identity:
                    logger.error("Error during MSSQL IDENTITY_INSERT handling for %s: %s",
                                qualified_table_name_for_mssql,
                                e_identity,
                                exc_info=True
                    )
                    connection.rollback() # Rollback if any part of identity insert handling fails
                    raise 

        else:
        # For other databases (PostgreSQL, SQLite)
            df.to_sql(
                name=table_name,
                con=engine, # Use engine directly for other DBs
                schema=schema_name,
                if_exists=if_exists,
                index=False,
                chunksize=chunksize,
            )

        logger.info(
            "Data successfully loaded to table '%s'. Number of loaded rows: %d",
            full_table_name_for_log,
            len(df),
        )
    except exc.SQLAlchemyError as e:
        logger.error(
            "SQLAlchemy error when uploading data to the table  '%s': %s",
            full_table_name_for_log,
            e,
            exc_info=True,
        )
    except Exception as e:
        logger.error(
            "Unexpected error when uploading data to the table '%s': %s",
            full_table_name_for_log,
            e,
            exc_info=True,
        )