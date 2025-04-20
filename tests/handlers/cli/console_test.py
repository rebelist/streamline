from typing import cast

from click import BaseCommand
from click.testing import CliRunner
from pytest_mock import MockerFixture

from streamline.config import settings


def test_console_version(mocker: MockerFixture) -> None:
    """Test that the --version option works correctly."""
    mocker.patch.dict(settings.app, {'version': '1.2.3', 'name': 'streamline-cli'})
    from streamline.handlers.cli import console

    console: BaseCommand = cast(BaseCommand, console)
    runner = CliRunner()
    result = runner.invoke(console, ['--version'])
    assert result.exit_code == 0
    assert 'streamline-cli, version 1.2.3' in result.output


def test_console_help(mocker: MockerFixture) -> None:
    """Test that the help command works correctly."""
    mocker.patch.dict(settings.app, {'version': '1.2.3', 'name': 'streamline-cli'})
    from streamline.handlers.cli import console

    console: BaseCommand = cast(BaseCommand, console)
    runner = CliRunner()
    result = runner.invoke(console, ['--help'])
    assert result.exit_code == 0
    assert 'Provides commands for executing Streamline workflows and utilities.' in result.output
    assert 'synchronizer' in result.output  # Ensure the synchronizer command is listed
