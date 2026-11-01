from typer.testing import CliRunner

from backend.cli.app import cli_app
from backend.config import settings


def test_cli_help_lists_env_command():
    result = CliRunner().invoke(cli_app, ["--help"])

    assert result.exit_code == 0
    assert "env" in result.output


def test_cli_env_prints_runtime_env():
    result = CliRunner().invoke(cli_app, ["env"])

    assert result.exit_code == 0
    assert settings.runtime_env in result.output
