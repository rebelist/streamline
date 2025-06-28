from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from pymongo import ASCENDING

from streamline.handlers.cli.commands.database_index import DatabaseIndexer, IndexTask, database_index


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI runner instance."""
    return CliRunner()


@pytest.fixture
def mock_collection():
    """Return a mocked MongoDB collection."""
    collection = MagicMock()
    collection.name = 'test_collection'
    return collection


@pytest.fixture
def mock_database() -> MagicMock:
    """Return a mocked MongoDB database with fake collections."""
    db = MagicMock()
    db.__getitem__.side_effect = lambda name: {
        'jobs': MagicMock(name='jobs'),
        'jira_sprints': MagicMock(name='jira_sprints'),
        'jira_tickets': MagicMock(name='jira_tickets'),
    }[name]
    return db


def test_index_task_add_and_execute(mock_collection: MagicMock):
    """Test that IndexTask adds and executes index creation correctly."""
    task = IndexTask(mock_collection)
    assert 'test_collection' in task.description

    task.add_index([('field1', ASCENDING)], unique=True, name='field1_unique_idx')

    assert len(task.indexes) == 1
    assert task.indexes[0]['keys'] == [('field1', ASCENDING)]
    assert task.indexes[0]['unique'] is True
    assert task.indexes[0]['name'] == 'field1_unique_idx'

    task.execute()

    mock_collection.drop_indexes.assert_called_once()
    mock_collection.create_index.assert_called_once_with([('field1', ASCENDING)], unique=True, name='field1_unique_idx')


def test_database_indexer_run(mock_database: MagicMock):
    """Test that DatabaseIndexer builds and executes all index tasks."""
    indexer = DatabaseIndexer(mock_database)

    with patch.object(IndexTask, 'execute') as mock_execute:
        indexer.run()

        # Should be called 3 times: jobs, jira_sprints, jira_tickets
        assert mock_execute.call_count == 3

        mock_database.__getitem__.assert_any_call('jobs')
        mock_database.__getitem__.assert_any_call('jira_sprints')
        mock_database.__getitem__.assert_any_call('jira_tickets')


def test_database_index_command(runner: CliRunner, mock_database: MagicMock):
    """Test the database:index CLI command integration."""
    with patch('streamline.handlers.cli.commands.database_index.DatabaseIndexer.run') as mock_run:
        result = runner.invoke(database_index, obj=MagicMock(database=lambda: mock_database))

        assert result.exit_code == 0
        mock_run.assert_called_once()
