import pytest
from click.testing import CliRunner

from rebelist.streamline.handlers.cli import console


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI runner instance."""
    return CliRunner()


def test_console_help(runner: CliRunner) -> None:
    """Check that `--help` returns usage information."""
    result = runner.invoke(console, ['--help'])
    assert result.exit_code == 0
    assert 'Provides commands for executing Streamline workflows' in result.output


def test_version_output(runner: CliRunner) -> None:
    """Check that `--version` returns the correct version output."""
    result = runner.invoke(console, ['--version'])
    assert result.exit_code == 0
    assert 'streamline, version' in result.output.lower()
