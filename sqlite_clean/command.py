"""
sqlite-clean command - provides command-line functionality wrappers
"""

from typing import Optional

import click

from sqlite_clean.catalog import SQLITE_CLEAN_CATALOG
from sqlite_clean.constants import LIKE_NULLS


@click.group()
def cli():
    """
    Utility for linting and fixing SQLite database files.
    """


@cli.command()
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
    # pass LIKE_NULLS tuple as joined string
    # see below notes for like_nulls_tuple
    default=",".join(LIKE_NULLS),
    help="Optional list of null-like values to pass in for linting actions.",
)
def lint(
    sql_engine: str,
    table_name: Optional[str],
    column_name: Optional[str],
    like_nulls: str,
):
    """
    Runs sqlite-clean linting functionality through command-line
    """

    # click doesn't allow for variable length tuple options
    # as a result we input a string for like_nulls and
    # recompose into tuple here for compatibility with linting ops
    like_nulls_tuple = tuple(like_nulls.split(","))

    for func in [item["ref"] for item in SQLITE_CLEAN_CATALOG["lint"]]:
        func(  # type: ignore
            sql_engine=sql_engine,
            table_name=table_name,
            column_name=column_name,
            like_nulls=like_nulls_tuple,
        )

    click.echo("Database linted, no issues detected!")


@cli.command()
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

    if not dest_path:
        dest_path = sql_engine

    click.echo(f"Database fixed at {dest_path}!")
