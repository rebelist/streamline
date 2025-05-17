from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from streamline.application.ingestion.models import Executable
from streamline.handlers.cli.commands.database_synchronize import Synchronizer, database_synchronize


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI runner instance."""
    return CliRunner()


@pytest.fixture
def mock_container():
    """Mock the container object."""
    container = MagicMock()
    container.sprint_job.return_value = MagicMock(spec=Executable, __doc__='Mock Sprint Job')
    container.ticket_job.return_value = MagicMock(spec=Executable, __doc__='Mock Ticket Job')
    return container


def test_synchronizer_command(runner: CliRunner, mock_container: MagicMock, mocker: MockerFixture) -> None:
    """Test the 'database:synchronize' command."""
    mock_synchronizer_run = mocker.patch.object(Synchronizer, 'run')

    result = runner.invoke(database_synchronize, obj=mock_container)

    assert result.exit_code == 0
    mock_container.sprint_job.assert_called_once()
    mock_container.ticket_job.assert_called_once()
    mock_synchronizer_run.assert_called_once()


def test_synchronizer_run(mocker: MockerFixture):
    """Test the Synchronizer.run method."""
    mock_job1 = MagicMock(spec=Executable, __doc__='Job 1')
    mock_job2 = MagicMock(spec=Executable, __doc__='Job 2')
    sync = Synchronizer()
    sync.register(mock_job1)
    sync.register(mock_job2)
    sync.run()
    mock_job1.execute.assert_called_once()
    mock_job2.execute.assert_called_once()
