"""
sqlite-clean command - provides command-line functionality wrappers
"""

from typing import Optional, Tuple

import click

from sqlite_clean.catalog import SQLITE_CLEAN_CATALOG
from sqlite_clean.constants import LIKE_NULLS


@click.command()
@click.option("--sql_engine", help="Filepath for SQLite database file.")
@click.option(
    "--table_name",
    default=None,
    help="Optional table name to focus on for linting actions.",
)
@click.option(
    "--column_name",
    default=None,
    help="Optional column name to focus on for linting actions.",
)
@click.option(
    "--like_nulls",
    default=None,
    help="Optional list of null-like values to pass in for linting actions.",
)
def lint(
    sql_engine: str,
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    like_nulls: Tuple[str, ...] = LIKE_NULLS,
):
    """
    Runs sqlite-clean linting functionality through command-line
    """
    for func in [item["ref"] for item in SQLITE_CLEAN_CATALOG["lint"]]:
        func(sql_engine, table_name, column_name, like_nulls)  # type: ignore


@click.command()
@click.option("--sql_engine", help="Filepath for SQLite database file.")
@click.option(
    "--dest_path",
    default=None,
    help="Destination filepath for fixed sqlite database file.",
)
@click.option(
    "--table_name",
    default=None,
    help="Optional table name to focus on for linting actions.",
)
@click.option(
    "--column_name",
    default=None,
    help="Optional column name to focus on for linting actions.",
)
@click.option(
    "--inplace",
    default=True,
    help=".",
)
def fix(
    sql_engine: str,
    dest_path: Optional[str] = None,
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    inplace: bool = True,
):
    """
    Runs sqlite-clean fix functionality through command-line
    """
    for func in [item["ref"] for item in SQLITE_CLEAN_CATALOG["fix"]]:
        func(sql_engine, dest_path, table_name, column_name, inplace)  # type: ignore
