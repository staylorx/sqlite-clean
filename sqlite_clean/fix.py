"""
sqlite-clean fixes - Applying fixes for SQLite databases.
"""

import logging
import os
import sqlite3
from typing import Optional, Tuple, Union

from sqlalchemy.engine.base import Engine

from sqlite_clean.constants import LIKE_NULLS
from sqlite_clean.lint import contains_str_like_null
from sqlite_clean.utils import collect_columns, engine_from_str

logger = logging.getLogger(__name__)


def update_columns_to_nullable(
    sql_engine: Union[str, Engine],
    dest_path: Optional[str] = None,
    table_name: Optional[str] = None,
    inplace: bool = True,
) -> Engine:
    """
    Update SQLite database columns to nullable where appropriate.
    Use a backup database to avoid data corruption issues and
    roughly follow 9-step procedure outlined by SQLite docs here:
    https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes

    Special notes:
    - We take advantage of Python >= 3.7 sqlite3 api backup capabilities
    to keep to a standard implementation for backup portion of this work.

    Parameters
    ----------
    sql_engine: str | sqlalchemy.engine.base.Engine
        filename of the SQLite database or existing sqlalchemy engine
    dest_path: str
        the destination of the updated database with nullable columns, by default None
    table_name: str
        optional specific table name to update within database, by default None
    inplace: bool
        whether to replace the source sql database, by default True

    Returns
    -------
    sqlalchemy.engine.base.Engine
        A SQLAlchemy engine for the changed database
    """

    logger.info("Updating database columns to nullable for provided database.")

    # setup a source database connection
    if isinstance(sql_engine, Engine):
        # gather sqlalchemy engine url replacing incompatible strings
        src_sql_url = str(sql_engine.url).replace("sqlite:///", "")
    else:
        src_sql_url = sql_engine

    source_engine = sqlite3.connect(src_sql_url)

    # add a default destination path which is separate from our source
    if dest_path is None:
        dest_path = f"{src_sql_url}_column_update"

    # setup a destination database connection
    dest_engine = sqlite3.connect(dest_path)

    # create backup of database using sqlite3 api
    source_engine.backup(dest_engine)

    # gather schema_version for later update
    schema_version = dest_engine.execute("PRAGMA schema_version;").fetchall()[0][0]

    # gather existing table(s) sql later update
    sql_stmt = "SELECT name, sql FROM sqlite_master WHERE type = 'table'"
    if table_name is not None:
        # if we have a table name provided, target only that table for the modifications
        sql_stmt += " and UPPER(name) = UPPER(:table_name)"

    table_sql_fetch = dest_engine.execute(
        sql_stmt, {"table_name": table_name}
    ).fetchall()

    # prepare table sql with removed not null columns
    table_sql_mod = {
        table[0]: table[1].replace("NOT NULL", "") for table in table_sql_fetch
    }

    if len(table_sql_mod) > 0:
        # check that we have sql to modify

        # disallow autocommit and create cursor for transaction
        dest_engine.isolation_level = None
        cursor = dest_engine.cursor()
        try:
            # begin transaction
            cursor.execute("begin")

            # enable schema writes
            cursor.execute("PRAGMA writable_schema=ON")

            # Prepare update statement which will perform the table sql update.
            # Here we use table sqlite_master as a reference instead of sqlite_schema
            # to avoid possible issues with os/image sqlite version differences.
            # See the following for more information:
            # https://sqlite.org/schematab.html#alternative_names
            sql_stmt = """
            UPDATE sqlite_master SET sql = :modified_sql
            WHERE type = 'table' AND UPPER(name) = UPPER(:table_name);
            """
            for name, modified_sql in table_sql_mod.items():
                cursor.execute(
                    sql_stmt, {"table_name": name, "modified_sql": modified_sql}
                )
            # increment the schema version to track the change
            cursor.execute(f"PRAGMA schema_version={schema_version+1};")

            # disable schema writes
            cursor.execute("PRAGMA writable_schema=OFF")

            # check the integrity of the database as advised by SQLite docs
            if cursor.execute("PRAGMA integrity_check").fetchall()[0][0] != "ok":
                raise sqlite3.IntegrityError(
                    "Detected integrity issue within database after modifications."
                )

            # commit the changes
            cursor.execute("commit;")

        except sqlite3.Error as err:
            logger.error(err)
            cursor.execute("rollback;")

    if inplace:
        # backup our destination into the source engine, overwriting our original
        dest_engine.backup(source_engine)

    # close our connections
    source_engine.close()
    dest_engine.close()

    if inplace:
        # remove working backup
        os.remove(dest_path.replace("sqlite:///", ""))

        # return source database
        return engine_from_str(src_sql_url)

    # return copied and modified destination database
    return engine_from_str(dest_path)


def update_values_like_null_to_null(
    sql_engine: Union[str, Engine],
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    like_nulls: Tuple[str, ...] = LIKE_NULLS,
) -> Engine:
    """
    Updates column values from 'nan' to NULL where possible.

    Parameters
    ----------
    sql_engine: str | sqlalchemy.engine.base.Engine
        filename of the SQLite database or existing sqlalchemy engine
    table_name: str
        optional specific table name to check within database, by default None
    column_name: str
        optional specific column name to check within database, by default None
    like_nulls: List[str]
        tuple strings which may represent null values

    Returns
    -------
    sqlalchemy.engine.base.Engine
        A SQLAlchemy engine for the changed database
    """
    logger.info("Updating column values with str's %s to NULL values.", like_nulls)

    # create an engine
    engine = engine_from_str(sql_engine)

    # gather columns to be used below
    columns = collect_columns(engine, table_name, column_name)

    # strings which are like nulls for later use in below SQL 'in'
    like_nulls_str_list = ",".join([f"'{x}'" for x in like_nulls])

    with engine.begin() as connection:
        for col in columns:
            # sql to update nan strings to sqlite nulls
            connection.execute(
                f"""
                UPDATE {col["table_name"]} SET {col["column_name"]}=NULL
                WHERE LOWER({col["column_name"]}) IN ({like_nulls_str_list})
                AND EXISTS(SELECT 1 FROM {col["table_name"]}
                    WHERE LOWER({col["column_name"]}) IN ({like_nulls_str_list})
                )
                """
            )  # nosec

    return engine


def clean_like_nulls(
    sql_engine: Union[str, Engine],
    dest_path: Optional[str] = None,
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    inplace: bool = True,
) -> Engine:
    """
    Updates column values from 'nan' to NULL, performing necessary
    database schema updates where necessary.

    Parameters
    ----------
    sql_engine: str | sqlalchemy.engine.base.Engine
        filename of the SQLite database or existing sqlalchemy engine
        dest_path: str
        the destination of the updated database with nullable columns, by default None
    table_name: str
        optional specific table name to check within database, by default None
    column_name: str
        optional specific column name to check within database, by default None
    inplace: bool
        whether to replace the source sql database, by default True

    Returns
    -------
    sqlalchemy.engine.base.Engine
        A SQLAlchemy engine for the database
    """

    logger.info(
        (
            "Updating column values with str 'nan' to NULL values, "
            "making changes where necessary."
        )
    )

    # if we detect that there are strings like nulls in the database
    if contains_str_like_null(sql_engine, table_name, column_name):

        # if we have at least one not-nullable column we must update the database
        # to allow for null values in those columns. Note: 1=True for notnull.
        if 1 in [
            col["notnull"]
            for col in collect_columns(sql_engine, table_name, column_name)
        ]:
            # perform the schema update
            sql_engine = update_columns_to_nullable(
                sql_engine, dest_path, table_name, inplace
            )

        # update the like nulls to actual null
        sql_engine = update_values_like_null_to_null(
            sql_engine, table_name, column_name
        )

    # return the sql engine
    return sql_engine
