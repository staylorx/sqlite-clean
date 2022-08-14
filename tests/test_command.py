""" Tests for sqlite_clean.command """

from click.testing import CliRunner

from sqlite_clean.command import fix, lint


def test_command_lint(database_engine_for_testing):
    """
    Test lint command
    """
    sql_filepath = str(database_engine_for_testing.url).replace("sqlite:///", "")
    runner = CliRunner()
    result = runner.invoke(lint, ["--sql_engine", sql_filepath])

    assert result.exit_code == 0
    assert result.output == "Database linted, no issues detected!\n"


def test_command_fix(database_engine_for_testing):
    """
    Test fix command
    """
    sql_filepath = str(database_engine_for_testing.url).replace("sqlite:///", "")
    runner = CliRunner()
    result = runner.invoke(fix, ["--sql_engine", sql_filepath])

    assert result.exit_code == 0
    assert result.output == f"Database fixed at {sql_filepath}!\n"
