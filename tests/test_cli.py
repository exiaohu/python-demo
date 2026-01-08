from click.testing import CliRunner
from app.cli import cli
from app.core.config import settings

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert f"{settings.APP_NAME} v{settings.VERSION}" in result.output

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "server" in result.output
    assert "migrate" in result.output
