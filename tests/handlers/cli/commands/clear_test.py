from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from streamline.handlers.cli.commands.clear import DatabaseEraser, clear


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI runner instance."""
    return CliRunner()


@pytest.fixture
def mock_container():
    """Mock the container object."""
    container = MagicMock()
    container.database.return_value = MagicMock()
    return container


def test_clear_command_yes(runner: CliRunner, mock_container: MagicMock) -> None:
    """Test the 'database:clear' command when the user confirms."""
    with patch('streamline.handlers.cli.commands.clear.click.confirm', return_value=True) as mock_confirm:
        with patch.object(DatabaseEraser, 'run') as mock_database_eraser_run:
            result = runner.invoke(clear, obj=mock_container, input='y\n')  # Simulate 'yes' input

            assert result.exit_code == 0
            mock_confirm.assert_called_once()
            mock_database_eraser_run.assert_called_once()
            mock_container.database.assert_called_once()


def test_clear_command_no(runner: CliRunner, mock_container: MagicMock) -> None:
    """Test the 'database:clear' command when the user declines."""
    with patch('streamline.handlers.cli.commands.clear.click.confirm', return_value=False) as mock_confirm:
        with patch.object(DatabaseEraser, 'run') as mock_database_eraser_run:
            result = runner.invoke(clear, obj=mock_container, input='n\n')  # Simulate 'no' input

            assert result.exit_code == 0
            mock_confirm.assert_called_once()
            mock_database_eraser_run.assert_not_called()
            assert 'Bye!' in result.output
            mock_container.database.assert_not_called()


def test_database_eraser_run(mocker: pytest.MonkeyPatch) -> None:
    """Test the DatabaseEraser.run method."""
    mock_database = MagicMock()
    mock_database.list_collection_names.return_value = ['collection1', 'collection2']
    mock_collection1 = MagicMock(name='collection1')
    mock_collection2 = MagicMock(name='collection2')
    mock_database.__getitem__.side_effect = {'collection1': mock_collection1, 'collection2': mock_collection2}.get
    mock_delete_many = MagicMock()
    mock_collection1.delete_many = mock_delete_many
    mock_collection2.delete_many = mock_delete_many
