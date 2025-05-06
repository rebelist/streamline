from datetime import datetime

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from pytest_mock import MockerFixture

from streamline.infrastructure.mongo.job import Job, JobRepository


def test_job_to_dict():
    """Test the Job.to_dict method."""
    now = datetime(2025, 5, 6, 19, 39, 0)
    job = Job(name='sync_sprints', team='TestTeam', executed_at=now, metadata={'source': 'jira'})
    expected_dict = {
        'name': 'sync_sprints',
        'team': 'TestTeam',
        'executed_at': now,
        'metadata': {'source': 'jira'},
    }
    assert job.to_dict() == expected_dict


def test_job_from_dict():
    """Test the Job.from_dict method."""
    data = {
        'name': 'sync_tickets',
        'team': 'AnotherTeam',
        'executed_at': datetime(2025, 5, 6, 19, 38, 0),
        'metadata': {'batch_id': 123},
    }
    job = Job.from_dict(data)
    assert job is not None
    assert job.name == 'sync_tickets'
    assert job.team == 'AnotherTeam'
    assert job.executed_at == datetime(2025, 5, 6, 19, 38, 0)
    assert job.metadata == {'batch_id': 123}


def test_job_from_dict_missing_metadata():
    """Test Job.from_dict when metadata is missing."""
    data = {
        'name': 'sync_something',
        'team': 'YetAnotherTeam',
        'executed_at': datetime(2025, 5, 6, 19, 40, 0),
    }
    job = Job.from_dict(data)
    assert job is not None
    assert job.metadata == {}


def test_job_repository_save(mocker: MockerFixture):
    """Test the JobRepository.save method using mocker."""
    mock_collection = mocker.MagicMock(spec=Collection)
    mock_database = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection

    repository = JobRepository(mock_database)
    now = datetime(2025, 5, 6, 19, 41, 0)
    job = Job(name='sync_data', team='DataTeam', executed_at=now, metadata={'run_id': 'abc'})
    repository.save(job)

    mock_database.get_collection.assert_called_once_with(JobRepository.COLLECTION_NAME)
    mock_collection.delete_one.assert_called_once_with({'team': 'DataTeam', 'name': 'sync_data'})
    mock_collection.insert_one.assert_called_once_with(job.to_dict())


def test_job_repository_find_found(mocker: MockerFixture):
    """Test the JobRepository.find method when a job is found using mocker."""
    mock_collection = mocker.MagicMock(spec=Collection)
    mock_database = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection

    found_data = {
        'name': 'analyze_logs',
        'team': 'LogTeam',
        'executed_at': datetime(2025, 5, 6, 19, 42, 0),
        'metadata': {'report_id': 456},
    }
    mock_collection.find_one.return_value = found_data

    repository = JobRepository(mock_database)
    job = repository.find('analyze_logs', 'LogTeam')

    mock_database.get_collection.assert_called_once_with(JobRepository.COLLECTION_NAME)
    mock_collection.find_one.assert_called_once_with({'name': 'analyze_logs', 'team': 'LogTeam'})
    assert job is not None
    assert job.name == 'analyze_logs'
    assert job.team == 'LogTeam'
    assert job.executed_at == datetime(2025, 5, 6, 19, 42, 0)
    assert job.metadata == {'report_id': 456}


def test_job_repository_find_not_found(mocker: MockerFixture):
    """Test the JobRepository.find method when a job is not found using mocker."""
    mock_collection = mocker.MagicMock(spec=Collection)
    mock_database = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection
    mock_collection.find_one.return_value = None

    repository = JobRepository(mock_database)
    job = repository.find('non_existent_job', 'UnknownTeam')

    mock_database.get_collection.assert_called_once_with(JobRepository.COLLECTION_NAME)
    mock_collection.find_one.assert_called_once_with({'name': 'non_existent_job', 'team': 'UnknownTeam'})
    assert job is None


def test_job_repository_find_empty_criteria(mocker: MockerFixture):
    """Test JobRepository.find with empty name or team using mocker."""
    mock_collection = mocker.MagicMock(spec=Collection)
    mock_database = mocker.MagicMock(spec=Database)
    mock_database.get_collection.return_value = mock_collection

    repository = JobRepository(mock_database)

    job_empty_name = repository.find('', 'SomeTeam')
    mock_collection.find_one.assert_not_called()
    assert job_empty_name is None

    job_empty_team = repository.find('SomeJob', '')
    mock_collection.find_one.assert_not_called()
    assert job_empty_team is None
